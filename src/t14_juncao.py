"""T14 - Filmes com mais votos que o filme-alvo: subconsulta x auto-juncao."""
from common import conectar, explain, salvar, tipos_de_no
from params import carregar


def medir(cur, sql):
    plano = explain(cur, sql)
    cur.execute(f"SELECT count(*) FROM ({sql}) q")
    return {
        "sql": sql,
        "linhas": cur.fetchone()[0],
        "nos": tipos_de_no(plano),
        "custo": plano["Plan"]["Total Cost"],
        "tempo_ms": plano["Execution Time"],
    }


def main():
    p = carregar()
    alvo = p["movie_titulo_alvo"]
    sub = f"SELECT title, votes FROM movie WHERE votes > (SELECT votes FROM movie WHERE title = '{alvo}')"
    jun = f"SELECT m.title, m.votes FROM movie m JOIN movie a ON m.votes > a.votes WHERE a.title = '{alvo}'"
    with conectar() as con, con.cursor() as cur:
        saida = {"titulo_alvo": alvo, "subconsulta": medir(cur, sub), "juncao": medir(cur, jun)}
    salvar("t14", saida)
    print(saida["subconsulta"]["nos"], saida["subconsulta"]["custo"])
    print(saida["juncao"]["nos"], saida["juncao"]["custo"])


if __name__ == "__main__":
    main()