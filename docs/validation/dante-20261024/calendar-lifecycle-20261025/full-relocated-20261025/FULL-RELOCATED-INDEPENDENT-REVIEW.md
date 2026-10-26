# Revisão independente A0 — FULL com outputs redirecionados, 25/10/2026

**Veredito: FULL executado com falha de ambiente; requisito de 102 PASS não atendido.** O runner completou os 102 checks: 101 PASS, 0 PRODUCT_FAIL, 0 TEST_HARNESS_FAIL, 1 ENVIRONMENT_ERROR, 0 BASELINE_FAIL e 0 NOT_RUN. Exit observado 1, duração 2790,959 s. O único check não aprovado foi `ui-visual-quality`: retorno 124, timeout 900,026 s. Seu percurso interno ficou incompleto. Não há aprovação global ou visual por herança.

## Identidade, execução e preservação

Comparei com o primeiro FULL completo desta onda, normalizando **somente o prefixo da pasta de evidência**: 102 IDs únicos, ordem e todos os 102 argv são idênticos. Wrapper efetivo 5eada, entrada oficial `--tier full`, runtime Python isolado, Node/Chrome/baseline preservados. Nenhum caso selecionado por subset, skip ou timeout ampliado.

O preflight bruto tem `returncode=0` e corpo **PREFLIGHT PASS**, com branch `codex/dante-guia-20261024` e HEAD `a4bf278cd4dc`. Portanto, o PASS não depende apenas da linha externa do wrapper. O mapping da rodada 97957 registra pai Ts / filho Z direto, pausa 0,419864 s e destino físico scratch; `resolve`/`samefile` foram conferidos também após o fim.

**679/679 inputs congelados conferidos após a suíte e a indexação documental: nenhuma ausência ou divergência.** Build 8c127c2f92de375e, HEAD a4bf278cd4dc38bbaa5b905ed17a79e33684fb67. Runner, juiz visual original, módulos, teste calendar, memória de regressões e ACTIVE-TASK conservam os bytes testados. O patch N3 de leitura agrupada permanece apenas proposta, sem aplicação.

As seis cópias curadas de agregado, comando, log, mapping, freeze e wrapper são byte-idênticas aos originais scratch. Não foi ampliada a inspeção para payloads pesados; o inventário abaixo é presença/metadados/recibos pertinentes, não comparação exaustiva de todo arquivo gerado.

## Saídas concluídas e recortes

Os 24 destinos `full_evidence` existem no destino novo. Os 23 checks correspondentes sem a UI têm PASS / returncode 0; a pasta UI é parcial. Os JSONs de cabeçalho/resultado inspecionados não contradizem o agregado.

- Calendário padrão: 14/14 PASS; `calendar-lifecycle-320-light` exatamente 1x e `calendar-edges-320-light` preservado. O lifecycle registra close antigo com dialog open, host ativo, marcador futuro removido, preservação financeira e contraprovas de Fechar/Escape/close real com timers=0 e activeRefreshes=0.
- Recovery: 8/8 PASS e seus 5 hashes de fonte conferidos. Distribution: 4/4 PASS, sourceUnchanged=true.
- Guia: 66/66 PASS, incluindo Dante, 14 casos próprios atuais, legado/v1, formas proprietárias e distribuições. Seus 30 inputs before/after coincidem com os bytes atuais; test_sha256 atual e source_unchanged=true conferidos.

O recibo detalhado `full-relocated-independent-audit.json` conserva os 24 destinos e identidades. A revisão não refez cada oráculo dos 101 checks aprovados nem criou novos resultados por inferência.

## UI: prova parcial e localização do timeout

O tail bruto tem 12000 caracteres e começa com linha cortada. Contém **326 linhas PASS completas, 326 IDs únicos**, na mesma sequência das posições 79–404 do array de **casos executados** do focal completo. Essa ordem não deve ser confundida com a ordem de `required_case_ids`. Não há IDs inesperados. Isso não comprova 404 ou 413 PASS nesta rodada; as 78 linhas anteriores não estão disponíveis individualmente nesse tail.

O último PASS é `compact-native200-submenu-dark`. Faltam evidências dos oito `closure-native200-*` e de `coverage-missing-and-zero-rejected`. O JSON visual final não existe. Portanto, classificação final própria, cobertura 413, finished_at e mapa 160 / source_unchanged da UI são **indisponíveis nesta execução interrompida**.

Separadamente, confrontei os 160 nomes/hashes do mapa visual conhecido do focal com os bytes atuais e o freeze: 160/160 iguais, sem drift. Essa prova externa de preservação não cria um recibo visual próprio nem substitui a conclusão ausente.

Há um perfil residual `visual-native200-k_svi5m0`, sem perfil closure. Fonte e stdout estreitam a etapa para a transição após o último compacto nativo e antes do primeiro closure: `assert_fixture_requests`, `context.close`, `rmtree` e preparação seguinte. **Não é possível repartir o tempo entre essas chamadas.** O assert de fixture é síncrono; perfil/mtime não são amostra de stack. A captura review-desktop e screenshots calendar/notification são capturas normais previstas.

O focal anterior foi 413/413 PASS em 853,471 s; seus gaps após o último compacto até o primeiro closure e até o fim foram 22,558 s e 26,719 s. Ele é evidência separada e não reclassifica o FULL. O redirecionamento de saída foi efetivo e o timeout 900 se repetiu: não há conclusão causal sobre CloudDocs/I/O, travamento, CPU ou intervenção humana. A proposta de reduzir RPCs permanece A1/N3, aguardando autoridade e provas próprias.

## Histórico, limites e identidades

Manter o primeiro FULL completo 101 PASS / 1 ENV, a repetição interrompida 130 / INCOMPLETE, os dois abortos de setup (com suas classes brutas diferentes), o focal 413 PASS e esta rodada completa com ENV em entradas separadas. Nenhum histórico precisa ser sobrescrito. Critério 102 PASS, aceite humano e limites nativos/documentados permanecem pendentes. A consulta de processos sem remanescentes foi informada pelo coordenador; não foi repetida pelo revisor.

- Agregado: `059476c2ff7498e4ce62e8d2e176232355320de7bb56f51884f2ebea6cb70b02`
- Comando/exit: `3b6590506ca6ff9d7139cd7119b19dec3d6461a15a6f2f8afbe0b3b414261b8e`
- Log: `a4ce3040a1e0942618ee65b55369fc65d6c3eb1c5bb4644acb6b8122961728a9`
- Mapping: `34982b80f667f904fa22d20c06cde8876cf3eaceaa949770d006f9e5ad507b8d`
- Freeze: `11cf8e2809ac3c871a729c5533ab3a86e5ef76a08511ea069b63e0a292639b65`
- Auditoria independente: `2745c399994d7abdee502d1382b4324485188ee1ffbe999d112275a44bbe9264`

Escritas somente destes recibos/relatório em scratch. Nenhum teste, browser, sinal, fonte, contrato ou operação Git de mutação executado nesta revisão.
