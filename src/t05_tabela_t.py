"""T5 — Tabela t.

Crie t(k serial primary key, v integer) com 100.000 tuplas, v = trunc(random() * t_cardinalidade_v),
chamando SELECT setseed(t_seed) antes do INSERT (valores em params.json).
Registre em resultados/t05.json: primeiras_10 (k, v ordenado por k), soma_v, tuplas.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t05", ...)
    raise NotImplementedError("t05_tabela_t")


if __name__ == "__main__":
    main()
