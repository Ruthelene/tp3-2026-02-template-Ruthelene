"""T15 — LIKE e indices.

Consultas (letras em params): prefixo_like (title LIKE 'X%'), prefixo_substr (substr(title,1,1) = 'X'),
sufixo_like (title LIKE '%Y') e sufixo_reverse (reverse(title) LIKE 'Y%').
Meça o plano ANTES e DEPOIS de criar os indices adequados (text_pattern_ops, indice funcional em substr,
indice em reverse(title) com text_pattern_ops). resultados/t15.json:
  antes e depois: {<consulta>: {sql, linhas, nos, custo}}, indices_criados: {nome: DDL}.
Os indices criados devem permanecer no banco.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t15", ...)
    raise NotImplementedError("t15_like")


if __name__ == "__main__":
    main()
