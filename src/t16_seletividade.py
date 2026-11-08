"""T16 — Estimativa de seletividade.

Para votes < params['movie_votos_baixo'] e votes > params['movie_votos_alto'] registre linhas estimadas x reais
com as estatisticas padrao e com SET STATISTICS 1000 em votes (depois restaure o padrao: SET STATISTICS -1).
resultados/t16.json: padrao e statistics_1000 ({baixo, alto}: {sql, estimadas, reais, no}), histograma_padrao.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t16", ...)
    raise NotImplementedError("t16_seletividade")


if __name__ == "__main__":
    main()
