"""T13 - MAX x >= ALL: consultas equivalentes com planos diferentes."""
from common import conectar, explain, salvar, tipos_de_no

CONSULTAS = {
    "max": "SELECT title FROM movie WHERE votes >= (SELECT MAX(votes) FROM movie)",
    "all": "SELECT title FROM movie WHERE votes >= ALL (SELECT votes FROM movie)",
}


def main():
    saida = {}
    with conectar() as con, con.cursor() as cur:
        for nome, sql in CONSULTAS.items():
            plano = explain(cur, sql)
            cur.execute(sql)
            resultado = sorted(linha[0] for linha in cur.fetchall())
            saida[nome] = {
                "sql": sql,
                "resultado": resultado,
                "nos": tipos_de_no(plano),
                "custo": plano["Plan"]["Total Cost"],
                "tempo_ms": plano["Execution Time"],
            }
            print(nome, saida[nome]["nos"], saida[nome]["custo"])
    salvar("t13", saida)


if __name__ == "__main__":
    main()