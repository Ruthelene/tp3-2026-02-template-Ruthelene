"""T16 - Estimativa de seletividade: estatisticas padrao x SET STATISTICS 1000 sobre votes."""
from common import conectar, explain, salvar
from params import carregar


def medir(cur, p):
    saida = {}
    for nome, sql in (("baixo", f"SELECT * FROM movie WHERE votes < {p['movie_votos_baixo']}"),
                      ("alto", f"SELECT * FROM movie WHERE votes > {p['movie_votos_alto']}")):
        plano = explain(cur, sql, analyze=False)
        cur.execute(f"SELECT count(*) FROM ({sql}) q")
        saida[nome] = {"sql": sql, "estimadas": plano["Plan"]["Plan Rows"], "reais": cur.fetchone()[0],
                       "no": plano["Plan"]["Node Type"]}
    return saida


def histograma(cur):
    cur.execute("SELECT histogram_bounds::text FROM pg_stats WHERE tablename = 'movie' AND attname = 'votes'")
    return cur.fetchone()[0]


def main():
    p = carregar()
    with conectar() as con, con.cursor() as cur:
        cur.execute("ALTER TABLE movie ALTER COLUMN votes SET STATISTICS -1")
        cur.execute("ANALYZE movie")
        padrao = medir(cur, p)
        hist_padrao = histograma(cur)
        cur.execute("ALTER TABLE movie ALTER COLUMN votes SET STATISTICS 1000")
        cur.execute("ANALYZE movie")
        stat1000 = medir(cur, p)
        hist_1000 = histograma(cur)
        cur.execute("ALTER TABLE movie ALTER COLUMN votes SET STATISTICS -1")  # restaura o padrao
        cur.execute("ANALYZE movie")
    salvar("t16", {"padrao": padrao, "statistics_1000": stat1000,
                   "histograma_padrao": hist_padrao,
                   "n_faixas_histograma_padrao": hist_padrao.count(","),
                   "n_faixas_histograma_1000": hist_1000.count(",")})
    print(padrao, stat1000)


if __name__ == "__main__":
    main()