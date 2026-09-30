# CHG-JPW-ALAVANCAGEM-ATUAL-20260926

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-ATUAL-20260926
status: approved
objective: Indicador MT5 informativo de alavancagem bruta atual sobre equity e pagina interna de documentacao/download no JP Wealth.
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
scope:
  allowed_files: [mt5/jpw-alavancagem-atual/, downloads/jpw-alavancagem-atual/, index.html, src/styles/app.css, src/js/20-ui/31-tools-services.js, src/js/40-app/01-navigation.js, src/js/manifest.json, sw.js, tools/rebuild_monolith.py, tools/build_reproducibility_test.py, tools/build_leverage_package.py, tools/leverage_*, tools/navigation_ia_test.py, tools/navigation_local_contract_test.py, tools/navigation_layout_choice_test.py, tools/nocuda_tools_test.py, tools/contextual_sidebar_test.py, docs/work/CHG-JPW-ALAVANCAGEM-ATUAL-20260926.md, docs/work/ACTIVE-TASK.md, docs/architecture/NAVIGATION-HIERARCHY.md, build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  forbidden_files: [docs/normative/, docs/decisions/, src/js/00-core/, src/js/10-domain/, data/, skills/, tools/quality_gate.py, tools/validate_project.py]
  allowed_actions: [local implementation, synthetic tests, isolated compilation if available, official artifact generation, independent review]
  forbidden_actions: [commit, push, PR, merge, deploy, production publication, real account access, operational MT5 installation, trading, financial state migration, harness or gate edits]
  regressions_forbidden: [existing routes and layouts, financial state, normative leverage, backup, PWA upgrade lifecycle]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, downloads/jpw-alavancagem-atual/JPW_Alavancagem_Atual_Fontes_v1.0.0.zip, compiled archive only after real compilation]
  generation_commands: [python3 tools/build_leverage_package.py, python3 tools/rebuild_monolith.py, isolated MetaEditor when available]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [official MetaQuotes documentation read only, loopback test server]
  temporary_artifacts: allowed
  cleanup_required: true
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [existing Python tests, isolated browser, official generators, isolated MetaEditor if proven]
acceptance_criteria:
  - Gross notional across all open positions in account currency divided by current ACCOUNT_EQUITY; no financial calculation in browser.
  - Supported fiduciary Forex and verifiable XAU/linear CFD contracts; one unsupported or stale input invalidates the total.
  - Current number never survives an invalid collection as if fresh; no trading, transfer, or storage of account data.
  - Third Ferramentas e Servicos destination after Calendario and Nocuda, accessible in four layouts.
  - Source package always real; compiled package only if .ex5 actually generated; offline/portable download integrity.
approved_tests: [MQL5 synthetic core, isolated MT5 native when available, four-layout browser, file and HTTP downloads, portable and PWA, full quality gate, independent audit]
rollback:
  source: [Remove only this branch delta and preserve the identified baseline and previous packages.]
  application_state: [No state migration or preference change.]
  data: [No product financial data or account credentials are accessed or changed.]
  environment: [Stop only processes started for this task; preserve the operator terminal.]
  verification: [Compare branch diff and build outputs with the recorded baseline.]
approved_by: Proprietario, PLEASE IMPLEMENT THIS PLAN nesta conversa
approved_at: 2026-09-26
expires_on: [target root or branch changes, material scope or baseline divergence, new controlling source, need for higher authority]
```

## Base e fronteiras confirmadas

`main` e `origin/main` apontavam para `f5145b25e86af6b4ccbfef847cba0d84d74e7c8a` na inspecao. O checkout principal tem 111 arquivos nao rastreados com sufixo ` 2`; nao serao limpos, movidos ou incluidos. A worktree desta tarefa nasceu limpa da base indicada, e o preflight de edicao passou com aviso de frescor material preexistente. A fonte canônica do Harness foi lida em `/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/1 - Suma & Estudo/99 - PROMPT/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`.

O documento de produto fornecido pelo proprietario define exatamente a metrica. Seu rotulo A2 nao reduz o risco N3 estabelecido por `AGENTS.md` e `CHANGE-PROCESS.md`; o pedido expresso de implementar a formula delimita esta alteracao local. Operacoes Git alem da criacao da branch/worktree especificada no plano continuam nao autorizadas.

## Compreensao e oraculo

O JP Wealth e um PWA local de organizacao financeira e gestao de risco. Esta tarefa distribui e explica uma leitura informativa calculada no MT5; nao cria outra fonte de estado financeiro do aplicativo. O submenu `Ferramentas e Servicos` atualmente contem Calendario e Nocuda no mesmo `section#tools`; a nova visao reutiliza a navegacao, sem alterar estado `S`, backup ou regras do Forex. Consumidores afetados: resolucao de rotas, quatro layouts, vista Tools, gerador portatil, precache e testes de navegacao/download.

Matriz financeira deste recorte: regra solicitada `soma(abs(nocional aberto convertido para moeda da conta)) / ACCOUNT_EQUITY` -> nucleo MQL5 unico -> testes sinteticos NZDUSD/XAUUSD/USDJPY/EURJPY, conversoes e hedging. O Estatuto V11, PDF p. 36, Art. 4.5 §§6º–8º e 13, define nocional bruto por conta, sem compensacao, convertido pela cotacao vigente, mas usa denominador normativo `min(Saldo_Inicial_Ciclo, Equity)`. A ferramenta solicitada usa apenas equity corrente e por isso recebe nome, formula e explicacao diferentes; nao calcula nem substitui a metrica normativa do ciclo, tetos, fases ou autorizacao de execucao. O Anexo Parametrico `X-LEV`/`P-02` define tetos por fase que permanecem fora deste indicador. Nenhum instrumento desconhecido ou cotacao antiga vira zero ou total parcial.

## Evidencia e estado

Antes das mudancas: testes novos, compilacao e execucao nativa `NOT_RUN`. MetaEditor foi localizado num prefixo Wine, mas ainda nao foi demonstrado um terminal isolado; nao usar eventual sessao operacional. Registros de testes, fingerprint, revisao de diff, seguranca, auditoria e limites serao adicionados apos execucao real. A pagina e os pacotes distinguirao fonte, compilacao, teste matematico e execucao nativa, sem reivindicar aceite humano.

## Candidate local para revisao

`jpw-alavancagem-atual-20260926-r1` usa o build `cf977fa0267e2206`. A rota `tools-leverage` e a pagina foram examinadas em quatro layouts, HTTP, `file://`, HTML portatil e PWA offline. O pacote de fontes v1.0.0 contem quatro arquivos; o manifesto declara tamanho e SHA-256 dos bytes distribuidos. Nenhum `.ex5` foi produzido ou anunciado como disponivel. O navegador nao calcula exposicao nem recebe dados da conta.

Focais finais: `leverage_package_test.py`, `build_reproducibility_test.py`, `validate_project.py` e `leverage_page_test.py` passaram. `git diff --check` passou. A verificacao visual em 1440 e 390 px corrigiu o cabecalho interno que herdava layout global e a quebra do nome do ZIP; em 390 px, estado e card mediram respectivamente 276/276 e 308/308 px de scroll/client, sem overflow horizontal do documento. Tema escuro foi inspecionado em Chromium. Safari/iPhone fisico nao foram verificados.

Os recibos integrais do full ficam em `tools/.artifacts/quality-20260926T171434-full.json` (51 PASS / 6 PRODUCT_FAIL), `quality-20260926T174815-full.json` (54 PASS / 3 PRODUCT_FAIL) e `quality-20260926T181456-full.json` (55 PASS / 2 PRODUCT_FAIL, candidate visual final). Nenhum resultado anterior foi reclassificado. No ultimo, Research completou as observacoes de rota/foco, mas `07-workspace-backup.js` falhou com `ERR_SOCKET_NOT_CONNECTED` e o provider nao ficou disponivel; Alladin teve provider ausente sem cadeia de request suficiente para atribuir causa. O gate nao passou. A auditoria independente concluiu `BLOCKED` para integracao: nenhum defeito P1 estatico remanescente foi demonstrado na formula, conversao, pacote ou pagina, mas as falhas canônicas e a validacao nativa ainda nao estao fechadas.

O script MQL5 de cenarios sinteticos usa o mesmo include do indicador, mas execucao matematica nativa, compilacao MetaEditor e uso em terminal isolado permanecem `NOT_RUN`. Nao foi aberta sessao operacional. O indicador pode deixar pares de conversao ativados no Market Watch; o efeito esta divulgado no README e na pagina. A varredura completa de simbolos pode retardar a primeira leitura e multiplos feeds cambiais legitimos usam desempate lexical sem prova de concordancia. O ZIP e abrangido pela regra existente `*.zip` do `.gitignore`; uma futura autorizacao de commit devera inclui-lo explicitamente, sem ampliar esta entrega.
