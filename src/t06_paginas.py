"""T6 - Paginas da tabela t."""
from common import conectar, salvar


def main():
    with conectar() as con, con.cursor() as cur:
        cur.execute("ANALYZE t")
        cur.execute("SELECT relpages, reltuples FROM pg_class WHERE relname = 't'")
        relpages, reltuples = cur.fetchone()
        cur.execute("SELECT pg_relation_size('t'), current_setting('block_size')::int")
        bytes_t, bloco = cur.fetchone()
        cur.execute("SELECT count(*) FROM t")
        tuplas = cur.fetchone()[0]
    salvar("t06", {
        "relpages": relpages,
        "reltuples": reltuples,
        "bytes": bytes_t,
        "block_size": bloco,
        "paginas_pelo_tamanho": bytes_t // bloco,
        "tuplas": tuplas,
        "tuplas_por_pagina": tuplas / relpages,
    })


if __name__ == "__main__":
    main()