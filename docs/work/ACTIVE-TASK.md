# Tarefa ativa — Fidelidade ao Claude Design (JPW-789ABC-C)

- Data de abertura: 2026-08-13
- `BASE_SHA`: `38bccfc11d47521cb17016a8476533298bc47678` (`main` limpo)
- Branch autorizada: `feature/claude-design-fidelity`
- Referência visual: `Auditoria visual JP Wealth/UX Engineering Baseline/JP Wealth - Redesign.dc.html`
- Nível: **N0-V** (composição, CSS, temas e responsividade) + **N1**
  (interações de interface e ciclo coerente de atualização da PWA) + **N0-D**
  (testes e reconciliação documental)
- Autoridade: **A2**, concedida pelo gestor para implementar o plano até a
  finalização técnica. Nenhuma alteração N2/N3 está autorizada.
- Git/publicação: criação e troca para a branch autorizadas e executadas. Commit,
  push, merge e deploy permanecem não autorizados.
- Estado: **implementação e validação técnica concluídas em 2026-08-13**;
  candidato local aguarda revisão humana e eventual autorização separada de
  commit.

## Estado observado

O candidato em `main@38bccfc` contém parte do redesign, mas as cinco telas ainda
divergem materialmente do protótipo em hierarquia, densidade, distribuição de
cards, navegação, formulários e responsividade. Em origem limpa o runtime atual
carrega sem erros. Em uma origem já controlada pelo service worker anterior foi
reproduzido um cliente híbrido — HTML novo com JavaScript cache-first antigo —
que gera erros de execução. O contrato PWA vigente documenta e aceita esse estado
transitório, incompatível com o uso seguro do terminal.

## Objetivo

Aplicar ao produto real a composição visual do protótipo nas telas Dashboard,
Execução, Contas, Contabilidade e Planejamento FX, preservando todas as funções e
contratos financeiros. Entregar temas claro e escuro, desktop e mobile, sem
overflow horizontal, e tornar o upgrade da PWA coerente: um cliente controlado
pelo worker anterior deve continuar usando integralmente o build anterior até a
ativação normal do novo worker.

## Escopo autorizado

1. Reconciliar shell, cabeçalho, navegação e tokens visuais com o protótipo.
2. Reordenar e dimensionar widgets do Dashboard sem alterar seus dados ou regras.
3. Ajustar a hierarquia e a densidade visual de Execução, Contas, Contabilidade
   e Planejamento FX; controles existentes devem permanecer acessíveis.
4. Alterar apenas comportamento de apresentação N1 necessário, como detalhes
   expansíveis, foco, navegação e estados vazios.
5. Corrigir a estratégia de navegação do service worker e fortalecer o teste de
   upgrade para proibir página híbrida utilizável e `pageerror` transitório.
6. Reconstruir os artefatos derivados pelo gerador oficial e reconciliar os
   documentos mutáveis afetados.

## Arquivos permitidos

- `docs/work/ACTIVE-TASK.md`
- `index.html`
- `src/styles/app.css`
- `src/js/manifest.json` somente para atualizar hashes de integridade dos
  scripts efetivamente alterados, sem mudar lista ou ordem
- `src/js/10-domain/05-brokers-prop-firms.js`
- `src/js/10-domain/04-stop-statistics.js`
- `src/js/20-ui/03-main-render.js`
- `src/js/20-ui/04-operational-clearance.js`
- `src/js/20-ui/05-execution-clearance.js`
- `src/js/20-ui/07-chart-crosshair-tooltip.js`
- `src/js/20-ui/08-input-bindings.js`
- `src/js/20-ui/12-nav-style.js`
- `src/js/30-accounting/02-accounting-engine.js`
- `src/js/30-accounting/03-mei-jp.js`
- `src/js/30-accounting/05-fx-planning/05-fx-ui.js`
- `src/js/40-app/01-navigation.js`
- `src/js/40-app/10-dashboard-immersive.js`
- `src/js/40-app/11-operational-shell.js`
- `src/js/40-app/12-global-dashboard.js`
- `src/js/40-app/13-dashboard-layout.js`
- `sw.js`
- `tools/service_worker_upgrade_test.py`
- `tools/smoke_test.py`
- `tools/quality_gate.py`
- `tools/rebuild_monolith.py` somente para execução, sem mudança planejada
- `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` somente via
  `tools/rebuild_monolith.py`
- `docs/architecture/PWA-UPDATE-LIFECYCLE.md`
- `docs/architecture/CODE-MAP.md`
- `docs/governance/CURRENT-STATE.md`
- `docs/governance/QUALITY-GATES.md`
- `README.md`, `tests/README.md`, `CHANGELOG.md`, `SESSION_HANDOFF.md` e
  `PROJECT-FILES.txt`, somente se a reconciliação final demonstrar impacto.

Qualquer necessidade fora dessa lista, ou qualquer passagem para N2/N3, interrompe
a implementação e exige nova autorização.

## Invariantes

- `jpwealth_v9_state`, `schemaVersion`, `DEFAULTS`, `migrate()`, backups e chaves
  auxiliares permanecem inalterados.
- Nenhuma fórmula, constante, limite, perfil, fase, DD, MDD, lote, LIFO,
  quarentena, contabilidade, MEI-JP ou Planejamento FX muda semanticamente.
- IDs DOM consumidos pelo runtime permanecem disponíveis; mover ou envolver um
  elemento não pode quebrar bindings, foco ou renderização.
- Ordem, lista e metadados funcionais de `src/js/manifest.json` permanecem
  inalterados; somente hashes dos scripts modificados acompanham o candidato.
- Nenhum dado real, backup privado, token ou credencial entra no worktree ou nas
  evidências.
- O ciclo PWA não limpa `localStorage`, não força takeover, não remove caches de
  outras aplicações e preserva uso offline do build coerente.
- O portátil é sempre derivado da fonte pelo gerador oficial.

## Critérios de aceitação

- As cinco telas reproduzem a hierarquia e a geometria essenciais do protótipo,
  com as mesmas áreas primárias, densidade e ordem de leitura.
- Navegação clássica com sublinhado ativo, cabeçalho e faixa contextual coerentes
  em claro/escuro.
- Dashboard: aviso de governança em largura total, cockpit em largura total e
  faixa P2 de Status, VRM, Notícias e Ações rápidas.
- Execução: clearance compacto com fatos em grade, seguido por Grade e LIFO.
- Contas: leitura tabular compacta; edição completa preservada em detalhe
  expansível e operável por teclado.
- Contabilidade: quatro indicadores no topo, seguida por Real x Projetado e
  Fechamento lado a lado; funções secundárias permanecem disponíveis.
- Planejamento FX: estado vazio e formulário em um card central linear, sem
  perder os quatro modos nem as funções existentes quando houver plano.
- Viewports mínimos verificados: desktop 1440×900 e mobile 390×844, nos temas
  claro e escuro; nenhum overflow horizontal.
- Zero `pageerror` e zero erro de console nos fluxos exercitados.
- No upgrade PWA, abas antigas e a navegação de descoberta permanecem no build
  antigo coerente; após fechar todos os clientes, o build novo abre online e
  offline, preservando caches externos.
- `python3 tools/quality_gate.py --tier full`, rebuild reproduzível,
  `git diff --check` e auditoria final aprovados no candidato.

## Resultado final

- `python3 tools/validate_project.py`: PASS — 60 scripts, 383 IDs estáticos e
  portátil reconstruído.
- `python3 tools/quality_gate.py --tier full`: PASS 19/19 — artefato
  `tools/.artifacts/quality-20260813T142631-full.json`; zero falha em todas as
  categorias.
- Navegador real: PASS nas cinco telas, 1440×900 e 390×844, claro/escuro, sem
  overflow horizontal; gaveta mobile, disclosures, expansão e foco de Contas
  exercitados; console sem warning/erro.
- Upgrade PWA: PASS — clientes antigos e descoberta permanecem no build antigo
  coerente; novo build abre online/offline somente após o fechamento dos
  clientes; caches externos preservados.
- Impacto agêntico: DETECTADO e reconciliado nos documentos consumidos por
  agentes/skills; nenhuma alteração local em agentes, skills ou routing foi
  necessária; `INDEX NOT REQUIRED`, `SYSTEM RECONCILED` para o blast radius
  estrito. Drifts documentais anteriores em `ARCHITECTURE.md`,
  `SECURITY-MODEL.md` e na tabela de superfície de `FX-PLANNING.md` permanecem
  fora da allowlist desta tarefa.

## Rollback

Reverter somente os arquivos desta tarefa para
`38bccfc11d47521cb17016a8476533298bc47678` e executar
`python3 tools/rebuild_monolith.py`. Como schema, chaves e dados não mudam, não há
migração nem exclusão de estado para desfazer. Não usar reset destrutivo.
