# Calendário econômico público — nove moedas e legado semanal

Este diretório prepara dois recortes do **mesmo snapshot** público do Forex
Factory: `economic-calendar.json` (v2, USD/EUR/GBP/JPY/CHF/CAD/AUD/NZD/CNY,
impactos Alto/Médio/Baixo/Sem classificação) e `ff-high-impact.json` (v1 legado,
somente USD/EUR/GBP/JPY de impacto Alto). A agenda pessoal e os dados financeiros
não são lidos, incluídos ou enviados pelo coletor.

## Fonte, permissão e ativação

O proprietário declarou possuir permissão para uso não comercial do Forex
Factory. Essa declaração é a base desta entrega local; o agente não verificou
instrumento contratual nem inferiu direito comercial, sublicenciamento ou
redistribuição pública. As [condições Forex Factory](https://www.forexfactory.com/notices)
continuam vinculadas às fontes. Publicação e ativação do novo endpoint externo
exigem decisão separada. A presença destes arquivos não ativa o alimentador.

A coleta usa apenas o [export semanal público fornecido pelo site](https://nfs.faireconomy.media/ff_calendar_thisweek.json),
com identificação verdadeira do aplicativo, sem login, cookies, proxy, CAPTCHA,
imitação de navegador ou contorno de bloqueio. Houve respostas 403 na investigação;
a captura normal posterior retornou 200. Isso não constitui garantia de acesso ou
SLA. O programa faz **um pedido**, sem repetição automática em 403/429.

O modelo de workflow local fica inativo sem a variável externa
`JPW_ECONOMIC_FEED_V2_ENABLED=true`. Ele documenta a cadência planejada de 30 minutos;
não foi publicado, disparado ou ativado nesta entrega. Antes de habilitá-lo no
repositório externo, a etapa de publicação deverá conferir que os dois JSONs e
os snapshots iniciais já estão versionados; `git diff` sozinho não detecta
arquivos inéditos. Não há contrato de limite
de requisições do provedor comprovado nesta pesquisa. A validade conservadora de
2 horas é uma regra de apresentação do JP Wealth, não SLA do Forex Factory.

## Observações e cobertura

O export só contém a semana corrente. Uma captura de25–31/10 **não** cobre o mês
inteiro, os meses anteriores nem todo evento econômico do mundo. A primeira
captura desta versão não cria retrospectivamente o histórico faltante.

- Cada coleta mantém recibo imutável com instante, SHA-256 e semana; os bytes
  idênticos são reutilizados por hash. A normalização é reproduzível sem rede.
- O pacote carrega o último estado de **cada semana**, com intervalos e indicador
  `archived`; a semana seguinte não invalida observações da semana anterior.
- No export FF não há ID estável, resultado realizado, publicação, revisão,
  cancelamento nem distinção confiável de horários provisórios. IDs do JP Wealth
  são de observação (`identityBasis: snapshot-observation`), nunca IDs nativos.
- A ausência em captura posterior fica `observationStatus: not-in-latest`,
  preservando dados e a indicação “não consta na última coleta”; não significa
  cancelamento. Mudanças de data/hora sem identidade comprovada não são ligadas
  automaticamente como reagendamento; as observações permanecem distintas.
- `impactOrigin: provider` identifica a classificação Forex Factory; o evento
  conserva seu `providerImpact`. Ausência não é convertida em impacto baixo.
- Timestamps preservam o offset original. `timeConfirmed: false` lembra que o
  export não distingue horários provisórios. Não há conversão para meia-noite
  ou inferência de publicação pela passagem do tempo.
- `collectedAt` descreve a leitura da fonte; `packagePublishedAt` é a referência
  de transformação local, explicitamente distinta de publicação remota;
  `sourcePublishedAt` e `providerUpdatedAt` permanecem nulos quando desconhecidos.
  Reprocessar arquivos locais não renova a coleta nem a validade da fonte.

## Complementos oficiais

`data/official-policy-2026.json` contém curadoria documental das famílias de
política monetária Fed/BoC em 28/10 e datas futuras anunciadas para 9/12. As fontes
foram consultadas por GET normal, com URLs, carimbos e hashes em sua proveniência.
Os extratos selecionados em `data/evidence/` são a evidência de datas/horários;
curadoria assistida por IA não é revisão ou aceite humano.

A classificação das fontes oficiais é **editorial JP Wealth**, identificada
separadamente. O encontro futuro do FOMC preserva apenas o dia anunciado; a coletiva
do BoC conserva a indicação de horário aproximado. Decisão e comunicado são dois
tópicos do mesmo anúncio, com fonte documental compartilhada. Sete associações
explícitas (`familyKey`) ligam somente os tópicos de outubro conhecidos às suas
observações FF. Não há regra genérica título+dia nem identidade FF inventada.

Fed permite conteúdo próprio em domínio público com atribuição, salvo exceções
identificadas. BoC exige atribuição, exatidão e indicação de alterações; serviços
pagos devem informar previamente que o conteúdo original é gratuito. Logos e
conteúdo terceiro têm exceções próprias. Condições e URLs acompanham as fontes.

## Comandos locais, sem publicação

```sh
# Único GET; produz v2 e v1 da mesma captura e conserva arquivo semanal.
python3 scripts/fetch_news.py --fetch-ff

# Reproduz o pacote com a fonte capturada; não acessa rede nem renova timestamps.
python3 scripts/fetch_news.py --rebuild-archives --check

# Importa uma captura autorizada com seu instante original (nunca o instante
# atual de uma simples cópia). --week-start é opcional para semana explícita.
python3 scripts/fetch_news.py --input-ff captura.json \
  --collected-at 2026-10-28T20:21:55Z
```

O CLI aceita destinos locais explícitos, referência de transformação `--as-of` e
recibo `--diagnostic-output`. A consulta de rede nunca aceita URL fornecida por
entrada. Os arquivos são validados antes da substituição; saída usa arquivo
provisório e troca individual atômica. **Não há transação atômica entre os dois
arquivos:** uma falha de disco entre trocas é reportada como falha, sem anunciar
sucesso. Não publicar saída parcial. Falhas de rede, HTTP, JSON ou validação
retornam código1 e preservam as duas últimas visões boas.

Os testes do coletor são offline, com dados sintéticos e diretórios temporários.
O aplicativo preserva o endpoint v1 existente como compatibilidade até a ativação
externa de v2; essa compatibilidade continua explicitamente parcial, quatro
moedas/Alto. O pacote local v2 funciona no build HTTP/offline/arquivo/portátil.
