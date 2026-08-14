# Tarefa ativa — Migração do Motor de Lote para o Execution Board

- Data de abertura: 2026-08-13
- `BASE_SHA`: `60ec561` (`main` limpo)
- Branch de implementação: `feature/exec-motor-migration`
- Nível: **N1** (navegação e superfície) + **N0-V** (workspace) + **N0-D**
  (teste e reconciliação)
- Autoridade: **A2**. Nenhuma alteração N2/N3 autorizada e nenhuma executada —
  a migração é de superfície de acesso, sem tocar schema, dado ou cálculo.
- Git/publicação: branch e implementação autorizadas. **Commit, merge e push não
  foram executados.**
- Estado: implementação e validação técnica concluídas; aguardando teste manual.

## Divergências entre o pedido e o repositório

| Premissa | Realidade encontrada | Decisão |
|---|---|---|
| O submenu do Execution Board tem `Visão Operacional`, `Grade da Operação` e `Monitor LIFO` como destinos (§1, §5) | Grade e LIFO **não são destinos**: são widgets dentro do Painel Operacional (`#execPhaseGridsCard`, `#execLifoMonitor`, filhos de `#execWidgetGrid`) | Tratar o diagrama como descrição do conteúdo. Promover widgets a destinos seria redesenho, proibido pelo §14 |
| O gatilho de câmbio "1× por sessão" vive na abertura da subpágina da Central (§2, comentário em `01-navigation.js:4-6`) | **Não vive.** Está em `06-boot.js:22`, incondicional. O ramo em `09-settings-modal.js:248-251` é código morto: `06-boot.js` carrega antes e a flag nunca é resetada | Remover o código morto e corrigir o comentário. Não há gatilho a mover |
| "O Estudos NoCoda deve consumir os instrumentos provenientes do Motor de Lote" (§7) | O Motor **não é a fonte** — é outro consumidor de `S.instruments`, como o NoCoda via `instrumentCatalog()` | Nada a fazer. É justamente por isso que mover o Motor não afeta o NoCoda |

## Riscos encontrados e neutralizados

1. **`restoreLegacySettingsNodes()` arrancaria o grid.** Ela reanexa
   `#motorWidgetGrid` à `section#motor` incondicionalmente a cada fechamento da
   Central, sem verificar se foi ela quem moveu. A entrada `tool-motor` do mapa
   de transporte saiu junto com a folha. Coberto por teste que abre e fecha a
   Central e confirma que a grade não se moveu.
2. **A Central não abriria.** Remover a folha de `SETTINGS_LEAVES` mantendo o id
   em `children` lança `TypeError` em `groupPanel()`. As cinco estruturas saíram
   juntas.
3. **O app ficaria sem tela visível.** Sem o intercept, `navigateToScreen('motor')`
   limparia `.active` de todas as telas e sairia no `if(!screen) return`.
   Resolvido por `SCREEN_TO_MODULE_VIEW`, irmão do mapa que substitui.
4. **Controles congelados durante edição de layout.** A regra
   `html[data-layout-editing="true"] .screen.active [data-layout-card] > *`
   é escopada por tela, não por zona. Resolvido removendo `data-layout-card`
   dos dois cards — vestigial, pois nunca estiveram registrados no motor de
   layout. Isso também barra o long-press na primeira linha do handler.

## Fora de escopo — não tocado

`renderMotor()`, cálculos de position sizing, tetos, perfis de risco, câmbio,
`S.instruments`, `S.expAlvo`, schema, migração, Estatuto, Estudos NoCoda,
Planejamento FX, Checklist e Parâmetros (que permanecem na Central).

## Evidência

| Verificação | Resultado |
|---|---|
| `python3 tools/exec_submenu_test.py` | PASS — inclui seis blocos novos de migração |
| `python3 tools/settings_modal_test.py` | PASS — a Central abre sem a folha |
| `python3 tools/validate_project.py` | PASS — 63 scripts, 392 IDs (−1, o da `section#motor`) |
| `python3 tools/quality_gate.py --tier full` | ver `CURRENT-STATE.md` |
| Navegador real | NOT_RUN |

## Riscos residuais

- A tela migrada não foi inspecionada visualmente por um humano.
- A busca da Central perdeu os termos da folha removida — "motor de lote",
  "position sizing", "lote", "câmbio", "nocional", "teto", "perfis de risco"
  não encontram mais nada lá, o que é coerente com a migração, mas quem
  procurava por ali precisa aprender o caminho novo.
- O grupo "Operação" da Central ficou com dois itens: Parâmetros e Checklist.
