"""T2 - Armazenamento: blocos do sistema de arquivos / PostgreSQL e leitura sequencial x aleatoria."""
import mmap
import os
import random
import subprocess
import tempfile
import time

from common import conectar, salvar

BLOCO = 8192
N_BLOCOS = 32768          # arquivo de 256 MB
N_ALEATORIOS = 20000      # leituras aleatorias medidas


def stat(*args):
    return int(subprocess.run(["stat", *args, "/app"], capture_output=True, text=True, check=True).stdout)


def criar_arquivo(caminho):
    with open(caminho, "wb") as f:
        for _ in range(N_BLOCOS * BLOCO // (1 << 20)):
            f.write(os.urandom(1 << 20))
        f.flush()
        os.fsync(f.fileno())


def abrir_para_leitura(caminho):
    """Tenta O_DIRECT (ignora o cache do SO); se nao der, descarta o cache com fadvise."""
    try:
        return os.open(caminho, os.O_RDONLY | os.O_DIRECT), "O_DIRECT"
    except OSError:
        fd = os.open(caminho, os.O_RDONLY)
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
        return fd, "fadvise_dontneed"


def medir():
    buf = mmap.mmap(-1, BLOCO)  # buffer alinhado, exigido pelo O_DIRECT
    with tempfile.TemporaryDirectory() as d:
        caminho = os.path.join(d, "teste.bin")
        criar_arquivo(caminho)
        fd, modo = abrir_para_leitura(caminho)
        try:
            t0 = time.perf_counter()
            for i in range(N_BLOCOS):
                os.preadv(fd, [buf], i * BLOCO)
            t_seq = time.perf_counter() - t0
            if modo != "O_DIRECT":
                os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
            rnd = random.Random(1)
            posicoes = [rnd.randrange(N_BLOCOS) * BLOCO for _ in range(N_ALEATORIOS)]
            t0 = time.perf_counter()
            for p in posicoes:
                os.preadv(fd, [buf], p)
            t_rand = time.perf_counter() - t0
        finally:
            os.close(fd)
    seq_bloco = t_seq / N_BLOCOS
    rand_bloco = t_rand / N_ALEATORIOS
    return {
        "modo_leitura": modo,
        "arquivo_mb": N_BLOCOS * BLOCO / (1 << 20),
        "blocos_sequenciais": N_BLOCOS,
        "blocos_aleatorios": N_ALEATORIOS,
        "seq_mb_s": N_BLOCOS * BLOCO / (1 << 20) / t_seq,
        "aleatorio_iops": N_ALEATORIOS / t_rand,
        "tempo_por_bloco_seq_us": seq_bloco * 1e6,
        "tempo_por_bloco_aleatorio_us": rand_bloco * 1e6,
        "razao_custo_aleatorio_sequencial": rand_bloco / seq_bloco,
    }


def main():
    with conectar() as con, con.cursor() as cur:
        cur.execute("SHOW block_size")
        pg_bloco = int(cur.fetchone()[0])
    salvar("t02", {
        "fs_bloco_fundamental": stat("-f", "-c", "%S"),
        "fs_bloco_io_stat": stat("-c", "%o"),
        "pg_block_size": pg_bloco,
        "leitura": medir(),
    })


if __name__ == "__main__":
    main()
