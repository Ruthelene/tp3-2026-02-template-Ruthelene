"""T7 - Estatisticas de t e blocos lidos por uma consulta de igualdade sobre v."""
from common import conectar, explain, salvar
from params import carregar


def main():
    p = carregar()
    valor = p["t_cardinalidade_v"] // 2
    with conectar() as con, con.cursor() as cur:
        cur.execute("SET max_parallel_workers_per_gather = 0")
        cur.execute("SELECT attname, null_frac, avg_width, n_distinct, most_common_vals::text, "
                    "most_common_freqs, histogram_bounds::text, correlation "
                    "FROM pg_stats WHERE tablename = 't' ORDER BY attname")
        colunas = [d.name for d in cur.description]
        stats = [dict(zip(colunas, linha)) for linha in cur.fetchall()]
        # zera os contadores da tabela, executa a consulta uma vez e forca o flush das estatisticas
        cur.execute("SELECT pg_stat_reset_single_table_counters('t'::regclass)")
        plano = explain(cur, f"SELECT * FROM t WHERE v = {valor}")
        cur.execute("SELECT pg_stat_force_next_flush()")
        cur.execute("SELECT pg_stat_clear_snapshot()")
        cur.execute("SELECT heap_blks_read, heap_blks_hit FROM pg_statio_user_tables WHERE relname = 't'")
        lidos, hits = cur.fetchone()
    raiz = plano["Plan"]
    salvar("t07", {
        "valor_consultado": valor,
        "plano_no_raiz": raiz["Node Type"],
        "pg_stats": stats,
        "heap_blks_read": lidos or 0,
        "heap_blks_hit": hits or 0,
        "explain_buffers": {"hit": raiz.get("Shared Hit Blocks", 0), "read": raiz.get("Shared Read Blocks", 0)},
    })


if __name__ == "__main__":
    main()