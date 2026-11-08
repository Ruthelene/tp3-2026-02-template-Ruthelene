"""T10 — Indice descendente.

Repita T9 com CREATE INDEX ... ON t(v DESC NULLS FIRST) e fillfactors [100] + params['fillfactors'].
resultados/t10.json: mesmo formato de t09.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t10", ...)
    raise NotImplementedError("t10_desc")


if __name__ == "__main__":
    main()
