"""T11 - Metadados dos indices da tabela movie (pgstatindex, pageinspect, pg_class)."""
from common import conectar, salvar

INDICES = ["movie_key", "movie_title", "movie_votes"]


def atributo_do_indice(cur, indice):
    cur.execute("SELECT a.attname FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid "
                "JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = i.indkey[0] "
                "WHERE c.relname = %s", (indice,))
    return cur.fetchone()[0]


def folhas(cur, indice, altura):
    """Numero de itens (chaves) de cada pagina-folha, lido com bt_page_stats."""
    cur.execute("SELECT pg_relation_size(%s::regclass) / current_setting('block_size')::int", (indice,))
    paginas = cur.fetchone()[0]
    itens = []
    for blkno in range(1, paginas):
        cur.execute("SELECT type, live_items FROM bt_page_stats(%s, %s)", (indice, blkno))
        tipo, vivos = cur.fetchone()
        if tipo == "l" or (tipo == "r" and altura == 0):
            itens.append(vivos)
    return itens


def main():
    saida = []
    with conectar() as con, con.cursor() as cur:
        cur.execute("ANALYZE movie")
        cur.execute("SELECT count(*), (pg_relation_size('movie') / current_setting('block_size')::int) FROM movie")
        linhas, blocos_tabela = cur.fetchone()
        for indice in INDICES:
            atributo = atributo_do_indice(cur, indice)
            cur.execute("SELECT tree_level, leaf_pages FROM pgstatindex(%s)", (indice,))
            altura, blocos_folha = cur.fetchone()
            itens = folhas(cur, indice, altura)
            cur.execute(f"SELECT count(DISTINCT {atributo}) FROM movie")
            distintas = cur.fetchone()[0]
            # media de blocos de dados distintos que guardam as linhas de uma mesma chave (medido pelo ctid)
            cur.execute(f"SELECT avg(n) FROM (SELECT count(DISTINCT (ctid::text::point)[0]::bigint) AS n "
                        f"FROM movie GROUP BY {atributo}) g")
            dados_por_chave = float(cur.fetchone()[0])
            linhas_por_chave = linhas / distintas
            saida.append({
                "indice": indice,
                "tabela": "movie",
                "atributo": atributo,
                "altura": altura,
                "max_chaves_por_bloco_folha": max(itens),
                "media_chaves_por_bloco_folha": sum(itens) / len(itens),
                "blocos_folha": blocos_folha,
                # estimativa: linhas da chave / entradas por folha (no minimo 1 bloco por chave)
                "media_blocos_folha_por_chave": max(1.0, blocos_folha / distintas),
                "media_blocos_dados_por_chave": dados_por_chave,
                "linhas": linhas,
                "chaves_distintas": distintas,
                "linhas_por_chave": linhas_por_chave,
                "blocos_da_tabela": blocos_tabela,
            })
            print(saida[-1])
    salvar("t11", saida)


if __name__ == "__main__":
    main()