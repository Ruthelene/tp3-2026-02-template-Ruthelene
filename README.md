# TP3 — Introdução a Bancos de Dados (ICC205, 2026/02)

Trabalho prático sobre uso do PostgreSQL: armazenamento, índices, otimizador, transações.
O enunciado completo está em [`ENUNCIADO.md`](ENUNCIADO.md).

## Roteiro mínimo

```
echo "<sua matrícula>" > matricula.txt
make up
make params
make load
make parteI parteII parteIII parteIV
make test
```

Requisitos: Docker (com o plugin `docker compose`) e `make`. Nada precisa ser instalado fora dos contêineres.

## Onde está cada coisa

| Caminho | Conteúdo |
| --- | --- |
| `src/t01_*.py` … `src/t17_reservas.py` | uma tarefa por arquivo; o comentário inicial traz o enunciado e o formato do JSON |
| `src/common.py`, `src/tabela_t.py` | utilitários de conexão, `EXPLAIN` e da tabela `t` |
| `src/params.py` | geração dos parâmetros individuais a partir da matrícula |
| `src/load_tpch.py`, `src/load_movie.py`, `src/gen_consultas.py` | carga dos dados e geração das consultas (fornecidos; não editar) |
| `tests/check.py` | verificador automático (`make test`) |
| `queries/` | `movie.sql`, esquema TPC-H e consultas geradas |
| `resultados/` | saída das tarefas (versionada) |
| `docs/` | `previsao.md` e `tp3_relatorio.pdf` |

## Entrega

Repositório individual e privado, criado a partir deste template na organização `bd1-icomp-ufam`, com o docente como colaborador e a tag `v1.0` enviada ao remoto (`git push origin v1.0`). Detalhes na Seção 11 do enunciado.

`docs/previsao.md` deve ser commitado **antes** do primeiro commit que contenha `resultados/`.
