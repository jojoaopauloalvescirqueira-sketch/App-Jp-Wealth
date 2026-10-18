# Preparação isolada do teste de downloads — 2026-10-16

O proprietário autorizou expressamente o patch de uma linha, seus testes e dois commits separados no mesmo PR: correção desta fixture e edição documental curada. A branch existente é `codex/stoikus-continuity-20261014`, base `7e8b9a055503d514dd7ab91178f85b585df7b8b9`. Não há autorização de merge, publicação, alteração de produto ou adoção do harness documental.

```yaml
schema: jp-harness/chg/v1
change_id: CHG-DOWNLOAD-FIXTURE-WELCOME-20261016
status: approved
risk_level: N3
authority_required: A4
approval_scope: exact_fixture_patch_validation_separate_commit_push_and_PR_on_existing_branch
objective: Isolar o primeiro acesso nos contextos sintéticos de invalidação do teste de downloads, preservando suas verificações.
target:
  branch: codex/stoikus-continuity-20261014
  baseline_sha: 7e8b9a055503d514dd7ab91178f85b585df7b8b9
scope:
  allowed_files:
    - tools/download_assets_browser_test.py
    - docs/work/CHG-DOWNLOAD-FIXTURE-WELCOME-20261016.md
  allowed_actions:
    - Aplicar somente a chamada de init_script previamente revisada na fixture de invalidação.
    - Registrar este contrato, executar provas focais e full, obter revisão independente.
    - Registrar commit próprio, separado da edição documental, enviar a branch existente e abrir PR conjunto.
  forbidden_actions:
    - Alterar produto, critérios, cenários, assertions, oráculos, timeouts, bootstrap compartilhado ou CI.
    - Reclassificar recibos anteriores ou ativar exceção para gate falho.
    - Criar ou trocar branch/worktree, reescrever histórico, fazer merge ou publicar.
    - Incluir originais documentais não rastreados ou dados pessoais no commit.
data_policy: synthetic_disposable_profiles_only
approved_by: Resposta expressa do proprietário ao patch revisável em 2026-10-16.
expires_on: material_scope_change_or_source_identity_drift
```

## Antes, causa e mudança delimitada

O full anterior terminou com 74 PASS e um `PRODUCT_FAIL` em `download-assets-browser`; esse recibo permanece falho. O teste original foi reproduzido sem edição: o Welcome agendado a 350 ms intercepta cliques reais durante cenários com download retido. Fechar o modal e alterar artificialmente `S.onboarding.done` depois da carga não cancela o timer pendente.

Os cinco contextos do primeiro laço já instalam `window.__onbShown=true` antes da carga. A correção acrescenta a mesma preparação aos oito contextos de invalidação do segundo laço. Não muda a experiência de primeiro acesso do produto. Após remover a chamada acrescentada, a AST é idêntica à original; ações, cenários, corrupção de hash/tamanho, invalidações, bytes e assertions são conservados. Não se usa clique forçado ou timeout maior.

| Identidade | SHA-256 |
|---|---|
| Teste original | `7f158dcf24dc004a7cf0f8f8104cc48276bc53430c20192a9bb8cee681a99a8c` |
| Teste proposto e autorizado | `ba6c180b51527408f5b0a70bf09cda11a0439b0ca8df6289212c64ef26f404f0` |
| Patch autorizado | `f10506126499198ad2ce1989c2d068e348b54e6ab0f36442f5c475aac71e0eba` |
| Full anterior, preservado | `4637b01b816d343a310a00bfcd9aa8e597229e32b187446db1826f99e8217a39` |
| Parecer independente da proposta | `51cabcaa385646ae7011467efa880204b83e1dfbcd0beab5ec44c20a3f92e292` |

O diagnóstico externo preserva 12 contextos temporais: a fixture original com timer pendente bloqueia três de três cliques; a flag anterior à carga evita o agendamento e permite três de três. A experiência da proposta somente em memória concluiu 111 verificações, mas é diagnóstico, não PASS do teste ativo ou do full. A revisão independente aprovou tecnicamente o alcance e a causa, sem conceder autorização ou antecipar aceite comportamental.

## Validação e critérios

Executar o teste ativo completo com os mesmos 111 checks e uma nova execução integral de `quality_gate.py --tier full` sobre os bytes congelados. Complementar com os três casos `welcome-*` da suíte própria `onboarding_first_access_test.py`: ela não integra os 75 checks do full e sua prova será identificada separadamente. Conferir diff, hashes, ausência de delta do produto e preservação dos 216 arquivos documentais selecionados e 870 originais históricos.

Uma revisão independente do candidato aplicado deve conferir o diff exato, o antes/depois, os recibos reais e a preservação dos critérios. Sem full aprovado e sem essa revisão, os commits continuam bloqueados. Este contrato é registrado antes da edição do teste e não declara antecipadamente resultados. Aprovação de fixture não comprova execução MT5, aceite financeiro, instalação ou adoção de prompts.

## Impacto agêntico e recuperação

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. AFFECTED: preparação sintética de um teste ativo e seu registro dedicado. NOT_AFFECTED: hierarquia de instruções, normas financeiras, classificadores de resultado, gates, CI, produto, schemas, bancos, contexto global, roteamento de skills, grafos e memória. Não há propagação normativa ou indexação a executar. O drift contextual anterior permanece separado; esta mudança não refaz a revisão geral do sistema.

A edição documental C2 permanece um lote independente e imutável, sem alteração de seus 216 caminhos congelados. O delta desta fixture terá commit próprio antes do commit documental; ambos seguirão no mesmo PR conforme autorização explícita. Os recibos e pareceres anteriores ficam preservados externamente, inclusive o full falho e a tentativa original.

Rollback delimitado: restaurar somente os bytes originais do teste a partir do hash registrado e retirar este CHG do delta ainda não integrado, mediante autorização aplicável à operação Git; depois executar as provas pertinentes. Não apagar recibos, originais documentais ou dados. Uma reversão restauraria a corrida conhecida e não pode ser descrita como aprovação do teste anterior.
