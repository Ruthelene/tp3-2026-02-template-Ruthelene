"""Gera params.json a partir da matricula (seed individual do TP3).

Uso: python src/params.py   (le matricula.txt, escreve params.json)

O arquivo params.json NAO deve ser editado: o corretor automatico recalcula
os parametros a partir da matricula e compara com o que foi usado.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

TITULOS_ALVO = ["Star Wars", "Titanic", "Pulp Fiction", "Braveheart",
                "Blade Runner", "Forrest Gump", "Saving Private Ryan", "American Beauty"]
LETRAS_PREFIXO = ["I", "T", "S", "B", "M", "C"]
LETRAS_SUFIXO = ["A", "I", "a"]


def gerar(matricula: str) -> dict:
    h = hashlib.sha256(("tp3-2026-02:" + matricula.strip()).encode()).digest()
    rnd = random.Random(int.from_bytes(h[:8], "big"))
    return {
        "matricula": matricula.strip(),
        "sf": rnd.choice([0.05, 0.06, 0.08, 0.1]),
        "tpch_consultas": sorted(rnd.sample([q for q in range(1, 23) if q != 15], 8)),
        "qgen_seed": rnd.randint(1000, 999999),
        "t_seed": round(rnd.uniform(-0.99, 0.99), 6),
        "t_cardinalidade_v": rnd.choice([10, 20, 50, 100]),
        "fillfactors": sorted(rnd.sample([50, 60, 70, 75, 80, 85, 90, 95, 100], 4)),
        "movie_titulo_alvo": rnd.choice(TITULOS_ALVO),
        "movie_votos_baixo": rnd.choice([800, 1000]),
        "movie_votos_alto": rnd.choice([35000, 40000, 45000]),
        "movie_letra_prefixo": rnd.choice(LETRAS_PREFIXO),
        "movie_letra_sufixo": rnd.choice(LETRAS_SUFIXO),
        "assentos": rnd.choice([120, 150, 180, 200]),
        "tempo_escolha_s": 0.1,
        "agentes": [1, 2, 4, 6, 8, 10],
    }


def carregar(caminho: str = "params.json") -> dict:
    return json.loads(Path(caminho).read_text())


if __name__ == "__main__":
    mat = Path("matricula.txt").read_text().strip()
    if not mat:
        sys.exit("matricula.txt esta vazio: escreva sua matricula nele")
    p = gerar(mat)
    Path("params.json").write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(p, indent=2, ensure_ascii=False))
