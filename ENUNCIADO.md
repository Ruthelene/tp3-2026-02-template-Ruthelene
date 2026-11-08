Universidade Federal do Amazonas
Instituto de Computação
Introdução a Bancos de Dados — ICC205 — 2026/02
Docente: Altigran Soares da Silva <alti@icomp.ufam.edu.br>

# Trabalho Prático III — 15/10/2026
# Data da entrega: 20/11/2026 até 23:59

## 1. Apresentação

Este trabalho consiste no uso de um SGBD relacional, o PostgreSQL, para observar e medir os mecanismos estudados nas Unidades II e III: armazenamento em páginas, índices, estatísticas, planos de execução, otimização de consultas, transações e níveis de isolamento. Cada tarefa é um programa em Python que executa operações sobre o PostgreSQL e registra o resultado em um arquivo JSON. O trabalho é dividido em quatro partes:

- **Parte I — ambiente, armazenamento e benchmark.** Parâmetros do sistema, blocos de disco e consultas analíticas do benchmark TPC-H.
- **Parte II — índices e estatísticas.** Páginas de uma tabela, estatísticas do otimizador, criação de índices B-tree, `fillfactor` e índices descendentes.
- **Parte III — otimizador de consultas.** Planos de execução sobre a base `movies`: consultas por intervalo, equivalência de consultas, `LIKE` e estimativa de seletividade.
- **Parte IV — transações e concorrência.** Um sistema de reserva de assentos com vários agentes concorrentes, em dois níveis de isolamento.

O produto do trabalho não é apenas o conjunto de programas em funcionamento. O que se avalia é a **análise dos resultados medidos**: o que cada número mostra sobre o funcionamento do SGBD, o que foi previsto antes da medição e o que explica as divergências.

O trabalho deve ser desenvolvido **individualmente**, em Python 3.12, sobre o PostgreSQL 16, ambos executados em contêineres Docker. O repositório-template fornece o ambiente, a carga dos dados, a geração dos parâmetros individuais e um verificador automático; a implementação das tarefas e a análise são responsabilidade de cada estudante.

## 2. Parâmetros individuais

Cada estudante recebe parâmetros próprios, derivados da sua matrícula: fator de escala do TPC-H, as 8 consultas TPC-H que serão executadas (e seus parâmetros de substituição), a semente e a cardinalidade da tabela aleatória, os valores de `fillfactor`, o filme-alvo, os limiares de votos e as letras das consultas `LIKE` na base `movies`, e o número de assentos do sistema de reservas.

Para gerar os parâmetros, escrever a matrícula no arquivo `matricula.txt` e executar `make params`, que produz `params.json`. Esse arquivo não deve ser editado: o verificador o recalcula a partir da matrícula. Como os dados e as consultas diferem entre estudantes, **os números de um trabalho não servem a outro**. O relatório deve ser escrito sobre os resultados do próprio estudante.

## 3. Ambiente

O repositório-template traz um `docker-compose.yml` com dois serviços: o PostgreSQL 16 (`db`) e um contêiner de ferramentas (`app`) com Python, as bibliotecas necessárias, o gerador `dbgen`/`qgen` do TPC-H e o cliente `psql`. As extensões `pageinspect`, `pgstattuple` e `pg_trgm` são instaladas pelo script de carga.

```
make up              # sobe o PostgreSQL e constrói a imagem de ferramentas
make params          # gera params.json a partir de matricula.txt
make load            # gera e carrega o TPC-H (fator de escala individual) e a base movies
make parteI          # executa as tarefas T1 a T4
make parteII         # executa as tarefas T5 a T10
make parteIII        # executa as tarefas T11 a T16
make parteIV         # executa a tarefa T17
make test            # verificador automático
make shell           # shell no contêiner de ferramentas
```

Os programas das tarefas ficam em `src/`, um por tarefa (`t01_sistema.py` a `t17_reservas.py`). Cada esqueleto traz, no comentário inicial, o enunciado da tarefa e o formato exato do JSON que ela deve produzir em `resultados/`. A função `common.explain` e os utilitários de `src/tabela_t.py` estão disponíveis para uso.

## 4. Parte I — ambiente, armazenamento e benchmark

**T1 — Identificação do sistema.** Registrar processador, número de núcleos, memória, tamanho do disco, caches, distribuição, versão do kernel e os parâmetros do PostgreSQL relevantes para o otimizador (`block_size`, `shared_buffers`, `effective_cache_size`, `seq_page_cost`, `random_page_cost`, `work_mem`, `default_statistics_target`). Saída: `resultados/t01.json`.

**T2 — Armazenamento.** Registrar o tamanho de bloco do sistema de arquivos (com o comando `stat`) e o do PostgreSQL, e medir, em um arquivo criado pelo próprio programa, o custo de leitura sequencial e o de leitura aleatória de blocos de 8 KB. No relatório, explicar como se altera o tamanho de bloco em cada nível e por que os tempos medidos dentro de um contêiner não são comparáveis entre máquinas. Saída: `resultados/t02.json`.

**T3 — TPC-H.** O comando `make load` gera o TPC-H no fator de escala individual e o carrega. Registrar o número de linhas e o tamanho de cada uma das oito tabelas. Saída: `resultados/t03.json`.

**T4 — Consultas TPC-H.** Executar, com `EXPLAIN (ANALYZE, BUFFERS)`, as 8 consultas individuais geradas em `queries/tpch_aluno/`. Para cada uma, registrar os tipos de nó do plano, o custo estimado, as linhas estimadas e reais, os blocos lidos e o tempo de execução, e comentar o tipo de acesso observado. Saída: `resultados/t04.json`.

## 5. Parte II — índices e estatísticas

Todas as tarefas desta parte usam a tabela `t(k serial primary key, v integer)`, com `v = trunc(random() * C)`, onde `C` é a cardinalidade individual. A semente individual deve ser aplicada com `setseed` antes da inserção, de modo que a tabela seja reproduzível.

**T5 — Tabela aleatória.** Criar `t` com 100.000 tuplas e registrar as 10 primeiras, ordenadas por `k`, e a soma de `v`. Saída: `resultados/t05.json`.

**T6 — Páginas.** Registrar `relpages`, `reltuples`, o tamanho em bytes e o número de tuplas por página. Saída: `resultados/t06.json`.

**T7 — Estatísticas e blocos lidos.** Registrar as estatísticas de `t` em `pg_stats` e os blocos de dados lidos e encontrados em memória por uma consulta de igualdade sobre `v`, medidos por `pg_statio_user_tables` e por `EXPLAIN (BUFFERS)`. Saída: `resultados/t07.json`.

**T8 — Índice sobre `v`.** Para 100.000 e para 1.000.000 de tuplas, criar o índice, medir o tempo de uma consulta de igualdade sobre `v`, o tempo de recriação do índice e as características do índice: páginas, altura, páginas-folha e densidade média das folhas. Saída: `resultados/t08.json`.

**T9 — `fillfactor`.** Com 1.000.000 de tuplas, criar o índice com cada `fillfactor` individual e comparar tamanho, altura, tempo de criação e tempo de consulta. Saída: `resultados/t09.json`.

**T10 — Índice descendente.** Repetir T9 com `CREATE INDEX ... ON t(v DESC NULLS FIRST)`, incluindo o `fillfactor` de 100. Saída: `resultados/t10.json`.

## 6. Parte III — otimizador de consultas

Esta parte usa a tabela `movie` (carregada por `make load`, a partir do script `queries/movie.sql`), que já possui índices sobre `id`, `title` e `votes`.

**T11 — Metadados dos índices.** Para cada índice de `movie`, obter do catálogo: nome, tabela, altura, número máximo e médio de chaves por bloco-folha, número de blocos-folha, média de blocos-folha por chave, média de blocos de dados por chave, número de linhas e de chaves distintas. Saída: `resultados/t11.json`.

**T12 — Consultas por intervalo.** Escrever uma consulta sobre `votes` que recupere menos de 10 tuplas (usando o limiar individual) e outra que recupere mais de 80% das tuplas. Executar `EXPLAIN ANALYZE` em ambas e determinar o valor `X` a partir do qual a consulta `votes < X` deixa de usar o índice. No relatório, explicar por que o índice não é sempre usado. Saída: `resultados/t12.json`.

**T13 — Operadores de agregação.** Comparar os planos e custos das consultas equivalentes `votes >= (SELECT MAX(votes) FROM movie)` e `votes >= ALL (SELECT votes FROM movie)`. Saída: `resultados/t13.json`.

**T14 — Subconsulta e junção.** Comparar os planos de duas formulações equivalentes (subconsulta e auto-junção) da consulta que retorna os filmes com mais votos que o filme-alvo individual. Saída: `resultados/t14.json`.

**T15 — `LIKE` e índices.** Para as letras individuais, medir os planos das consultas `title LIKE 'X%'`, `substr(title, 1, 1) = 'X'`, `title LIKE '%Y'` e `reverse(title) LIKE 'Y%'`. Em seguida, criar os índices adequados a cada uma (`text_pattern_ops`, índice sobre expressão) e medir novamente. Os índices criados devem permanecer no banco. No relatório, justificar quais consultas passaram a usar índice e por quê. Saída: `resultados/t15.json`.

**T16 — Estimativa de seletividade.** Para as consultas `votes < B` e `votes > A` (valores individuais), comparar linhas estimadas e linhas reais com as estatísticas padrão e com `SET STATISTICS 1000` sobre `votes`, restaurando o padrão no final. No relatório, discutir a hipótese de distribuição uniforme. Saída: `resultados/t16.json`.

## 7. Parte IV — transações e concorrência

Considere a tabela `assentos(num_voo, disp)`, com `N` assentos (valor individual) inicialmente disponíveis. A reserva de um assento é feita em três passos:

1. recuperar a lista de assentos disponíveis;
2. o cliente escolhe um assento: simulado pela escolha aleatória de um assento disponível, seguida de uma espera de `tempo_escolha_s` segundos (valor em `params.json`);
3. registrar a reserva, atualizando `disp` para `false`.

Duas versões devem ser implementadas:

- **Versão a:** os três passos em uma única transação.
- **Versão b:** uma transação para o passo 1 e outra para o passo 3; o passo 2 fica fora de transações.

Cada agente de viagens é uma *thread* com sua própria conexão e reserva um assento por vez. Os experimentos usam `k = 1, 2, 4, 6, 8, 10` agentes, até que os `N` clientes tenham sido atendidos, nos níveis de isolamento `READ COMMITTED` e `SERIALIZABLE`. Reservas que falham por conflito (assento já tomado, falha de serialização, *deadlock*) são refeitas. Cada reserva concluída deve ser gravada na tabela `reservas_log(config, cliente, assento, tentativas)`.

**T17 — Reservas.** Implementar as versões a e b e executar as 24 configurações (2 versões × 2 níveis de isolamento × 6 valores de `k`). Registrar, para cada uma, o tempo total, o número de reservas e o máximo, o mínimo e a média de tentativas por cliente (`resultados/t17.json`), e produzir um gráfico de linhas de `k` contra tempo total para cada par (versão, isolamento) (`resultados/t18_<versao>_<isolamento>.png`). Nenhum assento pode ser reservado mais de uma vez.

## 8. Verificador automático

O comando `make test` executa o verificador (`tests/check.py`), o mesmo usado na correção. Ele confere, sobre o banco carregado pela própria execução do estudante, que:

- `params.json` corresponde à matrícula;
- os parâmetros do PostgreSQL e os blocos relatados coincidem com os do sistema;
- o número de linhas das tabelas coincide com o banco e com o fator de escala;
- os resultados de T5 a T10 (tuplas, `relpages`, altura e páginas dos índices) coincidem com uma reconstrução independente a partir da semente;
- as consultas de T12 a T16 satisfazem as condições do enunciado (menos de 10 tuplas, mais de 80%, uso ou não de índice, estimativas reproduzidas);
- as reservas de T17 não têm assento duplicado e todos os clientes foram atendidos, e as tentativas relatadas coincidem com o registro.

Tempos de execução em milissegundos são informados, mas **não são comparados entre máquinas** e não entram na verificação. O verificador não substitui a análise: ele garante que os números do relatório correspondem ao que o programa produz.

## 9. Relatório

O relatório, em arquivo único `docs/tp3_relatorio.pdf`, deve conter as seções abaixo.

**9.1. Decisões de projeto.** Como cada experimento foi organizado e por quê; escolhas de implementação das reservas (como o conflito é detectado e refeito).

**9.2. Previsão antes da medição.** Antes de executar cada parte, registrar em `docs/previsao.md` e **versionar no repositório**: o número esperado de páginas de `t` e de tuplas por página, a altura esperada do índice para 100.000 e para 1.000.000 de tuplas e o efeito esperado do `fillfactor`, o tipo de acesso esperado em cada consulta de T12 e T15, a estimativa de seletividade esperada em T16 e o comportamento esperado do tempo total em T17 quando `k` cresce, em cada versão e nível de isolamento. O arquivo `docs/previsao.md` deve estar em um commit anterior ao primeiro commit que contenha o diretório `resultados/`.

**9.3. Medição.** Tabelas com os resultados de cada tarefa, extraídos de `resultados/` (T1 a T17), e os gráficos de T17.

**9.4. Comparação e explicação das divergências.** Confronto entre 9.2 e 9.3. Onde o previsto e o medido divergirem, explicar a causa a partir do funcionamento do PostgreSQL. Divergências existem e não são penalizadas; o que se avalia é a explicação.

**9.5. Análises por parte.** Responder, com base nos números do próprio trabalho:

- *Parte I:* o tipo de acesso de cada consulta TPC-H e sua relação com o custo medido; como se altera o tamanho de bloco; a relação entre o custo aleatório/sequencial medido e `random_page_cost`.
- *Parte II:* por que `relpages` e as tuplas por página têm o valor encontrado; por que a altura do índice muda de 100.000 para 1.000.000 de tuplas; o efeito do `fillfactor` sobre tamanho, altura e tempo; a diferença entre o índice crescente e o descendente.
- *Parte III:* por que o índice sobre `votes` não é sempre usado e o que determina o limiar medido; por que os planos de T13 e T14 diferem se as consultas são equivalentes; quais consultas de T15 passaram a usar índice depois da criação de cada um e por que a de sufixo só o usa com a reescrita; quando a hipótese de distribuição uniforme erra a estimativa de T16 e como as estatísticas adicionais mudam o resultado.
- *Parte IV:* o comportamento do tempo total com `k`, o número de tentativas e as diferenças entre as versões a e b e entre os dois níveis de isolamento, com a explicação a partir do protocolo de controle de concorrência do PostgreSQL.

**9.6. Declaração de uso de ferramentas de IA.** Seção obrigatória. Deve informar quais ferramentas foram usadas, em que partes do trabalho, o que foi solicitado a elas e o que foi modificado posteriormente. **O uso declarado não implica desconto de nota.** O que se avalia é a consistência entre a declaração e o código entregue.

## 10. Estrutura do repositório

```
/
├── src/                código Python (uma tarefa por arquivo) e utilitários
├── queries/            movie.sql, consultas TPC-H (geradas) e arquivos de apoio
├── tests/              check.py (verificador)
├── resultados/         JSON e gráficos produzidos pelas tarefas (versionados)
├── docs/               previsao.md e tp3_relatorio.pdf
├── matricula.txt       matrícula do estudante
├── params.json         gerado por make params
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

O diretório `resultados/` e o arquivo `params.json` devem ser versionados. O repositório deve funcionar do zero com a sequência `make up`, `make params`, `make load`, `make parteI` a `make parteIV` e `make test`, sem depender de caminho absoluto, de configuração manual não documentada ou de pacote instalado fora dos contêineres.

## 11. Entrega

A entrega é feita por **repositório GitHub individual e privado**, criado a partir do template `tp3-2026-02-template` na organização `bd1-icomp-ufam`. Cada estudante deve:

1. criar o repositório a partir do template;
2. adicionar o docente como colaborador;
3. marcar a versão final com a tag **`v1.0`**, exatamente com esse nome;
4. enviar a tag ao GitHub: `git push origin v1.0`.

Será corrigido o commit apontado pela tag `v1.0` no repositório remoto no encerramento do prazo. Antes do prazo, confirmar que a tag aparece no remoto:

```
git ls-remote --tags origin
```

Tags com outro nome, branches chamados `v1.0` e repositórios sem o docente como colaborador não caracterizam entrega.

## 12. Avaliação

- Implementação funcional das quatro partes, conferida pelo verificador: **35%**
- Análise experimental e coerência entre relatório e execução: **55%**
- Rito de entrega, reprodutibilidade e previsão registrada antes da medição: **10%**

Divergência entre os números do relatório e os produzidos pela execução dos programas entregues é o item de maior peso negativo do trabalho.

## 13. Comentários gerais

Comece cedo. As Partes I a III usam conteúdo já estudado na Unidade II (armazenamento, índices, processamento e otimização de consultas) e podem ser desenvolvidas desde a publicação do enunciado. A Parte IV usa o conteúdo de controle de concorrência e níveis de isolamento, abordado nas aulas de 05/11 (escalonamento) e 17/11 (controle de concorrência); a entrega em 20/11 foi definida para acompanhar essas aulas.

O uso de ferramentas de IA é permitido e deve ser declarado. O que o trabalho avalia não é a produção do código, e sim o entendimento do sistema observado: os números medidos, as previsões e a capacidade de explicar ambos.

## 14. Referências

1. ELMASRI, R.; NAVATHE, S. B. *Sistemas de Banco de Dados*, 7ª ed. Pearson, 2018. Capítulos sobre estruturas de indexação, processamento e otimização de consultas, e controle de concorrência.
2. SILBERSCHATZ, A.; KORTH, H. F.; SUDARSHAN, S. *Sistema de Banco de Dados*, 6ª ed. Elsevier, 2012.
3. The PostgreSQL Global Development Group. *PostgreSQL 16 Documentation*: Using EXPLAIN; Planner Statistics; Transaction Isolation; `pageinspect`; `pgstattuple`. https://www.postgresql.org/docs/16/
4. Transaction Processing Performance Council. *TPC-H Benchmark*, especificação e `dbgen`. https://www.tpc.org/tpch/
