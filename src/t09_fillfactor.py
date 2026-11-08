"""T9 — Fillfactor do indice.

Com t de 1.000.000 tuplas, para cada fillfactor em params['fillfactors'] crie o indice com esse fillfactor.
resultados/t09.json: lista de {fillfactor, tempo_criacao_ms, tempo_consulta_ms, indice:{paginas, altura, paginas_folha, densidade_media_folha}}.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t09", ...)
    raise NotImplementedError("t09_fillfactor")


if __name__ == "__main__":
    main()
