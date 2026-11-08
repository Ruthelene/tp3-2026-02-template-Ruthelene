"""T13 — MAX x >= ALL.

Compare SELECT title FROM movie WHERE votes >= (SELECT MAX(votes) FROM movie) com
SELECT title FROM movie WHERE votes >= ALL (SELECT votes FROM movie).
resultados/t13.json: chaves 'max' e 'all', cada uma {sql, resultado, nos, custo, tempo_ms}.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t13", ...)
    raise NotImplementedError("t13_agregacao")


if __name__ == "__main__":
    main()
