"""T5 - Tabela t com 100.000 tuplas (seed individual)."""
from common import conectar, salvar
from params import carregar
from tabela_t import criar_t


def main():
    p = carregar()
    with conectar() as con, con.cursor() as cur:
        criar_t(cur, 100_000, p["t_seed"], p["t_cardinalidade_v"])
        cur.execute("SELECT k, v FROM t ORDER BY k LIMIT 10")
        primeiras = [list(x) for x in cur.fetchall()]
        cur.execute("SELECT sum(v), count(*) FROM t")
        soma, n = cur.fetchone()
    salvar("t05", {"primeiras_10": primeiras, "soma_v": int(soma), "tuplas": n})


if __name__ == "__main__":
    main()