# CHG-JPW-ALAVANCAGEM-CONSULTA-MDD-20260928 — MT5 1.2.1

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-CONSULTA-MDD-20260928
status: approved
objective: Permitir consultar sob demanda o máximo de DD/saldo observado e a amostra vencedora em uma janela temporária do MT5.
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
  derived_from: jpw-alavancagem-atual-20260928-r5
  r5_fingerprint: 40ee992acceb153caaca133bcd37b0e9529c5380c6192fe0ac4a3ed643877917
scope:
  allowed_files: [docs/work/CHG-JPW-ALAVANCAGEM-CONSULTA-MDD-20260928.md, docs/work/ACTIVE-TASK.md, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_MDD.mqh, mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Consultar_MDD.mq5, mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Metrics_Tests.mq5, mt5/jpw-alavancagem-atual/README.md, downloads/jpw-alavancagem-atual/manifest.json, downloads/jpw-alavancagem-atual/JPW_Alavancagem_Atual_Fontes_v1.2.1.zip, index.html, tools/leverage_page_test.py, tools/leverage_package_test.py, build-id.js, sw.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, external canonical MT5 specification at its confirmed current path]
  forbidden_files: [docs/normative/, docs/decisions/, skills/, tools/quality_gate.py, mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Profile.mqh, mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Terminal.mqh]
  allowed_actions: [local implementation, synthetic tests, official regeneration, isolated native validation if available, external candidate freeze, independent read-only audit]
  forbidden_actions: [real-account access by agent, operational MT5 installation, trading, commit, push, merge, deploy, publication, rewrite of r5 evidence]
  regressions_forbidden: [formula or panel change, two-slot record format change, false history claim, partial or cross-account record display]
derived_artifacts:
  allowed: [versioned source ZIP, build-id.js, sw.js, portable HTML]
  generation_commands: [python3 tools/build_leverage_package.py, python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: forbidden
  allowed_targets: []
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  schema_change: forbidden
  persistence: read-only access to the existing account-scoped MT5 Files record; MessageBox automatically mirrors displayed financial values into local MT5 Experts logs
toolchain:
  dependency_changes: []
  allowed_processes: [existing Python focused tests and quality gate, isolated MetaEditor/MT5 only if available]
acceptance_criteria:
  - A separate script reads only the record of the current installation and account under the existing exclusive lock, releases it before MessageBox and never writes/recalculates MDD.
  - Valid maximum, observation start, record time labelled computer UTC, winning balance/equity and currency appear; no chronological-history claim.
  - README, page and canonical specification disclose that MT5 copies MessageBox text, including financial values, to local Experts logs; no site or network transfer is introduced.
  - Missing, busy, invalid, incompatible and unavailable-account states are distinguished without fabricated zero or cross-account fallback.
  - Three chart lines, formulas, record format and original r5 evidence remain intact.
  - Manifest, source ZIP, README, page, offline derivatives and canonical specification identify version 1.2.1 consistently; no EX5 without exact native provenance.
approved_tests: [synthetic two-slot/account/USC/lock/read-only cases, focused package/page/structure, full quality gate once, isolated native compilation and inspection only if usable, independent adversarial audit]
rollback:
  source: Restore preserved r5 snapshot by its 36 hashes and fingerprint.
  application_state: No browser state changes.
  data: Existing local MDD record is never changed by the viewer.
  environment: No operational MT5 installation.
  verification: Compare r5 hashes, confirm current record bytes unchanged and absence of EX5 without native receipt.
approved_by: Proprietário, pedido expresso nesta conversa para implementar o plano 1.2.1.
approved_at: 2026-09-28 America/Sao_Paulo
```

## Preflight e fronteira

O r5 preservado em `/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-alavancagem-atual-v1.2.0-r5-20260928/CANDIDATE.json` conferiu 36/36 arquivos sem divergência antes deste CHG. `git status` já contém o delta r5 não commitado; a base Git permanece `f5145b25e86af6b4ccbfef847cba0d84d74e7c8a`. O preflight `audit` passou com avisos; `edit` apontou 26 mudanças preexistentes, cobertas pela comparação exata com o snapshot r5. Esse aviso não é apagado ou reclassificado. A fonte Harness externa permanece no SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`.

O dado representa o máximo **observado** de `100 × max(0, balance − equity) / balance`, distinto do DD normativo de fase do Estatuto e de MDD pico-a-vale. O leitor não introduz uma série histórica. A edição da especificação canônica é apenas reconciliação do contrato do produto; não altera o Harness, Estatuto ou control plane. O site não acessa dados da conta. Evidências nativas do r5 não homologam a versão derivada.

## Risco de log local e incidente administrativo observado

A documentação oficial do MQL5 informa que `MessageBox()` também escreve seu texto no Experts log; a documentação do MT5 informa que esse log é persistido em arquivos locais `MQL5/Logs`. A janela solicitada exibe valores financeiros, portanto eles aparecerão também nesse log local. O script não escreve os slots de MDD, mas a apresentação tem esse efeito da plataforma; README, página e especificação devem informá-lo, e os logs não devem ser compartilhados sem revisão. A validação nativa da revisão continua necessária.

Durante a primeira execução do full, a raiz principal Git foi movida externamente de `99 - SOFTWARES & EAS` para `99B - SOFTWARES & EAS`; o ponteiro `.git` desta worktree ficou inválido, embora a entrada administrativa tivesse backlink exato, branch e HEAD esperados. O full registrou suas classificações reais, mas seus checks Git ficaram inválidos. O ponteiro original foi preservado em `/private/tmp/jpw-alavancagem-atual-v121-evidence/git-pointer-before-repair.txt` e somente esse ponteiro foi atualizado para a entrada `99B`; branch/HEAD e worktree foram confirmados. O ZIP histórico 1.2.0 foi regenerado incorretamente enquanto o manifesto ainda apontava a versão antiga; a cópia errada foi preservada externamente e o ZIP r5 foi restaurado ao SHA-256 `f0f1659f8bb7e110ca13dc7b9c9b4647ac7a1b10be6bd763247546ec89b4c066` do snapshot. Nenhum arquivo do r5 preservado foi alterado.

## Recibo de validação do derivado 1.2.1

O gerador oficial produziu build `42613e9b9f1b8766` e ZIP de fontes v1.2.1 de 53.239 bytes, SHA-256 `7c107117093ad3dfb995ecb653509b3f937fb43b01cc2071c3904d4b5ae2ec72`. O fingerprint dos fontes MQL declarado no manifesto é `e1b5f2e7434d1cc022a2c38dd0d8d21daab5209861cf9456671556705cdca62d`. Não há EX5 distribuído. Os 36 arquivos do r5 permanecem no snapshot; 10 diferem na worktree atual por este recorte, e o ZIP v1.2.0 local voltou ao hash original. Indicador, núcleo matemático, adaptador MT5, perfil USC e formato dos dois slots não mudaram.

`leverage_package_test.py`, `leverage_page_test.py`, `leverage_panel_test.py` e `validate_project.py` passaram. A página foi percorrida nos quatro layouts, temas claro/escuro, larguras 320/390/1440, HTTP, arquivo local, portátil e PWA offline. O preflight após reparar o vínculo passou com avisos relativos às mudanças preexistentes e ao frescor do contexto; `git diff --check` passou.

O primeiro full, com vínculo Git quebrado no meio da rodada, registrou **48 PASS / 7 PRODUCT_FAIL / 2 NOT_RUN** em `tools/.artifacts/quality-20260928T170552-full.json`; esse recibo permanece histórico e não é composto com outro. A execução final sobre o conjunto corrigido e com Git funcional registrou **52 PASS / 5 PRODUCT_FAIL / 0 NOT_RUN** em `tools/.artifacts/quality-20260928T173444-full.json`: `research-navigation`, `exec-submenu`, `pivot-studies`, `finpes-overview` e `storage-governance` mantêm a classificação bruta `PRODUCT_FAIL`. Seus focais desta revisão não substituem o full; nenhuma falha foi reclassificada ou repetida para obter verde.

Compilação MetaEditor X64 Regular, execução do script de testes e inspeção da janela/Experts log da **1.2.1**: **NOT_RUN**. Não há ambiente MT5 isolado utilizável identificado; a sessão operacional do usuário não foi tocada. O PASS manual de versões anteriores não é herdado. A versão é fonte/página revisável e não tem prontidão operacional demonstrada. A especificação canônica antes da edição tinha SHA-256 `8cb1f945f22b48a86ae5c25223f1561e880f0e22bb2f91d10ba9bcf2fb9b56ac`, preservado em `/private/tmp/jpw-alavancagem-atual-v121-evidence/Script-para-Metatrader-5-ALAVANCAGEM-REAL-before-v121.md`; a revisão atual sob `2 - TRABALHO/99A -   SOFTWARE DEV/` tem SHA-256 `2510d3c9dbe5a690fd84b8a5f37c21058c709771b31b8f5076a28c8520caf8e6`.
