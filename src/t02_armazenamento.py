"""T2 — Armazenamento.

Registre em resultados/t02.json:
  fs_bloco_fundamental  (stat -f -c %S /app), fs_bloco_io_stat (stat -c %o /app),
  pg_block_size (SHOW block_size),
  leitura: {seq_mb_s, aleatorio_iops, razao_custo_aleatorio_sequencial}
A medicao compara leitura sequencial e aleatoria de blocos de 8 KB num arquivo seu.
No relatorio: como alterar o tamanho de bloco (sistema de arquivos e PostgreSQL) e por que
os numeros medidos no contêiner nao sao comparaveis entre maquinas.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t02", ...)
    raise NotImplementedError("t02_armazenamento")


if __name__ == "__main__":
    main()
