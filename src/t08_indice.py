"""T8 — Indice em v.

Para n = 100.000 e n = 1.000.000 (recriando t com a mesma seed) registre em resultados/t08.json
uma lista de dicts: n, valor, tempo_consulta_ms, no_raiz_consulta, tempo_criacao_ms, tempo_recriacao_ms,
indice: {paginas, altura, paginas_folha, densidade_media_folha}.
Use SET max_parallel_maintenance_workers = 0 para tornar a construcao do indice reprodutivel.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t08", ...)
    raise NotImplementedError("t08_indice")


if __name__ == "__main__":
    main()
