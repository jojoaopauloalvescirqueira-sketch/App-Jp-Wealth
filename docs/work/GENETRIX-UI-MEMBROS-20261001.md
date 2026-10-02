# GENETRIX — Recibo de autoria da lista de membros

Data: 2026-10-01. Candidate: `/private/tmp/jpw-genetrix-risk-ledger-20261001`, branch `codex/genetrix-risk-ledger-20261001`, HEAD `deffc5061fe2eff3d83b6f6e742fa105ac9c5b06`.

Autoria UI, não aprovação independente da UI. Delta autorizado pelo coordenador: completar os detalhes do ciclo com identificadores individuais históricos de membros; não alterar risco, site, contabilidade, fixtures financeiros, fórmulas, preferências ou seleção de conta.

## Comportamento implementado

O ledger publica `member_identifiers` como lista canônica crescente de POSITION_IDENTIFIER e `members_available` como disponibilidade da projeção. A UI lê a lista; não a reconstrói a partir de posições atuais. Mostra identificadores observados, incluindo posições encerradas, explicitamente distintos de tickets atuais. Não deriva nem publica tickets de negociação.

Os detalhes vinculam a lista à geração e ao UTC da publicação. Cobertura histórica incompleta continua explícita: a lista observada não afirma conhecer todos os membros desde a origem. Publicação antiga sem a projeção mostra “Membros indisponíveis”, sem afirmar zero. Uma lista explicitamente disponível e vazia em ciclo provisório antes da primeira execução recebe esse estado, sem resultado financeiro zero. Dados financeiros inválidos continuam N/A.

Cada membro passa pela quebra de texto existente, incluindo identificadores longos, e pelas páginas de detalhes existentes. A navegação conserva a seleção pelo cycle_id; selecionar outro ciclo reinicia a página e mostra somente seus membros. Não houve mudança no codec V3 de preferências, nas seis métricas anteriores, em cobertura financeira, no cálculo ou nos eventos de negociação.

## Hashes do delta congelado

| Arquivo | Antes deste delta | Depois deste delta |
|---|---|---|
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_UI.mqh` | `8f850f5583016832bd0174de722b86565041e01e567e9c9224b8c54b9be76343` | `1051702bc2b1dbd195f42d6efadaeb1ad6ab2ba3a5b3e3383a0fe65c352d6ca6` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Presentation.mqh` | `728f5e0a4c2571c461e636b7c6079e0fbf58771f7f31a411c4bd41f9e06da1c1` | `9dfd50971c0937cf1bd0ca55169437c0f963b614badebf3fe14e5eeb0c4cc48f` |
| `tools/jpw_genetrix_ui_test.py` | ampliado somente para o novo contrato/observáveis | `622efece36f8e305b7156a2ee3d34cacc241beb728176a5a319a125a4dce8189` |

Consumidores de contexto consultados, sem edição neste delta: Indicator `af25842c09a0efc4494607fb890d15d1ed66a291d1e36d18065263f6c4e4b06c`; Cockpit `a45c386edcbd07312aba7d4535c66d3d6102e9e120dcca44d6130bdcff610c54`. Ledger oracle financeiro permanece `a26fe59b37edfd4dbc4d8759e87dc6a9f6ffffce74d427e950c5e2bfd434fc1f`.

## Verificações observadas

Executadas no candidate acima, com C++ host e adaptadores sintéticos de APIs/texto/gráfico. Não são compilação MQL nativa ou ensaio MT5.

| Comando | Resultado e fronteira |
|---|---|
| `python3 tools/agent_preflight.py --mode audit` | PASS; 210 alterações herdadas/conhecidas e SOURCE REVISION UNKNOWN registrados; não constitui aprovação do produto. |
| `python3 tools/agent_preflight.py --mode edit --allow-dirty` | PASS na cópia autorizada; mesma ressalva de baseline herdado. |
| `python3 tools/jpw_genetrix_ui_test.py` | 10.396 PASS / 0 FAIL. Helpers, codec V3, collector, seleção por evento, bloco real dos detalhes, wrap e paginação reais. APIs de terminal/store/gráfico são shims. |
| `python3 tools/leverage_details_event_test.py` | 77 PASS / 0 FAIL; evento real com API sintética; warning de argumento dparam não usado preservado. |
| `python3 tools/leverage_geometry_test.py` | 673 asserts MQL distribuído, 6.021 verificações host/48 viewports/192 casos de cantos, 87 casos de layout, 32 casos fonte/DPI Stops e estabilidade HUD PASS. Métricas de texto/DPI nativas NOT_RUN. |
| `python3 tools/jpw_mt5_design_test.py` | 20 PASS / 0 FAIL; foco/eventos host, interação nativa NOT_RUN. |
| `git diff --check` | PASS, sem saída. |

O focal acrescenta casos de lista antiga indisponível, disponibilidade falsa mesmo com texto residual, lista inválida, ciclo provisório sem execução, IDs decimais acima de 2^53, membros históricos encerrados, cobertura parcial, 95 membros em páginas estreitas, alcance de todas as linhas/último membro, limites anterior/próximo, preservação de amostra/montante e troca de ciclo. Os critérios anteriores continuam; nenhum fixture financeiro nem teste legado foi editado para produzir PASS.

Uma tentativa de aplicar patch falhou por contexto de teste não encontrado, sem execução de teste nessa tentativa; o patch corrigido foi aplicado e o focal passou. A remoção posterior de uma variável placeholder sem uso no builder foi seguida por nova execução focal com o hash final acima e o mesmo resultado 10.396/0. Não houve falha funcional de teste escondida ou expectativa financeira reescrita.

Nativa MQL/EX5, renderização MT5, DPI/temas/tamanhos de fonte nativos e demo permanecem NOT_RUN. O focal prova paginação com texto sintético; não prova responsividade nativa no limite máximo de registros. Revisão independente do delta fica a cargo do autor de Risk; minha autoria não a substitui. Refreeze e gates finais pertencem à integração do candidate RC2.

Rollback delimitado: restaurar os dois arquivos de apresentação ao fingerprint anterior deste delta, preservando o ledger/formatos novos e dados; a publicação antiga/sem lista continua devendo ser tratada como ausência, jamais contagem zero. Não executar rollback operacional ou apagar bancos sem autorização específica.
