"""Helpers da tabela t (Parte II)."""
import statistics
import time


def criar_t(cur, n, seed, cardinalidade_v, nome="t"):
    """Cria a tabela t(k serial pk, v int) com n tuplas e valores v em [0, cardinalidade_v)."""
    cur.execute(f"DROP TABLE IF EXISTS {nome} CASCADE")
    cur.execute(f"SELECT setseed({seed})")
    cur.execute(f"CREATE TABLE {nome} (k serial PRIMARY KEY, v integer)")
    cur.execute(f"INSERT INTO {nome}(v) SELECT trunc(random() * {cardinalidade_v}) FROM generate_series(1, {n})")
    cur.execute(f"ANALYZE {nome}")


def info_indice(cur, indice):
    """Paginas, altura (nivel) e densidade media das folhas de um indice B-tree."""
    cur.execute("SELECT pg_relation_size(%s::regclass) / current_setting('block_size')::int", (indice,))
    paginas = cur.fetchone()[0]
    cur.execute("SELECT tree_level, leaf_pages, avg_leaf_density FROM pgstatindex(%s)", (indice,))
    nivel, folhas, dens = cur.fetchone()
    return {"paginas": paginas, "altura": nivel, "paginas_folha": folhas, "densidade_media_folha": float(dens)}


def tempo_consulta(cur, sql, repeticoes=5):
    """Mediana do tempo de execucao (ms) segundo EXPLAIN ANALYZE."""
    ts = []
    for _ in range(repeticoes):
        cur.execute(f"EXPLAIN (ANALYZE, FORMAT JSON) {sql}")
        ts.append(cur.fetchone()[0][0]["Execution Time"])
    return statistics.median(ts)


def tempo(cur, sql):
    t0 = time.perf_counter()
    cur.execute(sql)
    return (time.perf_counter() - t0) * 1000
