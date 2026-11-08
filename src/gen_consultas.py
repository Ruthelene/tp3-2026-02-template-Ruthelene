"""Gera as 8 consultas TPC-H do aluno em queries/tpch_aluno/qNN.sql (qgen com seed da matricula).

Fornecido pelo template; nao editar. Uso: make consultas
"""
import re
import subprocess
from pathlib import Path

from params import carregar

QGEN = "/opt/tpch-dbgen/qgen"


def gerar_consulta(n, sf, seed):
    r = subprocess.run([QGEN, "-s", str(sf), "-r", str(seed), str(n)],
                       cwd="/opt/tpch-dbgen", capture_output=True, text=True, check=True,
                       env={"DSS_QUERY": "/opt/tpch-dbgen/queries", "PATH": "/usr/bin:/bin"})
    sql = r.stdout
    # remove marcadores do qgen e limites de linha proprios do dialeto
    linhas = [l for l in sql.splitlines()
              if not l.strip().startswith("--") and not l.strip().lower().startswith("where rownum")]
    sql = "\n".join(linhas)
    sql = re.sub(r"(day|month|year)\s*\(\d+\)", r"\1", sql)   # dialeto Oracle -> PostgreSQL
    return sql.strip().rstrip(";") + ";\n"


def main():
    p = carregar()
    out = Path("queries/tpch_aluno")
    out.mkdir(parents=True, exist_ok=True)
    for n in p["tpch_consultas"]:
        (out / f"q{n:02d}.sql").write_text(gerar_consulta(n, p["sf"], p["qgen_seed"]))
        print("gerada", f"queries/tpch_aluno/q{n:02d}.sql")


if __name__ == "__main__":
    main()
