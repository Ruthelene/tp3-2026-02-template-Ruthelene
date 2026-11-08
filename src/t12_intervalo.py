"""T12 — Consultas por intervalo em movie.votes.

Escreva uma consulta seletiva (< 10 tuplas, usando params['movie_votos_alto']) e uma nao seletiva (> 80% das tuplas,
usando params['movie_votos_baixo']). resultados/t12.json:
  pequena e grande: {sql, linhas, nos, custo, tempo_ms, buffers},
  limiar_votos_menor_que (menor X, em passos de 50, tal que 'votes < X' passa a usar Seq Scan),
  linhas_no_limiar, fracao_no_limiar.
No relatorio: por que o indice sobre votes nao e sempre usado.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t12", ...)
    raise NotImplementedError("t12_intervalo")


if __name__ == "__main__":
    main()
