"""Carga da base movies (fornecido pelo template; nao editar). Uso: make load-movie"""
from pathlib import Path

from common import conectar


def main():
    sql = Path("queries/movie.sql").read_text()
    with conectar() as con, con.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS movie CASCADE")
        # o script original comeca com 'drop table movie;' (falha se nao existe)
        cur.execute(sql.replace("drop table movie;", ""))
        cur.execute("ANALYZE movie")
        cur.execute("CREATE EXTENSION IF NOT EXISTS pageinspect")
        cur.execute("CREATE EXTENSION IF NOT EXISTS pgstattuple")
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        cur.execute("SELECT count(*) FROM movie")
        print("movie:", cur.fetchone()[0], "linhas")


if __name__ == "__main__":
    main()
