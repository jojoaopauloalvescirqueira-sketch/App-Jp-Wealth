# Fontes e cobertura — 28/10/2026

A captura Forex Factory de **28/10/2026 às 17:21:55 em São Paulo** (`2026-10-28T20:21:55Z`) contém 97 observações nas nove moedas, semana 25–31/10. São 23 Alto, 10 Médio, 63 Baixo e 1 Sem classificação (`Holiday`, preservado como tipo do provedor). Isso não comprova mês econômico completo.

A curadoria nova possui 9 tópicos oficiais Fed/BoC: 7 em 28/10 e 2 decisões futuras em 9/12. Sete associações documentais explícitas unem cada tópico de outubro à observação FF correspondente, conservando as referências oficiais. Após composição: **153 registros locais = 54 oficiais anteriores + 97 FF + 9 oficiais novos − 7 associações**. São 150 registros com data em outubro, 1 em novembro e 2 em dezembro; contagem de registros não significa cobertura integral.

| Moeda | Observações FF | Base oficial preservada | Novos oficiais exclusivos | Registros compostos |
|---|---:|---:|---:|---:|
| USD | 26 | 5 | 1 | 32 |
| EUR | 25 | 0 | 0 | 25 |
| GBP | 8 | 37 | 0 | 45 |
| JPY | 12 | 9 | 0 | 21 |
| CHF | 3 | 0 | 0 | 3 |
| CAD | 7 | 0 | 1 | 8 |
| AUD | 8 | 0 | 0 | 8 |
| NZD | 5 | 3 | 0 | 8 |
| CNY | 3 | 0 | 0 | 3 |
| Total | 97 | 54 | 2 | 153 |

O pacote tem 22 descritores de fonte e 25 linhas de cobertura. Os descritores pendentes (por exemplo BLS, demais eventos Fed, BoE, BoJ, agenda NZD completa/RBNZ e agendas oficiais CHF) continuam explícitos. **CHF possui agora observações FF da semana; isso não resolve a licença ou a cobertura das agendas oficiais suíças.**

Os componentes preservados são BEA 5 registros, ONS 37, SBJ 9 e Stats NZ 3. Seus antigos prazos de revisão permanecem preservados: rótulo bruto `confirmed` de uma família não garante que sua validade continue vigente; a consulta sinaliza vencimento sem apagar eventos.

Os nove descritores FF compartilham a mesma fonte e coleta. Todos têm cobertura **parcial 25–31/10**, nunca cobertura confirmada do mês inteiro. Fed/BoC novos cobrem somente as famílias selecionadas em 28/10 e 9/12. Seis horários dos tópicos de outubro coincidem com referências oficiais confirmadas; a coletiva do BoC continua aproximada. A decisão futura FOMC conserva apenas a data anunciada, sem hora inventada.

### Proveniência e datas

- SHA256 do corpo FF recebido: `83c21ceff5cbd36553d5d478b4a910cb5e5f6e92359bf852feacdb4cefebad52`.
- Coleta FF: `2026-10-28T20:21:55Z`; referência de geração local do novo pacote: `2026-10-28T20:22:57Z`.
- Publicação/atualização nativa do provedor: **não informada**, campos nulos.
- O `updatedAt` superior da base mensal anterior continua `2026-10-23T15:52:12Z`. Ele identifica a revisão da base original, **não** a última coleta conjunta; a coleta FF atual fica em `publicFeed` e na cobertura de sua fonte.
- Fontes Fed/BoC foram consultadas normalmente em 28/10; URLs, hashes e extratos acompanham `data/official-policy-2026.json`. Não houve consulta nova nesta conferência final.

Inventário detalhado, hashes atuais e intervalos por fonte: [inventário detalhado](SOURCE-INVENTORY.json).

## Ativação e limites — texto para a entrega

> O calendário local recebeu a captura Forex Factory nas nove moedas, com origem e cobertura visíveis. O endpoint remoto padrão continua sendo o v1 preexistente, limitado a quatro moedas/Alto; esta entrega não publicou o v2 externo nem ativou cron. O coletor e o modelo de atualização a cada 30 minutos estão preparados para uma etapa separada. A validade econômica usa o instante da coleta, com aviso após duas horas, e não o instante em que o navegador baixou um arquivo antigo.
>
> A permissão FF para uso não comercial foi declarada pelo proprietário. O agente não verificou documento contratual, sublicenciamento ou direito comercial, e não converte a declaração em autorização de publicação. Falhas de consulta preservam o último conjunto válido e mostram sua idade. A exportação semanal não fornece resultado realizado, ID nativo estável, cancelamento, revisão ou precisão confiável dos horários; dados ausentes permanecem desconhecidos.

Não afirmar que o feed remoto v1 já existente foi criado, desligado ou reativado aqui. O que permaneceu não ativado nesta entrega foi a **ampliação externa v2 e seu modelo novo de publicação**. Antes de habilitar o modelo externo, conferir os dois JSONs e snapshots iniciais já versionados, autorização de publicação e alcance da permissão. Não executar essa etapa como parte da validação local.


Este inventário não comprova execução agendada, teste humano ou FULL; consultar os recibos próprios.
