# GENETRIX — Modelos de registro de engenharia e gauntlet

Estes modelos são instruções analíticas derivadas. Os campos devem conter evidência acessível; campos vazios não são confirmação. Use `NOT_RUN`, `INCONCLUSIVE` ou indisponibilidade quando pertinente. Não invente identidade, log, autoridade, sessão, compilação, instalação ou aprovação para preencher um formulário.

O contrato do piloto é [ENG-AC01-12.md](ENG-AC01-12.md), com estrutura canônica em [ENG-AC01-12.json](ENG-AC01-12.json). Os enums de julgamento são os do avaliador JP Wealth existente. Resultados brutos do Core e estados financeiros/normativos ficam em campos independentes.

## 1. Contrato de tarefa / CHG

```yaml
schema: jp-harness/chg/v1
change_id: CHG-AAAA-NNNN
status: proposed | approved | expired | completed | rejected
objective: resultado inequívoco
risk_level: N0-D | N0-V | N1 | N2 | N3
authority_required: A2 | A3 | A4

target:
  root: caminho absoluto ou identidade inequívoca
  branch: nome-da-branch
  baseline_sha: sha-ou-null

scope:
  allowed_files: []
  forbidden_files: []
  allowed_actions: []
  forbidden_actions: [commit, push, merge, deploy]
  regressions_forbidden: []

derived_artifacts:
  allowed: []
  generation_commands: []
  manual_edit: forbidden | allowed

external_side_effects:
  network: forbidden | allowed
  allowed_targets: []
  temporary_artifacts: forbidden | allowed
  cleanup_required: false

data:
  test_policy: synthetic_only | explicitly_approved
  approved_real_data: []
  schema_change: forbidden | approved

toolchain:
  dependency_changes: []
  allowed_processes: []

acceptance_criteria: []
approved_tests: []

rollback:
  source: []
  application_state: []
  data: []
  environment: []
  verification: []

approved_by: null
approved_at: null
expires_on:
  - target root ou branch mudar
  - objetivo, risco ou escopo mudar materialmente
  - HEAD/baseline divergir de forma relevante
  - surgir nova fonte de verdade ou restrição
  - ação exigir autoridade superior
```

Campos MT5 suplementares são um sidecar de contexto ligado a change_id; não constituem contrato de autorização alternativo: tipo de programa, versão do harness, dependências, modelo normativo por item, unidades, APIs e evidências nativas.


Não redefina classes de risco, autoridade ou estado. O pedido concreto pode autorizar a mudança reversível no alvo reconhecível; aprovação de contratação, publicação, negociação ou normas não nasce deste template.

## 2. Manifesto de fontes e VERSION_CHECK

```yaml
VERSION_CHECK:
  checked_at: instante-e-fuso
  search_scope: locais-realmente-consultados
  SEARCH_STATUS: VERIFIED_IN_ACCESSIBLE_SOURCES | UNVERIFIED_NO_ACCESS
  SEARCH_GAPS: []
  UPDATE_STATUS: UPDATE_FOUND | NO_UPDATE_FOUND_IN_SCOPE
  CURRENT_VIGENCY_EVIDENCE: DECLARED_IN_SOURCE | VERIFIED_APPLICABLE | UNRESOLVED
  CONFLICT_STATUS: NONE_FOUND_IN_SCOPE | VERSION_CONFLICT
  HISTORICAL_APPLICABILITY: VERIFIED | HISTORICAL_APPLICABILITY_UNRESOLVED | NOT_APPLICABLE_TO_REQUEST
  observed_edition: identificacao
  newest_found_edition: identificacao-ou-nao-determinada
  applicable_reference: fonte-item-periodo-ou-nao-resolvido
  software_version: identificacao
  harness_version: identificacao
  source_manifest: caminho-e-sha256
```

UPDATE_STATUS e CONFLICT_STATUS sem busca suficiente ficam null/não determinados, com causa e lacunas. Não acrescente enums. Manifesto suplementar por fonte: origem, snapshot, tipo (original/cópia/recorte/transcrição/sintético), versão, hash, instante, passagem, autoridade e evidências de vigência; comparação mantém old_manifest/new_manifest, delta semântico e conclusões dependentes. Não substituir os eixos canônicos pelo resumo desses campos.


Nome, pasta, data de modificação, número de versão e hash não comprovam ratificação. `PENDING`, `NOT_HOMOLOGATED`, `BLOCKED` e estados reais como `NOT_HOM` devem permanecer literais e contextualizados.

## 3. Freeze da rodada e do fixture

```yaml
ROUND_ID: <ENG-R1>
FROZEN_AT_UTC: <antes da primeira execução>
CONTRACT_PATH_AND_SHA256: <contrato imutável>
HARNESS_PATH_AND_SHA256: <harness avaliado>
CRITERIA_REVISION: <R1>
FIXTURE_MANIFEST_SHA256: <manifesto separado>
FIXTURES:
  - FIXTURE_ID: <ENG-FIXxx>
    TYPE: <sintético/recorte fiel/cópia real>
    PATHS_AND_HASHES: <todos os inputs>
    PRECONDITIONS: <condições verificáveis>
    EXPECTED_RESULTS_REFERENCE: <oracle externo ao código reparado>
    ROUNDING_OR_TOLERANCE: <política explícita ou não aplicável>
    FAILURE_INJECTION: <ponto e efeito esperado quando aplicável>
    KNOWN_LIMITATIONS: <host vs MQL5, histórico, dados ausentes>
PLANNED_CASES: <12 nesta revisão>
FRESH_AGENT_SESSIONS_PER_CASE: 3
PLANNED_VALID_ATTEMPTS: 36
AUTHOR_OF_FIXTURE: <identidade real>
AUTHOR_OF_CRITERIA: <identidade real>
EXECUTOR_ASSIGNMENT: <sessão nova por tentativa>
JUDGE_ASSIGNMENT: <separado do executor/autor da solução>
JUDGE_CONTEXT_EXPOSURE: <o que recebeu e o que não foi fornecido>
JUDGE_CALIBRATION: <controle e recibos; ainda NOT_RUN se ausentes>
INVALIDATION_RULE: <delta material abre nova revisão; anterior preservada>
```

Uma referência pode estar no contrato público e ser conhecida pelo executor. Declare essa condição: regressão publicada não demonstra generalização. Três processos novos de teste não constituem três sessões agentes novas. Todas as tentativas iniciadas permanecem, inclusive inválidas, extras e interrompidas.

## 4. Registro de tentativa

```yaml
ATTEMPT_ID: <ENG-R1-ACxx-T01>
CASE_ID: <ENG-ACxx>
CASE_CONTRACT_SHA256: <hash congelado>
FIXTURE_SHA256S: <entradas verificadas>
FRESH_SESSION_ID: <ID real; não só PID de teste>
FRESH_SESSION_EVIDENCE: <como foi iniciada sem respostas anteriores>
EXECUTOR_ID: <agente>
MODEL_IF_KNOWN: <conhecido ou indisponível>
CONTEXT_PROVIDED: <instruções, fontes, memória, compartilhamento>
TOOLS_AVAILABLE: <nomes/capacidades observados>
PERMISSIONS: <contrato e exclusões>
STARTED_AT_UTC: <momento real>
FINISHED_AT_UTC: <momento real ou ausente>
TEST_EXECUTION_STATUS: NOT_RUN
OUTPUT_PATH_AND_SHA256: <resposta integral>
TOOL_CALLS_AND_OUTPUTS: <logs integrais ou limitação explícita>
FILES_BEFORE_AFTER: <hashes/diff quando aplicável>
LOCAL_COMMANDS_AND_EXIT_CODES: <com evidência>
NATIVE_ACTIVITY: <separada; NOT_RUN se ausente>
DOMAIN_STATE_LITERAL: <valores/estados preservados>
CORE_RAW_RESULTS: <recibos originais; não rebatizados>
ERRORS_AND_INTERRUPTION: <causa observada, hipótese distinta>
ATTEMPT_RESULT: NOT_RUN
JUDGMENT_RECEIPT: <referência do julgador>
PREVIOUS_OR_EXTRA_ATTEMPTS: <todas; não escolher só a melhor>
```

`COMPLETED` descreve término da tentativa, inclusive diagnóstico correto de um bloqueio; não é resultado favorável. Evidência ausente não deve ser fabricada nem atribuída automaticamente a falha do assistente quando o requisito não foi demonstrado.

## 5. Ficha de julgamento

```yaml
JUDGMENT_ID: <ID>
ATTEMPT_ID: <ID>
JUDGE_ID: <identidade real distinta do executor>
JUDGE_ROLE: <revisão interna / outro agente / julgamento separado>
JUDGE_CONTEXT_AND_EXPOSURE: <o que recebeu, inclusive resultados prévios>
AUTHOR_EXECUTOR_JUDGE_SEPARATION: <observada e limitações>
CONTRACT_AND_FIXTURE_MATCH: <hashes, pré-condições, alcance>
CRITERIA:
  - CRITERION_ID: <ENG-ACxx-Cyy>
    MANDATORY: true
    RESULT: NOT_RUN
    OBSERVABLE_EVIDENCE: <trecho/log/diff/resultado localizável>
    ORACLE_AND_COMPARISON: <referência independente>
    VALIDITY_OR_LIMIT: <coleta/fixture/ambiguidade>
    CRITICAL_VIOLATION: <sim/não; razão>
NATIVE_GATES:
  compilation: NOT_RUN
  tester: NOT_RUN
  terminal_interaction: NOT_RUN
  persistence_mt5: NOT_RUN
  alerts_sound: NOT_RUN
  installation: NOT_RUN
DOMAIN_STATES_UNCHANGED: <literais e origem>
CORE_RAW_RESULTS_PRESERVED: <recibos>
ATTEMPT_RESULT: NOT_RUN
CASE_RESULT: NOT_RUN
SCOPE_OF_CONCLUSION: <propriedades efetivamente demonstradas>
CAUSE_CLASSIFICATION: <assistente/ferramenta/ambiente/fixture/avaliador/não determinada>
CONTESTED_ITEMS: <discordância material; evidências e encaminhamento>
```

PASS exige evidência de todos os obrigatórios aplicáveis. Violação obrigatória demonstrada gera FAIL; ausência/ambiguidade sem violação demonstrada gera INCONCLUSIVE. Um fixture inválido num item não apaga violação independente em outro. Uma divergência material de julgamento permanece com os pareceres originais e deve ser encaminhada ao usuário; não escolha o mais favorável.

## 6. Gauntlet, diagnóstico e correção

```yaml
LOOP_ID: <ENG-R1-L01>
BASELINE_FREEZE: <ID/hash>
CRITERIA_FREEZE: <ID/hash>
CANDIDATE_FREEZE: <ID/hash após implementação>
ATTEMPTS_INCLUDED: <todas, com válidas/inválidas/extras separadas>
FALSIFICATION_FINDINGS:
  - FINDING_ID: <ID>
    CRITERION_OR_INVARIANT: <ID>
    RAW_RESULT: <literal>
    EVIDENCE: <localizável>
    OBSERVED_CAUSE: <quando demonstrada>
    HYPOTHESES: <quando não demonstradas>
    AUTHOR_OF_FIX: <identidade real>
    MINIMUM_REPAIR: <mudança isolada>
    REPAIR_DIFF_AND_HASH: <artefatos>
    NEW_TEST_OR_REFERENCE: <somente se justificado/versionado>
    NEW_FREEZE: <nova revisão>
    REGRESSION_AND_UNRESOLVED: <o que permanece>
LEARNING_THIS_ROUND: <evidência nova, não opinião favorável>
CONSECUTIVE_ROUNDS_WITHOUT_NEW_LEARNING: <contagem>
NEXT_STEP: <corrigir/recongelar/voltar ao diagnóstico/limitar conclusão>
```

Qualquer alteração no candidato invalida seu freeze para novo julgamento dependente. Não altere critério, expected, timeout ou asserts para obter verde. Um erro demonstrado do juiz exige revisão própria com motivo, diff, preservação do raw e nova calibração; a necessidade não autoriza modificar o produto e o control plane silenciosamente no mesmo contrato.

Três rodadas sem aprendizado novo exigem retorno ao diagnóstico. Isso não remove falhas nem aprova por esgotamento. A cláusula `HISTORICAL_UNRESOLVED_FAILURE` só pode ser aplicada quando sua ativação e todas as condições competentes estiverem comprovadas; a mera presença no Core não libera a exceção.

## 7. Relatório de rodada e comparação

```yaml
REPORT_ID: <ID>
HARNESS_AND_CONTRACT_VERSION: <identidades/hash>
SCOPE: <casos e condições executados>
COUNTS_WITH_DENOMINATORS:
  cases_designed: 12
  valid_attempts_planned: 36
  attempts_started: <número observado>
  valid_attempts_completed: <número observado>/36
  invalid_or_extra_attempts: <número observado, listadas>
  cases_pass: <número>/12
  cases_fail: <número>/12
  cases_inconclusive: <número>/12
  cases_not_run: <número>/12
  critical_violations: <número e IDs>
CASE_RESULTS: <12 linhas, com três tentativas e extras>
SUITE_RESULT: NOT_RUN
LOCAL_AND_NATIVE_RESULTS_SEPARATED: <quadros próprios>
RAW_RESULTS_AND_DEBT: <não rebatizados>
INDEPENDENT_REVIEW: <parecer e limitações>
MATERIAL_DISAGREEMENTS: <evidência/encaminhamento>
WHAT_IS_DEMONSTRATED: <alcance exato>
WHAT_FAILED: <critério/evidência>
WHAT_REMAINS_INCONCLUSIVE_OR_NOT_RUN: <razão/próximo passo>
VERSION_COMPARISON:
  previous: <ID/hash>
  candidate: <ID/hash>
  changes: <passagens/diff>
  source_basis: <fontes>
  impact: <dependências e riscos>
  checks_performed: <recibos desta revisão>
  previous_preserved: <local/hash>
DELIVERY_INTEGRITY: <arquivos/manifesto equivalência/renderização>
```

Sem nota agregada compensatória. Um caso PASS exige três tentativas válidas com todos os obrigatórios demonstrados; falha válida em qualquer tentativa produz FAIL. A versão do harness é independente da versão do GENETRIX e da edição JP Wealth. Não transfira aprovações de outra revisão.

## 8. Uso e handoff mínimo

1. Carregar integralmente o harness e conferir o Core/governança/avaliador acessíveis, com VERSION_CHECK e manifesto.
2. Selecionar modo e tarefa; delimitar período, componente, permissões e ações autorizadas.
3. Congelar critérios/inputs/oracles e escolher papéis reais; não iniciar reparo antes do contrato do ensaio.
4. Executar somente a cópia autorizada; conservar registros e verificar o efeito observável.
5. Submeter candidato congelado a julgador separado; corrigir em revisão nova com rollback.
6. Entregar resultado delimitado, fontes/hash, evidências, limitações e próximas verificações. Não solicitar acesso/credenciais desnecessários nem pedir autorização já coberta pelo pedido.

Exemplo de ativação preenchível:

> Use o JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0 integralmente para [diagnosticar/planejar/implementar/auditar] [componente] na cópia [local]. Objetivo: [comportamento]. Base: [versão/hash]. Consulte as fontes acessíveis e registre VERSION_CHECK. Permissões: [ações]; exclusões: [ações]. Aplique os critérios [IDs], referências [oracles] e gauntlet com executor/julgador separados. Entregue diffs, resultados brutos, evidências e rollback; preserve estados pendentes. Não declare teste nativo, homologação, instalação ou aceite sem suas evidências.
