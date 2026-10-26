# Primeiro acesso vazio — impacto nas fixtures acumuladas

## Autoridade e limites

Leitura inicial delegada e, depois, autorização explícita do agente raiz para adaptar somente quatro verificadores sob CHG-JPW-EMPTY-FIRST-USE-TESTS-20261024. Branch conferida `codex/primeiro-acesso-vazio-20261024`, HEAD `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`. Preflight edit --allow-dirty PASS; alterações preexistentes da mesma execução preservadas. Nenhuma fonte de produto, runner, bootstrap global ou dependência alterada por este agente.

## Dependências confirmadas e delta executado

| Arquivo | Dependência anterior | Ajuste delimitado | Oráculo preservado/reforçado |
|---|---|---|---|
| `tools/investor_password_test.py` | Primeiro caso abria contexto novo e acessava `S.accounts[0]`, antes fornecido por DEFAULTS | Uma conta sintética explícita no setup daquele caso, sem capital e sem dados reais | Senha só em RAM; ausente de armazenamento, checkpoint, backup, reload e migração antiga; testes modular e portátil inalterados |
| `tools/backup_import_audit_test.py` | AUD01 clonava DEFAULTS e assumia sua primeira conta; AUD02 tratava resposta null como malformada | Conta sintética explícita para cadeia de 26/27/35 revisões; somente `value-null` sai de malformed e entra em compatibilidade `null-zero` | Mesma cadeia real criada pelo comando, mesmas contagens e roundtrip. Mantidos root/group/items/item nulos, missing, string, boolean, negativo, fração e >2. Novo teste de import+reload conserva null e zero distintos, sem recovery |
| `tools/backup_reliability_test.py` | Roundtrip usava ALLADIN_SEED, que não cria registro Forex, e depois acessava `S.accounts[0]` | Uma conta sintética explícita no próprio cenário multimódulo antes da normalização/save | Todos domínios, campos desconhecidos, segredos, workspace, falhas, atomicidade e roundtrip continuam examinados |
| `tools/alladin_foundation_test.py` | Casos A/M assumiam vizinho saldoIni number em boot vazio | Captura JSON integral de params antes da mutação e comparação exata após reload/migração | Agora prova params intactos incluindo null ou números, em vez de mera verificação de tipo; estrutura PF e todos demais oráculos inalterados |

Os três setups de conta são locais aos cenários que precisam de registro legado. Não foi criado helper genérico nem modificado `browser_bootstrap_fixture.py`; o novo teste de primeiro acesso deve continuar sem seed de estado financeiro.

## Falsos positivos inspecionados: não adaptar preventivamente

- `fx_consolidated_ui_test.py:28` já define duas contas sintéticas antes de acessar índice0.
- `fx_consolidated_storage_test.py:35` já define três contas; `fx_account_setup_test.py`, `fx_account_registration_test.py`, `forex_account_profile_test.py` importam esse SEED. Seus valores3/4 são contagens da fixture, não das quatro contas antigas do produto.
- `forex_accounts_workspace_test.py:18`, `forex_execution_projection_test.py`, `operation_copy_test.py:44`, `operation_finalize_test.py`, `operation_wiring_test.py`, `operation_history_test.py`, `order_guards_test.py`, `smoke_test.py` e `import_xss_security_test.py` já possuem contas sintéticas locais; preservar.
- `state_integrity_test.py:126` deve continuar recusando `delete doc.params.saldoIni`. Aceitar null explícito não autoriza preencher chave apagada.
- `persistence_failure_test.py` e demais casos de persistência que explicitamente atribuem saldos sintéticos antes do ato não precisam recuperar capital default. Os incrementos posteriores pertencem aos mesmos cenários já semeados.
- `session_epoch_protocol_test.py` e serialização usam marcadores/contas próprios; contagens de preservação não representam o boot antigo.
- `onboarding_first_access_test.py:421` usa contagem inicial relativa e cria conta por confirmação: preservar; após mudança deve partir de0.
- Não foi localizada expectativa acumulada de placar23/30; os testes de checklist existentes focam montagem, rascunhos, navegação e preservação das respostas.
- Os exemplos de Galton/Gêmeos/Correntes e DEFAULTS de domínios locais não são seeds financeiros do Forex e não devem ser tocados.

## Comandos e execução

O runner permanece intacto. Contagem estática: FAST4, STANDARD59, FULL102. O focal novo deve ser executado adicionalmente; não está implicitamente incluído no runner.

Ambiente já disponível:

```text
.superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3
```

Focais de cada delta, após liberação do candidato do produto:

```text
python3 tools/investor_password_test.py
python3 tools/backup_import_audit_test.py --artifact /private/tmp/jpw-empty-first-use-20261024/backup-import-audit.json
python3 tools/backup_reliability_test.py --artifact /private/tmp/jpw-empty-first-use-20261024/backup-reliability.json
python3 tools/alladin_foundation_test.py
python3 tools/quality_gate.py --tier full --artifact /private/tmp/jpw-empty-first-use-20261024/full.json
```

`backup_reliability_test.py` é focal adicional (fora do FULL atual). Seu --help foi executado e confirmou --artifact obrigatório, --root opcional e --case repetível. Não reduzir timeouts/skips/thresholds, nem ativar seed global para contornar falha.

### Resultado atual

- Sintaxe dos quatro arquivos (ast.parse): PASS.
- git diff --check dos quatro arquivos: PASS.
- Runtime focal run1: investor-password PASS (modular+portátil,7,45s); backup-import-audit35/35 PASS (29,31s); alladin-foundation PASS (32,58s). Backup-reliability26/26 casos PASS, mas receipt integral TEST_HARNESS_FAIL/exit1 por drift de build-id.js e manifest durante57,17s. Tentativa integral preservada, não promovida a PASS; repetir com snapshot estável. Fontes financeiras permaneceram idênticas nesse recibo.
- FULL: NOT_RUN por este agente; execução final pertence ao agente raiz.
- Revisão independente dos verificadores/contraprovas: pendente.

Diff exato e hashes: `fixture-adaptations.patch`, `fixture-adaptations-receipt.json` nesta pasta. Esses registros não constituem PASS de runtime nem aceite humano.
