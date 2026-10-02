# Parecer independente do autor de risco sobre a UI GENETRIX

Data: 2026-10-01. Estado: STATIC_REVIEW_WITH_LIMITS. Nenhum blocker material confirmado no delta da UI revisado. O achado editorial P3 foi resolvido pelo root no delta conferido abaixo; limitações nativas permanecem pendentes. Esta conclusão não aprova o Risk do próprio revisor, o Ledger ou a versão inteira.

## Independência e escopo

Revisor: agente charts_audit, autor dos componentes Risk; autor distinto da UI, com contexto compartilhado, revisão não cega. Fontes UI somente leitura. Este arquivo é o único registro escrito durante a revisão. Não houve MT5, conta, ordem, teste de negociação, alteração de fixtures ou compilação nativa.

Leitura integral do novo JPW_Genetrix_UI.mqh, Indicator, Cockpit e Panel. Nos três arquivos extensos Coordinator, Presentation e Actions, revisão do delta e de seus caminhos de integração: aceitação/invalidação de samples, coleta/publicação, orçamento, HUD, novo seletor/detalhes/Sistema, migração de preferências e rotas de eventos. Leitura auxiliar de Samples e Ledger_Bridge; os cálculos e persistência do Ledger não são aprovados por este parecer.

## Achados

1. P3 editorial, não blocker: Presentation linha 1150 mantém tooltip «Teclas 1–6: cartões», enquanto Actions linha 713 aceita 49..55 (1–7) e existem sete cartões. Ajustar para 1–7 melhora a descoberta do novo cartão. Nenhum comportamento financeiro deriva desse texto.
2. Não foi confirmado defeito material de moeda, percentual ou ciclo no delta: os valores do cartão vêm dos campos do ledger e de sua moeda, sem soma financeira na UI. O percentual informa saldo da amostra, não equity nem saldo no encerramento. A seleção usa cycle_id, símbolo/direção exatos e permanece RAM. Ausência de catálogo/seleção não produz zero fictício.
3. APIs síncronas limitam qualquer alegação de tempo: o orçamento é consultado antes de Bridge/Store, porém DatabaseOpen/ReadProjection/ReadLive/FileRead podem consumir tempo nativo. A ordenação protege a publicação anterior das seis métricas; não demonstra teto físico de 500 ms para o ciclo, despacho em 1 s, ausência de bloqueio de thread ou carga histórica grande. Essas propriedades permanecem NOT_RUN_NATIVE.

## Evidências e localizadores

- Cockpit 8–13 e 139–162: V3, sete bits; V1/V2 verificados com checksum antigo antes da migração. mask=0 permanece 0; V1 não zero ganha 96 e V2 não zero ganha 64, preservando os bits antigos/canto/densidade. Estado malformado não se aplica parcialmente. Actions 9–28 conserva objeto inválido e default temporário; 81–109 escreve apenas preferência visual V3 e verifica leitura.
- Indicator 53–58: arrays dimensionados pelo total de métricas; 218–263: seletor exige dono de UI/contexto/identidade, testa a existência do controle e resolve o ID exato antes de selecionar. 340–348: evento novo interceptado antes do handler antigo. Nenhuma chamada de armamento, OrderSend, PositionClose ou escritor de Risk/Ledger nesse delta.
- Coordinator 95–126: métrica 6 usa STATE/ledger_census sem emprestar resultado numérico do ciclo anterior; validade limitada também a observed_mono_ms + 30 s da fonte. Samples 35–59 permite STATE válido sem valor numérico e exige contexto/deadline para exibição.
- Coordinator 128–169: catálogo integral, confirmação account_key, falha invalida a disponibilidade; risco é leitura separada apenas com orçamento restante. A presença de um único ciclo permite seleção inequívoca; múltiplos exigem seleção. Não há agregação de ciclos.
- Coordinator 542–550: troca de identidade descarta os dois novos readmodels, a seleção e todos os samples. Indicator 223–229 também protege eventos contra corrida de contexto.
- Coordinator 661–665: Stop risk (sexta métrica) é aceito antes de GenetrixCollectLedger. AcceptCollection 770–780 publica as cinco originais e depois chama MonitorStopRisk. O delta não altera fórmulas/coletores das seis leituras para acomodar o ledger; a sétima usa a janela restante.
- Genetrix_UI 56–73 e 78–86: Current exige ciclo válido, histórico/custos completos, source recente e amount_valid; Partial e Historical ficam explícitos e não expõem subtotal como total atual no HUD/cartão. Percentual ausente permanece N/A, preservando somente o montante válido.
- Genetrix_UI 89–117: seleção/invalidação RAM. 145–177: envelope aceito também deve estar válido; detalhes identificam origem contábil inferida/ambígua, timestamps, saldo e limites de V11/RC.
- Presentation 1236–1269: catálogo paginado e botões mapeados por IDs estáveis; a janela pequena é protegida antes em 1162–1171. 1325–1359: detalhe data snapshot/subtotal parcial, exibe componentes projetados e flags de completude, sem tratá-los como flutuante atual nem custos ausentes como zero.
- Genetrix_UI 128–143 e Presentation 1454–1457: Sistema apresenta Supervisor somente como registro observado; stale/N/A não apresenta leverage zero, não garante executor ativo, não substitui V11, não arma nem negocia.
- Presentation 138–247, Cockpit 165–167, Actions 864–868: sete controles de visibilidade independentes. Preferência all-hidden conserva acesso ao botão Genetrix sem reexibir métricas escondidas.

## Escritas e fronteira de autoridade

O delta de ciclo/supervisor é de leitura. A UI completa já possui ações explícitas anteriores para preferências visuais, configurações/cenários Raiz N, diagnóstico e exportação; este parecer não afirma ausência total de escrita na aplicação. A nova seleção não escreve estado financeiro, não troca conta operacional, não declara GÊNESE/tese, não envia/cancela ordens e não arma o Supervisor. Nenhum estado de saúde técnica homologa a métrica, o Estatuto ou permissão de execução.

## Limites de verificação

Revisão documental/estática dos bytes abaixo. O harness jpw_genetrix_ui_test.py foi lido como desenho de cobertura (codec efetivo e slices, adapters sintéticos), mas não foi executado por este revisor e seus resultados são recibos separados do root. Nativo MQL5, gráfico, temas/DPI, template save/reload, execução de eventos reais, concorrência DB e latência permanecem NOT_RUN_NATIVE. Os três processos host do root não equivalem a três sessões MT5. O Core/Store Risk do próprio revisor não integra o veredicto independente.

## Hashes congelados antes/depois

Cada par de hashes é igual. Fontes revisadas não foram modificadas.

- `mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5`
  - Antes: `af25842c09a0efc4494607fb890d15d1ed66a291d1e36d18065263f6c4e4b06c`
  - Depois: `af25842c09a0efc4494607fb890d15d1ed66a291d1e36d18065263f6c4e4b06c`
- `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Coordinator.mqh`
  - Antes: `171ff84918db3dda9ee25801f1d53508ed3929ee8b0865a17da7ff899a668b0b`
  - Depois: `171ff84918db3dda9ee25801f1d53508ed3929ee8b0865a17da7ff899a668b0b`
- `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Presentation.mqh`
  - Antes: `7fa0cc307df67e8b95d652d69dcf06c8477bc7fffa01357c5b79ae94f8a6fe2c`
  - Depois: `7fa0cc307df67e8b95d652d69dcf06c8477bc7fffa01357c5b79ae94f8a6fe2c`
- `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh`
  - Antes: `a45c386edcbd07312aba7d4535c66d3d6102e9e120dcca44d6130bdcff610c54`
  - Depois: `a45c386edcbd07312aba7d4535c66d3d6102e9e120dcca44d6130bdcff610c54`
- `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh`
  - Antes: `25c3ebb7ca7a914341393e9af55008f4a00ccb194286670df66e9e4fc588f3fd`
  - Depois: `25c3ebb7ca7a914341393e9af55008f4a00ccb194286670df66e9e4fc588f3fd`
- `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Actions.mqh`
  - Antes: `68d64bf52f881946e06cba7fea07589126c93655f4bf63029235cb0df14ba73b`
  - Depois: `68d64bf52f881946e06cba7fea07589126c93655f4bf63029235cb0df14ba73b`
- `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_UI.mqh`
  - Antes: `8f850f5583016832bd0174de722b86565041e01e567e9c9224b8c54b9be76343`
  - Depois: `8f850f5583016832bd0174de722b86565041e01e567e9c9224b8c54b9be76343`

## Delta final — tooltip corrigido pelo root

Releitura somente do delta em Presentation:1150: «Teclas 1–7: cartões; setas: páginas; Esc: fechar.» coerente com sete métricas e handler 1..7. O achado P3 do parecer inicial está RESOLVIDO. SHA-256 atual da Presentation: `728f5e0a4c2571c461e636b7c6079e0fbf58771f7f31a411c4bd41f9e06da1c1`. A substituição inversa apenas desse texto reproduz o hash antes `7fa0cc307df67e8b95d652d69dcf06c8477bc7fffa01357c5b79ae94f8a6fe2c`; portanto não houve outro delta nesse arquivo em relação aos bytes revistos. Os seis demais hashes do escopo inicial seguem iguais. Nenhuma fonte UI foi alterada por este revisor. Mantido o escopo/documentação da revisão anterior para conteúdo inalterado. Não é aprovação nativa, do Risk ou do Ledger. O resultado UI10031 PASS informado pelo root continua sendo evidência host separada, não execução por este revisor.

## Delta focal final — membros individuais do ciclo

Estado: STATIC_DELTA_REVIEW_WITH_LIMITS; nenhum blocker material confirmado nesse delta. Autor da UI distinto do revisor, contexto compartilhado, revisão não cega. Não altera ou aprova o Risk do revisor. Nenhuma execução de caso, MT5 ou edição de produto realizada pelo revisor. O parecer anterior permanece válido para o conteúdo inalterado.

Bytes antes/depois: `JPW_Genetrix_UI.mqh` passou de `8f850f5583016832bd0174de722b86565041e01e567e9c9224b8c54b9be76343` para `1051702bc2b1dbd195f42d6efadaeb1ad6ab2ba3a5b3e3383a0fe65c352d6ca6`; `JPW_Alavancagem_Presentation.mqh` passou de `728f5e0a4c2571c461e636b7c6079e0fbf58771f7f31a411c4bd41f9e06da1c1` para `9dfd50971c0937cf1bd0ca55169437c0f963b614badebf3fe14e5eeb0c4cc48f`. A retirada apenas das duas adições (parser e bloco de detalhe dos membros) reproduziu os dois hashes anteriores; os cinco demais arquivos do escopo inicial seguem com os hashes preservados. Não houve mudança nas sete preferências, fórmulas financeiras, seleção de ciclo, contrato de samples, orçamento ou rotas de armamento.

- Genetrix_UI:58–76: o parser consome a projeção `member_identifiers` somente com `members_available`. Não consulta PositionsTotal/ticket atual, não calcula ou completa membros a partir de posições abertas. Os identificadores permanecem strings decimais, sem conversão em double, preservando IDs acima de 2^53 e até long máximo. Conteúdo ausente/malformado retira a lista; vazio conhecido só é apresentado como ciclo provisório antes da execução, não como zero histórico.
- Presentation:1359–1381: lista identificada por geração e horário UTC da publicação. O texto diz expressamente «incluindo encerradas; não são tickets atuais». Ausência de lista em codec antigo é «indisponível», sem declarar zero. A lista não redefine Current/Partial/Historical nem substitui flags de histórico/custos. Cobertura incompleta continua explicitamente incompleta; «completa» é qualificada como declaração não verificada automaticamente.
- Contrato auxiliar conferido, sem aprovação integral do Ledger: Ledger_Core:159–202 valida lista canônica ordenada, IDs únicos por geração/ciclo e presença da Gênese inferida, projeta todos os membros observados sem filtro por volume remanescente; Ledger_Store:95–118 aceita envelope v1 e v2, mas v1 mantém `members_available=false` após ClearCycle. O readmodel validado oferece a proveniência da lista; a UI não a reconstrói nem presume sua completude histórica.
- Wrap e pager existentes preservados: cada membro vai para as linhas de detalhe e a paginação geral, sem criar writer, amostra financeira ou seleção paralela. A seleção por cycle_id e contexto continua RAM; não são carregados membros de outro ciclo após a troca. A posição histórica exibida não vira referência operacional nem ordem.

O harness UI, hash `622efece36f8e305b7156a2ee3d34cacc241beb728176a5a319a125a4dce8189`, foi lido como desenho de cobertura adicional: codec antigo indisponível, IDs grandes/malformados, histórico parcial, 95 membros em wrap estreito, pager real e seleção cruzada. O resultado informado pelo autor/root (10.396 PASS, APIs de chart/store sintéticas) permanece recibo host separado. Não foi repetido por este revisor. Nativo MQL5, gráfico/DPI, template/eventos reais, banco e aceitação operacional permanecem NOT_RUN_NATIVE.
