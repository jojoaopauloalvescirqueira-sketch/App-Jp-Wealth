# Mudanças dos adaptadores de regressão

Autorização: o plano humano aprovado acrescenta a sétima métrica e a preferência compatível. Os fixtures financeiros `risk-oracles-v1.json` e `ledger-oracles-v1.json` permanecem intactos. Não há mudança de gate, tolerância do limite em 7x ou resultado econômico esperado.

- Cockpit: contrato V3 com máscara padrão 127; bits válidos 0 a 6; bit 128 inválido; varredura ampliada para 128 máscaras. V1 mantém os cinco bits originais e acrescenta os bits 5 e 6, exceto quando todas as métricas estavam ocultas (máscara zero). Checksum, decodificação inválida e isolamento por gráfico continuam examinados.
- Details/events: máscara padrão 127 e rascunho 123 após alternar o bit 2; os controles de visibilidade passam a 60–66. O adaptador mantém o novo evento de ciclo inativo para caracterizar as rotas antigas. Seu comportamento efetivo é verificado na suíte focal GENETRIX.
- Geometry: o adaptador encaminha o novo helper de qualidade e preserva a semântica das seis métricas anteriores. O snapshot aceita sete métricas. O layout de desktop verifica todos os sete cartões; os limites de geometria, DPI, fontes e casos estreitos são preservados.
- Panel: atalhos 1–7 e encaminhamento do formatter. O teste normaliza internamente os enums numéricos, mantendo o critério original. Nenhum assert de contexto, teclado ou transbordamento foi removido.

As primeiras falhas revelaram expectativas de seis métricas e hooks ausentes; as tentativas foram registradas antes das correções. Os testes da nova métrica estão separados. Stubs de fronteira não constituem evidência do ledger ou de execução. Os recibos distinguem regressão adaptada e validação nativa `NOT_RUN`.

- Reliability/scheduler/positions e MT5 design: arrays, hooks e globals de fronteira para a sétima métrica. Os blocos MAIN e os asserts anteriores foram comparados por AST e preservados pelo autor da interface.
- Package/page: metadados do candidato 1.17.0/MQL 1.170 e 13 novos membros explícitos (12 arquivos de código e um manual), preservando os 87 anteriores. Os critérios de arquivo determinístico, dependências declaradas e recusa de EX5 sem recibo permanecem. A contagem fixa da página também foi atualizada de 87 para 100 após a primeira tentativa falhar. Isso não constitui publicação ou integração no site em trabalho paralelo.
