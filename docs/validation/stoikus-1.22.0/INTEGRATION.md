# Stoikus 1.22.0 — candidato local validado

Base Git `0f247215cc20829fdba40c3b33458ee976c17ea1`, branch `codex/stoikus-renaming-20261012`, worktree `/private/tmp/jpw-stoikus-renaming-20261012`. Plano e criação de branch/worktree aprovados pelo proprietário. [Produto](../../work/CHG-STOIKUS-RENAMING-20261012.md), [control plane](../../work/CHG-STOIKUS-CONTROL-20261012.md) e [contexto](../../work/CTX-STOIKUS-RENAMING-20261012.md) possuem trilhas próprias. Implementação local aguarda teste manual e aceite humano. Não representa commit, push, merge ou publicação.

## Produto e compatibilidade

Marca pública **Stoikus**, produto **1.22.0**, metadata MQL central **1.220**, cálculo **1.9.0**. [Mapa de 29 arquivos/recursos MQL e cinco ferramentas](../../../mt5/jpw-alavancagem-atual/STOIKUS_RENAME_1_22_0.md). NoCuda mantém nome e versão própria 1.30; Supervisor e scripts conservam seus versionamentos específicos. Logo JP Wealth e slogan preservados, sem redesign.

APIs, funções, tipos, macros/guards, IDs DOM, rotas, bancos, schemas, chaves, locks e preferências permanecem. Nenhuma migração de dados. Novos indicadores reconhecem nomes anteriores na admissão; isso não modifica binários antigos. Antes de futura instalação autorizada, retirar componentes antigos dos gráficos e utilizar o pacote completo, sem misturar includes/programas entre versões. Nenhum terminal operacional foi alterado.

## Identidade e distribuição

R2 congelado: `bbe9293595d4ba22b146b9aeb2a2931be6e65ba52e06c25db4802fca9d46f6ab` (935 arquivos enumerados com separador NUL). Global build `fba597b06c3497af`; runtime build `382db58b4cfde5e7c725088f15fe993261328ca742aee7fa6e6412a8a19cf45d`; fingerprint MQL `5d9f76c5f55c94fba498a3616b5baaf8ddf8e77c96801f61b24c8793606aafac`. Hash de arquivos não é commit nem prova nativa.

`JPW_Stoikus_Fontes_v1.22.0.zip`: **763854 bytes**, **133 membros**, SHA-256 `79d481a624d37dccb2237f37db7a35b2746a0b8281d183b1ce30fcba0bfc9c95`. 29 nomes remapeados do inventário histórico de 132 membros, mais documento de transição; 111 inputs runtime e 33 programas. Geradores oficiais `tools/build_leverage_package.py` e `tools/rebuild_monolith.py`; igualdade de bytes, reprodução e idempotência verificadas em fixtures isoladas. `nativeArtifact=null`, sem EX5 desta revisão.

123 arquivos históricos conferidos byte a byte contra a base/suplemento, incluindo os três ZIPs, 103 documentos de validação, dez manuais e sete arquivos do harness. Recursos BMP 8/8 preservados. A dívida HIS-AC20 e o piloto histórico permanecem declarados; não transferem aprovação para Stoikus.

O campo `genetrixCandidate.siteIntegration=NOT_RUN` conserva o checkpoint pré-validação do manifesto, conforme semântica registrada em [INTEGRATION 1.21.2](../genetrix-1.21.2/INTEGRATION.md). Recibos R2 demonstram integração **local** atual. Não reinterpretar esse checkpoint como prova de publicação nem alterá-lo retroativamente para simular evidência anterior.

Os textos novos do README e do mapa Stoikus dentro do ZIP são o checkpoint de preparação daquele pacote congelado. Sua menção a validação em andamento encaminha aos recibos próprios deste INTEGRATION; o resultado local atual é R2. O ZIP não foi reconstruído para carimbar testes posteriormente.

## Verificações observadas

| Verificação | Resultado | Escopo e limite |
|---|---|---|
| Preflight audit/edit | PASS | Branch/Base conferidas; alterações conhecidas e aviso de frescor preservados |
| `leverage_suite.py --scope all` | PASS | 40/40 verificações no R2; host C++ e browser sintéticos, sem MT5 nativo |
| `quality_gate.py --tier full` | PASS | 57/57 verificações no R2; zero nas demais classes |
| `jpw_stoikus_oracle_test.py` | PASS | Sete casos de risco e 19 referências Decimal, fixtures congeladas intactas |
| Marca e aliases | PASS | 12 casos reais de admissão, 12629 assertions de render e dois mutants sensíveis |
| Página/distribuição | PASS | Cinco abas, teclado/foco, quatro layouts, HTTP/file/portátil/PWA, integridade e recusa de downloads inválidos, persistência sintética preservada |
| Revisão independente focal | PASS | Antes/depois, identidade, oráculos e largura incorreta +8/-8 recusada; parecer e vinculação final em recibo externo |
| Contexto estrutural R2 | PASS | 101 controles negativos; não comprova autoridade nem carregamento por cliente |
| Compilação/execução MT5 | NOT_RUN | Sem EX5, instalação ou armamento; operação continua BLOCKED |
| Teste manual/aceite do proprietário | NOT_RUN | Próximo gate humano |
| Commit/push/merge/publicação | NOT_RUN | Autorizações específicas não recebidas |

Recibos em `/private/tmp/jpw-stoikus-evidence-20261012`: `host-all-R2.json`, `full-R2.json`, `oracle-R2/receipt.json`, `identity-R2.json`, `context-R2.log` e `FREEZE-R2.json`. O fecho R3 altera somente documentação informativa/contextual fora de MT5/runtime; `R2-TO-R3.json`, `context-R3.log` e `fast-R3.json` registram comparação e verificações afetadas. O full foi executado no **R2**, não no R3. Todos os inputs de produto, CP, ferramentas, fixtures, manifesto, ZIP, HTML e derivados devem permanecer byte-idênticos para reutilizar essas provas.

## Diagnósticos preservados e resolvidos

R1 host: 37 PASS / 3 PRODUCT_FAIL brutos, por referências públicas antigas e contagem antiga do rótulo no bridge geométrico. R1 full: 57 PASS, sem cobrir esses achados. R2 corrigiu referências e expectativa independente de 16 para 15 caracteres, conservando igualdade exata e limites. Falhas e parecer R1 ficam preservados.

A enumeração inicial sem `git ls-files -z` omitiu oito nomes Unicode; `BASELINE-SUPPLEMENT.json` conferiu HEAD=disco para todos, sem alteração. Um parser auxiliar de identidade buscou o nome errado do global build e foi corrigido sem alterar o candidate (`TEST_HARNESS_FAIL` diagnóstico). A checagem de escopo detectou omissão do próprio registro CHG de produto na enumeração CTX; corrigida no fecho informativo, com `scope-R2-first-attempt.json` preservado. Não houve exceção ou relaxamento de gate.

## Impacto agêntico focal

**AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED**

**BASIS:** renomes e produto 1.22.0 alcançam o registro de testes, manifestos, mapa de contexto e fotografias operacionais. A análise IMPACT/RECONCILE da skill de governança confrontou esses consumidores com fontes/paths atuais; propagação limitada ao plano humano, sem mudança de autoridade, routing global ou norma.

| Categoria | Impacto / ação local | Reconciliação e evidência |
|---|---|---|
| Instruções de agentes e bootstrap | AFFECTED / NOT_REQUIRED | Consultam contexto atualizado por referência; AGENTS raiz e pacote, harness e skills conservam bytes/limites |
| Skills e routing global | AFFECTED / NOT_REQUIRED | Leem os mapas atuais; busca não encontrou comandos correntes dos cinco runners antigos nestas camadas |
| Registro de runners e gates | AFFECTED / REQUIRED | Nomes/paths atualizados; critérios, negativos e oráculos preservados, revisão própria e host/full R2 |
| Manifestos e inventários | AFFECTED / REQUIRED | 102 scripts na mesma ordem, 133 membros e hashes pelos geradores oficiais |
| Contexto operacional e contratos da tarefa | AFFECTED / REQUIRED | CURRENT-STATE, ACTIVE-TASK, CTX/CHGs, README, CHANGELOG e handoff reconciliados somente neste escopo |
| Contratos/arquitetura do componente | AFFECTED / REQUIRED | Novo mapa/documento de transição; arquitetura, limites e contratos financeiros preservados |
| Normas e decisões financeiras | NOT_AFFECTED / NOT_REQUIRED | Nenhum arquivo/regra/valor alterado; não se declara nova homologação |
| Histórico/imports congelados | NOT_AFFECTED / NOT_REQUIRED | 123 hashes históricos e oito BMPs preservados, sem substituir fotografias antigas |
| Memória/vetor externo | NOT_AFFECTED / NOT_REQUIRED | Nenhuma atualização de memória/reindexação executada ou requerida pelos consumidores desta trilha |

Índices estáticos de distribuição/build foram regenerados; nenhuma vetorização realizada. **SYSTEM RECONCILED: focal**, não auditoria ou reconciliação integral de toda dívida documental do projeto.

## Rollback e próximo gate

Repor somente o delta da renomeação e seus derivados a partir de BASE/arquivos preservados, sem apagar bancos, locks, preferências ou estudos. Qualquer operação Git de recuperação exige autorização própria. Aguardar teste manual e aceite do proprietário; commit, envio, integração, publicação, compilação e instalação possuem gates separados.
