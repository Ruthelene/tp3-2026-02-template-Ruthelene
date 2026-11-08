"""T17–T19 — Reserva de assentos.

Implemente as versoes a (um unico BEGIN/COMMIT para os 3 passos) e b (transacao para o passo 1, passo 2 fora
de transacao, transacao para o passo 3). Tabela assentos(num_voo, disp) com params['assentos'] linhas, k agentes
(params['agentes']), niveis READ COMMITTED e SERIALIZABLE, espera de params['tempo_escolha_s'] no passo 2.
Grave cada reserva em reservas_log(config, cliente, assento, tentativas), com config = '<versao>/<isolamento>/k=<k>'
(isolamento: read_committed | serializable). resultados/t17.json:
  {assentos, tempo_escolha_s, experimentos: [{versao, isolamento, k, tempo_total_s, reservas,
   tentativas_max, tentativas_min, tentativas_media}]}
e um grafico por (versao, isolamento): resultados/t18_<versao>_<isolamento>.png (k x tempo total).
Um assento nunca pode ser reservado duas vezes.
"""
from common import conectar, salvar  # noqa: F401
from params import carregar  # noqa: F401


def main():
    p = carregar()
    # TODO: implemente a tarefa e grave o resultado com salvar("t17", ...)
    raise NotImplementedError("t17_reservas")


if __name__ == "__main__":
    main()
