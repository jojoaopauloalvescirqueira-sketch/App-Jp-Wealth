# Tarefa ativa — Faixa hierárquica de Planejamento FX

- Data de abertura: 2026-08-13
- `BASE_SHA`: `e835bb5a723f3d0d7d262076cb9020fb4a1c9387` (`main` limpo)
- Branch de implementação: `feature/nav-planning-fx-submenu`
- Commit material: `478a55826977f37d2f7b60848454f4f3aa80943a`
- Integração local em `main`: `55d22671c3479b43762922ec01cad454d4e90ac0`
- Nível: **N0-V** (painel e animação) + **N1** (hover, teclado, foco e
  navegação interna) + **N0-D** (teste e reconciliação documental)
- Autoridade: **A2**, confirmada pelo gestor após auditoria e plano. Nenhuma
  alteração N2/N3 está autorizada.
- Git/publicação: criação da branch, commit e merge em `main` autorizados e
  executados. Push e deploy não foram executados.
- Estado: implementação, validação técnica e integração local concluídas.

## Estado observado

`#nav` contém cinco botões `.tab[data-screen]` irmãos. O shell global transporta
o mesmo `#nav` para `#gdTopbarNavSlot`; `01-navigation.js` alterna a tela;
`12-nav-style.js` mede diretamente a geometria de cada botão; e
`11-operational-shell.js` controla a gaveta móvel. O primeiro protótipo colocou
os quatro modos internos em um popover absoluto dentro de `#nav`, enquanto
`05-fx-ui.js` continuou renderizando as quatro abas equivalentes no conteúdo.
Essa combinação sobrepunha o conteúdo e criava duas fontes visíveis de
navegação para a mesma seleção de UI.

## Objetivo

Prototipar navegação hierárquica somente para Planejamento: o menu superior
representa o módulo e uma segunda faixa estrutural seleciona Visão Geral,
Planejamento FX, Realizado ou Histórico. A faixa participa do fluxo normal,
expande o conjunto do header e desloca fisicamente contexto e conteúdo.

## Escopo autorizado

1. Manter o acionador de Planejamento filho direto de `#nav` e preservar
   `data-screen="fxplan"`.
2. Inserir a faixa contextual entre o header principal e a faixa de contexto,
   com descrições curtas estáticas e sem popup, overlay, card ou sidebar.
3. Abrir por hover fino e teclado; fechar com delay de 400 ms, Escape e clique
   fora; preservar a travessia ponteiro acionador → painel.
4. Suportar setas, Home, End, Enter/Espaço, Tab natural e devolução de foco.
5. No mobile, recolher a gaveta global após ativar Planejamento e manter o
   submenu empilhado no fluxo vertical, sem overlay.
6. Reusar os quatro modos existentes por uma superfície pública estritamente de
   UI; nenhuma mutação financeira ou persistência nova.
7. Remover apenas as abas internas equivalentes; conteúdos e renderizadores dos
   quatro modos permanecem inalterados.
8. Cobrir o contrato em teste focado e navegador real; reconstruir derivados
   somente pela ferramenta oficial.
9. Diferenciar abertura transitória por hover de abertura fixada por clique:
   quando fixada, a faixa só fecha por clique externo ou Escape acessível.
10. Dar à faixa um terceiro tom próprio, intermediário entre header e contexto,
    preservando claro/escuro.
11. Registrar o padrão reutilizável em contrato arquitetural próprio.

## Arquivos permitidos

- `docs/work/ACTIVE-TASK.md`
- `index.html`
- `src/styles/app.css`
- `src/js/40-app/11-operational-shell.js`
- `src/js/30-accounting/05-fx-planning/05-fx-ui.js`
- `src/js/manifest.json` somente para hashes dos scripts alterados, sem mudar
  lista ou ordem
- `tools/fx_planning_test.py`
- `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` somente via
  `tools/rebuild_monolith.py`
- `docs/architecture/CODE-MAP.md`, `docs/governance/CURRENT-STATE.md`,
  `CHANGELOG.md` e `SESSION_HANDOFF.md` somente na reconciliação final, se o
  impacto for confirmado
- `docs/architecture/NAVIGATION-HIERARCHY.md` e
  `docs/governance/CONTEXT-MAP.md` para o contrato reutilizável autorizado pelo
  gestor
- `PROJECT-FILES.txt` para registrar o novo contrato arquitetural no inventário
  canônico

Qualquer necessidade fora da lista ou passagem para N2/N3 exige nova
autorização.

## Invariantes

- Nenhum arquivo de `00-core`, `10-domain`, engine/model/state do Planejamento
  FX ou outro módulo funcional será alterado.
- `jpwealth_v9_state`, `S.fxPlanning`, `schemaVersion`, `DEFAULTS`, `migrate()`,
  backups, auditoria e chaves auxiliares permanecem inalterados.
- Fórmulas, premissas, séries, reservas, ledger, realizado e histórico não mudam
  semanticamente.
- Os cinco botões principais continuam na mesma ordem e somente Planejamento
  ganha `aria-haspopup`/submenu.
- Pill/Kinetic continuam medindo o botão Planejamento real; o acionador não
  ganha wrapper.
- O submenu não prende Tab, não depende de hover em ponteiro coarse e não torna
  destinos ocultos focáveis.
- O portátil é sempre derivado da fonte pelo gerador oficial.

## Critérios de aceitação

- Hover abre suavemente e a travessia à faixa não fecha; se não houver clique,
  a saída fecha após tolerância de 400 ms.
- Clique ou Enter/Espaço no acionador fixa a faixa aberta; saída do ponteiro,
  redimensionamento e novo clique no acionador não a fecham. Clique externo ou
  Escape encerram o estado fixado.
- Foco/Enter/Espaço/setas abrem e operam o painel; Escape fecha e devolve foco;
  clique externo fecha.
- Selecionar cada item ativa `#fxplan` e o modo correspondente quando há plano;
  no estado vazio, guarda a intenção visual sem criar ou alterar plano. A faixa
  permanece disponível até fechamento explícito ou saída tolerada.
- A expansão usa grid-row/clip em 300 ms, aumenta a altura estrutural e desloca
  `#gdContextRow` e `#appMain` sem sobreposição.
- Não existe mais `role="tablist"`/`data-fxp-view` equivalente dentro de
  `#fxPlanningRoot`.
- O fundo da faixa é um terceiro tom, distinto do header e da faixa de contexto
  nos temas claro e escuro.
- Desktop e mobile, claro e escuro, sem overflow, oclusão ou regressão das cinco
  rotas.
- Demais módulos continuam sem submenu.
- `fx_planning_test.py`, gate aplicável, build reproduzível e auditoria final
  aprovados.

## Rollback

Reverter somente os arquivos desta tarefa para
`e835bb5a723f3d0d7d262076cb9020fb4a1c9387` e executar
`python3 tools/rebuild_monolith.py`. Não há migração nem estado financeiro para
desfazer. Não usar reset destrutivo.

## Resultado verificado

- `python3 tools/fx_planning_test.py`: PASS — estados transitório/fixado,
  estrutura em fluxo, terceiro tom, teclado, clique externo, mobile e quatro
  modos.
- `python3 tools/validate_project.py`: PASS — 60 scripts, 386 IDs estáticos e
  portátil reconstruído.
- `python3 tools/quality_gate.py --tier full`: PASS 19/19 — zero falha ou teste
  omitido; relatório `tools/.artifacts/quality-20260813T160548-full.json`.
- Navegador real: PASS em 1440×900 e 390×844, claro/escuro, sem overflow e com
  console limpo.
- Build ID: `4d9b36661c689c26`.
- Impacto agêntico detectado e reconciliado no blast radius estrito; agentes,
  skills e routing não exigiram alteração local; `INDEX NOT REQUIRED`.
