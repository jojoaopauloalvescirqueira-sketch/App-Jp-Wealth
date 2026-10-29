# Revisão independente final — pacote de controles V3

## Veredicto

AUDIT_PASS delimitado ao delta FFv3 e sua evidência focal. Pacote V3 apto a ser apresentado para autorização N3 específica. FFV2-01 está resolvido nesta identidade: o teste agora exige aviso visível antes de comparar o texto. Não houve enfraquecimento de proveniência, horário pendente ou controles adjacentes.

Isto não é autorização para aplicar, aprovação da suíte integral ou aceite humano. Os pareceres v1/v2 e os recibos anteriores permanecem históricos, sem sobrescrita. Nenhum browser, teste funcional ou escrita no repositório foi executado pelo revisor neste acompanhamento.

## Comparação de fontes

Conferi por comparação exata que FFv3 difere de FFv2 somente pela adição:

    expect(event_row.locator('.calendar-event-warning')).to_be_visible()

A linha antecede to_contain_text('Horário a confirmar.'). O fluxo CAD/USD porID exato, abertura i, detalhe único, sourceUrl exata, origem FF, horário original/fuso e recolhimento permanece. Também permanecem transporte/cache, legado semanal, concorrência, rascunho/foco/cursor, host/mês/dia e financeiro.

O pacote completo contém exatamente os mesmos cinco arquivos. Comparei as quatro seções de patch nãoFF contra o pacote37: idênticas byte a byte. Seus candidatos físicos também conservam os hashes registrados. Parsing AST do FFv3 foi executado sem importar o módulo. Nenhum delta em gates116, catálogo visual413, timeout900, tolerância2px, produto, schemas ou fontes de dados.

## Recibo nominal e contraprova

Li pipeline-and-counterproof-v3.json, log e launcher run_v3_pipeline.py. O launcher importa exatamente FFv3 e reutiliza shared_calendar_pipeline sobre os fontes reais reconstruídos, sem overlay de produto. As duas execuções nominais1440/light e390/dark registram PASS, com as duas proveniências e o aviso visível.

A contraprova injeta CSS para ocultar somente o aviso da observação SYN-primeira-CAD, preservando o texto 'Horário a confirmar.'. A mesma função falha na nova linha134, expect(...).to_be_visible(), com 'Locator expected to be visible / Actual value: hidden'. A classificação exige mensagem real, último frame pertencente ao arquivo FFv3, função shared_calendar_pipeline, linha134 e texto exato da asserção. Não pesquisa o callsite inteiro e não repete o falsoPASS anterior do launcher de contraprovas.

Resultado recebido e conferido: PASS2/2 nominais + PASS1/1 de rejeição do aviso oculto. O aviso manteve seu texto durante o estímulo; logo esta contraprova discrimina visibilidade de mera presença textual e resolve precisamente FFV2-01. Leitura de recibo é evidência da execução do autor, não execução própria.

## Identidade conferida por SHA256

- Pacote V3:7c9ca1442b18cbd5081ee2a56179a3697062637da3be119825a983d53cec9159
- FFv3:a3f3a00c5a1ff8e1059bc7eb1fd8c69870a5ecf48d1ea2020b8033503194862a
- Launcher:e369d606cb813cf27c04ddc4c4ef2e4fde2e348da1fbf2fc3005007d30558865
- Recibo:f7f5d1477825ba2d85cc2eaa89a9aa62e7ff3b013dfd944f372c8287242bca5e
- Helper preservado:35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a
- Produto JS no recibo:1e2e518bef9dccca48790f9752c48ba62619cd64c128ec87c55c6c58c779c831
- Produto CSS no recibo:f1007dfe4122ac80aa2e8260b4db91079ad5291cec5f1b2dd6ab0aa3910beb38

O recibo registra fontes antes/depois iguais. A evidência186/186 do FFv2 continua parcial/histórica para a nova identidade; não declarar que todo FFv3 ou FULL rodou a partir de dois pipelines e uma contraprova.

## Pendências e autorização

A autorização deve nomear o pacote V3/hash e os cinco arquivos, substituindo a pergunta anterior sobre37 sem presumir consentimento. Aplicação, execução do FF inteiro V3 e gates/full/distribuição/nativos/aceite humano são etapas separadas conforme o escopo autorizado.

proposal-hashes.json conserva o status de preparação 'browser NOT_RUN pending GO', anterior ao novo recibo. Deve ser interpretado como fotografia de proposta, com o recibo posterior identificado; este parecer não alterou os documentos do autor. Não é bloqueador técnico do patch, mas não usar aquela frase como estado atual da execução focal.
