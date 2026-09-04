# JP Wealth — Mapa de Navegação e Orientação para IAs

> **STATUS DOCUMENTAL:**  
> **ORIENTAÇÃO / MAPA DE NAVEGAÇÃO**  
> **SEM FORÇA NORMATIVA**

Este README orienta pessoas e agentes de IA na leitura do acervo. Não cria regra, parâmetro, vigência, autoridade ou homologação; não substitui a Constituição JP Wealth, o Estatuto ou o Anexo Paramétrico Canônico. Em divergência, prevalece a fonte normativa vigente de maior autoridade. A localização física ajuda a identificar a função documental, mas não cria autoridade.

## Estrutura documental

| Local | Função | Como usar |
|---|---|---|
| **Raiz do vault — arquivos `0` a `9`** | Fonte normativa principal | `0 - Parte Preliminar Normativa…` e os Livros `1 —` a `9 —`, na ordem de I a IX: regras, obrigações, proibições, protocolos, definições, risco, governança, método, funções, mesas, alocação e disposições finais. |
| **Raiz do vault — `00` e `0.1`** | Materiais introdutórios e não normativos | [`00 Prefácio e Apresentação.md`](00%20Pref%C3%A1cio%20e%20Apresenta%C3%A7%C3%A3o.md) e [`0.1 Introdução ao Mercado de Derivativos e CFDs.md`](0.1%20Introdu%C3%A7%C3%A3o%20ao%20Mercado%20de%20Derivativos%20e%20CFDs.md): contexto e fundamentos explicativos; não criam regra nem parâmetro. |
| [`99 - ANEXO PARAMÉTRICO CANÔNICO.md`](99%20-%20ANEXO%20PARAM%C3%89TRICO%20CAN%C3%94NICO.md) | Anexo vigente dentro da delegação recebida | Na raiz do vault. Fonte canônica dos elementos `DELEGATED_N3`. |
| [`04 - EXTRAS/03 — GOVERNANÇA DOCUMENTAL/`](04%20-%20EXTRAS/03%20%E2%80%94%20GOVERNAN%C3%87A%20DOCUMENTAL/) | Atos, cutovers e candidates de proveniência/revogação | Subcamada de `04 - EXTRAS`. Distinguir ato formal de conteúdo normativo. |
| [`04 - EXTRAS/`](04%20-%20EXTRAS/) | Auditorias, manifestos, relatórios, registros e notas expiradas | Investigação histórica apenas. `HISTÓRICO ≠ ESTADO ATUAL`. |
| [`04 - EXTRAS/IMPLEMENTAÇÕES PENDENTES FUTURAS/`](04%20-%20EXTRAS/IMPLEMENTA%C3%87%C3%95ES%20PENDENTES%20FUTURAS/) | Camada **não normativa** de projetos especificados e ainda **não autorizados** para execução | Cada projeto tem status e gate próprios. Especificação registrada **não** é autorização de execução. |
| [`01 — PESQUISA E MELHORIAS/`](01%20%E2%80%94%20PESQUISA%20E%20MELHORIAS/) | Camada **não normativa** de pesquisa e evolução futura | Estudos, hipóteses, propostas, análises exploratórias, backlog, experimentos e ferramentas auxiliares. Prepara decisões futuras; não é fonte de decisão atual. Nada nesta pasta cria autoridade normativa. |

## Precedência

```text
Constituição JP Wealth
↓
Corpus Normativo vigente
↓
Anexo normativo dentro da delegação recebida
↓
Atos formais aplicáveis
↓
Artefatos derivados
↓
Auditorias e histórico
↓
Pesquisa e melhorias
↓
Inferência
```

Uma fonte inferior nunca altera silenciosamente uma fonte superior.

## Anexo Paramétrico Canônico

Arquivo: [`99 - ANEXO PARAMÉTRICO CANÔNICO.md`](99%20-%20ANEXO%20PARAM%C3%89TRICO%20CAN%C3%94NICO.md), na raiz do vault.

Ele está vigente e é fonte canônica exclusivamente para os elementos efetivamente `DELEGATED_N3`. É uma compressão fiel do Estatuto, não substitui a norma hospedeira e não pode prevalecer sobre ela em caso de divergência.

| `AUTHORITY_MODE` | Leitura correta |
|---|---|
| `DELEGATED_N3` | Elemento efetivamente delegado à governança paramétrica. |
| `PENDING_N3` | Elemento delegado sem valor homologado. |
| `MIRROR_N2` | Regra N2 reproduzida apenas para consulta; a autoridade permanece no Livro hospedeiro. |
| `MIRROR_N1` | Doutrina resumida. |
| `MIRROR_N0` | Regra superior resumida. |
| `INDETERMINATE / NON_N3` | Elemento fora da governança paramétrica N3; não o converter silenciosamente em N3. |

```text
PENDING
≠ ZERO
≠ FALLBACK
≠ VALOR HISTÓRICO
≠ AUTORIZAÇÃO IMPLÍCITA
```

As faixas internas das fases e os tetos de alavancagem das fases são N2. Aparecem no Anexo como `MIRROR_N2` e não podem ser recalibrados por simples alteração paramétrica. Para os detalhes dos 27 elementos delegados, consultar o Anexo; para decisão normativa, consultar a norma hospedeira indicada nele.

## Estado documental atual

```text
COERÊNCIA_INTERNA = PASS
   escopo: ausência de contradição normativa interna.
   NÃO cobre conflito estrutural declarado (monotonicidade da Fase 2),
   gates de ratificação (RAT-1/2/3) nem validação empírica.
   FECHAMENTO DOCUMENTAL ≠ VALIDAÇÃO EMPÍRICA.

ANEXO_PARAMÉTRICO = VIGENTE

PARAMETRIC_DELEGATED_COUNT = 26

P22 = INDETERMINATE / NON_N3
P29 = DERIVED / NON_N3

P10 = PENDING
P17 = PENDING
P18 = PENDING

OPERABILITY = BLOCKED

EMPIRICAL_VALIDATION = NOT_VALIDATED

NI01 = EXPIRADA_POR_CONDIÇÃO

DOCUMENT_ARCHITECTURE = ORGANIZED

RESEARCH_AND_IMPROVEMENT_LAYER = 01 — PESQUISA E MELHORIAS

RESEARCH_LAYER_AUTHORITY = NON_NORMATIVE
```

## Estados epistemológicos

```text
DOCUMENTALMENTE RESOLVIDO
≠
NORMATIVAMENTE RESOLVIDO
≠
MATEMATICAMENTE VALIDADO
≠
EMPIRICAMENTE VALIDADO
```

Coerência documental não prova eficácia. Vigência não prova edge. Um parâmetro vigente não é automaticamente empiricamente validado, e resultado financeiro isolado não valida processo.

O Estatuto disciplina, contém e governa risco; não demonstra sozinho expectativa positiva, edge, rentabilidade futura, probabilidade de sucesso ou probabilidade de ruína. Até nova autorização humana, `EMPIRICAL_VALIDATION = NOT_VALIDATED`. Não iniciar backtests ou calibração apenas por encontrar referências no projeto.

## Arquitetura temporal

```text
D1 = contexto auxiliar e não decisório

H4 = horizonte decisório

H1 = horizonte de execução/refinamento
```

H1 não cria, confirma, sustenta ou invalida tese H4. D1 não substitui o horizonte decisório.

## Princípios centrais

1. Preservação do Capital;
2. Sobrevivência Operacional da Conta;
3. Cumprimento Integral dos Protocolos de Risco;
4. Qualidade da Execução;
5. Consistência de Longo Prazo;
6. Rentabilidade.

Lucro isolado não valida conduta; prejuízo isolado não invalida conduta conforme. O mercado é tratado probabilisticamente: risco precede retorno.

## Como uma IA deve trabalhar

```text
READ FIRST
↓
IDENTIFY AUTHORITY
↓
LOCATE CANONICAL SOURCE
↓
CHECK PENDING / BLOCKERS
↓
ASSESS SCOPE
↓
ACT ONLY WITH AUTHORITY
```

Antes de propor mudança:

1. Localize a fonte vigente e identifique sua classe normativa.
2. Verifique dependências, `PENDING`, `INDETERMINATE` e `BLOCKED`.
3. Procure decisões formais aplicáveis.
4. Distinga defeito real de preferência estética.
5. Apresente evidência.
6. Modifique somente com autorização humana compatível e suficiente.

Se duas fontes aparentemente conflitarem:

```text
IDENTIFICAR
↓
CITAR
↓
CLASSIFICAR AUTORIDADE
↓
EXPLICAR IMPACTO
↓
PARAR SE HOUVER DECISÃO MATERIAL
```

É proibido resolver silenciosamente por inferência, analogia, costume, preferência, documento histórico ou valor antigo. Ausência de regra não é liberdade operacional. Nunca invente percentual, multiplicador, prazo, fator, fallback ou autorização.

## Histórico, governança e NI-01

Não editar retroativamente documentos históricos para refletir o estado atual. Preservar hashes, paths históricos, nomes antigos, conclusões da época, baselines e diffs. Histórico descreve determinado momento; não constitui automaticamente o estado atual.

```text
NI-01/2026 — Defesa Limitada

STATUS = EXPIRADA_POR_CONDIÇÃO
CURRENT_AUTHORITY = NONE
```

A NI-01 está preservada apenas como evidência histórica e não pode fundamentar operação corrente.

## Camada de pesquisa e melhorias

A pasta [`01 — PESQUISA E MELHORIAS/`](01%20%E2%80%94%20PESQUISA%20E%20MELHORIAS/) é a camada onde o sistema pensa antes de decidir. Destina-se a estudos, pesquisas, hipóteses, propostas de alteração, análises exploratórias, backlog, experimentos e ferramentas auxiliares ligadas à evolução futura.

Ela **prepara** decisões. Não as **toma**.

```text
RESEARCH_AND_IMPROVEMENT_LAYER = 01 — PESQUISA E MELHORIAS
RESEARCH_LAYER_AUTHORITY = NON_NORMATIVE
```

```text
PESQUISA ≠ NORMA
HIPÓTESE ≠ DECISÃO
PROPOSTA ≠ APROVAÇÃO
ESTUDO ≠ VALIDAÇÃO
```

Nada nesta pasta pode, por mera presença, criar regra, alterar N0, N1, N2 ou N3, alterar o Anexo Paramétrico, homologar parâmetro, preencher `PENDING`, criar fallback, autorizar operação, alterar vigência, demonstrar validação empírica ou substituir norma hospedeira. A localização de um arquivo aqui descreve sua função; não lhe confere autoridade — e conteúdo que tenha sido movido para cá não ganha autoridade por causa da mudança de pasta.

Mudança derivada desta camada só integra o sistema depois de, cumulativamente:

1. análise;
2. rito normativo ou paramétrico aplicável;
3. aprovação humana competente;
4. atualização formal da fonte vigente.

## Segurança e agentes de código

Não procurar deliberadamente passwords, tokens, seeds, chaves, cookies ou credenciais. Se um segredo surgir incidentalmente, não o reproduza, copie nem inclua em relatório; registre apenas o incidente e recomende rotação quando aplicável.

Para Codex, Claude Code ou equivalente: o filesystem real prevalece sobre handoff quando houver divergência factual. Verifique o estado antes de escrever, preserve trabalho humano, use backup/checkpoint proporcional ao risco, revise o diff e pare em `MATERIAL_DISCOVERY`. Não execute commit, push ou merge sem autorização específica.

## Leitura rápida recomendada

```text
1. README.md

2. raiz do vault
   → 0 - Parte Preliminar Normativa…
   → 1 — Estrutura Operacional Normativa

3. 99 - ANEXO PARAMÉTRICO CANÔNICO.md

4. Livro específico da matéria analisada
   (arquivos 1 — a 9 — na raiz)

5. 04 - EXTRAS/
   03 — GOVERNANÇA DOCUMENTAL/
   somente para atos/proveniência

6. 04 - EXTRAS/
   somente para investigação histórica

7. 01 — PESQUISA E MELHORIAS/
   somente para estudos, hipóteses,
   propostas ou desenvolvimento futuro

8. 04 - EXTRAS/
   IMPLEMENTAÇÕES PENDENTES FUTURAS/
   projetos já especificados, aguardando
   autorização humana para execução
```

Para consulta operacional rápida, use o Anexo Paramétrico. Para decisão normativa, use a norma hospedeira indicada pelo Anexo.

## Limite de atuação

Este README não autoriza IA a editar o Estatuto, alterar parâmetro, homologar `PENDING`, alterar vigência, revogar documento, criar exceção, ampliar risco, recalibrar sistema, mover arquivos ou apagar histórico. Toda alteração exige autorização humana específica e suficiente.

> Preserve primeiro. Identifique a autoridade. Compreenda a fonte. Modifique somente mediante autorização suficiente.

```text
EM DÚVIDA:

NÃO INFERIR
NÃO AMPLIAR
NÃO ESCREVER
ESCALAR PARA DECISÃO HUMANA
```
