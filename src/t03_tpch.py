"""T3 - TPC-H carregado: linhas e tamanho de cada uma das 8 tabelas."""
from common import conectar, salvar
from params import carregar

TABELAS = ["region", "nation", "part", "supplier", "partsupp", "customer", "orders", "lineitem"]


def main():
    p = carregar()
    saida = {}
    with conectar() as con, con.cursor() as cur:
        for t in TABELAS:
            cur.execute(f"SELECT count(*) FROM {t}")
            linhas = cur.fetchone()[0]
            cur.execute("SELECT pg_relation_size(%s::regclass), pg_total_relation_size(%s::regclass)", (t, t))
            tabela, total = cur.fetchone()
            saida[t] = {"linhas": linhas, "bytes_tabela": tabela, "bytes_total": total}
    salvar("t03", {"sf": p["sf"], "tabelas": saida})


if __name__ == "__main__":
    main()
