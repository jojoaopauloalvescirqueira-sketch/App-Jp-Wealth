# CHG-JPW-SIDEBAR-ICONS-20261022 — coerência dos ícones da lateral

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-SIDEBAR-ICONS-20261022
status: approved
objective: Tornar os ícones da lateral coerentes — um desenho Lucide por área, controles de recolher/abrir grupo na mesma família — sem alterar rotas, ordem, preferências ou módulos.
risk_level: N1   # N0-V nos ícones; N1 pelo ajuste de renderRailToggle em 02-sidebar.js
authority_required: A2
approved_by: "Proprietário, nesta conversa (Cowork, 2026-10-22): 'Aprovo a implementação' da proposta do canvas 'JP Wealth — Lateral e ícones'; escolhas: 'Worktree nova' e 'Ícones + controles'."
approved_at: 2026-10-22
target:
  root: "JP Wealth OS/.worktrees/sidebar-icones (worktree; excluída por .git/info/exclude)"
  branch: claude/sidebar-icones-20261022   # criada de main com autorização expressa
  baseline_sha: d517be0748f886085b3029c809bd68046e5c0f77
preexisting_work: "A pasta principal está em codex/planejamento-prazos-passado-20261022 com 22 alterações de outra tarefa. Não foram tocadas."
scope:
  allowed_files:
    - index.html            # símbolos shell-icon-*, <use> dos 5 destinos, chevron dos 4 grupos, markup inicial do #railToggle
    - src/styles/app.css    # somente: tamanho do SVG do #railToggle; chevron Lucide da lateral padrão
    - src/js/20-ui/02-sidebar.js   # somente renderRailToggle: glifo de texto -> <use> Lucide
    - src/js/manifest.json  # somente sha256 de 02-sidebar.js
    - src/vendor/lucide/icons/{microscope,target,chart-candlestick,wallet,wrench,panel-left-close,panel-left-open,chevron-right}.svg  # novos, byte a byte
    - src/vendor/lucide/icons/{search,chart-no-axes-combined,house,sliders-horizontal}.svg  # removidos: sem consumidor após a troca
    - src/vendor/lucide/PROVENANCE.json
    - src/vendor/lucide/README.md
    - tools/sidebar_icon_coherence_test.py   # teste focal novo, fora dos gates
    - docs/work/CHG-JPW-SIDEBAR-ICONS-20261022.md
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/**, docs/normative/**, tools/quality_gate.py, tools/ui_visual_quality_test.py, tools/agent_preflight.py, .github/**, sw.js, manifests/**, src/js/00-core/**, src/js/10-domain/**, src/js/30-accounting/**, docs/work/ACTIVE-TASK.md]
  allowed_actions: [leitura, implementação delimitada, download do commit Lucide fixado, testes sintéticos em navegador isolado, geração oficial]
  forbidden_actions: [commit, push, PR, merge, deploy, dados reais, novas dependências no repositório, alteração de gates]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, "src/vendor/downloads/*payload*.{js,json} e src/vendor/market-hours/runtime-payload.js (somente buildId, conferido)", src/vendor/pdfjs/runtime-assets.js (se idêntico)]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
data:
  test_policy: synthetic_only
  schema_change: forbidden
regressions_forbidden:
  - rotas, aliases, ordem, títulos, nomes acessíveis e visibilidade dos destinos
  - layouts topbar, glass e submenu (o chevron ::after do submenu permanece)
  - identidade do nó #railToggle, seu movimento para Configurações e as chaves jpw_rail / jpw_nav_submenu_rail
  - Dashboard: marcas i-area-* dos cartões (fora do escopo)
acceptance_criteria:
  - nenhum desenho de ícone repetido entre os destinos visíveis da lateral
  - todos os ícones da lateral e do #railToggle vêm do sprite shell-icon-* (Lucide fixado), 20 px, traço 1,75 em currentColor
  - abrir grupo: chevron Lucide; fechado aponta à direita, aberto gira 90°
  - ícone centralizado no botão na lateral recolhida (tolerância 2 px, UI-VISUAL-QUALITY)
  - PROVENANCE lista exatamente os símbolos shell-icon-* do index, com hashes conferidos
rollback: "Descartar a worktree/branch claude/sidebar-icones-20261022; nenhuma migração, preferência nova ou dado tocado."
```

## Brief — seis respostas

1. **Finalidade.** JP Wealth é aplicação financeira local-first; a lateral é o mapa das áreas. Esta tarefa melhora reconhecimento das áreas, principalmente com a lateral recolhida, onde o ícone é o único rótulo visível.
2. **Responsabilidade.** `index.html` é dono dos controles e do sprite; `app.css` da composição; `02-sidebar.js` renderiza o conteúdo do `#railToggle`; `11-operational-shell.js` move os mesmos nós (não alterado). Fonte: CHG-HEADER-NAVIGATION-LUCIDE-20260923 (a690bc88f527), §Compreensão.
3. **Comportamento.** Hoje (index.html 8fc9cfd12512, linhas 340–352): Planejamento e Forex usam o mesmo `shell-icon-chart-no-axes-combined`; Research usa lupa, Finanças Pessoais casa, Ferramentas sliders; `renderRailToggle` (02-sidebar.js a6a87b354f04, l.30) escreve `‹`/`›` em texto; a seta de grupo é um `::after` com bordas (app.css 8493d7ac6211, l.8635). Depois: microscope, target, chart-candlestick, wallet, wrench; `panel-left-close/open`; `chevron-right` em `<svg><use>`.
4. **Impacto.** Somente apresentação. Testes que usam `#railToggle` dependem da identidade do nó e do pai, não do texto (navigation_sidebar_hover_test, navigation_layout_choice_test, contextual_sidebar_test). `#railToggle` aparece também em Configurações (`settingsRailSlot`) e no layout submenu: o mesmo SVG serve a todos, com rótulo preservado.
5. **Limites.** Sem mudança de rota, ordem, preferência, gravação, foco ou nomes acessíveis; SVGs decorativos (`aria-hidden`), nome acessível continua no botão. Sem alteração de gates (adicionar casos ao `ui_visual_quality_test.py` é control plane e fica como pendência).
6. **Evidência.** Teste focal novo `tools/sidebar_icon_coherence_test.py` (unicidade, origem no sprite, centralização no recolhido, chevron, rail toggle em claro/escuro); testes de navegação existentes; `validate_project.py`; `build_reproducibility_test.py`; `quality_gate.py --tier standard` quando o ambiente permitir.

## Registro de execução

Candidate: worktree `claude/sidebar-icones-20261022` sobre `d517be0`, sem commit. Fingerprint = SHA-256 da lista de hashes dos arquivos alterados/novos (`candidate3.sha256`): `fe373b659e9ca6ab…`; este registro foi escrito depois e altera somente este documento. Testes de navegador executados numa cópia do candidate e numa baseline reconstruída (`git archive d517be0` dos caminhos alterados), em Linux/Chromium 141 headless; Playwright 1.60.0 (versão de `requirements-dev.txt`) em venv temporário, fora do repositório.

| Verificação | Candidate | Baseline d517be0 | Resultado |
|---|---|---|---|
| `sidebar_icon_coherence_test.py` (novo; source + portable) | 186/186 | 8 falhas estáticas + falhas de navegador (ícone repetido, glifo de texto, sem chevron Lucide) | PASS; RED na baseline comprovado |
| Contraprova: chevron sem margem −5 px | 1 falha: “Finanças Pessoais” passa a 2 linhas | — | oráculo rejeita a regressão encontrada e corrigida |
| `git diff --check` (device) | limpo | — | PASS |
| `validate_project.py` | OK | — | PASS |
| `navigation_layout_choice_test.py` | rc 0 | — | PASS |
| `settings_modal_test.py`, `navigation_ia_test.py` | rc 0 | — | PASS |
| `smoke_test.py` | rc 0 em 3 execuções isoladas | rc 0 em 3 execuções isoladas | PASS (falhou 1× em cada árvore sob carga paralela: instabilidade do ambiente) |
| `navigation_sidebar_hover_test.py` | keyboard e geometry 320 falham | mesmas 4 falhas | BASELINE_FAIL |
| `contextual_sidebar_test.py` | `research-probability-lab` | mesma falha | BASELINE_FAIL |
| `apple_experience_test.py` | 10 falhas “panorama chapters”; “sidebar icons do not displace labels” PASS | mesmas 10 | BASELINE_FAIL |
| standard sem os 3 itens que exigem git (49 entradas) | mesmo conjunto aprovado/falho da baseline | — | sem diferença; `exec-submenu` (ERR_FAILED de rede), `alladin-foundation` e `session-epoch-protocol` (histórico raso) falham nas duas = ENVIRONMENT_ERROR |
| `ui_visual_quality_test.py` | 150 PASS, 0 FAIL, driver Playwright caiu (EPIPE) antes do fim | não executado | ENVIRONMENT_ERROR |
| `quality_gate.py --tier standard` completo | — | — | NOT_RUN: o device tem git sem Playwright; a nuvem tem Playwright sem `.git` |
| `build_reproducibility_test.py`, `navigation_order_test.py` | exigem `git ls-files`/`rev-parse` | — | ENVIRONMENT_ERROR |

Geração oficial: `python3 tools/rebuild_monolith.py` (device). Payloads de `src/vendor/downloads` e `market-hours` mudaram somente no `buildId` (conferido por normalização).

Pendências: rodar `python3 tools/quality_gate.py --tier standard` no Mac; casos da lateral no `ui_visual_quality_test.py` exigem CHG de control plane; registro em `tools/regression-memory.json` não feito (arquivo também alterado pela tarefa Codex em andamento); marcas `i-area-*` dos cartões do Dashboard (Planejamento usa a marca do Forex) ficaram fora do escopo. Teste manual e aceite visual do proprietário pendentes; commit não autorizado.

## Autorização de Git

Proprietário, nesta conversa (2026-10-23): "autorizo o commit e integração deste design". Cobre o commit na branch `claude/sidebar-icones-20261022` e a integração (merge) em `main` local. Push, PR e publicação não foram autorizados nesta mensagem. Conteúdo commitado conferido byte a byte contra o candidate testado (`fe373b659e9ca6ab…`); só este documento difere. `quality_gate --tier standard` completo segue NOT_RUN, conforme o registro acima.
