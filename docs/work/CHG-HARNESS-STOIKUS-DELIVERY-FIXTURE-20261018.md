# Harness Stoikus — fixture de distribuição — 18/10/2026

A autorização específica do proprietário foi **“Autorizar patch e validação”**, em resposta à proposta `PROPOSTA-FIXTURE.patch`, SHA-256 `0c8de6171d3aba78a2d154055063b7955b89546c670b246643afa32574e119d4`. A frase literal e o vínculo à suíte completa/novo CI foram transmitidos pelo executor principal nesta conversa. O horário abaixo registra essa autorização, sem atribuir um timestamp original inexistente. Este CHG documenta a decisão e não concede autoridade por si.

## Compreensão, causa e comparação

O JP Wealth organiza planejamento e risco financeiro e distribui fontes Stoikus. O teste de entrega exercita builder, página, bytes embarcados e service worker com dados sintéticos; sua preparação não define fórmulas nem altera os downloads reais. O gerador oficial atual exige os30 `MARKET_HOURS_BUILD_INPUTS`. A fixture copiava o gerador real sem copiar essa dependência transitiva, e recusava o build antes dos oráculos de distribuição.

No CI do PR43/head `1928137c55ef940ff2d609f64b3605d85edcefce`, a suíte completa registrou53 PASS e1 PRODUCT_FAIL bruto. O diagnóstico causal é **TEST_HARNESS_FAIL**: entrada obrigatória ausente da fixture. O bruto continua preservado e o gate anterior permanece falho; esta classificação explicativa não concede waiver. O builder do merge sintético foi comparado diretamente e é idêntico ao local, SHA-256 `d9872b73aa35775e223a45b122b4a1ba205e59e79fb3b1e939ce273a06758e7a`.

Antes: teste SHA-256 `f6148ed0b3bca0f3da3f13b58775028d2f3b340e8a80e790e04267efec2aad4a`. Depois autorizado: `5618a61d340db58360f6fe1f50729c1dd4ba170dec2052ac1c172fa7974ea6ef`. O delta de oito linhas lê por AST a lista literal do dono oficial e copia esses mesmos bytes no setup existente, sem glob, fallback, import novo ou mudança no gerador. Todos os20 métodos/40 casos R4/R5, subcasos, asserções, prazos e ordem permanecem. A futura ausência de qualquer input oficial continua falhando explicitamente.

## Proteção e evidência preservadas

Regressão permanente identificável: `STOIKUS-DELIVERY-FIXTURE-MARKET-INPUTS-20261018`, executada pelos40 casos de `tools/stoikus_interface_delivery_test.py`, incluindo `test_portable_embeds_three_exact_artifacts_with_matching_mime_and_bytes` e `test_derivative_build_rejects_unbounded_or_corrupt_artifacts_before_outputs`. O teste já versionado e selecionado no escopo `all` é a proteção; este registro vincula causa, entradas e recibos sem ampliar os dois arquivos autorizados.

Cópias isoladas dos mesmos47 arquivos de apoio: RED original com40 testes/56 falhas/exit1; GREEN com apenas a patch,40 testes/OK/exit0. A contraprova separada adicionou os30 inputs oficiais, fez o build e manteve a recusa de um pin R4 corrompido pelo mesmo oráculo de tamanho/SHA. Asserções não foram derivadas da correção. Evidências privadas preservadas em `jpw-consolidacao-worktrees-20261018/ci-host-head1928137/`, especialmente `DIAGNOSTICO.json`, `counterproof.json` e `fixture-proposal/red-green-execution.json`. Não se copiam logs privados para o Git.

Estado ao criar este registro: aplicação autorizada em curso; suíte oficial nova e revisão independente pós-aplicação pendentes. O recibo novo ficará em `ci-host-head1928137/final-applied/`. O FULL web anterior, runtime nativo Windows/MT5 e aceite humano são estados separados; a suíte MT5 sintética não os declara aprovados. O executor principal cuida do novo CI e da integração posterior.

## Impacto agêntico delimitado

**AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED.** **BASIS:** o setup de um teste do Harness muda, logo sua execução e trilha de auditoria são alcançadas. O consumo continua pelo mesmo runner e pelos mesmos40 casos, com a lista oficial do builder. Critérios, descoberta, classificação e autoridade não mudam.

| Categoria examinada | Impacto e ação local |
|---|---|
| Teste/contrato de evidência | AFFECTED; oito linhas e este CHG autorizados. |
| Runner, CI, gates e memória de regressão | AFFECTED por execução/referência; sem alteração local autorizada ou necessária para seleção dos40 casos. Vínculo causal permanente neste CHG. |
| Contexto operacional e auditoria da consolidação | AFFECTED pelos novos resultados; relatório externo desta etapa, reconciliação posterior pelo executor principal. ACTIVE e CURRENT não são editados. |
| Agentes, skills, routing, registries, bootstrap e arquitetura | NOT_AFFECTED: não muda responsabilidade, entrada pública, autoridade, ordem de script, contrato de uso ou descoberta; continuam lendo as fontes e runners existentes. |
| Fontes canônicas financeiras, dados e índices | NOT_AFFECTED: nenhum parâmetro, norma, persistência, credencial ou mecanismo de índice muda. INDEX NOT REQUIRED. |

O aviso de frescor do preflight sobre286 caminhos após a base histórica `bf0b1e8` pertence à consolidação já registrada; esta mudança é ancorada no HEAD atual e no mapa completo antes/depois. Não reescreve fotografias históricas nem promove execução esperada a fato.

## Contrato tipado

O contrato é CHG de teste, sem alteração de contexto operacional; não se fabrica um CTX. O validador de instruções aceita somente alvos de instrução/documentação e pares CHG/CTX, por isso seu modo explícito não governa o alvo deste teste. Seu modo default e o juiz permanecem intactos; o schema deste CHG é conferido sem ampliar a allowlist do validador.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-HARNESS-STOIKUS-DELIVERY-FIXTURE-20261018",
  "status": "approved",
  "objective": "Completar apenas os inputs oficiais da fixture de distribuição para executar os mesmos oráculos R4/R5 com o gerador atual",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-stoikus-installer-20261014",
    "branch": "codex/stoikus-installer-20261014",
    "baseline_sha": "1928137c55ef940ff2d609f64b3605d85edcefce"
  },
  "scope": {
    "allowed_files": [
      "tools/stoikus_interface_delivery_test.py",
      "docs/work/CHG-HARNESS-STOIKUS-DELIVERY-FIXTURE-20261018.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      "tools/leverage_suite.py",
      "tools/rebuild_monolith.py",
      ".github/workflows/",
      "src/",
      "mt5/",
      "downloads/",
      "dist/",
      "docs/normative/",
      "docs/decisions/"
    ],
    "allowed_actions": [
      "Acrescentar somente as oito linhas da PROPOSTA-FIXTURE.patch aprovada ao DeliveryTest.setUp",
      "Registrar este CHG dedicado e executar a suíte MT5 completa em recibo novo externo",
      "Comparar mapa integral de fontes, HEAD, diff e evidências antes/depois"
    ],
    "forbidden_actions": [
      "Alterar casos, estímulos, asserções, oráculos, ordem, timeout, critério ou classificação do runner",
      "Modificar produto, gerador, CI, ACTIVE, instruções ou dependências",
      "Executar UI, VM, commit, push, merge ou publicação nesta etapa"
    ],
    "regressions_forbidden": [
      "Omitir ou dispensar qualquer um dos 54 checks obrigatórios",
      "Aceitar corrupção, MIME incorreto, envelope inválido ou bytes divergentes",
      "Sobrescrever o PRODUCT_FAIL bruto anterior ou confundir fonte/host com execução MT5"
    ]
  },
  "derived_artifacts": {
    "allowed": [],
    "generation_commands": [],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "Servidores loopback e contexts isolados das fixtures existentes; sem serviço público ou perfil real"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python 3.12 do runtime congelado existente",
      "Node existente do runtime bundled",
      "Chromium/Google Chrome em contexto de teste isolado via Playwright",
      "Compilador C++ host já utilizado pelo runner",
      "Git somente leitura"
    ]
  },
  "acceptance_criteria": [
    "Diff limitado aos dois caminhos e patch de oito linhas byte-idêntica à autorizada",
    "Todos os 20 métodos, 40 casos R4/R5, subcasos, asserções, ordem e timeouts preservados",
    "leverage_suite.py --scope all executa todos os 54 checks e todos passam sem waiver",
    "Mapa integral de fontes e HEAD permanecem estáveis durante a suíte",
    "Auditoria independente e novo CI do PR43 antes de merge, sob controle do executor principal"
  ],
  "approved_tests": [
    "python3 tools/stoikus_interface_delivery_test.py (40 casos, incluído no escopo all)",
    "python3 tools/leverage_suite.py --scope all --artifact <recibo externo novo>",
    "python3 tools/agent_instruction_structure_test.py (contrato inline existente)",
    "Comparação AST antes/depois, SHA-256, git diff --check e mapa integral"
  ],
  "rollback": {
    "source": [
      "Retirar somente as oito linhas autorizadas do setup; hash original f6148ed0b3bca0f3da3f13b58775028d2f3b340e8a80e790e04267efec2aad4a",
      "Preservar este CHG como histórico da autorização e todos os recibos"
    ],
    "application_state": [
      "Nenhuma alteração de estado ou dados reais do aplicativo"
    ],
    "data": [
      "Preservar brutos de CI, RED/GREEN, contraprovas e backups externos"
    ],
    "environment": [
      "Nenhuma instalação ou alteração global; encerrar somente processos próprios dos testes"
    ],
    "verification": [
      "Conferir hash original, diff de escopo e HEAD sem alteração"
    ]
  },
  "approved_by": "Proprietário: “Autorizar patch e validação”, resposta direta à proposta com SHA-256 0c8de6171d3aba78a2d154055063b7955b89546c670b246643afa32574e119d4",
  "approved_at": "2026-10-18T18:52:43.900914+00:00",
  "approval_timestamp_note": "Horário UTC de registro da autorização comunicada pelo executor principal; não é timestamp recuperado da mensagem humana, que não consta no registro disponível",
  "authorization_evidence": "Frase literal transmitida pelo executor principal: “Autorizar patch e validação”. A pergunta vinculava a patch de oito linhas, suíte MT5 completa e novo CI do PR43 antes de merge.",
  "expires_on": [
    "Mudança de escopo, arquivos permitidos, critérios ou dependências",
    "Mudança material do candidato exige revalidação das evidências afetadas"
  ]
}
```
