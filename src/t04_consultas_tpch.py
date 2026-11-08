"""T4 — Consultas TPC-H com EXPLAIN (ANALYZE, BUFFERS).

Para cada consulta de queries/tpch_aluno/qNN.sql registre em resultados/t04.json, chave 'qNN':
  nos (tipos de no do plano), custo_estimado, linhas_estimadas, linhas_reais,
  buffers {hit, read}, tempo_execucao_ms, acesso_dominante.
No relatorio: comente o tipo de acesso de cada consulta (varredura sequencial, indice, junção hash...).
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t04", ...)
    raise NotImplementedError("t04_consultas_tpch")


if __name__ == "__main__":
    main()
