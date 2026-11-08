"""T7 — Estatisticas e blocos lidos.

Registre em resultados/t07.json: valor_consultado, pg_stats (lista, um item por atributo de t),
heap_blks_read e heap_blks_hit (pg_statio_user_tables depois de uma consulta v = valor,
zerando antes os contadores da tabela e forçando o flush das estatisticas),
explain_buffers {hit, read} da mesma consulta.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t07", ...)
    raise NotImplementedError("t07_estatisticas")


if __name__ == "__main__":
    main()
