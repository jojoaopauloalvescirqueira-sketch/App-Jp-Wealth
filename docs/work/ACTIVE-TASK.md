# Tarefa ativa — Tickets MVP (JPW-NPQRST, JPW-QRNPKM, JPW-785634)

- Data de abertura: 2026-08-12
- `BASE_SHA`: `1cca1f7451d0` (`main`, com JPW-CBA987 e JPW-436587 integrados e enviados)
- Branch autorizada: `feature/tickets-mvp`
- Nível: **N1** (interface, ordenação e fluxo) + **N0-D** (testes e documentação)
- Autoridade: A2. Nenhuma alteração N2/N3 — `S.mvpNotes` permanece na versão 5,
  sem migração, sem campo novo, sem alteração de chave, backup ou importação.
- Git: branch criada em 2026-08-12. Commit e merge autorizados na conversa;
  push permanece por conta do GitHub Desktop.

## Escopo — três deltas independentes no mesmo módulo

| Delta | Ticket | O quê |
|---|---|---|
| A+B | JPW-NPQRST | `⋯` por ticket em popup moderno, com ação Concluir sob confirmação |
| C | JPW-QRNPKM | `priority === 'critical'` no topo das listas, por ordenação derivada |
| D | JPW-785634 | Módulo apresentado como **Tickets**; nomenclatura interna preservada |

## Decisão do gestor (2026-08-12, vinculante)

**Alvo do `⋯`: novo botão no card do ticket.** Não existia `⋯` por nota — o card
tinha apenas o ícone de copiar. Os três `⋯` do aplicativo eram: pasta
(`<details>` legado), editor (`[•••]` do inspector) e widget de Notícias (fora do
módulo). Escolhido o card por ser a única leitura em que todas as frases do
ticket fecham. O ícone de copiar virou o primeiro item do menu.

## Decisões técnicas assumidas (registradas)

1. **Confirmação por `confirm()` nativo.** É o padrão real de confirmação do
   módulo (excluir pasta, excluir ticket, descartar rascunho). Garante também,
   por construção, que cancelar não escreve nada.
2. **`⋯` da pasta permanece em `<details>`.** Fora do alvo escolhido; convertê-lo
   é delta próprio.
3. **Sem "Reabrir ticket".** O ticket veda criar a ação sem comportamento
   anterior ou autorização específica; o status segue editável pelo inspector.

## Invariantes

- Abrir o menu: zero escrita. Cancelar conclusão: zero escrita. Ordenar por
  criticidade: zero escrita. Renomear UX: zero migração.
- `schemaVersion` 5, chave `jpwealth_v9_state`, IDs, `folders[]` e formato de
  backup intocados.
- Criticidade nunca torna visível o que a visão excluiu.
- Nenhum nome de função, arquivo ou identificador interno renomeado.

## Fora de escopo (deliberado)

Redesenho do módulo, novo storage, novo schema, workflow, Kanban, SLA,
comentários, subtarefas, assignees, notificações, automações, novas categorias.

## Plano de rollback

Reverter os arquivos alterados para `1cca1f7451d0` e reexecutar
`tools/rebuild_monolith.py`. Nenhum estado persistido novo a desfazer.

## Resultado do candidato (2026-08-12)

- `tools/quality_gate.py --tier full`: **PASS=19**, nenhuma falha.
- Verificação visual em navegador real: 1440×900 e 375×812 — lista com críticos
  no topo, menu `⋯` e posição de "Concluir ticket" logo abaixo de "Copiar
  referência".
- Defeito encontrado e corrigido na verificação: o menu não devolvia o foco ao
  `⋯` quando fechado por clique no backdrop.
- **AGENTIC IMPACT: nenhum** — nenhuma skill, agente, router ou documento de
  governança depende semanticamente do nome "Notas". `CODE-MAP.md` atualizado
  por ser descrição de superfície.
