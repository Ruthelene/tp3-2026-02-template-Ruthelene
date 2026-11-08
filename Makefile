# TP3 — Introducao a Bancos de Dados (IBD 2026/02)
#
#   make up            sobe o PostgreSQL e constroi a imagem
#   make params        gera params.json a partir de matricula.txt
#   make load          carrega TPC-H (SF individual) e a base movies
#   make parteI ... parteIV    executa as tarefas de cada parte
#   make test          autoverificacao (o mesmo teste que corrige o trabalho)
#   make down          derruba os servicos (make clean-all apaga tambem os dados)

DC := docker compose
RUN := $(DC) run --rm app

.PHONY: up down clean-all params load load-tpch load-movie consultas parteI parteII parteIII parteIV test shell

up:
	$(DC) up -d --build db
	$(DC) build app

down:
	$(DC) down

clean-all:
	$(DC) down -v

params:
	$(RUN) python src/params.py

load: load-tpch load-movie

load-tpch: consultas
	$(RUN) python src/load_tpch.py

load-movie:
	$(RUN) python src/load_movie.py

consultas:
	$(RUN) python src/gen_consultas.py

parteI:
	$(RUN) python src/t01_sistema.py
	$(RUN) python src/t02_armazenamento.py
	$(RUN) python src/t03_tpch.py
	$(RUN) python src/t04_consultas_tpch.py

parteII:
	$(RUN) python src/t05_tabela_t.py
	$(RUN) python src/t06_paginas.py
	$(RUN) python src/t07_estatisticas.py
	$(RUN) python src/t08_indice.py
	$(RUN) python src/t09_fillfactor.py
	$(RUN) python src/t10_desc.py

parteIII:
	$(RUN) python src/t11_catalogo.py
	$(RUN) python src/t12_intervalo.py
	$(RUN) python src/t13_agregacao.py
	$(RUN) python src/t14_juncao.py
	$(RUN) python src/t15_like.py
	$(RUN) python src/t16_seletividade.py

parteIV:
	$(RUN) python src/t17_reservas.py

test:
	$(RUN) python tests/check.py

shell:
	$(RUN) bash
