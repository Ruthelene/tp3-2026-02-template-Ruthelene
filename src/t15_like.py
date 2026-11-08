"""T15 - LIKE e indices: planos antes e depois de criar os indices adequados (que ficam no banco)."""
from common import conectar, explain, salvar, tipos_de_no
from params import carregar

INDICES = {
    "movie_title_pattern": "CREATE INDEX movie_title_pattern ON movie (title text_pattern_ops)",
    "movie_title_substr": "CREATE INDEX movie_title_substr ON movie (substr(title, 1, 1))",
    "movie_title_reverse": "CREATE INDEX movie_title_reverse ON movie (reverse(title) text_pattern_ops)",
}


def medir(cur, sql):
    plano = explain(cur, sql, analyze=False)
    cur.execute(f"SELECT count(*) FROM ({sql}) q")
    return {"sql": sql, "linhas": cur.fetchone()[0], "nos": tipos_de_no(plano), "custo": plano["Plan"]["Total Cost"]}


def medir_todas(cur, consultas, diagnostico=False):
    saida = {}
    for nome, sql in consultas.items():
        saida[nome] = medir(cur, sql)
        if diagnostico:
            # mesma consulta com a varredura sequencial desligada: mostra se o indice seria possivel
            cur.execute("SET enable_seqscan = off")
            plano = explain(cur, sql, analyze=False)
            cur.execute("RESET enable_seqscan")
            saida[nome]["nos_sem_seqscan"] = tipos_de_no(plano)
            saida[nome]["custo_sem_seqscan"] = plano["Plan"]["Total Cost"]
        print(nome, saida[nome]["nos"], saida[nome]["custo"])
    return saida


def main():
    p = carregar()
    pre, suf = p["movie_letra_prefixo"], p["movie_letra_sufixo"]
    consultas = {
        "prefixo_like": f"SELECT * FROM movie WHERE title LIKE '{pre}%'",
        "prefixo_substr": f"SELECT * FROM movie WHERE substr(title, 1, 1) = '{pre}'",
        "sufixo_like": f"SELECT * FROM movie WHERE title LIKE '%{suf}'",
        "sufixo_reverse": f"SELECT * FROM movie WHERE reverse(title) LIKE '{suf}%'",
    }
    with conectar() as con, con.cursor() as cur:
        for nome in INDICES:
            cur.execute(f"DROP INDEX IF EXISTS {nome}")
        cur.execute("ANALYZE movie")
        antes = medir_todas(cur, consultas)
        for ddl in INDICES.values():
            cur.execute(ddl)
        cur.execute("ANALYZE movie")
        depois = medir_todas(cur, consultas, diagnostico=True)
    salvar("t15", {"antes": antes, "depois": depois, "indices_criados": INDICES})


if __name__ == "__main__":
    main()