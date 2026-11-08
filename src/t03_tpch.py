"""T3 — TPC-H carregado.

Registre em resultados/t03.json:
  sf, tabelas: {<tabela>: {linhas, bytes_tabela, bytes_total}} para as 8 tabelas do TPC-H.
(A carga em si e feita por 'make load'; aqui se confere e documenta o que foi carregado.)
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t03", ...)
    raise NotImplementedError("t03_tpch")


if __name__ == "__main__":
    main()
