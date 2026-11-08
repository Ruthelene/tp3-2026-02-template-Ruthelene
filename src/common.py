"""Utilitarios comuns: conexao, EXPLAIN em JSON, gravacao de resultados."""
import json
import os
from pathlib import Path

import psycopg

RESULTADOS = Path(os.environ.get("RESULTADOS", "resultados"))


def conectar(autocommit=True):
    return psycopg.connect(
        host=os.environ.get("PGHOST", "db"), user=os.environ.get("PGUSER", "tp3"),
        password=os.environ.get("PGPASSWORD", "tp3"), dbname=os.environ.get("PGDATABASE", "tp3"),
        autocommit=autocommit)


def explain(cur, sql, analyze=True):
    """Retorna o plano (dict) de EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)."""
    opts = "ANALYZE, BUFFERS, " if analyze else ""
    cur.execute(f"EXPLAIN ({opts}FORMAT JSON) {sql}")
    return cur.fetchone()[0][0]


def tipos_de_no(plano):
    """Lista (ordem prefixada) dos tipos de no de um plano."""
    saida = []

    def visita(no):
        saida.append(no["Node Type"])
        for f in no.get("Plans", []):
            visita(f)
    visita(plano["Plan"])
    return saida


def salvar(nome, dados):
    RESULTADOS.mkdir(exist_ok=True)
    (RESULTADOS / f"{nome}.json").write_text(json.dumps(dados, indent=2, ensure_ascii=False, default=str) + "\n")
    print(f"gravado resultados/{nome}.json")
