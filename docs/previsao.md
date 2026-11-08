# Previsão antes da medição (TP3)

Escrito antes de executar as tarefas e antes de commitar `resultados/` (Seção 9.2 do enunciado).
Parâmetros: C = 100 valores distintos em `v`, fillfactors 70/85/95/100, filme-alvo "American Beauty",
votos baixo = 1000 e alto = 35000, letras C (prefixo) e I (sufixo), 120 assentos, espera de 0,1 s.

## 1. Páginas de `t` (100.000 tuplas) e tuplas por página
- Cada tupla: cabeçalho 23 B (alinhado a 24) + k (4 B) + v (4 B) = 32 B, mais 4 B de ponteiro de linha = 36 B.
- Página de 8192 B, cabeçalho de 24 B: 8168 B úteis. 8168 / 36 = 226 tuplas por página.
- 100.000 / 226 = 442,5, logo **443 páginas** (relpages esperado = 443; cerca de 3,5 MB).

## 2. Altura do índice sobre `v`
- Como v tem só 100 valores distintos, o PostgreSQL 16 agrupa os TIDs repetidos (deduplicação, 6 B por TID).
  O índice fica pequeno: cerca de 6 B x n_tuplas, com folhas a 90% de ocupação (fillfactor padrão 90).
- 100.000 tuplas: cerca de 90 páginas-folha, **altura 1** (a raiz aponta direto para as folhas).
- 1.000.000 de tuplas: cerca de 850 a 900 páginas-folha. Uma página interna comporta algumas centenas de
  ponteiros, então uma só raiz não basta: **altura 2**. Incerteza: se couber numa só raiz, a altura seria 1.

## 3. Efeito do fillfactor (índice com 1.000.000 de tuplas)
- Tamanho: quanto menor o fillfactor, mais páginas-folha (aprox. proporcional a 1/fillfactor):
  70 tem cerca de 40% mais folhas que 100. Ordem esperada: 70 > 85 > 95 > 100.
- Altura: igual (2) para todos, talvez sem mudança porque a raiz ainda comporta os ponteiros.
- Tempo de criação: ligeiramente maior com fillfactor baixo (mais páginas para escrever).
- Tempo de consulta: praticamente igual, pois domina o acesso às tuplas da tabela, não às páginas do índice.
- Índice descendente (T10): mesmo tamanho, altura e tempos próximos aos do crescente, pois a B-tree pode
  ser lida nos dois sentidos e não há NULLs. A diferença só aparece em ordenações.

## 4. Tipo de acesso esperado
T12 (votes em movie):
- Consulta seletiva (< 10 tuplas, votes > 35000): **Index Scan** (ou Bitmap) sobre o índice de votes.
- Consulta não seletiva (> 80% das tuplas): **Seq Scan**. Ler quase tudo pelo índice custaria mais
  (acessos aleatórios) do que varrer a tabela em sequência.
- Limiar X de `votes < X`: o ponto em que o plano troca para Seq Scan deve ficar em uma fração
  pequena a moderada da tabela (algo entre 5% e 20% das linhas), porque random_page_cost (4) é maior
  que seq_page_cost (1).

T15 (letras C e I):
- `LIKE 'C%'` antes: Seq Scan (índice padrão não atende LIKE em locale não-C). Depois do índice com
  text_pattern_ops: Index/Bitmap Scan (se a fração de títulos começando com C for pequena o bastante).
- `substr(title,1,1) = 'C'` antes: Seq Scan. Depois do índice sobre a expressão: usa índice.
- `LIKE '%I'` antes e depois: Seq Scan (sufixo não permite busca por faixa de índice B-tree).
- `reverse(title) LIKE 'I%'` antes: Seq Scan. Depois do índice em reverse(title) com text_pattern_ops:
  usa índice (poucos títulos terminam em I).

## 5. Estimativa de seletividade em T16
- O otimizador usa o histograma de 100 faixas de mesma frequência e supõe distribuição uniforme dentro
  de cada faixa. Os votos têm distribuição muito assimétrica (poucos filmes com muitos votos).
- votes < 1000 (região densa): estimativa próxima da real.
- votes > 35000 (cauda esparsa): maior erro relativo, pois as faixas do topo são muito largas.
- Com SET STATISTICS 1000: histograma mais fino, estimativas mais próximas das reais, sobretudo na cauda.

## 6. Tempo total em T17 quando k cresce (120 clientes, espera de 0,1 s por reserva)
- Referência: com k = 1, 120 x 0,1 s = cerca de 12 s, sem conflitos.
- Versão a (tudo em uma transação) em READ COMMITTED: a espera acontece dentro da transação. Vários agentes
  escolhem o mesmo assento; quem perde espera o lock, vê o assento ocupado e refaz. Tempo cai com k,
  mas menos que 1/k, e as tentativas crescem.
- Versão a em SERIALIZABLE: muitas falhas de serialização (abortos) e refações; o tempo melhora pouco ou
  até piora com k alto. É a configuração mais lenta.
- Versão b em READ COMMITTED: transações curtas, conflitos só no passo 3 (assento tomado durante a espera);
  tempo cai quase em 1/k, com poucas tentativas extras. Deve ser a mais rápida.
- Versão b em SERIALIZABLE: janelas curtas, poucas falhas; tempo próximo ao de b/READ COMMITTED,
  um pouco acima por causa de abortos ocasionais.
