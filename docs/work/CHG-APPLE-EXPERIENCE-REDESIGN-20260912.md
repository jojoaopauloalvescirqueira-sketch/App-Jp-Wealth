# APPLE-GUIDED COMPLETE EXPERIENCE REDESIGN

## Brief e autorização

Pedido humano integral em anexos 46e374e2 e 03c20777 (byte-idênticos), em 2026-09-12.
Autoriza oito ondas de redesign amplo, decisões locais de apresentação/interação,
branch/worktree própria, testes/derivados e documentação diretamente afetada.
Não concede aceite ou Git/publicação desta campanha.

JP Wealth apoia organização financeira, risco e estudo; interface projeta fontes
canônicas e estados de indisponibilidade. Usuários precisam distinguir registro,
projeção, estudo e ato financeiro. 20-ui apresenta dados; 40-app coordena fluxo;
index/CSS compõem superfícies. Nenhum novo cálculo, schema ou save é autorizado.
A10–A13 constam do ancestral ac6875b5 e PR16; PR17 integrou DESIGN01 em fafb228.
A12 permanece parcial e A13 pausa/preserva RAM. Main principal não foi sincronizada.

Fontes: AGENTS, README, CONTEXT-MAP, PROJECT-CONTEXT, CURRENT-STATE, ACTIVE-TASK,
NAVIGATION-HIERARCHY; X1/filosofia v1, X2, Atlas parcial; Harness §§12–20/31/49,
SHA c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8.
Fontes Apple atuais, URLs/hashes e capturas Sketch: ../evidence/apple-source-index.json
na raiz externa da campanha; material externo nunca concede autoridade.

Inspeção inicial: 18 superfícies × desktop claro/mobile escuro/tablet claro,
dados sintéticos e rede loopback em before-02. É inspeção de estados, não prova
de todos os fluxos. Primeira tentativa preserva dois seletores incorretos do
controlador, corrigidos somente no controlador externo. Não é falha do produto.
A ausência de overflow nesses estados não comprova responsividade integral.

## CHG

```yaml
schema: jp-harness/chg/v1
change_id: CHG-APPLE-EXPERIENCE-REDESIGN-20260912
status: approved
objective: Redesenhar apresentação e interação existentes em oito ondas e entregar candidate local.
risk_level: N1
authority_required: A2
target:
  root: /Users/joaopauloalves/.codex/apple-redesign/20260912/product
  branch: codex/apple-experience-redesign-20260912
  baseline_sha: fafb228316cbcad8091ebc4632443a51687ace43
scope:
  allowed_files:
    - index.html
    - src/styles/app.css
    - src/js/20-ui/25-dash-macro.js
    - src/js/20-ui/24-alladin-views.js
    - src/js/20-ui/23-research-views.js
    - src/js/20-ui/20-finpes-comparison.js
    - src/js/20-ui/18-finpes-budget.js
    - src/js/20-ui/19-finpes-debts.js
    - src/js/20-ui/21-finpes-scenarios.js
    - src/js/20-ui/22-finpes-overview.js
    - src/js/20-ui/14-nocoda-studies.js
    - src/js/20-ui/15-pivot-studies.js
    - src/js/20-ui/13-exec-views.js
    - src/js/40-app/09-settings-modal.js
    - src/js/40-app/11-operational-shell.js
    - src/js/40-app/14-mvp-notes.js
    - src/js/40-app/17-economic-calendar.js
    - src/js/40-app/18-galton-board/05-renderer.js
    - src/js/40-app/18-galton-board/06-controller.js
    - src/js/manifest.json
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
    - tools/apple_experience_test.py
    - docs/architecture/APPLE-EXPERIENCE-DIRECTION.md
    - docs/architecture/NAVIGATION-HIERARCHY.md
    - docs/architecture/CODE-MAP.md
    - README.md
    - SESSION_HANDOFF.md
    - docs/governance/CURRENT-STATE.md
    - docs/work/ACTIVE-TASK.md
    - docs/work/CHG-APPLE-EXPERIENCE-REDESIGN-20260912.md
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/**, docs/normative/**, src/js/00-core/**, src/js/10-domain/**, src/js/30-accounting/**, .github/**, sw.js, tools/quality_gate.py, tools/validate_project.py, tools/rebuild_monolith.py]
  allowed_actions: [redesign visual e interação delimitada, oito ondas, testes sintéticos, derivados oficiais, documentação factual afetada, evidência externa]
  forbidden_actions: [staging, commit do produto, tag, push, PR, merge, deploy, reset Git, stash, dados reais, nova persistência, dependências, reindexação]
  regressions_forbidden: [mudança financeira, perda de rascunhos ou preferências, duplicação de eventos, ocultação de bloqueios, alteração de matemática do Lab]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [Apple Developer, Sketch público, W3C, loopback de testes]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [Python Chromium e ferramentas existentes, gerador oficial, Git leitura e worktree autorizada, fixtures Git sintéticas próprias sem remotos hooks ou ligação ao produto]
acceptance_criteria: [oito ondas examinadas, mesmos dados e resultados financeiros, A10-A13 preservados, rascunhos e foco, 320 390 768 1024 1440 claro escuro, acessibilidade focal, identidade e recuperação, auditoria independente]
approved_tests: [apple_experience_test, regressões de navegação PF Research Alladin Notas Settings Galton existentes, standard, FULL final, reprodutibilidade, PWA]
rollback:
  source: baseline.json e baseline.tar externos; recuperar em cópia e comparar hashes; reverter somente delta próprio após conferir trabalho posterior
  data: perfis sintéticos isolados; não modificar dados reais
  environment: preservar worktrees stash e evidências anteriores
  verification: hashes modos e recuperação integral do candidate final
approved_by: proprietário no prompt integral de redesign
approved_at: 2026-09-12
expires_on: [mudança financeira ou persistência necessária, novo requisito de domínio, dependência material, conflito de fontes, impossibilidade de rollback]
```

Restrições internas: funções de domínio dentro de arquivos UI permanecem intactas;
manifest apenas hashes, sem mudar ordem; Lab renderer somente desenho, controller
somente panelHTML/apresentação; nenhum novo lifecycle; nav resolver intacto.

## CTX — representação factual delimitada (N3/A4 local)

```yaml
schema: jp-harness/ctx/v1
context_change_id: CTX-APPLE-EXPERIENCE-REDESIGN-20260912
status: approved
root: /Users/joaopauloalves/.codex/apple-redesign/20260912/product
mode: SEQUENCIAL
approved_branch: codex/apple-experience-redesign-20260912
create: [docs/work/CHG-APPLE-EXPERIENCE-REDESIGN-20260912.md, docs/architecture/APPLE-EXPERIENCE-DIRECTION.md]
modify: [docs/architecture/NAVIGATION-HIERARCHY.md, docs/architecture/CODE-MAP.md, README.md, SESSION_HANDOFF.md, docs/governance/CURRENT-STATE.md, docs/work/ACTIVE-TASK.md]
preserve: [históricos, main, stash, outras worktrees, checkpoints, A10-A13]
do_not_touch: [Harness, skills, autoridade, normas, índices, grafo]
source_of_truth: [produto observado na baseline e no delta, autorização humana, pesquisa oficial citada]
information_promotion: [distinguir APPLE de adaptação e decisão própria; não promover hipótese ou teste antigo a fato novo]
acceptance_criteria: [representações afetadas coerentes, ausência de autoridade nova, fontes rastreáveis]
approved_by: proprietário na seção24 do prompt de redesign
approved_at: 2026-09-12
expires_on: [necessidade de alterar instruções ou curadoria geral]
```

IMPACT: CURRENT-STATE/ACTIVE-TASK/handoff estão históricos após PR17; novos
cabeçalhos representarão somente esta campanha. Arquitetura de apresentação e
CODE-MAP afetados; políticas, skills e Atlas não recebem edição. Nenhum índice.

## Ondas e expectativas fixadas antes da implementação

1. Pesquisa e auditoria → direção, inventário de ícones, mapas gráfico/3D.
2. Tokens/ícones/componentes → sem renomear tokens consumidos; estados e contraste.
3. Shell → labels claros, ícones semânticos, mesmas rotas/ordem/alternativa superior.
4. Dashboard/Forex → orientação compacta, contexto exclusivo, sem mascarar risco.
5. PF/Research/Lab → hierarquia e formulários legíveis; mesmo estado e matemática.
6. Alladin/Notas/Settings → cadastros versus fatos, escrita sem ruído, foco preservado.
7. Gráficos/3D → somente oportunidade justificada com dados existentes; rejeitar decoração.
8. Consistência/acessibilidade/performance → matriz, focais, standard, FULL, recuperação/auditoria.

Antes de cada alteração comportamental, fixar casos no teste focal. Baseline
sem capacidade proposta não é bug financeiro. Falhas brutas são preservadas.
Validação sintética não é pesquisa humana ou certificação WCAG integral.

## Revisão V2 — correção focal pós-auditoria

V1 preservada no manifesto/diff/tar externos. Auditoria V1 apontou P2: label
Encerrar ausente do nome acessível. Dentro do mesmo escopo N1, index passa a
mostrar Finalizar sessão, preservando aria-label/title/handler e confirmações;
CSS permite altura automática no cabeçalho móvel. Teste Apple verifica inclusão
do label no nome e sua geometria; referências de rótulo acompanham a revisão.
Derivados oficiais e nova identidade; FULL V1 não é execução da V2. Revalidar
focais de nome/geometria/navegação, FULL final e auditoria focal. Rollback somente
desse delta usa recovery-v1; baseline original continua preservada.


# APPLE-COMPLETION-01 — complemento autorizado

Fonte: pedido humano integral 1de6482d-a233-4c4c-b7f6-56e7a82ac5b2, 12/09/2026.
A2/N1 para composição e interação; CTX factual delimitado N3/A4 conserva as regras anteriores. Mesma raiz /Users/joaopauloalves/.codex/apple-redesign/20260912/product e branch codex/apple-experience-redesign-20260912; HEAD fafb228316cbcad8091ebc4632443a51687ace43. V2 é pai preservado, não candidate aceito: SHA256 79dc7dba3a4940a8960f6ca3bca41dc3285396171e99ba1b96c35c103a87d323, build ecb3a3c493cc95e7, 303 inputs reconferidos. Nova fase registrada antes da primeira escrita em evidence/completion/phase-start.json; 877 registros anteriores inventariados.

## Finalidade e fronteiras
JP Wealth organiza finanças, risco e estudos. Esta fase torna clara a tarefa antes de seus controles: Dashboard orienta prioridades via mesmos quatro read-models; Forex distingue prontidão e ação; PF distingue competência, planejado/realizado e lançamentos; Research oferece bancadas de estudo; Alladin separa entidades de fatos econômicos; Notas prioriza conteúdo; Settings organiza preferências. Index e renderizadores compõem os nós; CSS define hierarquia; handlers e domínios continuam os autores dos atos. Dados sintéticos e falhas expostas demonstram preservação. Leitura visual não prova interação, teste verde não prova transformação.

Mantida a allowlist completa do CHG original (caminhos relativos à raiz acima). Escritas previstas no completion: index.html; src/styles/app.css; src/js/20-ui/{25-dash-macro,24-alladin-views,23-research-views,18-finpes-budget,19-finpes-debts,20-finpes-comparison,21-finpes-scenarios,22-finpes-overview,14-nocoda-studies,15-pivot-studies,13-exec-views}.js; src/js/40-app/{09-settings-modal,14-mvp-notes,17-economic-calendar}.js; src/js/40-app/18-galton-board/{05-renderer,06-controller}.js; src/js/manifest.json somente hashes; build-id.js e dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html somente gerador; tools/apple_experience_test.py; e os oito documentos já delimitados pelo CHG/CTX. Somente os efetivamente necessários serão alterados. Nenhum arquivo de domínio, persistência, regras, A10/A11/A12/A13 lifecycle, skill, CI ou gate recebe edição.

## Contrato de apresentação e validação fixado antes da transformação
- Comparação das 40 duplas V2 por lead e críticos separados, classificação A/B/C por superfície, decisões concretas antes de implementar.
- Dashboard: mesmos quatro resumos/valores/CTA e exceções, resumo e ação antes de detalhe; sem novos cálculos/consultas, Sistema/Atalhos mantidos.
- PF: resumo da competência antes dos blocos de edição, Receitas e Despesas antes de informações auxiliares; mesma materialização/rollback/change, controles e rascunhos. Reordenar DOM conforme leitura visual, não somente CSS order.
- Forex: contexto, onboarding e bloqueios visíveis; composição de workspace, nenhuma aprovação operacional inferida.
- Research: estudos com seleção/entrada/resultado/estado distintos; calendário continua lista temporal com mesma fonte/filtragem; canvas Lab e executar antes das métricas secundárias, mesmos parâmetros/física/RAM/pausa e controles. Nenhuma persistência nova.
- Alladin: títulos/contexto de entidade e ledger/saldo/quantidade com ações associadas; qualidade nunca vira empty/zero. UI em módulos read-only continua sem form/input.
- Notas: estados e conteúdo orientam a seleção/organização; nenhum autosave, retry ou fechamento alterado.
- Settings: escolha de preferência mais direta, busca/categorias/slots/histórico e proteções inalterados.
- Ícones: fonte SVG original única quando substituição necessária; texto nas ações ambíguas, sem substituir operadores matemáticos/semânticos por busca global.
- Gráficos: decisão por pergunta/dado canônico, 3D comparado concretamente como conceito externo antes de escolher; não requer engine nova.

Focais existentes e extensão Apple antes/junto do delta: identidade/ausência de duplicatas, ordem DOM e geometria, mesmas ações e valores sintéticos;320/390/768/1024/1440 claro/escuro, teclado/foco, reduced motion e contraste. Depois standard/FULL existentes, reprodutibilidade/PWA e revisão independente funcional/visual/a11y/escopo/fontes. Gate obrigatório não enfraquecido. Testes e falhas anteriores preservados; fixtures mesmas nas comparações. As expectativas da V2 que descrevem apresentação deliberadamente substituída serão diferenciadas dos invariantes de domínio, com justificativa explícita.

## Recuperação e encerramento
V2 preservada em candidate-v2.{json,diff,tar}, recovery-v2 e capturas/comparador; nunca sobrescrever. Somente delta desta fase pode ser revertido após conferir autoria posterior, sem reset/stash. Evidências novas em evidence/completion; controles externos existentes recebem variantes com nomes novos se necessário. Candidate final será novo manifesto/diff/tar/recuperação, com V2→final e baseline→final e auditoria independente. Nenhuma escrita em main/outras worktrees. Sem staging/commit/push/PR/merge/deploy nem aceite presumido. Parar apenas diante de necessidade material fora desses limites.


### Completion pass — delta efetivo e fechamento de escopo
Os13 renderizadores alterados são UI14,15,18–22,24,25; app09,14,17 e app18/06
somente panelHTML. Somam-se index/CSS, manifest-hashes, derivados oficiais,
focal Apple e os8 documentos já autorizados. Sem novos caminhos além dos3
introduzidos naV2. Campos/mutações/testes de domínio/gates intactos.
A projeção NoCoda usa geometria canônica e interrompe visualização sem escala
finita; Pivots usa median/n existentes. Contratos e alertas permanecem.
Crítica intermediária revelou precedência CSS de headers/SVG e esforço móvel;
correções de apresentação foram feitas antes do freeze seguinte. Logs antigos,
inclusive interrupções de teste/identidade concorrente, permanecem externos.
Manifesto, avaliação, recuperação e encerramento ficam no diretório completion;
não se modifica o candidate congelado para registrar teste ou aceite posterior.
