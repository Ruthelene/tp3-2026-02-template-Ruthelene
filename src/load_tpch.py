"""Carga do TPC-H (fornecido pelo template; nao editar).

Gera os dados com o dbgen no scale factor definido em params.json, carrega
via COPY e cria chaves e indices. Uso: make load-tpch
"""
import os
import subprocess
import tempfile
from pathlib import Path

from common import conectar
from params import carregar

TABELAS = ["region", "nation", "part", "supplier", "partsupp", "customer", "orders", "lineitem"]
DBGEN = Path("/opt/tpch-dbgen")


def main():
    p = carregar()
    sf = p["sf"]
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["cp", "-r", str(DBGEN), tmp + "/g"], check=True)
        g = Path(tmp) / "g"
        subprocess.run(["./dbgen", "-s", str(sf), "-f"], cwd=g, check=True,
                       stdout=subprocess.DEVNULL)
        with conectar() as con, con.cursor() as cur:
            for t in reversed(TABELAS):
                cur.execute(f"DROP TABLE IF EXISTS {t} CASCADE")
            cur.execute(Path("queries/tpch/create_tbl.sql").read_text())
            for t in TABELAS:
                with open(g / f"{t}.tbl") as f, cur.copy(f"COPY {t} FROM STDIN WITH (DELIMITER '|')") as cp:
                    for linha in f:
                        cp.write(linha.rstrip("\n").rstrip("|") + "\n")
                print("carregada", t)
            cur.execute(Path("queries/tpch/create_idx.sql").read_text())
            cur.execute("ANALYZE")
    print(f"TPC-H carregado com SF={sf}")


if __name__ == "__main__":
    main()
