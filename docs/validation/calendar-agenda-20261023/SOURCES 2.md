# Inventário de fontes e cobertura

Pacote local inicial, sem alimentador remoto publicado. Moedas selecionáveis: USD, GBP, JPY, NZD, CHF. Os números abaixo representam divulgações do recorte curado, não cobertura integral de cada economia.

| Moeda | Fonte | Eventos no pacote | Condição de uso registrada |
|---|---|---:|---|
| USD | [U.S. Bureau of Economic Analysis](https://www.bea.gov/news/schedule/icalendar) | 5 | [U.S. public domain](https://www.bea.gov/help/faq/147) |
| USD | [U.S. Bureau of Labor Statistics — pendente](https://www.bls.gov/schedule/) | 0 | Somente referência oficial; nenhum evento redistribuído nesta entrega |
| USD | [Federal Reserve — pendente](https://www.federalreserve.gov/newsevents/calendar.htm) | 0 | Somente referência oficial; nenhum evento redistribuído nesta entrega |
| GBP | [Office for National Statistics](https://www.ons.gov.uk/releasecalendar) | 37 | [Open Government Licence v3.0](https://www.ons.gov.uk/help/terms-conditions) |
| GBP | [Bank of England — pendente](https://www.bankofengland.co.uk/news) | 0 | Somente referência oficial; nenhum evento redistribuído nesta entrega |
| JPY | [Statistics Bureau of Japan](https://www.stat.go.jp/english/) | 9 | [Public Data License 1.0 / CC BY 4.0 compatible](https://www.stat.go.jp/english/info/riyou.html) |
| JPY | [Bank of Japan — pendente](https://www.boj.or.jp/en/) | 0 | Somente referência oficial; nenhum evento redistribuído nesta entrega |
| NZD | [Stats NZ — publicações selecionadas](https://www.stats.govt.nz/release-calendar/) | 3 | [CC BY 4.0 (Crown copyright; exceptions apply)](https://www.stats.govt.nz/about-us/copyright/) |
| NZD | [Stats NZ — calendário completo pendente](https://www.stats.govt.nz/release-calendar/) | 0 | Somente referência oficial; nenhum evento redistribuído nesta entrega |
| NZD | [Reserve Bank of New Zealand — pendente](https://www.rbnz.govt.nz/) | 0 | Somente referência oficial; nenhum evento redistribuído nesta entrega |
| CHF | [CHF — licença de agenda pendente](https://opendata.swiss/) | 0 | Somente referência oficial; nenhum evento redistribuído nesta entrega |

Total: 54 eventos; referência do pacote 2026-10-23T15:52:12Z. Classificação de impacto editorial JP Wealth. Publicação do pacote, consulta e revisão de cada fonte são campos distintos nos metadados; passagem do tempo não confirma divulgação.

BEA e ONS possuem normalização reproduzível; fontes estatísticas SBJ/StatsNZ foram curadas com evidências oficiais. BLS/Fed/RBNZ incompletos não são apresentados como cobertura geral confirmada. CHF permanece pendente e possui links oficiais; não foram obtidos calendários automatizados de RBNZ/BoE/BoJ/SNB.

Reprodução offline: `python3 infra/monthly-economic-feed/build_package.py --check`. Ver [inventário técnico e proveniência](../../../infra/monthly-economic-feed/README.md). Preferências e dados pessoais nunca entram no pacote público.
