"""T1 — Identificacao do sistema.

Registre em resultados/t01.json (use common.salvar("t01", {...})):
  cpu_modelo, cpu_nucleos, ram_mb, disco_bytes, caches (dict), so, kernel,
  postgres: {server_version, block_size, shared_buffers, effective_cache_size,
             seq_page_cost, random_page_cost, work_mem, default_statistics_target}
Os valores de 'postgres' devem ser os de SHOW <parametro>. Execute dentro do contêiner.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t01", ...)
    raise NotImplementedError("t01_sistema")


if __name__ == "__main__":
    main()
