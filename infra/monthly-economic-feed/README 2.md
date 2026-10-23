# Calendário econômico mensal — pacote público parcial

Este diretório reúne horários/datas de divulgação de fontes oficiais e gratuitas.
O pacote de outubro de 2026 cobre **o mês inteiro das famílias selecionadas**, com
passado e futuro. Não comprova um mês econômico completo das cinco moedas.
Não contém consenso, valores divulgados/anteriores, surpresa ou recomendação.

| Moeda | Conteúdo comprovado | Lacuna explícita |
|---|---|---|
| USD | 5 eventos do calendário completo da BEA no mês | BLS e Federal Reserve pendentes |
| GBP | 37 divulgações ONS de catálogo econômico selecionado; consultas publicadas, futuras e canceladas | Bank of England e publicações fora do catálogo pendentes |
| JPY | 9 eventos de seis famílias SBJ, com dia da fonte | Horário não comprovado; outras famílias e Bank of Japan pendentes |
| NZD | CPI trimestral e SPI publicados em outubro; próximo SPI anunciado para 17/11 | Exportação mensal completa Stats NZ não validada; RBNZ pendente |
| CHF | Nenhum evento redistribuído | Licença comercial gratuita de agenda oficial não comprovada |

`confirmed` é uma afirmação **da fonte/família indicada**, nunca de toda a moeda.
A lista de exclusões e as identidades selecionadas ONS estão em
`data/curation-2026-10.json`. A fonte ONS padrão devolve somente publicadas;
o levantamento consultou também `release-type=type-upcoming` e
`release-type=type-cancelled`, com 67/16/1 registros respectivamente, sem
paginação restante. Séries temporais que acompanham uma divulgação e conteúdos
fora do catálogo escolhido não viram eventos adicionais.

## Uso no app

`src/js/40-app/16-monthly-economic-data.js` é um script clássico com um único
pacote JSON embutido. Funciona offline e em HTML portátil; não acessa DOM,
rede, cache, armazenamento ou estado financeiro. Não compartilha nem duplica o
pipeline semanal ForexFactory, e nenhum dado ForexFactory foi importado.

```js
const result = window.JPWEconomicCalendar.queryRange({
  from: '2026-10-01', to: '2026-10-31',
  currencies: ['USD', 'GBP', 'JPY', 'NZD', 'CHF'],
  impacts: ['high', 'medium', 'low', 'unclassified'],
  timeZone: 'America/Sao_Paulo'
});
// {events, coverage: [...], updatedAt}
window.JPWEconomicCalendar.sources();
window.JPWEconomicCalendar.metadata();
```

- Limites inclusivos de dias civis, `YYYY-MM-DD`, sem datas normalizadas em erro.
  Fuso inválido e intervalo invertido são recusados. O padrão de fuso é UTC.
- Filtro omitido seleciona todas as opções disponíveis; `[]` seleciona nenhuma.
  Resultado vazio por filtro não altera cobertura. Moeda/mês sem pacote retorna
  cobertura `unavailable`, sem se passar por agenda vazia confirmada.
- Para `precision: instant`, `date` na resposta é o dia do usuário via `Intl`;
  `sourceDate` conserva o dia original e `at` o instante explícito. ONS usa os
  instantes UTC publicados, inclusive a mudança britânica de horário de verão.
- Para `precision: date`, `at` é `null` e o dia da fonte permanece fixo. A UI
  deve explicar “dia da fonte; horário não informado”. Nenhuma hora foi inventada
  para os calendários anuais SBJ ou para o anúncio SPI de novembro.
- CPI/SPI Stats NZ trazem `10:45am` no DOM da publicação. A normalização usa a
  convenção local do publicador, `Pacific/Auckland`, registrada como
  `timeZoneBasis`; o texto da página não traz offset numérico próprio.
- `status: scheduled` descreve o calendário; a passagem do tempo não o transforma
  em `published`. ONS informa o estado nativo e as duas páginas NZD já publicadas
  comprovam seu estado. Cancelamentos são preservados quando fornecidos.
- BEA usa `UID`, ONS usa URI, e curadorias SBJ/NZD usam família/período de
  referência como identidade. A data de divulgação não entra na identidade;
  reagendamento substitui a revisão anterior pelo mesmo ID. IDs são únicos.
- Links precisam ser HTTP(S), sem credenciais; timestamps precisam declarar
  offset; registros inválidos são recusados e sua cobertura é rebaixada a parcial.
  A API devolve cópias para impedir que consumidores alterem o pacote.
- `coverage` é um array por `currency/sourceId/month`, com status, intervalo,
  motivo, revisão e validade. Revisões confirmadas/parciais vencem em 48 horas e
  passam a `stale`; isso sinaliza necessidade de conferir a agenda, sem apagar
  os eventos históricos ou produzir dados novos. Não há atualização automática.

## Produção do pacote, sem publicação

Somente BEA possui coletor de rede instalado. O comando é explícito, fixa o
endpoint oficial, usa Python stdlib e nunca publica, agenda execução ou lê chaves.
Não acessa RBNZ. HTML de erro, feed incompleto, UID ausente e data inválida
interrompem a coleta antes de substituir o JSON existente.

```sh
python3 infra/monthly-economic-feed/collect_feed.py --month 2026-10 --fetch-bea \
  --output infra/monthly-economic-feed/data/bea-2026-10.json \
  --snapshot-output infra/monthly-economic-feed/evidence/bea-schedule.ics
```

Para reprocessar sem rede, substituir `--fetch-bea` por
`--input-bea infra/monthly-economic-feed/evidence/bea-schedule.ics`.
O timestamp de uma transformação local não é chamado de nova captura da fonte;
`capturedAt` fica nulo nesse modo. A atualização de um arquivo BEA exige revisar
as evidências e reconstruir o pacote antes de disponibilizá-lo.

Os demais dados foram curados documentalmente de fontes oficiais, com auxílio de
IA, a partir das evidências indicadas, sem alegar revisão/aceite humano. O registro
`evidence/source-captures.json` conserva URLs, método, horário de GET/leitura DOM,
SHA-256 dos bytes recebidos quando aplicável e SHA-256 do extrato armazenado.
As primeiras respostas GET Stats NZ tinham somente o shell JavaScript; foram
preservadas como tal e substituídas como evidência substantiva por leitura normal
do DOM no Chromium, sem contorno de restrição, CAPTCHA ou acesso a RBNZ.

```sh
python3 infra/monthly-economic-feed/build_package.py
python3 infra/monthly-economic-feed/build_package.py --check
PYTHONDONTWRITEBYTECODE=1 python3 tools/monthly_economic_feed_test.py
```

`build_package.py` só lê arquivos locais, verifica os hashes documentais e a
contagem completa das consultas ONS, monta o JSON canônico e substitui o bloco
marcado no modelo. Não executa coleta nem publicação. A inclusão de novo mês ou
fonte requer curadoria, licença verificada, cobertura e testes correspondentes;
não basta trocar o rótulo do mês.

## Impacto e redistribuição

Impacto é **editorial JP Wealth** (`jpw-macro-impact-v1`), autorizado para este
produto; nenhum órgão de origem atribuiu essas categorias. CPI/GDP/mercado de
trabalho UK/varejo UK e renda pessoal BEA são altos; produção, serviços, comércio,
preços ao produtor, finanças públicas, alguns rendimentos, trabalho JP, consumo
JP e SPI NZ são médios; outras famílias selecionadas são baixas. Sem uma
classificação aplicável, o contrato admite `unclassified`. Não é um sinal
operacional nem uma regra do motor Forex.

As condições e atribuições de redistribuição estão em `SOURCES-LICENSES.md` e no
catálogo retornado por `sources()`. A exibição deve manter as atribuições e links
às fontes e indicar que o conteúdo foi adaptado por JP Wealth. Imagens, logos,
conteúdo de terceiros e identidade visual dos órgãos não integram o pacote.
