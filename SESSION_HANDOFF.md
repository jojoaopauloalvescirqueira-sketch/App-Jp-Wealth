# Session Handoff — navegação hierárquica de Planejamento

- Data: 2026-08-13
- Branch: `feature/nav-planning-fx-submenu`
- `BASE_SHA` e HEAD: `e835bb5a723f3d0d7d262076cb9020fb4a1c9387`
- Estado: candidato material local, validado e não commitado
- Manifest: 60 scripts; lista/ordem preservadas, dois hashes de UI alterados
- Build ID: `4d9b36661c689c26`
- Publicação: nenhuma; commit, push, merge e deploy não autorizados

Esta nota representa o candidato local após a aprovação visual e o refinamento
de persistência por clique. Expira se fonte, manifest, teste ou gerado mudar.

## Implementado

- Planejamento permanece no primeiro nível global e ganhou uma segunda faixa
  estrutural com Visão Geral, Planejamento FX, Realizado e Histórico.
- A faixa vive entre o header e o contexto, desloca o conteúdo em 300 ms e não
  usa overlay, popup, card flutuante, sidebar ou sombra elevada.
- Hover fino abre transitoriamente e fecha após 400 ms fora de toda a região.
- Clique, Enter ou Espaço fixam a faixa. Pointerleave, resize, novo clique no
  acionador e seleção interna não fecham; clique externo ou Escape fecham.
- O fundo é um terceiro tom entre header e contexto, derivado dos tokens atuais
  e validado em claro/escuro.
- No mobile, o toque fecha a gaveta global e mantém o submenu empilhado no fluxo.
- As tabs internas equivalentes foram removidas. Os quatro conteúdos e
  renderizadores permanecem e usam `window.JPWFx.ui.selectView()`.
- O padrão reutilizável está em
  `docs/architecture/NAVIGATION-HIERARCHY.md`, descobrível pelo mapa de contexto.

## Invariantes confirmados

- Nenhuma fórmula, constante, perfil, fase, DD/MDD, lote, LIFO, stop,
  quarentena, contabilidade, MEI-JP ou regra do Planejamento FX mudou.
- `jpwealth_v9_state`, `S.fxPlanning`, schema, migração, backups e chaves de
  storage permanecem inalterados.
- O estado transitório/fixado do submenu é apenas memória de UI e não persiste.
- Nenhum dado real, token, senha, dependência, endpoint ou integração foi usado.

## Evidência

| Verificação | Resultado |
|---|---|
| `python3 tools/fx_planning_test.py` | PASS — estrutura, animação, hover, estado fixado, clique externo, teclado, mobile, quatro modos e zero duplicidade |
| Navegador real | PASS — 1440×900 e 390×844, claro/escuro, três tons distintos, segundo clique preservado, toque externo fecha, sem overflow e console limpo |
| `python3 tools/validate_project.py` | PASS — 60 scripts, 386 IDs estáticos, hashes/ordem coerentes e portátil reconstruído |
| `python3 tools/quality_gate.py --tier full` | PASS 19/19 — `quality-20260813T160548-full.json`; zero falha e zero teste omitido |
| Build reproduzível e `git diff --check` | PASS |

## Impacto agêntico

`AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED`

`BASIS:` foi criado um contrato arquitetural consumido por agentes e alterada a
responsabilidade do shell no mapa do código. `NAVIGATION-HIERARCHY.md`,
`CONTEXT-MAP.md`, `CODE-MAP.md`, contexto operacional, changelog, inventário e
este handoff foram reconciliados. Agentes, skills e routing já consultam essas
fontes e não exigem edição local. `INDEX NOT REQUIRED`; `SYSTEM RECONCILED` para
o blast radius estrito.

## Próxima ação humana

Revisar o candidato em `http://127.0.0.1:8778/`. Commit, push, merge e deploy
continuam etapas independentes e não autorizadas.

## Rollback

Reverter somente os arquivos desta tarefa para
`e835bb5a723f3d0d7d262076cb9020fb4a1c9387` e executar
`python3 tools/rebuild_monolith.py`. Não há migração ou estado financeiro para
desfazer. Não usar reset destrutivo.
