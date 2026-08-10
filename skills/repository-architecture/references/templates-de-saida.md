# Templates de saída — repository-architecture

Formatos de entrega por modo. Adapte ao projeto: omita seções sem conteúdo real em vez de preencher com filler. Em repositórios grandes, agregue por área em vez de listar arquivo a arquivo.

---

## 1. DISCOVERY — Inventário

```markdown
# Discovery — <projeto>

## Visão geral
- Raiz analisada: <path>
- Tamanho aproximado: <nº arquivos / áreas principais>
- VCS: <git/nenhum> · Branch: <nome> · Árvore limpa: <sim/não>
- Precondições explícitas da tarefa: <atendidas / DIVERGENTES — se obrigatória divergiu, a execução parou aqui>
- Duplicatas adjacentes do repositório: <nenhuma detectada / paths e risco>

## Primeiro contato com a raiz (cold-start)
- Ponto de entrada humano evidente: <sim/não — qual>
- Mapa (PROJECT_MAP/CODE-MAP/equivalente) descobrível a partir da raiz: <sim/não>
- Categorias compreensíveis sem nomes internos: <sim/parcial/não>
- Source vs generated distinguível sem conhecimento tácito: <sim/não>
- Observações: <fatos, sem propostas>

## Árvore anotada
<árvore resumida, com responsabilidade de cada área em uma linha>

## Entrypoints e geradores
| Elemento | Path | Papel | Produz/Consome |
|---|---|---|---|

## Inventário classificado
| Path | Tipo | Responsabilidade | Source/Generated | Editável | Entrypoint | Path-sensitive | Domínio | Status | Confiança |
|---|---|---|---|---|---|---|---|---|---|

Status: ACTIVE / LEGACY / ARCHIVE / UNKNOWN.
Confiança: alta / média / baixa (baixa ou UNKNOWN ⇒ investigar antes de qualquer decisão).
DISCOVERY observa, não propõe: destino futuro de qualquer elemento pertence ao DESIGN.

## Dependências de path relevantes
| Elemento | Referenciado por | Mover quebra? |
|---|---|---|

## UNKNOWNs e perguntas ao usuário
- <item>: <o que falta saber e por quê>
```

---

## 2. AUDIT — Diagnóstico

```markdown
# Audit — <projeto>

## Resumo executivo
<3–6 frases: maturidade da organização, principais problemas, risco, urgência.>

## Avaliação por dimensão
| Dimensão | Situação observada | Evidência |
|---|---|---|
| Navegabilidade interna | | |
| Cold-start discoverability | | |
| Clareza semântica | | |
| Separação de responsabilidades | | |
| Source vs generated | | |
| Previsibilidade | | |
| Consistência de nomes | | |
| Documentação de navegação | | |
| Raiz | | |

## Problemas
| # | Problema | Severidade (P0/P1/P2/COSMETIC) | Dano concreto | Área |
|---|---|---|---|---|

## Nota de navegabilidade — opcional
Use somente quando houver evidência suficiente para sustentar uma escala 0–10. Se não houver base, omita esta seção inteira — nunca invente um score porque o campo existe. A nota pondera navegabilidade interna E cold-start discoverability.
Nota: <0–10>
Evidências (internas e de cold-start):
- <indicador concreto>
- <indicador concreto>

## Recomendação: KEEP | MINOR | MODERATE | MAJOR REORGANIZATION
<justificativa em 2–4 frases; se KEEP, dizer explicitamente que não vale reorganizar.>
<KEEP não significa "nada a melhorar": liste aqui recomendações P1/P2 de navegação/documentação (README, PROJECT_MAP, rótulos de generated) que coexistem com KEEP.>
```

---

## 3. DESIGN — Proposta e plano de migração

```markdown
# Design — <projeto>

## Árvore proposta
<árvore com responsabilidade de cada diretório em uma linha>

## Racional
<por que este modelo (feature/layer/domain/hybrid/outro), derivado do que foi observado.>

## Contratos de localização
| Categoria | Novos elementos nascem em | Observação |
|---|---|---|

## Mapa de migração
| Atual | Novo | Motivo | Dependências a atualizar | Risco |
|---|---|---|---|---|

## Ondas
| Onda | Conteúdo | Pré-condição | Verificação ao final |
|---|---|---|---|

## Rollback
- Baseline: <commit/branch/backup>
- Retorno: <como desfazer cada onda>
- Preservação de histórico: <git mv / outra estratégia>

## Riscos e impactos
<build, CI, service worker, deploy, scripts — o que pode quebrar e como será tratado.>

## Critérios de aceite
- [ ] <testes/lint/build reais do projeto passam>
- [ ] Nenhuma referência ao path antigo remanescente
- [ ] Comportamento preservado (ANTES ≈ DEPOIS)
- [ ] PROJECT_MAP/README atualizados

## Fora de escopo desta migração
<melhorias funcionais notadas mas deliberadamente não incluídas.>

⚠️ Nenhum arquivo foi movido. A migração depende de aprovação explícita deste plano.
```

---

## 4. MIGRATION — Relatório de execução

```markdown
# Migration — <projeto> — onda <n/total>

## Executado
| Ação | De | Para | Referências atualizadas |
|---|---|---|---|

## Desvios do plano
<vazio idealmente; qualquer desvio explicado e autorizado.>

## Validação
| Check | Comando real | Resultado |
|---|---|---|
| Testes | | |
| Lint/Typecheck | | |
| Build | | |
| Grep por paths antigos | | |

## Regressões ou diferenças detectadas
<reportar fielmente; falha é falha.>

## Melhorias funcionais anotadas (NÃO executadas)
- <item> — requer tarefa própria.

## Estado final
- Árvore resultante: <resumo>
- Docs de navegação atualizados: <PROJECT_MAP/README>
- Rollback disponível até: <baseline>
```

---

## 5. GUARD — Alerta de conformidade

```markdown
# Guard — <projeto>

| # | Violação | Contrato violado | Destino recomendado | Severidade | Ação imediata? |
|---|---|---|---|---|---|

## Detalhe por violação
### <#> <violação>
- O que foi observado: <fato>
- Por que é um problema: <contrato/convenção e dano>
- Proposta: <mover para X / renomear para Y / atualizar contrato>
- Nada foi movido. Correção depende de autorização.

## Convenção possivelmente desatualizada?
<se o mesmo "desvio" se repete consistentemente, propor atualização do contrato.>
```
