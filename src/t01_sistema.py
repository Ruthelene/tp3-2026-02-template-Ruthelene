"""T1 - Identificacao do sistema. Grava resultados/t01.json."""
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path

from common import conectar, salvar

PARAMETROS = ["server_version", "block_size", "shared_buffers", "effective_cache_size",
              "seq_page_cost", "random_page_cost", "work_mem", "default_statistics_target"]


def lscpu():
    """Campos do comando lscpu como dicionario (vazio se o comando falhar)."""
    try:
        saida = subprocess.run(["lscpu"], capture_output=True, text=True, check=True).stdout
    except Exception:
        return {}
    campos = {}
    for linha in saida.splitlines():
        if ":" in linha:
            k, v = linha.split(":", 1)
            campos[k.strip()] = v.strip()
    return campos


def caches(campos):
    """Caches L1/L2/L3 vindos do lscpu; se nao houver, do /sys."""
    c = {k: v for k, v in campos.items() if re.match(r"^L\d", k)}
    if not c:
        for d in sorted(Path("/sys/devices/system/cpu/cpu0/cache").glob("index*")):
            try:
                nivel = (d / "level").read_text().strip()
                tipo = (d / "type").read_text().strip()
                c[f"L{nivel} {tipo}"] = (d / "size").read_text().strip()
            except Exception:
                pass
    return c


def ram_mb():
    for linha in Path("/proc/meminfo").read_text().splitlines():
        if linha.startswith("MemTotal"):
            return int(linha.split()[1]) // 1024


def nome_so():
    try:
        for linha in Path("/etc/os-release").read_text().splitlines():
            if linha.startswith("PRETTY_NAME="):
                return linha.split("=", 1)[1].strip('"')
    except Exception:
        pass
    return platform.system()


def main():
    campos = lscpu()
    modelo = campos.get("Model name") or platform.processor() or platform.machine()
    pg = {}
    with conectar() as con, con.cursor() as cur:
        for nome in PARAMETROS:
            cur.execute(f"SHOW {nome}")
            pg[nome] = cur.fetchone()[0]
    salvar("t01", {
        "cpu_modelo": modelo,
        "cpu_nucleos": os.cpu_count(),
        "ram_mb": ram_mb(),
        "disco_bytes": shutil.disk_usage("/app").total,
        "caches": caches(campos),
        "so": nome_so(),
        "kernel": platform.release(),
        "postgres": pg,
    })


if __name__ == "__main__":
    main()
