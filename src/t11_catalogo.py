"""T11 — Metadados dos indices de movie.

Para cada indice de movie (movie_key, movie_title, movie_votes) registre em resultados/t11.json:
indice, tabela, atributo, altura, max_chaves_por_bloco_folha, media_chaves_por_bloco_folha, blocos_folha,
media_blocos_folha_por_chave, media_blocos_dados_por_chave, linhas, chaves_distintas.
Fontes: pgstatindex, bt_page_stats (pageinspect), pg_stats, pg_class.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t11", ...)
    raise NotImplementedError("t11_catalogo")


if __name__ == "__main__":
    main()
