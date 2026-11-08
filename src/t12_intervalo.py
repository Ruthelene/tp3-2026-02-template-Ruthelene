"""T12 - Consultas por intervalo em movie.votes e limiar a partir do qual o indice deixa de ser usado."""
from common import conectar, explain, salvar, tipos_de_no
from params import carregar


def medir(cur, sql):
    plano = explain(cur, sql)
    raiz = plano["Plan"]
    cur.execute(f"SELECT count(*) FROM ({sql}) q")
    return {
        "sql": sql,
        "linhas": cur.fetchone()[0],
        "nos": tipos_de_no(plano),
        "custo": raiz["Total Cost"],
        "tempo_ms": plano["Execution Time"],
        "buffers": {"hit": raiz.get("Shared Hit Blocks", 0), "read": raiz.get("Shared Read Blocks", 0)},
    }


def tipo_do_plano(cur, x):
    cur.execute(f"EXPLAIN (FORMAT JSON) SELECT * FROM movie WHERE votes < {x}")
    return cur.fetchone()[0][0]["Plan"]["Node Type"]


def main():
    p = carregar()
    with conectar() as con, con.cursor() as cur:
        cur.execute("ANALYZE movie")
        cur.execute("SELECT count(*), max(votes) FROM movie")
        total, maximo = cur.fetchone()
        pequena = medir(cur, f"SELECT * FROM movie WHERE votes > {p['movie_votos_alto']}")
        grande = medir(cur, f"SELECT * FROM movie WHERE votes > {p['movie_votos_baixo']}")
        # menor X (em passos de 50) em que 'votes < X' passa a usar varredura sequencial
        limiar, historico = None, []
        for x in range(50, maximo + 100, 50):
            tipo = tipo_do_plano(cur, x)
            historico.append([x, tipo])
            if tipo == "Seq Scan":
                limiar = x
                break
        cur.execute(f"SELECT count(*) FROM movie WHERE votes < {limiar}")
        linhas_limiar = cur.fetchone()[0]
    salvar("t12", {
        "total_linhas": total,
        "pequena": pequena,
        "grande": grande,
        "fracao_grande": grande["linhas"] / total,
        "limiar_votos_menor_que": limiar,
        "linhas_no_limiar": linhas_limiar,
        "fracao_no_limiar": linhas_limiar / total,
        "plano_por_x": historico,
    })


if __name__ == "__main__":
    main()