# Fontes, condições e proveniência

Verificação documental: 23/10/2026; não representa parecer jurídico, autorização
dos órgãos ou licença de seus logotipos. Este pacote usa apenas metadados
textuais de divulgação e suas próprias classificações editoriais.

| Fonte | Fonte primária e regra aplicável | Aplicação no pacote |
|---|---|---|
| BEA | [ICS oficial](https://www.bea.gov/news/schedule/ics/online-calendar-subscription.ics); [documentação](https://www.bea.gov/news/schedule/icalendar); [FAQ de copyright](https://www.bea.gov/help/faq/147) | Informação do site em domínio público salvo aviso específico. Nenhum aviso diferente no calendário capturado. Atribuição: “Source: U.S. Bureau of Economic Analysis”. |
| ONS | [API oficial](https://developer.ons.gov.uk/search/search-releases/); [termos ONS](https://www.ons.gov.uk/help/terms-conditions); [OGL v3](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) | Termos ONS incluem seus feeds e reuso OGL; excluem fotos/ilustrações/vídeos de terceiros. Atribuição: “Source: Office for National Statistics, © Crown copyright 2026; adapted by JP Wealth”. |
| Statistics Bureau of Japan | [uso do site](https://www.stat.go.jp/english/info/riyou.html) | PDL1.0 permite uso comercial, cópia, transmissão e adaptação com fonte e declaração de edição; a página declara compatibilidade CC BY 4.0. Atribuição e edição estão no catálogo de fontes. Não usar símbolos/logos/mídia de terceiros. |
| Stats NZ | [copyright atual](https://www.stats.govt.nz/about-us/copyright/) | DOM verificado: conteúdo produzido pelo órgão sob CC BY 4.0 salvo aviso; copiar, distribuir e adaptar com atribuição. Exceções para fotos, gráficos, logos ou aviso específico; nenhum desses itens é utilizado como mídia neste pacote. |
| CHF | Nenhuma licença comercial gratuita de calendário oficial comprovada nesta investigação | Fonte inativa com cobertura pending, sem eventos SNB/FSO/SECO copiados. Licença de séries estatísticas não foi extrapolada para agenda. |

Para Stats NZ adaptado/em coleção, manter a atribuição indicada pelo órgão:

> This work is based on/includes Stats NZ’s data which are licensed by Stats NZ for reuse under the Creative Commons Attribution 4.0 International licence.

Acrescentar “Adapted by JP Wealth”, o link da publicação e o link da licença.
O uso da licença não substitui regras de acesso do site nem autoriza coletar
fontes que vedam automação. Em particular, **RBNZ não foi acessado por robô e
não há alegação de curadoria humana RBNZ**. BLS, Fed, BoE e BoJ são registros de
lacuna, sem reivindicação de licença ou pacote próprio nesta entrega.

## Evidências verificáveis

- `evidence/bea-schedule.ics`: bytes do feed oficial. Seu hash está em
  `data/bea-2026-10.json`, com captura, período e contagem completa (168 eventos).
- `evidence/ons-published.json`, `ons-upcoming.json`, `ons-cancelled.json`:
  respostas de intervalo 01–31/10/2026, totais 67/16/1. As URLs exatas com parâmetros
  e hashes constam em `source-captures.json`.
- `evidence/sbj-*.txt`: extratos dos seis calendários anuais oficiais e dos termos.
  Horários não foram comprovados por esses calendários; as datas são civis japonesas.
- `evidence/statsnz-*-rendered.txt`: extratos de leitura DOM pública do copyright,
  CPI, SPI e página de calendário. CPI 22/10/2026 10:45am; SPI 16/10/2026 10:45am;
  próxima SPI 17/11/2026 sem hora anunciada nessa página.
- `evidence/*-license.txt`: termos capturados BEA/ONS/SBJ. As primeiras capturas
  Stats NZ sem conteúdo são evidência do shell, não da licença nem dos eventos.
- `data/curation-2026-10.json`: decisões documentais, IDs por família/período,
  catálogo ONS selecionado/excluído e referência à evidência de cada evento.

Cada fonte SBJ/NZD pode reagendar sua publicação; o ID por família/período
permanece, e a data/instante e revisão devem ser atualizados pelo processo de
curadoria. ONS usa URI da divulgação e BEA usa UID original. Não inferir ID pela
data do calendário. As capturas não comprovam aceitação humana, atualidade
perpétua, nem que os órgãos endossam este produto.
