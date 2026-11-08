"""Autoverificacao do TP3 (o mesmo teste e usado na correcao).

Confere que os numeros em resultados/*.json batem com o que o PostgreSQL
produz agora, sobre o banco carregado pela propria execucao do aluno.
Uso: make test   (apos make load e make parteI ... parteIV)
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "src")
from common import conectar  # noqa: E402
from params import carregar, gerar  # noqa: E402
from tabela_t import criar_t, info_indice  # noqa: E402

RES = Path("resultados")
placar = []


def check(grupo, nome, ok, detalhe=""):
    placar.append((grupo, nome, bool(ok), detalhe))
    print(f"[{'ok' if ok else 'FALHOU':6}] {grupo} {nome} {detalhe if not ok else ''}")
    return bool(ok)


def ler(nome):
    f = RES / f"{nome}.json"
    if not f.exists():
        return None
    return json.loads(f.read_text())


def perto(a, b, tol=0.02):
    return abs(a - b) <= max(1, tol * max(abs(a), abs(b)))


def tem_indice(nos):
    return any("Index" in n or "Bitmap" in n for n in nos)


def so_leitura(con, sql):
    """Executa SQL do aluno somente para leitura (EXPLAIN / contagem)."""
    s = sql.strip().rstrip(";")
    if not s.lower().startswith("select"):
        raise ValueError("apenas SELECT")
    return s


def ordem_dos_commits():
    """docs/previsao.md deve ter sido commitado antes de resultados/ (None se nao ha repositorio git)."""
    def primeiro(caminho):
        r = subprocess.run(["git", "-c", "safe.directory=/app", "log", "--reverse", "--format=%ct", "--", caminho],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return "sem-git"
        linhas = r.stdout.split()
        return int(linhas[0]) if linhas else None
    return primeiro("docs/previsao.md"), primeiro("resultados")


def main():
    p = carregar()
    check("rito", "params.json bate com a matricula", p == gerar(p["matricula"]))
    prev, res = ordem_dos_commits()
    if prev != "sem-git":
        check("rito", "docs/previsao.md versionado antes de resultados/", prev is not None and (res is None or prev <= res),
              "previsao.md ausente do historico" if prev is None else "")
    check("rito", "relatorio docs/tp3_relatorio.pdf presente",
          Path("docs/tp3_relatorio.pdf").exists() and Path("docs/tp3_relatorio.pdf").stat().st_size > 5000)
    con = conectar()
    cur = con.cursor()

    # ---------------- Parte I ----------------
    r = ler("t01")
    if check("I.T1", "resultado presente", r):
        pg = {}
        for k in r["postgres"]:
            cur.execute(f"SHOW {k}")
            pg[k] = cur.fetchone()[0]
        check("I.T1", "parametros do PostgreSQL batem", pg == r["postgres"])
        check("I.T1", "cpu/ram/so/kernel preenchidos", all(r.get(k) for k in ("cpu_modelo", "ram_mb", "so", "kernel")))
        check("I.T1", "informacoes de cache", bool(r.get("caches")))
    r = ler("t02")
    if check("I.T2", "resultado presente", r):
        fs = int(subprocess.run(["stat", "-f", "-c", "%S", "/app"], capture_output=True, text=True).stdout)
        cur.execute("SHOW block_size")
        check("I.T2", "bloco do sistema de arquivos", r["fs_bloco_fundamental"] == fs)
        check("I.T2", "bloco do PostgreSQL", r["pg_block_size"] == int(cur.fetchone()[0]))
        check("I.T2", "razao aleatorio/sequencial medida", r["leitura"]["razao_custo_aleatorio_sequencial"] > 0)
    r = ler("t03")
    if check("I.T3", "resultado presente", r):
        sf = p["sf"]
        esperado = {"orders": 1_500_000 * sf, "customer": 150_000 * sf, "part": 200_000 * sf,
                    "supplier": 10_000 * sf, "partsupp": 800_000 * sf, "nation": 25, "region": 5}
        check("I.T3", "SF da carga e o da matricula", r["sf"] == sf)
        for t, n in esperado.items():
            cur.execute(f"SELECT count(*) FROM {t}")
            real = cur.fetchone()[0]
            check("I.T3", f"{t}: relatado = banco = esperado", r["tabelas"][t]["linhas"] == real and perto(real, n, 0.001), f"{r['tabelas'][t]['linhas']} {real} {n}")
        cur.execute("SELECT count(*), (SELECT count(*) FROM orders) FROM lineitem")
        li, od = cur.fetchone()
        check("I.T3", "lineitem: relatado = banco", r["tabelas"]["lineitem"]["linhas"] == li and 3 * od < li < 5 * od)
    r = ler("t04")
    if check("I.T4", "resultado presente", r):
        check("I.T4", "consultas sao as da matricula", sorted(r) == [f"q{n:02d}" for n in p["tpch_consultas"]], str(sorted(r)))
        for q, d in (r or {}).items():
            sql = Path(f"queries/tpch_aluno/{q}.sql").read_text().strip().rstrip(";")
            cur.execute(f"SELECT count(*) FROM ({sql}) x")
            check("I.T4", f"{q}: linhas reais batem", cur.fetchone()[0] == d["linhas_reais"])
            check("I.T4", f"{q}: plano registrado", bool(d["nos"]))

    # ---------------- Parte II ----------------
    seed, card = p["t_seed"], p["t_cardinalidade_v"]
    con.execute("SET max_parallel_maintenance_workers = 0")
    criar_t(cur, 100_000, seed, card, "t_chk")
    r = ler("t05")
    if check("II.T5", "resultado presente", r):
        cur.execute("SELECT k, v FROM t_chk ORDER BY k LIMIT 10")
        check("II.T5", "10 primeiras tuplas batem com a seed", [list(x) for x in cur.fetchall()] == [list(x) for x in r["primeiras_10"]])
        cur.execute("SELECT sum(v) FROM t_chk")
        check("II.T5", "soma de v bate com a seed", int(cur.fetchone()[0]) == r["soma_v"])
    r = ler("t06")
    if check("II.T6", "resultado presente", r):
        cur.execute("SELECT relpages FROM pg_class WHERE relname = 't_chk'")
        check("II.T6", "relpages bate", cur.fetchone()[0] == r["relpages"])
        check("II.T6", "paginas pelo tamanho = relpages", r["paginas_pelo_tamanho"] == r["relpages"])
    r = ler("t07")
    if check("II.T7", "resultado presente", r):
        check("II.T7", "valor consultado e pg_stats", r["valor_consultado"] is not None and len(r["pg_stats"]) >= 2)
        check("II.T7", "blocos lidos registrados", r["heap_blks_hit"] + r["heap_blks_read"] > 0)
    for n, nome in ((100_000, "100k"), (1_000_000, "1M")):
        pass
    r = ler("t08")
    if check("II.T8", "resultado presente", r):
        for item in r:
            criar_t(cur, item["n"], seed, card, "t_chk")
            cur.execute("DROP INDEX IF EXISTS t_chk_v")
            cur.execute("CREATE INDEX t_chk_v ON t_chk(v)")
            ref = info_indice(cur, "t_chk_v")
            check("II.T8", f"n={item['n']}: altura do indice", ref["altura"] == item["indice"]["altura"])
            check("II.T8", f"n={item['n']}: paginas do indice", perto(ref["paginas"], item["indice"]["paginas"]), f"{ref['paginas']} {item['indice']['paginas']}")
    criar_t(cur, 1_000_000, seed, card, "t_chk")
    for nome, ordem, ffs in (("t09", "", p["fillfactors"]), ("t10", " DESC NULLS FIRST", [100] + p["fillfactors"])):
        r = ler(nome)
        if check(f"II.{nome.upper()}", "resultado presente", r):
            check(f"II.{nome.upper()}", "fillfactors da matricula", [x["fillfactor"] for x in r] == ffs, str([x["fillfactor"] for x in r]))
            for item in r:
                cur.execute("DROP INDEX IF EXISTS t_chk_v")
                cur.execute(f"CREATE INDEX t_chk_v ON t_chk(v{ordem}) WITH (fillfactor = {item['fillfactor']})")
                ref = info_indice(cur, "t_chk_v")
                check(f"II.{nome.upper()}", f"ff={item['fillfactor']}: paginas e altura",
                      perto(ref["paginas"], item["indice"]["paginas"]) and ref["altura"] == item["indice"]["altura"],
                      f"{ref} {item['indice']}")
    cur.execute("DROP TABLE IF EXISTS t_chk")

    # ---------------- Parte III ----------------
    cur.execute("SELECT count(*) FROM movie")
    total = cur.fetchone()[0]
    r = ler("t11")
    if check("III.T11", "resultado presente", r):
        nomes = {x["indice"] for x in r}
        check("III.T11", "tres indices do catalogo", {"movie_key", "movie_title", "movie_votes"} <= nomes, str(nomes))
        for x in r:
            cur.execute("SELECT tree_level, leaf_pages FROM pgstatindex(%s)", (x["indice"],))
            alt, fol = cur.fetchone()
            check("III.T11", f"{x['indice']}: altura e folhas", x["altura"] == alt and x["blocos_folha"] == fol)
    r = ler("t12")
    if check("III.T12", "resultado presente", r):
        sql = so_leitura(con, r["pequena"]["sql"])
        cur.execute(f"SELECT count(*) FROM ({sql}) q")
        n = cur.fetchone()[0]
        cur.execute(f"EXPLAIN (FORMAT JSON) {sql}")
        no = cur.fetchone()[0][0]["Plan"]["Node Type"]
        check("III.T12", "pequena: < 10 tuplas", n < 10 and n == r["pequena"]["linhas"])
        check("III.T12", "pequena: usa indice", "Index" in no or "Bitmap" in no, no)
        sql = so_leitura(con, r["grande"]["sql"])
        cur.execute(f"SELECT count(*) FROM ({sql}) q")
        n = cur.fetchone()[0]
        cur.execute(f"EXPLAIN (FORMAT JSON) {sql}")
        no = cur.fetchone()[0][0]["Plan"]["Node Type"]
        check("III.T12", "grande: > 80% das tuplas", n > 0.8 * total and n == r["grande"]["linhas"])
        check("III.T12", "grande: varredura sequencial", no == "Seq Scan", no)
        x = r["limiar_votos_menor_que"]
        cur.execute(f"EXPLAIN (FORMAT JSON) SELECT * FROM movie WHERE votes < {x}")
        a = cur.fetchone()[0][0]["Plan"]["Node Type"]
        cur.execute(f"EXPLAIN (FORMAT JSON) SELECT * FROM movie WHERE votes < {x - 200}")
        b = cur.fetchone()[0][0]["Plan"]["Node Type"]
        check("III.T12", "limiar: plano muda em torno do valor relatado", a == "Seq Scan" and b != "Seq Scan", f"{a} {b}")
    r = ler("t13")
    if check("III.T13", "resultado presente", r):
        for k in ("max", "all"):
            sql = so_leitura(con, r[k]["sql"])
            cur.execute(f"EXPLAIN (FORMAT JSON) {sql}")
            custo = cur.fetchone()[0][0]["Plan"]["Total Cost"]
            check("III.T13", f"{k}: custo reproduzido", perto(custo, r[k]["custo"], 0.01), f"{custo} {r[k]['custo']}")
        check("III.T13", "as duas consultas devolvem o mesmo resultado", r["max"]["resultado"] == r["all"]["resultado"])
    r = ler("t14")
    if check("III.T14", "resultado presente", r):
        check("III.T14", "titulo-alvo da matricula", r["titulo_alvo"] == p["movie_titulo_alvo"])
        for k in ("subconsulta", "juncao"):
            sql = so_leitura(con, r[k]["sql"])
            cur.execute(f"SELECT count(*) FROM ({sql}) q")
            check("III.T14", f"{k}: linhas batem", cur.fetchone()[0] == r[k]["linhas"])
            check("III.T14", f"{k}: usa o titulo-alvo", p["movie_titulo_alvo"] in r[k]["sql"])
    r = ler("t15")
    if check("III.T15", "resultado presente", r):
        pre, suf = p["movie_letra_prefixo"], p["movie_letra_sufixo"]
        for k, d in r["depois"].items():
            sql = so_leitura(con, d["sql"])
            cur.execute(f"EXPLAIN (FORMAT JSON) {sql}")
            nos = [cur.fetchone()[0][0]["Plan"]["Node Type"]]
            cur.execute(f"SELECT count(*) FROM ({sql}) q")
            check("III.T15", f"{k}: linhas batem", cur.fetchone()[0] == d["linhas"])
            if k in ("prefixo_like", "prefixo_substr", "sufixo_reverse"):
                check("III.T15", f"{k}: usa indice depois de criar o adequado", tem_indice(nos) or tem_indice(d["nos"]), str(d["nos"]))
        check("III.T15", "antes: prefixo_like nao usava indice", not tem_indice(r["antes"]["prefixo_like"]["nos"]))
        check("III.T15", "indices criados estao no banco", all(
            (cur.execute("SELECT 1 FROM pg_indexes WHERE indexname = %s", (n,)), cur.fetchone())[1] for n in r["indices_criados"]))
    r = ler("t16")
    if check("III.T16", "resultado presente", r):
        for k, d in r["padrao"].items():
            cur.execute(f"SELECT count(*) FROM ({d['sql']}) q")
            check("III.T16", f"{k}: linhas reais batem", cur.fetchone()[0] == d["reais"])
            cur.execute(f"EXPLAIN (FORMAT JSON) {d['sql']}")
            est = cur.fetchone()[0][0]["Plan"]["Plan Rows"]
            check("III.T16", f"{k}: estimativa reproduzida", perto(est, d["estimadas"], 0.05), f"{est} {d['estimadas']}")

    # ---------------- Parte IV ----------------
    r = ler("t17")
    if check("IV.T17", "resultado presente", r):
        check("IV.T17", "numero de assentos da matricula", r["assentos"] == p["assentos"])
        exps = r["experimentos"]
        check("IV.T17", "4 combinacoes x k da matricula",
              len(exps) == 4 * len(p["agentes"]) and sorted({e["k"] for e in exps}) == sorted(p["agentes"]))
        for e in exps:
            cfg = f"{e['versao']}/{e['isolamento']}/k={e['k']}"
            cur.execute("SELECT count(*), count(DISTINCT assento), max(tentativas), min(tentativas), avg(tentativas) "
                        "FROM reservas_log WHERE config = %s", (cfg,))
            n, distintos, mx, mn, md = cur.fetchone()
            check("IV.T17", f"{cfg}: sem assento duplicado e todos atendidos",
                  n == p["assentos"] and distintos == p["assentos"] and e["reservas"] == p["assentos"])
            check("IV.T17", f"{cfg}: retentativas conferem", mx == e["tentativas_max"] and mn == e["tentativas_min"] and abs(float(md) - e["tentativas_media"]) < 0.01)
        for v in "ab":
            for iso in ("read_committed", "serializable"):
                check("IV.T18", f"grafico {v}/{iso}", (RES / f"t18_{v}_{iso}.png").exists())

    total = len(placar)
    ok = sum(1 for _, _, o, _ in placar if o)
    (RES / "check.json").write_text(json.dumps(
        {"verificacoes": total, "ok": ok, "falhas": [f"{g} {n} {d}" for g, n, o, d in placar if not o]},
        indent=2, ensure_ascii=False))
    print(f"\n{ok}/{total} verificacoes ok")
    sys.exit(0 if ok == total else 1)


if __name__ == "__main__":
    main()
