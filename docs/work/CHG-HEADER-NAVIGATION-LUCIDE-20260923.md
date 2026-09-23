# CHG-HEADER-NAVIGATION-LUCIDE-20260923

```yaml
schema: jp-harness/chg/v1
change_id: CHG-HEADER-NAVIGATION-LUCIDE-20260923
status: approved
objective: Aplicar o acabamento da PV-01.2a ao cabeçalho e navegação reais, incorporando SVGs Lucide licenciados sem alterar comportamento ou módulos.
risk_level: N1
authority_required: A2
target:
  root: /Users/joaopauloalves/.codex/header-navigation-lucide/20260923/product
  branch: codex/header-navigation-lucide-20260923
  baseline_sha: b0cd4b61dc3fdd63f0fcf8bc1255455e6c59624e
scope:
  allowed_files:
    - index.html # símbolos dedicados e consumidores do cabeçalho/nav; avisos de licença
    - src/styles/app.css # somente seletores de cabeçalho/navegação
    - src/vendor/lucide/LICENSE
    - src/vendor/lucide/PROVENANCE.json
    - src/vendor/lucide/README.md
    - src/vendor/lucide/icons/bell.svg
    - src/vendor/lucide/icons/settings.svg
    - src/vendor/lucide/icons/log-out.svg
    - src/vendor/lucide/icons/layout-dashboard.svg
    - src/vendor/lucide/icons/search.svg
    - src/vendor/lucide/icons/chart-no-axes-combined.svg
    - src/vendor/lucide/icons/house.svg
    - src/vendor/lucide/icons/briefcase-business.svg
    - src/vendor/lucide/icons/sliders-horizontal.svg
    - src/vendor/lucide/icons/x.svg
    - src/vendor/lucide/icons/chevron-left.svg
    - docs/work/CHG-HEADER-NAVIGATION-LUCIDE-20260923.md
    - docs/work/ACTIVE-TASK.md # registro focal; histórico preservado
  forbidden_files: [src/js, tools, sw.js, manifests, docs/normative, AGENTS.md, skills, configurações do usuário, outras worktrees]
  allowed_actions: [branch e worktree isoladas autorizadas, leitura, implementação delimitada, download oficial Lucide, testes sintéticos, auditoria, capturas e evidências locais]
  forbidden_actions: [commit, push, PR, merge, deploy, integração onboarding, instalação de pacotes/aplicativos/fontes, investigação de transporte]
  regressions_forbidden: [mudança de rotas/aliases/ordem/preferências, alteração de módulos internos, perda de identidade/foco/rascunho, ícones universalmente visíveis, cálculo/gravação/confirmação alterados]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, src/vendor/pdfjs/runtime-assets.js]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [lucide.dev, github.com/lucide-icons/lucide, api.github.com/repos/lucide-icons/lucide, raw.githubusercontent.com/lucide-icons/lucide, loopback local isolado]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [Python existente, Playwright existente, Chromium isolado, servidor local do projeto, gerador e validadores existentes]
acceptance_criteria:
  - quatro layouts e temas preservam comportamento/visibilidade/identidade dos controles
  - azul nas ações e vinho na seleção; medidas e acabamento derivados da PV-01.2a, adaptados aos layouts existentes
  - apenas ícones usados no shell; geometria oficial comprovada por hash e avisos ISC/MIT preservados
  - módulos internos, código JS, testes, schemas e outros candidates idênticos
  - foco/teclado/abertura/fechamento e retorno testados, sem perdas de rascunho
  - capturas comparáveis e fingerprint do candidate; limitações explícitas
approved_tests:
  - baseline/candidate browser matrix: sidebar/topbar/glass/submenu, light/dark, 1440/1024/390/320; capturas na mesma origem sintética e cenário equivalente
  - DOM/control identities, financial storage/draft preservation, native focus/hit testing, header actions cancelled without operational confirmation
  - navigation_layout_choice_test.py; navigation_order_test.py; contextual_sidebar_test.py; forex_navigation_table_test.py; settings_modal_test.py
  - quality_gate.py --tier standard; validate_project.py; build_reproducibility_test.py; diff and asset license/provenance checks
  - revisão independente do candidate exato
rollback:
  source: [descartar somente delta desta worktree se solicitado, ou usar baseline preservada para comparação]
  application_state: [nenhuma migração ou nova preferência]
  data: [nenhum dado real acessado]
  environment: [parar servidor de revisão quando não necessário, sem alterar servidores existentes]
  verification: [hashes main/onboarding/prévias, diff delimitado]
approved_by: Proprietário, solicitação explícita anexada nesta conversa
approved_at: 2026-09-23
expires_on: [mudança material de raiz/branch/escopo/risco, dado real necessário, alteração de baseline]
```

## Compreensão e independência

JP Wealth é uma aplicação financeira local-first. Esta tarefa melhora identificação, hierarquia e acesso ao trabalho, sem tornar o shell fonte de regras ou dados. O HTML é dono dos controles; CSS define composição; `01-navigation.js` resolve destinos, `11-operational-shell.js` move os mesmos nós e controla níveis/gavetas, `02-sidebar.js` renderiza o recolhimento. Nenhum desses scripts será alterado.

Hoje existem quatro layouts e SVGs de procedência anterior não comprovada. Depois haverá SVGs Lucide restritos ao shell, acabamento azul/vinho e alvos/estados consistentes. Preservar mecanismos de duas linhas do menu, disclosures CSS/Unicode e glyph de rail quando ligados ao controlador; documentá-los como existentes, não como Lucide. Não modificar marca/avatar ou símbolos compartilhados de outras telas: adicionar IDs dedicados no sprite existente e trocar somente os consumidores autorizados.

Há chamadas do runtime à situação de onboarding na navegação e nas notificações. O delta visual não depende de corrigi-las: nenhum callback, guarda, cálculo, fluxo de cadastro ou período muda. O candidate de onboarding não é lido como fonte de implementação nem copiado. Sua classificação anterior PARTIALLY_VALIDATED / AUDIT_INCONCLUSIVE permanece.

Risco N1 conservador devido a foco/acessibilidade e impacto de apresentação na navegação. A autorização conversacional cobre branch/worktree e execução deste recorte, não aceite humano. A aparência de Liquid Glass e sua transparência permanecem próprias; os outros modos recebem superfícies sólidas. Não revelar SVGs onde o layout os oculta deliberadamente.

## Evidência e limites previstos

Evidências em `../evidence/`, incluindo baseline extraída por `git archive` (não uma nova branch/worktree), capturas, scripts locais de observação e resultados. Não editar testes existentes. Falha de carregamento será documentada sem diagnóstico RST/FIN, mudança de fila ou outro full. Testes da prévia não são usados como aprovação do produto. CSS será restrito aos hosts de shell; conteúdo de módulos e dados será comparado com a baseline. Portátil e build gerados pelo comando oficial inalterado; licença inline acompanha o sprite também no portátil.

## Fontes acessadas

A tabela a seguir registra hashes dos arquivos lidos; não constitui aprovação nem alteração dessas fontes.

| Fonte | SHA-256 | Recorte |
|---|---|---|
| /Users/joaopauloalves/.codex/header-navigation-lucide/20260923/product/AGENTS.md | `27e4289bd8aba1332e98a2f2fbb9f2c4de97d5bd37b8f984d127df7740d06cf6` | contrato/limites pertinentes ao shell; referência visual quando HTML |
| /Users/joaopauloalves/.codex/header-navigation-lucide/20260923/product/docs/governance/PROJECT-CONTEXT.md | `37637ca60dd014e938d3156cba402bec3045b88d4ec5989d776ff23482dc9a27` | contrato/limites pertinentes ao shell; referência visual quando HTML |
| /Users/joaopauloalves/.codex/header-navigation-lucide/20260923/product/docs/architecture/NAVIGATION-HIERARCHY.md | `d478195c021b4567a67aad44c9e351c10407058fd4cd21737b3bac8f76c06cc9` | contrato/limites pertinentes ao shell; referência visual quando HTML |
| /Users/joaopauloalves/.codex/header-navigation-lucide/20260923/product/docs/governance/CHANGE-PROCESS.md | `a3bce305d27a2b561a1b1ce1a57f27849632c8fac284bd8ba1d88e795c7de46e` | contrato/limites pertinentes ao shell; referência visual quando HTML |
| /Users/joaopauloalves/.codex/header-navigation-lucide/20260923/product/skills/jpw-design/references/design-philosophy.md | `fcc11d3eab563f3464e84e5b8886ddb9ee4784cff75530702f07776d19e0dff7` | contrato/limites pertinentes ao shell; referência visual quando HTML |
| /Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/99B - SOFTWARE DEV/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md | `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8` | §§12–14,24,28–30,36–49 |
| /Users/joaopauloalves/.codex/visualizations/2026/09/23/jpw-apple-resource-review/JP-Wealth-PV-01.2a.html | `479a9f37c65943d12150bea536126645f77ff140eebeed6c0153d60a83086127` | contrato/limites pertinentes ao shell; referência visual quando HTML |


## Resultado da execução — candidate para revisão

Implementação delimitada concluída, build `da24235203f5d84a`. Incorporação no candidate não é aceite humano, aprovação financeira/onboarding, integração ou publicação. O campo `status: approved` acima registra autorização do escopo pelo proprietário, não aprovação dos resultados.

- Runtime: somente `index.html` e um bloco adicional de 101 linhas em `src/styles/app.css`; 11 símbolos dedicados/consumidores Lucide. Os 33 símbolos legados, marca, avatar e atributos dos 176 botões permanecem iguais. `#appMain` textual íntegro. Todos os scripts, testes, manifesto e geradores inalterados.
- Lucide: commit `f06ac67e33d645c40b8ce19a0419c85c5d7dd751`; raw SVGs e licença originais; 20 px/traço 1,75 via CSS, geometria intacta. Avisos ISC/MIT integrais no sprite e portátil. Catálogo conferido depois da incorporação.
- Estrutura, diff-check, build reproduzível e cinco focais (layouts, ordem, Forex, Settings e build) PASS. Layouts incluem preferências, falhas sintéticas, tint, lifecycle, navegação, submenu, Notas, visual e portátil.
- `contextual_sidebar_test.py`: BASELINE_FAIL demonstrada por mesma assertiva `borderLeftWidth > 0` em classic na base e candidate; logs originais preservados. Não alterada a asserção.
- Matriz: 32/32 cenários por versão; quatro modos × dois temas × 1440/1024/390/320 px, 128 capturas por versão. HTML/campos/tabelas e 15 propriedades de estilo de Execution Board iguais nos 32 contextos. 32 comparações de interações preservam identidades, aliases, estado e armazenamento, com inicialização auxiliar de epoch idêntica à base. Glass mobile: 8/8 verificações de acesso às ações por rolagem PASS.
- Gate `standard` original: 45 PASS / 1 PRODUCT_FAIL. Em Alladin finalização, C12 reportou `fxActivePlanRaw is not defined`. Uma execução isolada na base e uma no candidate passaram. Falha original mantida, causa inconclusiva; sem outro gate, investigação de transporte ou mudança financeira.
- Auditoria independente estática PASS; inspeções visuais efetivas e testes de interação têm registros separados. Safari, iPhone físico e tecnologias assistivas reais não exercitados.

Limitações preexistentes preservadas: retorno ao BODY ao cancelar Finalizar Sessão; no Glass em 1024 px também após notificações/configurações/perfil. Itens N1 topbar de 20/26 px e Glass desktop de 42 px continuam compactos; não se afirma alvo de 44 px universal. As quatro ações de cabeçalho do candidate têm 44×44 px, inclusive quando alcançadas por rolagem no Glass compacto.

NO AGENTIC IMPACT: nenhuma mudança em autoridade, fluxo de tarefas, Harness, prompts, gates, contratos de domínio, APIs ou persistência. Atribuição/licença e contrato focal documentam somente esta mudança visual.

Preservação: main limpa no mesmo HEAD; hashes de 413 arquivos do candidate de onboarding e 86 arquivos das prévias/evidências anteriores iguais. Onboarding permanece PARTIALLY_VALIDATED / AUDIT_INCONCLUSIVE. Sem Git mutável após criação autorizada da branch/worktree, sem pacote/app/fonte instalado, sem recursos Apple extraídos.

Registro externo desta entrega: `../evidence/DELIVERY.md`, `REVIEW.html`, `CANDIDATE-FINGERPRINT.json`, `official/`, `browser/`, `independent-audit.md` e evidências de incorporação/preservação. O fingerprint identifica o delta completo sem commit. Rollback permanece o descarte exclusivamente deste delta, se solicitado, sem dados ou migrações.
