# Revisão independente A0 — proposta do ciclo de vida do calendário

24/10/2026. **Somente revisão; patch não aplicado.** O produto real continua no build `2c4a3d9f65b3c664`, branch `codex/dante-guia-20261024`, HEAD `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67` mais as alterações congeladas.

## Parecer

**Não identifiquei achado bloqueante P0–P3 na proposta examinada.** O guard `if(dialog.open)return;` é o menor ajuste correto identificado para o evento antigo que alcança o mesmo host já reaberto. A regressão proposta preserva o oráculo legítimo de zero marcador e acrescenta controles de fechamento real. Parecer favorável à apresentação da proposta para decisão humana; **não autoriza aplicação e não aprova o runtime Dante inteiro**.

O principal informou FULL com 673 inputs estáveis e falha `calendar-agenda/edges/320`: esperado zero marcador em 1/nov, observado um. A comprovação de preexistência não transforma esse FULL em PASS nem afasta a falha bruta. Esta revisão não executou o FULL e não concede exceção aos gates.

## Causa e fluxo examinados

**CONFIRMADO nas fontes e consistente com os recibos lidos:**

1. `JPWCalendar.close()` (módulo19:303) captura o rascunho, desativa a instância, incrementa request e limpa o timer antes de chamar `dialog.close()`.
2. `JPWCalendar.open()` (:299–301) reativa o mesmo objeto, chama showModal, marca o ícone expandido e inicia novo refresh.
3. O listener `close` atual (:288) faz a limpeza incondicional. Quando o fechamento anterior é entregue com `dialog.open===true`, ele desativa a nova abertura, incrementa sua request, limpa seu timer e mostra aria-expanded=false enquanto o diálogo permanece aberto.
4. `invalidate/refresh` (:321 e :66–80) exclui instâncias inativas; o refresh público retorna lista vazia. A tela conserva `st.data.app` anterior e o marcador de backup fica obsoleto.
5. `backupItem` (:46–53) já recusa estado unknown e data futura. O erro não exige mudar os 30 dias, DST, o timestamp aceito ou a expectativa do marcador; exige permitir que a instância aberta reconstrua a informação.

O mini-recibo `reports/calendar-lifecycle-minirepro.json`, executado por outro agente, mostra esse estímulo no produto atual e no portátil build `1b695b809fe80c26`: host aberto, evento close observado com open=true, zero instâncias atualizadas, estado do backup unknown e um marcador obsoleto. Não rerodei essa reprodução nativa nesta revisão.

**Preservação conferida independentemente:** módulo19 e domínio19 atuais são byte-exatos HEAD; ambos aparecem integralmente no portátil protegido da base anterior ao Dante. O módulo de persistência atual também aparece integralmente nesse portátil e coincide com seu entry da base protegida. Persistência tem alterações anteriores em relação ao HEAD; não as atribuí ao Dante. Esses confrontos sustentam que o trecho causal não foi introduzido pelo delta Dante.

## Avaliação do ajuste

`product.patch` é exatamente a introdução do guard no listener close. Não altera `open`, `close`, requests, timer, atualização da agenda, domínio, persistência, formulário ou regra do backup. O guard consulta o estado atual do próprio host: um evento antigo não deve encerrar o ciclo que já reabriu.

Quando o host está fechado (`dialog.open===false`), o restante do listener é idêntico. Isso mantém o tratamento necessário de fechamento nativo direto e complementa a limpeza síncrona feita pelo botão/Escape via `close()`. Usar só a limpeza de `close()` e remover o listener deixaria o fechamento nativo direto sem essa proteção; a proposta conserva esse caminho. Não é necessário introduzir geração/token adicional para resolver a transição demonstrada: a propriedade open já diferencia o estado atual relevante do evento antigo.

Request da tentativa anterior continua invalidada pela chamada de close e pelo novo refresh; o guard não torna elegível uma resposta antiga nem introduz writer. `resetContext` e descarte continuam fechando/desativando e reconstruindo seus estados pelos caminhos originais. Uma reabertura posterior passa a preservar o estado do ciclo novo.

### Prova independente do handler, sem browser ou edição

Extraí o `ensureDialog` real de cada fonte e executei sua inscrição de listeners em VM com host, instância, timer e launcher sintéticos. A avaliação chama o handler real registrado. Resultado:

| Fonte | Estado atual do diálogo | active | request (inicial7) | Timer | aria-expanded |
|---|---|---:|---:|---|---|
| Original | aberto | false | 8 | removido | false |
| Proposta | aberto | true | 7 | preservado | true |
| Original | fechado | false | 8 | removido | false |
| Proposta | fechado | false | 8 | removido | false |

As quatro asserções passaram. Essa unidade confirma a discriminação e os efeitos do handler; **não simula a fila nativa de eventos**, cuja prova vem do replay real lido.

## Oráculos, preservação dos testes e contraprovas

Análise AST independente de `calendar_agenda_test.py` versus cópia proposta: oito funções anteriores preservadas, nenhuma removida; só `main` muda para descobrir/configurar o novo caso. Três helpers novos: lifecycle_setup, lifecycle_close_controls e lifecycle. O corpo de `edges` é idêntico, inclusive a asserção de zero marcador em 1/nov e os controles de DST, meia-noite, preferências opacas e workspace.

O novo caso exige observar um evento close nativo com o host reaberto, uma instância alcançada pelo refresh, um timer e estado expandido verdadeiro. Só então altera explicitamente o timestamp da fixture em memória, exige backup unknown e zero marcador após refresh. Confronta o estado completo com o esperado e conserva bytes persistidos. Isso diferencia a causa de apenas esconder um ponto na UI.

Os controles de botão original, Escape e fechamento nativo direto exigem host fechado, timer zero, nenhum refresh ativo e aria-expanded=false. Botão/Escape ainda exigem retorno de foco ao ícone. Um listener vazio/guard que ignore todo fechamento não satisfaria esses oráculos. A prova de id/label/title, uma SVG e alvo mínimo44×44 é observável; não comprova fidelidade visual ou aceite humano.

`quality_gate.py:34` já executa o teste existente por padrão. A adição de lifecycle à lista padrão permite sua descoberta no mesmo check calendar-agenda. Não há novo runner, remoção de caso antigo ou relaxamento de tolerância/timeout. A configuração nova de timezone/clock do main se limita ao caso lifecycle; os casos existentes conservam suas condições.

### Replay do construtor conferido, sem rerun pelo revisor

Li `replay.py`, o log bruto e `replay-receipt.json`, e confirmei seus hashes contra fonte real e cópias atuais. O replay usa navegador headless e o aplicativo real; nas rodadas GREEN troca apenas a resposta HTTP do módulo19. O build mostrado permanece o build do produto real; a fonte substituída é identificada pelo hash separado da proposta, não por um build integrado novo.

| Caso | Resultado bruto lido |
|---|---|
| RED original/regressão | PRODUCT_FAIL esperado na CAL-LIFECYCLE-01, zero instâncias depois da reabertura |
| GREEN proposto/regressão | PASS |
| Fechamentos reais na fonte original | PASS: botão, Escape e native close |
| Fechamentos reais na proposta | PASS: botão, Escape e native close |
| Corpo edges original com a fonte proposta | PASS, mantendo zero marcador |

O exit0 do replay significa que os resultados corresponderam aos esperados, **incluindo o RED**; não transforma o original em aprovado. Nenhum pageerror foi registrado nos casos. `runtimeSourceUnchanged=true` coincide com os hashes reais dos três arquivos monitorados nesta revisão.

**Limite específico:** replay instala calendar_packet em todos os contextos, inclusive lifecycle; o main permanente proposto não instala esse pacote nesse caso. Lifecycle não faz asserção sobre eventos econômicos e a mini-reprodução foi independente do feed, portanto essa diferença não refuta a causa nem bloqueia o patch. Ainda assim, o caminho exato do runner permanente `--case lifecycle` não está demonstrado por esse replay; deve ser executado no candidato autorizado, conforme já previsto na proposta. O guard não deve ser anunciado como validado integralmente pelo FULL antes disso.

## Verificações próprias e classificação

- Confronto de hashes do recibo com fonte real/cópias/patches: **PASS**.
- Comparação exata do produto: somente a introdução do guard, **PASS**.
- Comparação AST das funções do teste e inspeção de main/runner: **PASS** no recorte de preservação estrutural descrito.
- `git apply --check /private/tmp/jpw-dante-20261024/calendar-fix-proposal/proposal.patch`: **PASS**, modo de checagem, sem aplicação.
- Concatenação de product.patch + regression.patch coincide com proposal.patch: **PASS**.
- VM dos handlers reais nos estados aberto/fechado: **PASS**, quatro controles.
- Replay de browser próprio, teste headed, aplicação de patch, build novo e FULL: **NOT_RUN** por este revisor.

## Limites e integração futura

A proposta é técnica e revisável; o projeto permanece sem essa correção. Não muda schema, writer financeiro, dados reais ou a regra do backup. O risco funcional de produto é N1; a edição de teste integra control plane N3/A4 segundo AGENTS. Requer autorização específica e CHG delimitado antes de tocar o projeto. A regra que impede estender o escopo Dante é explícita: “Não misturar correções adjacentes, refatoração ampla ou mudanças financeiras com a tarefa delimitada.” Esta revisão e o GREEN em scratch não dispensam essa fronteira.

Se autorizada, a menor sequência pertinente continua a descrita no pacote: aplicar os dois arquivos delimitados, executar lifecycle/edges pelo runner real, suíte de calendário e focais de agenda/backup/guia pertinentes, registrar regressão e contexto autorizados, gerar oficialmente artefatos e repetir o FULL atual com nova identidade estável. O novo build deve identificar a fonte aplicada; os recibos atuais são históricos para os bytes atuais/proposta por route.

Safari, comportamento nativo fora do Chromium observado, fechamento por backdrop na nova regressão, layouts/temas adicionais e aceite humano não foram estabelecidos por este replay. O fluxo antigo UI já contém backdrop e rascunho; sua presença não equivale a execução atual da suíte inteira. Não ampliei a proposta para cobrir manutenção adjacente nem recomendo alterar o oráculo financeiro/backup para obter verde.

## Identidades

- Real `src/js/40-app/19-calendar-agenda.js`: `8a4c74ff81a1d39765efa4a4c1cf8fd1a6e6b5d36dd1b24d7d1c6aa83ce8a3c3`
- Real `tools/calendar_agenda_test.py`: `ae0fcc5656cf4b1d87255b06d94ae1fe5b21b9d2fc94816a55b626d2cc91c59d`
- Real `build-id.js`: `b7ddb6a2a3ad74a508663b7b6181b51e88abfc1d4426bd951c9d4be7136c1e18`
- Proposta `19-calendar-agenda.proposed.js`: `da6c6738fe5776c5c75e9728176cb47812d2c594f130f9c3025a31969870a53c`
- Proposta `calendar_agenda_test.proposed.py`: `c19fe3272601bfb6816fe4a0ed1d7b01bca04905d878a4fbba56065490181a6e`
- Proposta `product.patch`: `7d66165a2f8c8fc52d53663cff8b91d82385b7fd5cf57546b3c91f179f5d0295`
- Proposta `regression.patch`: `a32f742875b63794401c8224435a7c9450d5c707ba52d98d4076cb89612d57eb`
- Replay receipt: `04fe4aeabc3216e2ea9918c087fd15b94dcf97eb77b1cad195f5c6a2cf7c566e`

Única escrita desta revisão: este relatório em `/private/tmp/jpw-dante-20261024/reports/calendar-fix-proposal-review.md`. Não apliquei patch, alterei produto/testes, iniciei browser ou executei operação Git de mutação.
