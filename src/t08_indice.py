"""T8 - Indice B-tree sobre v para 100.000 e 1.000.000 de tuplas."""
from common import conectar, explain, salvar
from params import carregar
from tabela_t import criar_t, info_indice, tempo, tempo_consulta


def main():
    p = carregar()
    valor = p["t_cardinalidade_v"] // 2
    consulta = f"SELECT * FROM t WHERE v = {valor}"
    saida = []
    with conectar() as con, con.cursor() as cur:
        cur.execute("SET max_parallel_maintenance_workers = 0")
        for n in (100_000, 1_000_000):
            criar_t(cur, n, p["t_seed"], p["t_cardinalidade_v"])
            t_criacao = tempo(cur, "CREATE INDEX t_v ON t(v)")
            no_raiz = explain(cur, consulta)["Plan"]["Node Type"]
            t_consulta = tempo_consulta(cur, consulta)
            info = info_indice(cur, "t_v")
            cur.execute("DROP INDEX t_v")
            t_recriacao = tempo(cur, "CREATE INDEX t_v ON t(v)")
            saida.append({
                "n": n,
                "valor": valor,
                "tempo_consulta_ms": t_consulta,
                "no_raiz_consulta": no_raiz,
                "tempo_criacao_ms": t_criacao,
                "tempo_recriacao_ms": t_recriacao,
                "indice": info,
            })
            print(n, info, no_raiz)
    salvar("t08", saida)


if __name__ == "__main__":
    main()