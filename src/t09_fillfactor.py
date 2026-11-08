"""T9 - Fillfactor do indice (1.000.000 de tuplas). A funcao rodar() tambem e usada pelo T10."""
from common import conectar, explain, salvar
from params import carregar
from tabela_t import criar_t, info_indice, tempo, tempo_consulta


def rodar(ordem, fillfactors, nome_saida):
    p = carregar()
    valor = p["t_cardinalidade_v"] // 2
    consulta = f"SELECT * FROM t WHERE v = {valor}"
    saida = []
    with conectar() as con, con.cursor() as cur:
        cur.execute("SET max_parallel_maintenance_workers = 0")
        criar_t(cur, 1_000_000, p["t_seed"], p["t_cardinalidade_v"])
        for ff in fillfactors:
            cur.execute("DROP INDEX IF EXISTS t_v")
            t_criacao = tempo(cur, f"CREATE INDEX t_v ON t(v{ordem}) WITH (fillfactor = {ff})")
            no_raiz = explain(cur, consulta)["Plan"]["Node Type"]
            saida.append({
                "fillfactor": ff,
                "tempo_criacao_ms": t_criacao,
                "tempo_consulta_ms": tempo_consulta(cur, consulta),
                "no_raiz_consulta": no_raiz,
                "indice": info_indice(cur, "t_v"),
            })
            print(ff, saida[-1]["indice"], no_raiz)
    salvar(nome_saida, saida)


def main():
    rodar("", carregar()["fillfactors"], "t09")


if __name__ == "__main__":
    main()