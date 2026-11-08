"""T17 - Reserva de assentos com varios agentes concorrentes (versoes a e b; READ COMMITTED e SERIALIZABLE).

Tabela assentos(num_voo, disp): num_voo identifica cada assento (1..N) e disp diz se esta disponivel.
Passos de uma reserva: (1) listar os disponiveis, (2) escolher um ao acaso e esperar tempo_escolha_s,
(3) registrar a reserva com UPDATE ... WHERE num_voo = X AND disp = true.
  versao a: os 3 passos em uma unica transacao.
  versao b: uma transacao para o passo 1, o passo 2 fora de transacao e outra transacao para o passo 3.
Conflito (reserva refeita): UPDATE que nao altera linha (assento ja tomado), falha de serializacao (40001)
ou deadlock (40P01). Cada reserva concluida e gravada em reservas_log(config, cliente, assento, tentativas).
"""
import queue
import random
import threading
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import psycopg  # noqa: E402

from common import RESULTADOS, conectar, salvar  # noqa: E402
from params import carregar  # noqa: E402

ISOLAMENTOS = {
    "read_committed": psycopg.IsolationLevel.READ_COMMITTED,
    "serializable": psycopg.IsolationLevel.SERIALIZABLE,
}
VERSOES = ["a", "b"]


def preparar_tabelas(cur, n):
    cur.execute("DROP TABLE IF EXISTS assentos")
    cur.execute("CREATE TABLE assentos (num_voo integer PRIMARY KEY, disp boolean NOT NULL DEFAULT true)")
    cur.execute("INSERT INTO assentos SELECT g, true FROM generate_series(1, %s) g", (n,))
    cur.execute("ANALYZE assentos")


def listar_livres(cur):
    cur.execute("SELECT num_voo FROM assentos WHERE disp = true")
    return [r[0] for r in cur.fetchall()]


def registrar(cur, assento):
    """Passo 3: so atualiza se o assento ainda estiver livre. Retorna True se conseguiu."""
    cur.execute("UPDATE assentos SET disp = false WHERE num_voo = %s AND disp = true", (assento,))
    return cur.rowcount == 1


def reservar_a(con, rnd, espera):
    """Versao a: passos 1, 2 e 3 na mesma transacao. Retorna o assento ou None (assento ja tomado)."""
    cur = con.cursor()
    livres = listar_livres(cur)
    if not livres:
        con.rollback()
        return None
    assento = rnd.choice(livres)
    time.sleep(espera)
    if not registrar(cur, assento):
        con.rollback()
        return None
    con.commit()
    return assento


def reservar_b(con, rnd, espera):
    """Versao b: transacao do passo 1, espera fora de transacao, transacao do passo 3."""
    cur = con.cursor()
    livres = listar_livres(cur)
    con.commit()
    if not livres:
        return None
    assento = rnd.choice(livres)
    time.sleep(espera)
    if not registrar(cur, assento):
        con.rollback()
        return None
    con.commit()
    return assento


def agente(versao, isolamento, fila, resultados, conflitos, erros, barreira, espera):
    reservar = reservar_a if versao == "a" else reservar_b
    rnd = random.Random()
    contagem = {"assento_tomado": 0, "falha_serializacao": 0, "deadlock": 0}
    try:
        con = conectar(autocommit=False)
        con.isolation_level = ISOLAMENTOS[isolamento]
        barreira.wait()
        feitos = []
        while True:
            try:
                cliente = fila.get_nowait()
            except queue.Empty:
                break
            tentativas = 0
            while True:
                tentativas += 1
                try:
                    assento = reservar(con, rnd, espera)
                except psycopg.errors.SerializationFailure:
                    con.rollback()
                    contagem["falha_serializacao"] += 1
                    continue
                except psycopg.errors.DeadlockDetected:
                    con.rollback()
                    contagem["deadlock"] += 1
                    continue
                if assento is None:
                    contagem["assento_tomado"] += 1
                    continue
                break
            feitos.append((cliente, assento, tentativas))
        con.close()
        resultados.extend(feitos)
    except Exception as e:  # noqa: BLE001 - registra o erro para a thread principal
        erros.append(repr(e))
        try:
            barreira.abort()
        except Exception:  # noqa: BLE001
            pass
    finally:
        conflitos.append(contagem)


def experimento(cur, versao, isolamento, k, n, espera):
    preparar_tabelas(cur, n)
    fila = queue.Queue()
    for c in range(1, n + 1):
        fila.put(c)
    resultados, conflitos, erros = [], [], []
    barreira = threading.Barrier(k + 1)
    threads = [threading.Thread(target=agente, args=(versao, isolamento, fila, resultados, conflitos, erros,
                                                      barreira, espera)) for _ in range(k)]
    for t in threads:
        t.start()
    try:
        barreira.wait()
    except threading.BrokenBarrierError:
        pass
    t0 = time.perf_counter()
    for t in threads:
        t.join()
    total = time.perf_counter() - t0
    if erros:
        raise RuntimeError(f"erro em agente: {erros[0]}")
    cur.execute("SELECT count(*) FROM assentos WHERE NOT disp")
    ocupados = cur.fetchone()[0]
    assentos_usados = {a for _, a, _ in resultados}
    if len(resultados) != n or len(assentos_usados) != n or ocupados != n:
        raise RuntimeError(f"inconsistencia: {len(resultados)} reservas, {len(assentos_usados)} assentos distintos, "
                           f"{ocupados} ocupados (esperado {n})")
    cfg = f"{versao}/{isolamento}/k={k}"
    cur.executemany("INSERT INTO reservas_log (config, cliente, assento, tentativas) VALUES (%s, %s, %s, %s)",
                    [(cfg, c, a, t) for c, a, t in resultados])
    tent = [t for _, _, t in resultados]
    soma = {chave: sum(c[chave] for c in conflitos) for chave in ("assento_tomado", "falha_serializacao", "deadlock")}
    return {
        "versao": versao,
        "isolamento": isolamento,
        "k": k,
        "tempo_total_s": total,
        "reservas": len(resultados),
        "tentativas_max": max(tent),
        "tentativas_min": min(tent),
        "tentativas_media": sum(tent) / len(tent),
        "tentativas_total": sum(tent),
        "conflitos": soma,
    }


def grafico(exps, versao, isolamento):
    pontos = sorted((e["k"], e["tempo_total_s"]) for e in exps if e["versao"] == versao and e["isolamento"] == isolamento)
    plt.figure(figsize=(6, 4))
    plt.plot([p[0] for p in pontos], [p[1] for p in pontos], marker="o")
    plt.xlabel("numero de agentes (k)")
    plt.ylabel("tempo total (s)")
    plt.title(f"Reservas - versao {versao}, {isolamento}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTADOS / f"t18_{versao}_{isolamento}.png", dpi=120)
    plt.close()


def grafico_comparativo(exps):
    plt.figure(figsize=(7, 4.5))
    for v in VERSOES:
        for iso in ISOLAMENTOS:
            pontos = sorted((e["k"], e["tempo_total_s"]) for e in exps if e["versao"] == v and e["isolamento"] == iso)
            plt.plot([p[0] for p in pontos], [p[1] for p in pontos], marker="o", label=f"{v} / {iso}")
    plt.xlabel("numero de agentes (k)")
    plt.ylabel("tempo total (s)")
    plt.title("Reservas - todas as configuracoes")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(RESULTADOS / "t18_comparativo.png", dpi=120)
    plt.close()


def main():
    p = carregar()
    n, espera = p["assentos"], p["tempo_escolha_s"]
    RESULTADOS.mkdir(exist_ok=True)
    exps = []
    with conectar() as setup, setup.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS reservas_log")
        cur.execute("CREATE TABLE reservas_log (config text, cliente integer, assento integer, tentativas integer)")
        for versao in VERSOES:
            for iso in ISOLAMENTOS:
                for k in p["agentes"]:
                    e = experimento(cur, versao, iso, k, n, espera)
                    exps.append(e)
                    print(f"{versao}/{iso}/k={k}: {e['tempo_total_s']:.2f}s, tentativas media "
                          f"{e['tentativas_media']:.2f} (max {e['tentativas_max']}), conflitos {e['conflitos']}")
    salvar("t17", {"assentos": n, "tempo_escolha_s": espera, "experimentos": exps})
    for versao in VERSOES:
        for iso in ISOLAMENTOS:
            grafico(exps, versao, iso)
    grafico_comparativo(exps)
    print("graficos gravados em resultados/t18_*.png")


if __name__ == "__main__":
    main()