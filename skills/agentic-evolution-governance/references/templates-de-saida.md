# Templates de saída — agentic-evolution-governance

Formatos de entrega por modo. Adapte ao projeto: omita seções sem conteúdo real em vez de preencher com filler. Em ecossistemas grandes, agregue por camada (agentes, routing, contexto, índice) em vez de listar item a item.

---

## 1. DISCOVERY — Inventário agêntico

```markdown
# Discovery agêntico — <projeto>

## Visão geral
- Raiz analisada: <path> · Revisão atual: <SHA/data>
- Precondições explícitas da tarefa: <atendidas / DIVERGENTES — se obrigatória divergiu, a execução parou aqui>
- Porte agêntico: <nº agentes / skills / camadas de contexto / vetor-índice: sim-não>

## Infraestrutura encontrada
| Camada | Artefato(s) | Papel (canônico/referência/cópia/cache/índice/memória/contexto/histórico) | Mecanismo de revisão |
|---|---|---|---|
| Instruções de agentes | | | |
| Routing/registry | | | |
| Bootstrap/preflight | | | |
| Contexto operacional | | | |
| Memória/índice/vetor | | | |
| Guard/gates | | | |
| Fontes canônicas | | | |

## Grafo lógico de dependências (elementos relevantes)
| Elemento | Tipo/Papel | Fonte canônica | Consome | Consumido por | Última sincronização conhecida | Status | Confiança |
|---|---|---|---|---|---|---|---|

## Mecanismos de revisão existentes
<SHAs, datas de fotografia, hashes, cláusulas de validade — o que o projeto já usa; só recomendar âncora nova se nada existir.>

## UNKNOWNs e perguntas ao usuário
- <item>: <o que falta saber e por quê>
```

---

## 2. IMPACT — Avaliação de impacto agêntico

```markdown
# Impact assessment — <projeto>

## CHANGE
<descrição objetiva da mudança, feita ou planejada>

## SCOPE / CHANGESET
<exatamente o que está sob análise: commit/SHA, revisão, documento, versão, evento ou conjunto delimitado de mudanças>

## CLASSIFICATION
<baixo | médio | alto | crítico> — <justificativa pelo efeito real, não pelo nome>

## CANONICAL SOURCE
<onde a nova verdade vive>

## AGENTIC BLAST RADIUS
| Elemento | Impacto | Local Action | Evidência |
|---|---|---|---|
| <artefato> | AFFECTED / NOT_AFFECTED / UNKNOWN | REQUIRED / NOT_REQUIRED / UNKNOWN | <por quê — herança por referência sustenta NOT_REQUIRED, nunca rebaixa Impacto a NOT_AFFECTED> |

Impacto: a mudança alcança semanticamente o elemento? · Local Action: o elemento precisa de alteração local? Dimensões independentes — registre as duas.

## Consumidores multi-projeto (se houver)
| Instalação/Projeto | Versão instalada | Atualização é decisão de |
|---|---|---|

## CONTEXT IMPACT
<quais camadas de contexto precisam refletir a mudança>

## INDEX/VECTOR IMPACT
INDEX REQUIRED / NOT REQUIRED / UNKNOWN / BLOCKED — <fonte a indexar e o que invalidar, se aplicável>

## RECONCILIATION REQUIRED: SIM / NÃO
<se NÃO: "NO AGENTIC RECONCILIATION REQUIRED" e encerrar aqui.>
```

---

## 3. RECONCILE — Tabela de reconciliação

```markdown
# Reconciliação — <projeto> · <mudança ou escopo>

Universo: blast radius do IMPACT para <changeset>. Dependência nova descoberta aqui volta ao IMPACT antes de entrar nesta tabela.

| Elemento | Estado atual (evidência) | Estado esperado | Status | Mudanças contribuintes | Ação necessária |
|---|---|---|---|---|---|
| <agente> | | | CURRENT | — | none |
| <router> | | | STALE | <CH-B> | update <apontar o quê> |
| <registry> | | | MISSING | <CH-A> | register |
| <índice> | | | STALE | <CH-B, CH-C> | reindex via <mecanismo oficial> |
| <ADR histórico> | | | NOT_AFFECTED | — | none (histórico correto sobre o passado) |
| <inventário não consumido pela camada agêntica> | | | NOT_AFFECTED / OUT OF SCOPE | — | problema real; encaminhar a <skill/processo responsável> |

## Consolidação acumulada (quando um artefato é alcançado por várias mudanças)
### <artefato> → <estado único: ex. STALE>
| Eixo divergente | Declarado | Real | Introduzido por | Preexistente? |
|---|---|---|---|---|
| <ex.: revisão/baseline> | | | <CH-x> | não |
| <ex.: inventário> | | | <CH-y> | não |
| <ex.: …> | | | — | sim (anterior ao change-set; apenas revelado) |

Causalidade: <qual mudança introduziu o quê; drift por acúmulo não é atribuído ao commit mais recente.>

## Conflitos que exigem decisão humana
- <CONFLICT>: <fonte A diz X · fonte B diz Y · quem tem autoridade não está claro porque…>

## UNKNOWNs
- <item>: <investigação necessária>

⚠️ Nenhuma ação foi executada. PROPAGATE/REINDEX dependem de aprovação explícita de um plano delimitado (itens enumerados ou lote homogêneo sem ambiguidade).
```

---

## 4. PROPAGATE — Relatório de propagação

```markdown
# Propagação — <projeto> · onda <n/total>

## Executado (somente itens aprovados)
| Elemento | Ação | Antes → Depois | Validação do consumidor |
|---|---|---|---|

## Desvios do plano
<vazio idealmente; qualquer desvio explicado e autorizado.>

## Registro de mudança
<mecanismo do projeto usado (changelog/ADR/auditoria/current-state) e entrada criada.>

## Estado sistêmico
- CHANGE APPLIED: <sim>
- SYSTEM RECONCILED: <sim/parcial — o que resta e por quê>
- Git/publicação: <status; autorização separada>
```

---

## 5. REINDEX — Avaliação e execução

```markdown
# Reindex — <projeto>

- Mecanismo oficial: <qual — se nenhum existe, este modo não se aplica>
- Veredito: INDEX REQUIRED / NOT REQUIRED / UNKNOWN / BLOCKED
- Fonte(s) a indexar: <somente canônicas e validadas>
- Exclusões: <o que NÃO entra e por quê>
- Invalidações: <representações antigas a remover/marcar>
- Modo: incremental / rebuild — <justificativa>
- Âncora de revisão registrada: <SHA/data>
- Executado: <sim com autorização / não — aguardando>
```

---

## 6. GUARD — Alerta de coerência

```markdown
# Guard agêntico — <projeto>

| # | Incoerência | Estado | Evidência | Reconciliação proposta | Severidade | Urgente? |
|---|---|---|---|---|---|---|
| | <ex.: skill criada e não roteada> | MISSING | | <registrar em X> | | |

## Detalhe
### <#> <incoerência>
- Estado canônico: <fato> · Representação divergente: <fato>
- Nada foi propagado nem reindexado. Correção depende de autorização.
```
