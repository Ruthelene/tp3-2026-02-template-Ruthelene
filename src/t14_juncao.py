"""T14 — Subconsulta x junção.

Filmes com mais votos que params['movie_titulo_alvo']: uma versao com subconsulta e outra com junção (auto-junção).
resultados/t14.json: titulo_alvo, e chaves 'subconsulta' e 'juncao', cada uma {sql, linhas, nos, custo, tempo_ms}.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t14", ...)
    raise NotImplementedError("t14_juncao")


if __name__ == "__main__":
    main()
