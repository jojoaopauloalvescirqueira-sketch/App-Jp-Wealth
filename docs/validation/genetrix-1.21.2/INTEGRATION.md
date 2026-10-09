# GENETRIX 1.21.2 — integração ao site e proveniência — 2026-10-08

Estado deste checkpoint: **CANDIDATE local em integração**, sem afirmar commit, push, merge ou publicação já realizados. Base `7f0828488b2fc0ea62dc7c421174799cda47a34a`, branch `codex/genetrix-1-21-2-site-20261008`. Contrato e autorizações: [CHG 1.21.2](../../work/CHG-GENETRIX-1-21-2-SITE-20261008.md). A suíte MT5 host R3 foi concluída e conferida: **40/40 PASS**. O full web R3 também concluiu **57/57 PASS**. A revisão independente final possui registro próprio; compilação e execução MT5 permanecem pendentes.

## Identidade e distribuição

| Item | Identidade |
|---|---|
| Produto / MQL / cálculo | 1.21.2 /1.212 /1.9.0 |
| ZIP fontes | `JPW_Genetrix_Fontes_v1.21.2.zip`; 760092 bytes,132 membros |
| SHA256ZIP | `a9a77be170036747fec8322fdba7d80bd6256fbcae87e4c6dadb1348ff916261` |
| Fingerprint 111 fontes/recursos | `9650de7a8573566f3532e3a3ecb2806d0a0e62e2afe7b8130f1331045c06a4b6` |
| Manifesto atual | `downloads/jpw-alavancagem-atual/manifest.json`; validado por seus próprios hashes |
| EX5 atual | Indisponível; compiled.available=false, path/hash/bytes=null |
| Prova nativa 1.21.2 | Compilação NOT_RUN; runtime BLOCKED / NOT_RUN; instalação NOT_RUN |

Os 132 membros canônicos permanecem byte-idênticos à origem, inclusive README, AGENTS, textos históricos e harness. Este documento integra o contexto atual sem alterar o pacote congelado. Nenhum EX5 1.20 é renomeado como 1.21.2. Os 33 EX5 da árvore produtiva antiga são retirados do conjunto atual, preservados no histórico Git e vinculados aos registros1.20, cujo acervo permanece em [genetrix-1.20.0](../genetrix-1.20.0/).

O manifesto recebido conserva seu checkpoint pré-integração `genetrixCandidate.siteIntegration=NOT_RUN` e referência histórica `integration.base=4ef5f000…`, com baseRole expresso. A base atual de integração é `genetrixCandidate.baselineCommit=7f082848…`. Recibos locais novos podem demonstrar integração atual; não reescrever retroativamente o checkpoint canônico para simular um resultado anterior.

## Funções e aliases atuais

| Componente | Papel e limite |
|---|---|
| Indicador Conta — JPW_Alavancagem_Atual | Resumo e Cockpit; alavancagem, flutuante, Genesis SL, Raiz N 1/2 semanas, risco dos stops e flutuante compensado, com estados de cobertura |
| Monitor — JPW_Genetrix_Monitor | Um EA no gráfico de apoio para conta inteira: monitoramento/histórico e contabilidade de ciclos; sem rotinas de negociação |
| NoCuda — JPW_NoCuda_Channels | Estudo gráfico, canais/Fibonacci e seus objetos; separado das leituras Conta |
| Supervisor — JPW_Genetrix_Supervisor | Proteção7x opcional em outro gráfico; observação/armamento explícito conforme contrato, não armado aqui |
| Observer / Accountant antigos | Legados preservados para referência e rollback; não instalar concorrentes com Monitor sem revisão de titularidade |

O MT5 aceita um EA por gráfico; a instalação recomendada usa Monitor em apoio e indicadores nos gráficos de trabalho. Esta nota não comprova execução do terminal. Abrir/fechar o Cockpit não deve ser confundido com iniciar/encerrar o produtor; fechar o gráfico do EA interrompe sua coleta.

`mt5/jpw-alavancagem-atual/AGENTS.md` e `harness/REPOSITORY_INTEGRATION.md` conservam seus cabeçalhos antigos como fotografias de origem. Para o trabalho atual, carregar instruções raiz, este mapeamento, manifesto e documento `GENETRIX_CORRECTIONS_1_21_2.md`, mantendo o harness integral como dependência analítica. Não criar precedência normativa entre esses prompts.

Harness 1.0.0 continua **CANDIDATE**. R2 **FAIL —25 PASS / 7 FAIL / 4 INCONCLUSIVE / 36**, R5 restrito **AC03 FAIL/AC04 PASS, full NOT_RUN** e proposta 1.0.1 **NOT_ADOPTED** são registros históricos, sem apagamento ou transferência de aprovação. HIS-AC20 mantém **PRODUCT_FAIL3/3** declarado. Estados PENDING / NOT_HOMOLOGATED / BLOCKED e indisponibilidade financeira permanecem.

## Delta canônico e trilha dedicada dos juízes

Comparação source-vs-main: **22 arquivos modificados e4 documentos novos**,26 diferenças no inventário fonte comparado, sem inventar alteração dos demais membros. Esse delta cobre as revisões1.20 → 1.21 e está separado da retirada dos 33 EX5 históricos e da página web. Propósito específico 1.21.2: ajuste do título Fibonacci ao espaço e colocação compacta do acessoNoCuda, preservando preferências, identificação, saída, IDs e estudos; nenhuma fórmula/schema financeiro mudou.

Fonte externa de comparação do coordenador: `source-vs-main-delta.json`, SHA256 `940dbde43161044859590a96f94b86f8070a8bd75d2323e032e676666a1eb74c`. O diff correspondente permanece nas evidências da revisão; este resumo não equivale a testar o produto.

24 registros do control plane:23 ferramentas Python e1 ensaio ATR MQL já pertencente aos 132 membros. Os contratos de origem foram aprovados antes da transferência, conforme packet e comparação do coordenador. O juiz não foi ajustado incidentalmente para tornar esta integração verde. **21 before existentes e3 ausências** conferidos contra a base 7f082848; **24 after** contra os arquivos copiados. A rechecagem documental realizou72 comparações de hash, todas coincidentes; isso demonstra identidade dos bytes, não sensibilidade universal ou validade matemática de todo juiz.

Recibos externos consultados: `judge-main-vs-freeze-provenance.json` SHA256 `37c5e561f3313389b0820c147915ab396f90c1c60bafa7f72c793e6b0ab4ff87`; `judge-provenance-review.json` SHA256 `3241ae2b8528b08575683da1a022f5c001138750de749d2d4df4296c6a13771f`. Os registros abaixo preservam o antes/depois no repositório, sem depender da duração de uma pasta temporária.

| Caminho | Before na base 7f082848 | After transferido |
|---|---|---|
| `mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Live_Tests.mq5` | `3de62cd34a13673f6c23474127e16839dba378c1439fb05b53650f4488fee0b7` | `3153a9a250fe389df563c858658ffbf60d159b7d13579ef5ab456539cfe71047` |
| `tools/jpw_genetrix_brand_test.py` | `bb669030a8f3c69efd7b0c787252400541b7ddd9f4da11a39943636293332b85` | `5d81b73ea342bf53b7f8e00a68208b7df8a37b73f42abad2dbd8cf28b5000c36` |
| `tools/jpw_genetrix_ui_test.py` | `622efece36f8e305b7156a2ee3d34cacc241beb728176a5a319a125a4dce8189` | `1e7dcb87f2811cc2e62a306483e88f0b0525b9645706cb48ad6529a4b623b69a` |
| `tools/jpw_mt5_design_test.py` | `fca2331abcfd94ecda06fe1fe85db97899bd89fd7265db1af2dd345f8656dfea` | `b4fb50e8505632237271b47e2af509129fe33f7b5435da154bc32f7d35db2aae` |
| `tools/jpw_nocuda_fibo_controller_test.py` | `ae216f5e1cf90d3b4533ca4eeac4910bc46928435dbb59dffc06de5c1a81ed63` | `8577d09bcd7edaea4ad909f300d7ef199a960b6dd1f99e71be006eea42e680b3` |
| `tools/jpw_nocuda_fibo_ui_test.py` | `5e2b61e29f5a00f5e5c1af1ffa81f16ccf5cc7ecaadad15eed35d17b1c5f39e3` | `5b535663ea5469834dd32ae0449ccd91b19f68afe8cdc201bd122e055df9ee62` |
| `tools/jpw_nocuda_integration_test.py` | `8ec80245dbd8b12e99e1d382c3f1846abbccd64b3fed1cea40979edb0a430865` | `1f3b2ba71d8a0152fea6443d823c0eb44b430bdc3d721fc6ba91852dc4bd64b5` |
| `tools/jpw_personal_history_test.py` | `cd2cd12aa82da5c22859df1712ccad1cd9c3673d22ea41d88132ff55f6dd8a9b` | `48faa02b9a42fe95335de257ae4301498220d12fef2ae3591ff5a28adae37f38` |
| `tools/jpw_positions_ui_test.py` | `9951e028a7e473aa95307d6ea5be35498509b2d07641640f03addead823f6ca7` | `a5989781f8a87d0b9de12bce06939d48ff6705b440e9b4f2c0508d40e24176f7` |
| `tools/jpw_signal_copy_ui_test.py` | `bc5a7b07fa380bda09f5840aae2107e49df45a3446e9c48d5b38f6b985a7e027` | `c1aaa05690a60273102728611c3f307ec7204f582971574b4a8318eff1804769` |
| `tools/leverage_details_event_test.py` | `efc4a3f14ac0b54e0e5d7a0e879a3c2082c583cdce519b4b8b4cd9b887a8c2da` | `ac4af51b831ff03439ffa64c74cbea79cd59ad45a1d4bd51b765ac3f862e6e23` |
| `tools/leverage_geometry_test.py` | `0bd3b17daa37a71c7a806af4d470787ebbef1c78dc3f2609127bd3597770ed3c` | `ade5b90d2dcd62bc91724373d7982e50beab914b2190184005db1bc38e1febd6` |
| `tools/leverage_host_layout.py` | Ausente na base — novo bridge | `cb17b9329aefeba20933c49ab6e6a310490cbfc9c18e082f1f5ba4d2368a1ac7` |
| `tools/leverage_host_runtime.py` | Ausente na base — novo bridge | `114186b7d68dbe01363e84e4890575ffb935d607df9cd7c7a3957918ed21d8ad` |
| `tools/leverage_host_shim.py` | Ausente na base — novo bridge | `d72191cbefad549986f89966bdf9f496b23707477c6d6d007cbdf432ccffa95c` |
| `tools/leverage_live_adapter_test.py` | `db33c98af497729e312a1dbc913130e811a8ac4afc15ecf862ee772256a3a325` | `49327579fc61a0e87a18b727f6c707d2102f9745e1f784825c70c26918413389` |
| `tools/leverage_package_test.py` | `27208e7dfe491d7f5568c831a28a516a4c59c1b5acf7665c7c984521d5fff39c` | `0ac1d03487f7bee32e48f4473a1fc52c768374c7cf6c990d4458b2b77b6b1a32` |
| `tools/leverage_panel_test.py` | `317e8a7c15e67169b151880578a5b3479811c1e4d05ee64f1d32e01695f35bfb` | `daf57b16c92abeb3e9ef299cdf908ef0ab71ab0083c26a830419401ae84658bc` |
| `tools/leverage_reliability_test.py` | `e3231117e0e7a7a22e04fbf2e73000d153741c9bfbcec36c59ae95e0b1199f05` | `557d0996a9c30f7eac003de27256c0ccaebe4944cbd3183300bc849598dd7e4a` |
| `tools/leverage_scheduler_test.py` | `d387757c6c6c933f2682ce31a7593d316196cb9aa2d36fddc4cad476ca6b2585` | `2f64e63e9f12711651caeb2642e54ec28032ae802d78a7ab489675a74ebad498` |
| `tools/leverage_stop_ui_test.py` | `7337da64e0702422f38e08d0780613bb3dd4c0224cf51c1c51e73671c965e859` | `aa9c6e591e92841a381fff8156bb360f30c2d9c1fa7e2c74a54bcbec32da822d` |
| `tools/leverage_suite.py` | `c3f77b409a569d59f92948bed82a29d27e1153594030f18626bc266f5d592b13` | `bc0d036ce48678d62b395185caf2049aa03dccaaa50725e341de322dff7e9bc3` |
| `tools/leverage_suite_test.py` | `8b5a74d06155550f2c365b2c31bef33221daffd33e5c4a8b45bfd465167c0244` | `7b2c09a3b6129ab0a5b0a97486088728f8cb10530adff4de171a497df63f20f2` |
| `tools/leverage_page_test.py` | `2a98ded10575c6e5de48b937cf771b70bd6a01e5df9aca0bbfe436f085a5ebb7` | `0aed9390fbb0016e34870668a4980c00e21cf4378227fdfda6743072ad327f72` |

As pontes de host são simulações de execução local. O ensaio ATR corrigido relê o valor a cada captura, sem mudar sua referência matemática. Juízes de produto/arquivo/UI/host e a página têm critérios próprios; nenhum resultado agregado elimina uma falha obrigatória. Pré-condição ou coleta defeituosa recebe sua classificação e trilha, sem reescrever o bruto.

## Validação corrente e camadas de evidência

| Verificação | Resultado neste checkpoint | Evidência/limite |
|---|---|---|
| ZIP 132 membros/SHA/tamanho e 24 registros before/after | PASS | Conferência direta nesta raiz e base Git,72 comparações de proveniência; não runtime |
| Preflight audit/edit com árvore conhecida | PASS | Edit inicial sem --allow-dirty bloqueado; tentativa e avisos conservados |
| Conferência dos seis documentos/links/diff | PASS | Links locais existentes; históricos preservados; diff --check e preflight finais sem erro; não valida runtime |
| Suíte web full final R3 | PASS — 57/57 | [Recibo completo](evidence/full-R3.json); nenhuma falha ou exclusão |
| Suíte MT5 host final R3 | PASS — 40/40, zero demais estados | Recibo R3 e 382 inputs atuais conferidos; simulações/compiladores de host, não MetaEditor/terminal |
| Revisão independente da integração final | PASS — aptidão para integração de fontes/site | [Parecer final](evidence/FINAL-REVIEW.md), R5 com 847 inputs intactos; MT5 e Git separados |
| Compilação MetaEditor 1.21.2 | NOT_RUN | Requer fonte/fingerprint/33 logs/EX5 correspondentes |
| Runtime, clipboard, popup/som, persistência MT5 | NOT_RUN / BLOCKED | Percursos nativos próprios, sem herdar prova de 1.20 |
| Instalação/armamento/negociação | NOT_RUN | Fora desta integração |

Não há GitHub Pages configurado segundo conferência do coordenador (`has_pages=false`, API 404). Esse fato é declaração verificada pelo coordenador, não consulta executada por este autor; GitHub/main e aplicativo local não são deploy externo. A instalação/publicação operacional continua exigindo sua etapa própria.

## Reconciliação e rollback

Contexto focal, tarefa ativa, mapa e changelog apontam para os mesmos estados, manifesto e candidato. AGENTS raiz, Core, skills, roteamento, normas, schemas e os 132 membros não recebem edição incidental. O estado global não é declarado reconciliado antes dos gates finais; fontes históricas permanecem históricas, sem transformar falhas em dívida liberada.

Rollback: conservar a base 7f082848 e os arquivos/recibos de origem; retornar somente o delta de integração mediante ação Git autorizada. Nenhum banco, histórico pessoal, configuração de conta, estudo ou preferência real é removido. Este autor não instala pacotes nem executa rollback.

## Checkpoint final desta autoria documental

Recibo efetivamente consultado: `/private/tmp/jpw-genetrix-site-evidence-20261008/mt5-host-R3.json`, SHA256 `16cffc1ea5c3f7ea7510289a05bbb17f6d01185323df56c0adcd0642b792ed69`. Contém 40 checks PASS, zero PRODUCT_FAIL/TEST_HARNESS_FAIL/ENVIRONMENT_ERROR/BASELINE_FAIL/NOT_RUN; input_fingerprint `712dad336f51acffd89304a342569228c0fc21735d5d3c4e11641530f9babffb`, inputs_unchanged=true. Rechecados os 382 source_hashes contra os arquivos atuais, sem diferença. Final UTC `2026-10-09T01:42:24.670074+00:00` corresponde à noite de 08/10 em São Paulo; não reinterpretar o relógio do recibo.

Este autor reabriu os seis documentos, verificou os links locais, preservou o conteúdo anterior por comparação com a base Git e confirmou 132/132 membros e hashes do ZIP contra a árvore fonte. O Core relocalizado mantém SHA256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`; autorizações, vigência, classificação CANDIDATE e aplicabilidade histórica permanecem independentes da identidade dos bytes. Os resultados do full e da revisão final deverão ser incorporados pelo coordenador quando houver recibos; não foram executados nem concluídos por esta autoria.

## Recibos finais locais — R3

- Web full: [57/57 PASS](evidence/full-R3.json).
- MT5 host: [40/40 PASS](evidence/mt5-host-R3.json), entradas estáveis.
- Página: [quatro processos concluídos PASS](evidence/UI-AUTHOR-RECEIPT.json); a segunda tentativa demorou no encerramento do Playwright, com causa ainda não determinada. Nenhum resultado foi promovido antes do exit0.
- Downloads: [três processos independentes](evidence/consumer-trial-1.json), pacote HTTP e bytes embutidos iguais ao ZIP canônico.
- Revisões R1/R2 invalidadas após ajustes finais de texto/link, tentativas preservadas no acervo externo. R3 permaneceu estável.

Integração Git terá registro próprio. Estes resultados locais não comprovam execução MT5, instalação operacional, armamento, hosting ou eficácia financeira.

## Adoção documental do parecer final

O parecer independente final foi recebido após os gates R3 e o congelamento R5. Seus 847 inputs foram conferidos sem divergência; a revisão aprovou a integração de fontes/site e conservou compilação MT5 `NOT_RUN` e aceite operacional `BLOCKED_NATIVE_VALIDATION`. A adoção deste parecer e recibos é camada documental N0-D, sem alteração de código, juiz, critérios ou pacote. Commit, push e merge serão demonstrados pelos recibos Git posteriores; este checkpoint não os presume.
