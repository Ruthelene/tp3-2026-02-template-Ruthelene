"""T6 — Paginas da tabela t.

Registre em resultados/t06.json: relpages, reltuples, bytes (pg_relation_size), block_size,
paginas_pelo_tamanho (bytes / block_size), tuplas_por_pagina. Faça ANALYZE antes.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t06", ...)
    raise NotImplementedError("t06_paginas")


if __name__ == "__main__":
    main()
