# Campanha A10–A13 — candidate local

## Brief e autorização recebida

Pedido integral do proprietário em 2026-09-11, anexo c97fb09e-3e66-49af-91a3-f326b4218558. A seção específica final autoriza A13 na mesma campanha e sucede a exclusão anterior de A13. Autoriza engenharia, preferência de apresentação, geração oficial, testes sintéticos e branch/worktree próprias; não autoriza integração. N2/A3 por persistência da ordem e projeção exportável. Nenhuma alteração de control plane ou regra financeira.

1. **Finalidade:** JP Wealth organiza finanças e risco localmente. Esta campanha reduz fricção de navegação e transcrição de fatos registrados, sem gerar recomendação nem operação.
2. **Responsabilidades:** `20-ui` projeta fatos; `40-app` coordena navegação, Editor e ciclo de vida; Research recebe estudo/experimentação; Forex mantém contexto operacional.
3. **Antes/depois:** mesmos cinco primários em ordem fixa passam a ordem configurável; metadados globais passam a Forex; operação única e histórico ganham cópia somente leitura; o único jogo Galton deixa Configurações e pertence a Research.
4. **Consumidores:** shell lateral/superior/móvel, Editor, subdestinos, render de cabeçalho, Consolidado, histórico e Galton. Operação é agregado de ordens, não sinônimo de uma ordem. Histórico não captura conta/equity final: não inventar esses dados.
5. **Limites:** preservar S, schemas, fórmulas, drafts, preferências anteriores e barreiras. A10 adiciona preferência por navegador, fora de S, sem migração. A12 usa whitelist de fatos, sem credenciais; campos de significado normativo conflitante permanecem NEEDS_HUMAN_RULE. A13 conserva física/PRNG/estatística e preferências.
6. **Provas:** expectativas fixadas abaixo, focais DOM/estado/armazenamento/clipboard, regressões próximas, FULL final, auditor independente e recuperação por snapshot/diff. Nenhum aceite humano antecipado.

Fontes examinadas na base: AGENTS, README, CONTEXT-MAP, PROJECT-CONTEXT, CURRENT-STATE/ACTIVE-TASK (fotografias anteriores); NAVIGATION-HIERARCHY, STATE-SCHEMA, DB-STORAGE-GOVERNANCE, DATA-RECOVERY, SECURITY-MODEL; código e consumidores correspondentes. Harness mestre v2, §§12–16,24,36–49. Skills preflight/change-control/data-safety/browser-verification/post-change-audit; X1 IMPLEMENTAR e Atlas seletivo. Autoridade vem do pedido, não deste documento. As evidências registram hashes de fontes e comandos, diferenciando leitura de execução.

## Expectativas anteriores aos patches

- A10: default `[dashboard,research,forex,personal-finance,alladin]`; qualquer uma das 120 permutações válidas; mesmos nós, primário ativo, rotas/aliases e página inicial. Prévia não grava; cancelar/fechar desfaz prévia; salvar confirma apenas ordem; restauração afeta somente ordem. Inválido mantém bytes e fallback utilizável. Recusa não anuncia sucesso; indeterminação não libera retry cego. Teclado, toque, mouse, temas e três composições.
- A11: uma `gdContextRow`, hidden/inert fora de Forex, sem espaço; volta com render canônico atual. Avisos globais de persistência permanecem fora da barra. Nenhum cálculo ou timer adicional.
- A12: operação ativa com múltiplas ordens e registro histórico distinto; texto de entrada/andamento/encerramento conforme fatos. Conta mestre atual não implica vínculo histórico. Ausência/PENDING não viram zero; payload explícito exclui login/senhas/chaves. Copiar não chama save, não cura estado, não carimba finalização, não cria evento ou muda dirty; feedback de sucesso/falha corresponde ao clipboard.
- A13: filho próprio `research-probability-lab`; único Galton/root/IDs/chave. Trocar subdestino pausa/reusa; sair de Research destrói; retorno recria placa vazia e conserva preferências. Settings/Notas/modal global e gaveta móvel sobrepostos pausam; fechamento retoma quando pertinente, pelo observer existente e estado inert. Nenhum jogo novo. Casos anteriores de matemática/física/reset continuam detectando defeitos; seletores/ownership de testes mudam somente para comportamento autorizado.

## Contrato CHG

```yaml
schema: jp-harness/chg/v1
change_id: CHG-PRODUCT-IMPROVEMENTS-20260911
status: approved
objective: Entregar A10+A11+A12+A13 localmente, validados e auditados, sem integração.
risk_level: N2
authority_required: A3
target:
  root: /Users/joaopauloalves/.codex/product-improvements/20260911/product
  branch: codex/product-improvements-a10-a13
  baseline_sha: d68a86fc046b82dddd4bfd6c9c9254f39d91dc2e
scope:
  allowed_files:
    - index.html
    - src/styles/app.css
    - src/js/20-ui/12-nav-style.js
    - src/js/20-ui/03-main-render.js
    - src/js/20-ui/16-operation-history.js
    - src/js/20-ui/23-research-views.js
    - src/js/40-app/01-navigation.js
    - src/js/40-app/09-settings-modal.js
    - src/js/40-app/11-operational-shell.js
    - src/js/40-app/12-global-dashboard.js
    - src/js/manifest.json
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
    - tools/smoke_test.py
    - tools/exec_submenu_test.py
    - tools/operation_history_test.py
    - tools/finpes_navigation_test.py
    - tools/navigation_order_test.py
    - tools/forex_context_bar_test.py
    - tools/operation_copy_test.py
    - tools/navigation_ia_test.py
    - tools/navigation_local_contract_test.py
    - tools/research_navigation_test.py
    - tools/settings_modal_test.py
    - tools/galton_board_test.py
    - tools/finalize_session_test.py
    - tools/contextual_sidebar_test.py
    - tools/navigation_layout_choice_test.py
    - README.md
    - docs/architecture/NAVIGATION-HIERARCHY.md
    - docs/architecture/GALTON-BOARD.md
    - docs/architecture/CODE-MAP.md
    - docs/architecture/ARCHITECTURE.md
    - docs/work/ACTIVE-TASK.md
    - docs/work/CHG-PRODUCT-IMPROVEMENTS-20260911.md
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/**, .github/**, docs/normative/**, tools/quality_gate.py, tools/validate_project.py, tools/rebuild_monolith.py, docs/governance/**]
  allowed_actions: [engenharia delimitada A10-A13, branch e worktree própria, geração oficial, fixtures e testes sintéticos, evidências externas]
  forbidden_actions: [staging, commit, tag, push, PR, merge, deploy, reset, stash, reindexação, APIs econômicas ao vivo]
  regressions_forbidden: [perda de dados ou preferências, alteração financeira, duplicação de router ou laboratório, credenciais na cópia, alteração de controles para obter aprovação]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [origin oficial somente leitura de identidade, localhost em testes com fixtures e barreira existente]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [Python existente, Chromium Playwright existente, Git somente leitura e criação autorizada da worktree e fixtures sintéticas dos testes existentes sem remotos/hooks, gerador oficial]
acceptance_criteria: [expectativas A10-A13 acima satisfeitas no escopo demonstrado, candidate identificado, auditoria independente, recuperação verificável, roteiro humano sem aceite presumido]
approved_tests: [focais A10-A13, regressões de navegação e preferências e operação e Galton, quality_gate full final, reprodutibilidade e PWA existentes, recuperação em cópia]
rollback:
  source: [baseline.tar e baseline.json em ../evidence, diff final e snapshot candidato; restaurar somente delta após conferência]
  application_state: [perfis sintéticos descartáveis separados dos reais, sem migração nem reset]
  data: [nenhum dado real acessado]
  environment: [preservar servidores e worktrees anteriores]
  verification: [comparar arquivos e hashes do snapshot recuperado]
approved_by: proprietário na solicitação integral da campanha
approved_at: 2026-09-11
expires_on: [drift material, alteração financeira ou control plane necessária, dados reais necessários, recuperação insegura]
```

## CTX delimitado

```yaml
schema: jp-harness/ctx/v1
context_change_id: CTX-PRODUCT-IMPROVEMENTS-20260911
status: approved
root: /Users/joaopauloalves/.codex/product-improvements/20260911/product
mode: CONCORRENTE
approved_branch: codex/product-improvements-a10-a13
create: [docs/work/CHG-PRODUCT-IMPROVEMENTS-20260911.md]
modify: [docs/work/ACTIVE-TASK.md, README.md, docs/architecture/NAVIGATION-HIERARCHY.md, docs/architecture/GALTON-BOARD.md, docs/architecture/CODE-MAP.md, docs/architecture/ARCHITECTURE.md]
preserve: [históricos, evidências e checkpoints anteriores, codex/nav-ref-context, stash, main e outras worktrees]
do_not_touch: [AGENTS.md, CLAUDE.md, skills, docs/governance, normas, grafo e índices]
source_of_truth:
  produto: código inspecionado nesta base mais delta autorizado
  autoridade: pedido integral do proprietário
information_promotion: [somente apresentação e finalidade efetivamente implementadas; resultados em evidência externa]
acceptance_criteria: [documentação informativa coerente com delta, sem ampliar autoridade nem declarar integração, impacto agêntico explicitado]
approved_by: proprietário no escopo documental diretamente afetado
approved_at: 2026-09-11
expires_on: [necessidade de control plane ou curadoria geral, novo dado sensível]
```

Evidências duráveis: `/Users/joaopauloalves/.codex/product-improvements/20260911/evidence/`. `baseline.json` e `baseline.tar` preservam os 293 inputs da main conferida; as outras worktrees não são transportadas. Base e igualdade de árvore do checkpoint anterior foram conferidas separadamente.

## Complemento de validação V2

O FULL da V1 (`b98f35a4…`, 297 inputs, build `d20b9df07f477956`) registrou 51 PASS e quatro PRODUCT_FAIL brutos. Os outputs preservados em `../evidence/full-v1-results.json` demonstram oráculos anteriores às decisões A10/A12: smoke e exec-submenu exigem a ordem antiga; finpes-navigation exige número visual 03; operation-history considera qualquer botão um editor. Classificação causal adicional: TEST_HARNESS_FAIL, sem transformar os resultados brutos da V1 em PASS.

A autorização de testes necessários da campanha cobre o ajuste dos quatro arquivos reais acima. Mantêm-se N2/A3, equality da ordem, identidade/rotas/ativação, proibição de campos mutáveis e de quaisquer botões além de uma cópia vinculada ao registro. A interação de cópia deve preservar S, armazenamento e ausência de save. Não há alteração de runtime, manifest, build, portátil, gate ou controle.

A V2 tem identidade própria. Seus focais afetados e FULL serão executados novamente por mudança demonstrada das expectativas de produto; focais de runtime da V1 permanecem evidência reaproveitada apenas mediante igualdade dos inputs. V1 e todos os resultados anteriores ficam preservados. Recuperação V2 abrange os quatro testes e este complemento; rollback limita-se ao delta correspondente, sem reset/stash. Não há aceite ou integração concedidos por este registro.

## Complemento A12-A + A13-A — revisão V5

Decisão expressa do proprietário: entregar a cópia factual A12 como **parcial** e
alterar A13 para conservar a simulação em memória, pausada ao sair do Laboratório
ou de Research, até retomada explícita. Esta decisão substitui somente a expectativa
anterior de descarte ao sair de Research e de retomada automática após navegação;
os contratos e resultados V1–V4 acima permanecem históricos. Não é aceite humano.

Antes da escrita, os 297 hashes/modos da V4 e de `candidate-v4.tar` foram conferidos:
fingerprint `9d0e33fb29f40c430dced46ed189f92570ba8850a9acd4afec930fe2ef50da45`,
build `d20b9df07f477956`, mesma raiz/branch/base. O recibo externo
`continuity-preparation-v5.json` preserva a identidade, arquivos de evidência,
stash e outras worktrees. As 33 alterações conhecidas são o candidate anterior,
não trabalho a incorporar ou descartar. Preflight edit inicialmente bloqueou a
árvore suja; após correspondência integral foi usado o `--allow-dirty` existente.

```yaml
schema: jp-harness/chg/v1
change_id: CHG-PRODUCT-IMPROVEMENTS-20260911-CONTINUITY
status: approved
risk_level: N2
authority_required: A3
target:
  root: /Users/joaopauloalves/.codex/product-improvements/20260911/product
  branch: codex/product-improvements-a10-a13
  baseline_sha: d68a86fc046b82dddd4bfd6c9c9254f39d91dc2e
scope:
  allowed_files:
    - src/js/20-ui/23-research-views.js
    - src/js/40-app/18-galton-board/06-controller.js
    - tools/galton_board_test.py
    - tools/research_navigation_test.py
    - tools/finalize_session_test.py
    - src/js/manifest.json
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
    - README.md
    - docs/architecture/GALTON-BOARD.md
    - docs/architecture/NAVIGATION-HIERARCHY.md
    - docs/architecture/CODE-MAP.md
    - docs/architecture/ARCHITECTURE.md
    - docs/work/ACTIVE-TASK.md
    - docs/work/CHG-PRODUCT-IMPROVEMENTS-20260911.md
  forbidden_actions: [staging, commit, tag, push, PR, merge, deploy, reset Git, stash, persistir simulacao, novas formulas, alterar controles]
approved_tests: [focal Galton antes e depois, regressao Research e Settings e finalizacao, FULL final existente, revisao independente focal, recuperacao por baseline e diff]
rollback:
  source: candidate-v4.tar e manifesto V4 preservados; restaurar somente arquivos do complemento em copia e conferir hashes
  data: somente fixtures sinteticas; nenhuma persistencia nova ou dado financeiro alterado
approved_by: proprietario, decisao A12-A + A13-A nesta conversa
```

O delta de lifecycle é N1, dentro do pacote N2/A3; mantêm-se FULL e revisão
independente proporcionais à campanha. A simulação pertence ao controller existente,
sem cache, gerenciador, schema ou infraestrutura novos. Em navegação: preservar
bolas/fila/histograma/resultados/parâmetros e identidade; cancelar RAF, desconectar
observer ativo, não acumular tempo. Retorno mantém pausa até `Continuar`. Sobrepor
Configurações permanece compatível e não perde a instância; ao fechar a sobreposição,
o retorno também mantém pausa até `Continuar`. Reset e Finalizar sessão
mantêm limpeza e liberação existentes; reload continua sem simulação persistida.

A12 não terá delta funcional. Lucro Técnico (D-20 versus soma positiva legada),
alavancagem (D-07 versus denominador SI), DD/fase (D-06 versus risco/perdas),
risco/clearance (moeda/stop e OPEN-05/FCR/FEO) continuam NEEDS_HUMAN_RULE nos
conflitos aplicáveis. Equity flutuante não foi demonstrada pelo saldo book;
conta/perfil/período/métricas finais não constam do snapshot histórico. Cadastro
atual não preenche o passado, e base do retorno não é saldo final. Esses requisitos
permanecem pendentes, sem reabertura normativa neste complemento.

CTX complementar `CTX-PRODUCT-IMPROVEMENTS-20260911-CONTINUITY`: mesma raiz e
branch, modo CONCORRENTE; somente as sete referências documentais listadas no CHG
acima podem mudar. Preservar históricos, AGENTS/skills/Harness/gates, contexto geral,
índices, normas e demais entregas. Representar A12 parcial e a nova continuidade A13
sem antecipar testes, aceite ou integração. Evidências V5 ficam em novos arquivos
no diretório existente; não sobrescrever `candidate-final.*` ou relatórios anteriores.
Reaproveitar provas somente por igualdade dos inputs pertinentes; lifecycle antigo
não serve de prova da nova decisão. Novo freeze/build/diff, FULL, auditoria e
recuperação deverão apontar para a mesma revisão.

## Complemento focal de validação — revisão V6

O FULL V5 (`3a53cb65106c7b23ea2c83e50561ff3cd09c2a11260a8e869dc2e25d11852181`,
build `02eba740dcabc48b`) conserva 54 PASS e 1 PRODUCT_FAIL bruto: leitura
imediata de foco em `tools/settings_modal_test.py:202`, após fechar o seletor
de ícone. A restauração existente ocorre em `requestAnimationFrame`.
`settings-focus-v5-results-05.json`, externo, compara V4 e V5 com o bootstrap
original: alvo conectado/visível, foco BODY antes do callback e retorno ao
mesmo `chooseAppIconBtn` depois. Reter o callback faz a asserção com espera
falhar nas duas versões. Classificação causal adicional: TEST_HARNESS_FAIL
do oráculo temporal; o timing exato do FULL anterior não foi capturado e
nenhum resultado bruto ou tentativa instrumental anterior é sobrescrito.

Este complemento CHG/CTX mantém a raiz, branch, N2/A3 e a autorização de
testes necessários A12-A/A13-A acima. Seu delta fica exclusivamente em:

- `tools/settings_modal_test.py`: esperar o mesmo foco pela asserção
  `expect(...).to_be_focused()`, timeout padrão de 5 segundos, mantendo
  também a igualdade literal e todas as demais expectativas;
- `docs/work/CHG-PRODUCT-IMPROVEMENTS-20260911.md`: este registro.

Não muda runtime, bootstrap, controles, timeouts configurados, dependências,
manifest, build ou portátil. Não transforma ausência de foco em aprovação.
V5 permanece recuperável por manifesto/diff/tar; V6 terá identidade própria,
recuperação, Settings focal, FULL final e revisão independente do delta de
validação. Focais A10/A11/A12/A13 e contraprovas de lifecycle só serão
reaproveitados mediante igualdade dos inputs pertinentes, sem nova execução
atribuída. Rollback limita-se a estes dois arquivos, usando V5 preservada em
cópia; sem reset/stash ou alteração de outra tarefa. Não há aceite humano
nem autorização de integração neste registro.
