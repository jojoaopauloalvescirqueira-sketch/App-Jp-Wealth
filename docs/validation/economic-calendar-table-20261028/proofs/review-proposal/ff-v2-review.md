# Revisão independente — adaptação FF v2

Escopo: leitura do delta FFv2, candidato, launcher, RED reproduzido e recibos pipeline/full FF disponíveis. Nenhum browser, execução de testes ou escrita no repositório pelo revisor.

## Conclusão

A substituição da expectativa antiga de fontes sempre visíveis é legítima: a apresentação aprovada move essas fontes para o detalhe acionado pelo i. O novo teste fortalece proveniência ao conferir individualmente CAD/USD pelo ID do payload, sourceUrl exata, fonte Forex Factory, horário original e fuso, com detalhe inicialmente fechado e fechamento posterior. A comparação semanal, cache, refresh concorrente, rascunho/foco/cursor, host/dia/mês e estado financeiro permanece intacta.

A mudança de 'A confirmar' para 'Horário a confirmar.' também é legítima, mas o candidato FFv2 tem uma lacuna corrigível antes da aprovação: to_contain_text lê textContent e pode passar com aviso oculto. A expectativa anterior sobre row.inner_text() não incluiria o aviso oculto. Assim, a nova expectativa não comprova a visibilidade que o próprio retorno bothPendingTimeWarningsVisible=True afirma.

Achado FFV2-01, MEDIUM/control-plane: acrescentar expect(warning).to_be_visible() antes de to_contain_text('Horário a confirmar.'). O texto e as duas observações continuam os mesmos. Não há motivo para alterar produto ou outro teste. Até esse ajuste, AUDIT_FAIL delimitado à preservação da condição de aviso visível; não é achado de defeito do produto.

## Evidência e rastreabilidade

O RED frozen-red-1440.json conserva PRODUCT_FAIL bruto do candidato FFf66f… em shared_calendar_pipeline:121. A triagem como TEST_HARNESS_FAIL por expectativa deliberadamente superada é sustentada pelo plano e DOM capturado: links corretos existem dentro dos detalhes fechados; os avisos usam a frase aprovada. A asserção122 ainda não rodou nessa reprodução e não foi atribuída como execução observada.

pipeline-green-v2.json registra2/2PASS1440/light e390/dark com FF4e7e… e helper35ea…. ff-cache-full-v2.json disponível registra a mesma identidade; ambos permanecem evidência desse candidato, não comprovam a futura asserção de visibilidade ainda ausente. O README começa com NOT_RUN/aguardandoGO e descreve uma fase anterior; deve receber adendo quando for congelada a próxima versão, conservando a história.

Identidades lidas:
- FFv2:4e7e48980da234a642a588ecfb124914d711545075a7fbd910b20da00e91e0f4
- delta:bb063b6506c2b1e6b6f0a5e444f49b5f17f164e4b4d12f1096a93a165303a835
- pacotev2:7aab330bd73ab7d6065751d7af6c878f8e912e7bf230046420383b2c173184e8
- pipeline receipt:6fd5391d54121da8048eebf783299ba18702a51432b2f81dd4ad1f03ede89bbd
- full FF receipt:87367aadfc5a820d14ef87df474b2d608f6d3d3ba0ec236a5fcfa755801bd297
- RED receipt:a3bcda45ed39c0fe0b8cfc93e94f0a5a5dacb1990b28bc6787eb3892c047fed2

Nenhuma alteração dos outros quatro candidatos ou produto é necessária para resolver o achado. Aprovação N3 deve identificar o pacote final após a correção, pois a autorização pendente do37 não se transfere automaticamente para novos bytes. FULL integral e aceite humano permanecem separados.
