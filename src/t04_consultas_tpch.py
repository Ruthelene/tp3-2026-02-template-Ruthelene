"""T4 - Consultas TPC-H com EXPLAIN (ANALYZE, BUFFERS)."""
from pathlib import Path

from common import conectar, explain, salvar, tipos_de_no
from params import carregar


def nos_do_plano(no, acc=None):
    """Todos os nos do plano, em ordem prefixada."""
    acc = [] if acc is None else acc
    acc.append(no)
    for filho in no.get("Plans", []):
        nos_do_plano(filho, acc)
    return acc


def linhas_do_no(no):
    return no.get("Actual Rows", 0) * no.get("Actual Loops", 1)


def acesso_dominante(plano):
    """Varredura que processa mais linhas (a que mais pesa no plano)."""
    varreduras = [n for n in nos_do_plano(plano["Plan"]) if "Scan" in n["Node Type"]]
    if not varreduras:
        return None
    n = max(varreduras, key=linhas_do_no)
    return f"{n['Node Type']} em {n.get('Relation Name', '?')}"


def main():
    p = carregar()
    saida = {}
    with conectar() as con, con.cursor() as cur:
        for n in p["tpch_consultas"]:
            q = f"q{n:02d}"
            sql = Path(f"queries/tpch_aluno/{q}.sql").read_text().strip().rstrip(";")
            plano = explain(cur, sql)
            raiz = plano["Plan"]
            saida[q] = {
                "nos": tipos_de_no(plano),
                "custo_estimado": raiz["Total Cost"],
                "linhas_estimadas": raiz["Plan Rows"],
                "linhas_reais": linhas_do_no(raiz),
                "buffers": {"hit": raiz.get("Shared Hit Blocks", 0), "read": raiz.get("Shared Read Blocks", 0)},
                "tempo_execucao_ms": plano["Execution Time"],
                "acesso_dominante": acesso_dominante(plano),
                "juncoes": [x["Node Type"] for x in nos_do_plano(raiz) if "Join" in x["Node Type"] or x["Node Type"] == "Nested Loop"],
            }
            print(q, saida[q]["acesso_dominante"], saida[q]["custo_estimado"])
    salvar("t04", saida)


if __name__ == "__main__":
    main()
