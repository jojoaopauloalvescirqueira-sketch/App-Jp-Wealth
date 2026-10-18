# Revalidação parcial Ásia/Oceania/Arábia — 15/10/2026

Pesquisa somente leitura das fontes; única entrega escrita é este relatório externo. Nenhum produto/Git foi alterado. Horários locais, ações à vista regulares; feriados prevalecem sobre semana; calendário não comprova operação ao vivo ou ausência de halt. Leitura prévia: calendar-research.md, calendar-research-addendum.md e PLANO-AISOL.md. Não foram usadas bibliotecas/calendários terceiros como autoridade.

## Cobertura recomendada nesta rodada

| Venue | Cobertura defensável / condição | Próxima abertura possível após 15/10 |
|---|---|---|
| JPX | 15/10–31/12/2026, calendário anual e sessão atuais lidos | 16/10 09:00 |
| HKEX | 15/10–31/12/2026, anual lido; meios pregões devem usar sessão própria | 16/10 09:30 |
| ASX | 15/10–23/12/2026 integral; 24/12 e 31/12 somente contínuo até14:10 verificado, fases posteriores carecem tabela própria | 16/10 início em janela09:59:45–10:00 |
| SSE | 15/10–31/12/2026 para feriados; nenhuma data restante listada no anual oficial. Sessões conforme pesquisa anterior, sem revalidar seu corpo completo nesta rodada | 16/10 09:30, condicionado à regra horária anterior |
| SZSE | Aviso específico confirma retorno08/10; anual localizado mas fetch falhou. Ainda falta anual legível para selar15/10–31/12 | Não certificar contador enquanto cobertura anual não for aceita |
| NSE | 15/10–07/11/2026 recomendado até resolver Muhurat08/11 e circular SEBI15/10. Anual contém datas restantes; regra CAS atual lida | 16/10 09:15 |
| BSE | Lacuna primária operacional e anual; NÃO copiar NSE nem anúncio corporativofevereiro | Não certificar contador |
| KRX | Regra semanal e sessões confirmadas por conteúdo indexado oficial; calendário anual/horário especial19/11 pendentes. NÃO certificar ano inteiro | Pode oferecer regra prevista, mas cobertura validada ainda não fechada |
| Saudi | Calendário oficial indexado contém feriados2026 completos e nenhum após23/09; corpo fetch não passou. Regra e horários oficiais recuperados por URL com parâmetrocsrt | 18/10, abertura na janela10:00–10:00:30, se aceitar calendário oficial indexado como evidência parcial |

As datas sugeridas são inferência da regra semanal + exceções lidas, não prova de operação. Todos os contadores precisam parar na fronteira de cobertura, inclusive se a próxima abertura ficar fora dela. Os limites menores não devem impedir exibição da praça com estado de calendário pendente.

## NSE: corpo atual lido, mudanças futuras não verificadas

[NSE CAS](https://www.nseindia.com/static/products-services/closing-auction-session) — corpo HTML lido, atualizado12/08/2026. Fase1 para ações cash com derivativos disponíveis. CTS CAS termina15:15; referência/transição15:15–15:20; entrada15:20–15:25; somente limit15:25 até encerramento aleatório15:28–15:30; matching/confirmação até15:35; transição15:35–15:50; pós15:50–16:00. NãoCAS segue CTS09:15–15:30. Janela aleatória não é contínuo verde.

[NSE préabertura](https://www.nseindia.com/static/products-services/equity-market-pre-open) — conteúdo oficial indexado lido, atualizado04/09/2026; fetch direto não feito nesta rodada. Envelope09:00–09:15; todas ordens09:00–09:05; limit09:05 até encerramento aleatório09:08–09:10; matching até09:12; buffer09:12–09:15. Portanto não usar antiga entrada até09:08 universal.

[NSE CMTR71775, capital market](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf) — PDF2p corpo lido. Restantes20/10Dussehra,10/11DiwaliBalipratipada,24/11GuruNanak,25/12Christmas. Domingo08/11Muhurat será realizado, horários em circular posterior. Não substituir por feriado fechado simples nem supor horário. [Página atual de feriados](https://www.nseindia.com/resources/exchange-communication-holidays?apiversion=v2) oscilou HTML/403; conteúdo indexado oficial confirmou as datas.

[SEBI circular15/10/2026](https://www.sebi.gov.in/legal/circulars/oct-2026/review-of-certain-aspects-of-the-closing-auction-session-market-timings-and-settlement-methodology-for-derivatives-contracts_105293.html) — HTML lido: HO/47/11/11(3)2025-MRD-POD2/I/23843/2026. Anexo canônico [1792079571420.pdf](https://www.sebi.gov.in/sebi_data/attachdocs/oct-2026/1792079571420.pdf) localizado via link oficial, mas corpo NÃO lido: web fetch falhou; curl padrão semDNS; tentativa require_escalated permitida porém conexão expirou30s sem bytes. A vigência alegada por imprensa (dezembro) NÃO foi adotada como fato. Pode limitar cobertura antes da mudança até obter corpo, não alterar regra dehoje automaticamente.

## BSE: lacuna permanece após alternativa escalada

[Cash20260801-1](https://www.bseindia.com/markets/MarketInfo/DispNewNoticesCirculars.aspx?page=20260801-1), [FAQ20260728-42](https://www.bseindia.com/markets/MarketInfo/DispNewNoticesCirculars.aspx?page=20260728-42) e [anual20251212-8](https://www.bseindia.com/markets/MarketInfo/DispNewNoticesCirculars.aspx?page=20251212-8) tiveram fetch web falho. Cash foi tentada via curl require_escalated e retornou HTTP403 imediato. Não é bloqueio de autoaprovação nem confirmação de inexistência. Corpos não lidos. Reprodução por distribuidores e comunicados oficiais de LinkedIn foram localizados, mas não substituíram estas circulares nesta rodada. Transcriçãofevereiro é anúncio futuro; continua inadequada para provar funcionamento corrente. Não usar circular de derivativos como horários cash.

## JPX/TSE: corpo e anual lidos

[Regras](https://www.jpx.co.jp/english/equities/trading/domestic/04.html) confirmam Zaraba termina15:25, préfechamento15:25–15:30 somente ordens, Itayose15:30. Manhã09:00–11:30 e tarde12:30–15:25 preservadas da pesquisa anterior; link atual traz fechamento, não foi feita nova leitura da subpágina de horas. [Anual](https://www.jpx.co.jp/english/corporate/about-jpx/calendar/index.html) corpo lido lista2026 e2027. Restantes2026:03/11CultureDay,23/11LaborThanksgiving,31/12MarketHoliday; sábados/domingo fechados. Sem meio pregão nesses dias. Não extrapolar derivativos noturnos para ações.

## HKEX: corpo e anual lidos

[Sessões](https://www.hkex.com.hk/Services/Trading-hours-and-Severe-Weather-Arrangements/Trading-Hours/Securities-Market?sc_lang=en) corpo lido: pré09:00–09:30, contínuo09:30–12:00 e13:00–16:00; CAS16:00 até encerramento aleatório16:08–16:10. Meio pregão: contínuo09:30–12:00, CAS12:00 até12:08–12:10; sem tarde. Extendedmorning12–13 se restringe a instrumentos elegíveis, não ação ordinária universal.

[CT/075/25 calendário2026](https://www.hkex.com.hk/-/media/HKEX-Market/Services/Circulars-and-Notices/Participant-and-Members-Circulars/SEHK/2025/ce_SEHK_CT_075_2025.pdf) PDF2p corpo lido: restantes19/10 e25/12 fechados;24/12 e31/12 meio pregão; sábado/domingo fechados. Não tratar feriado26/12 sábado como fechamento compensatório28/12, que não está no calendário.

## SSE e SZSE

[SSE anual2026 chinês](https://www.sse.com.cn/disclosure/dealinstruc/closed/) corpo lido. Lista ano integral: anoNovo01–03/01;SpringFestival15–23/02;Qingming04–06/04;Labor01–05/05;DragonBoat19–21/06;MidAutumn25–27/09;National01–07/10, retorno08/10. Sábados de compensação civil14/02,28/02,09/05,10/10 e domingo20/09 continuam fechados. Não há feriado depois07/10 no anual. Páginainglesa ainda exibe2025; não usar essa página para certificar2026.

[SZSE aviso17/09/2026](https://investor.szse.cn/disclosure/notice/general/t20260917_622911.html) corpo indexado oficial lido confirmaNational01–07/10 e retorno08/10; fetchdireto falhou. [Anual22/12/2025](https://www.szse.cn/disclosure/notice/t20251222_618087.html) localizado por listaoficial e referência de navegação, mas fetchcorpo falhou repetidamente; não alegar leitura. Não é prudente transferir calendárioSSE como autoridadeSZSE. Horários09:15–09:25auction,09:30–11:30/13:00–14:57contínuo,14:57–15:00closing permanecem da pesquisa anterior; precisam manter essa proveniência, não marcarnova leitura integral.

## KRX/KOSPI

[KOSPI regra geral](https://global.krx.co.kr/contents/GLB/06/0602/0602010201/GLB0602010201T1.jsp) conteúdo indexado oficial lido: seg–sex; feriadosgovernamentais,1maio,31dez (ou pregãoanterior na condição indicada), dias extras declarados; regular09–15:30; préoffhours08:30–08:40; pósao fechamento15:40–16:00; after16–20. Fetchdireto403/erro; não alegar corpo HTML integral. [Aftermarket](https://global.krx.co.kr/contents/GLB/06/0602/0602010203/GLB0602010203T1.jsp) conteúdo indexado oficial lido confirma16–20, método contínuo, apenas elegíveis; fetch403. Closingcall15:20–15:30 preservado da pesquisa anterior; nesta rodada página de tipos de ordem falhou403.

[KRX calendário corporativoKOSDAQ2026](https://kind.krx.co.kr/external/dst/reference/11625/2026%20%EC%BD%94%EC%8A%A4%EB%8B%A5%EC%8B%9C%EC%9E%A5%20%EA%B3%B5%EC%8B%9C%EC%9D%BC%EC%A0%95%20%EC%BA%98%EB%A6%B0%EB%8D%94_vF.pdf) PDF28p texto lido parcialmente: páginas20/22/24 calendáriosout/nov/dez; texto dezembro contémChristmas e encerramentoanual. É fonteoficial de obrigações corporativas, não circular operacionalKOSPI. Solicitações screenshot retornaram referência sem imagem visível; não alegar inspeçãovisual. [Avisos simuladorKRX](https://strn.krx.co.kr/corebbs5/BHPSTRN0401/list) localizam fechamentooutubro, mas simulador não é autoridade autossuficiente do pregãoreal. Feriadosrestantes25/12,31/12 parecem compatíveis com regras; anualcash completo e sessãoespecial19/11/2026 não confirmados primariamente. Deve marcar19/11 desconhecido, não aplicarhora habitual ou atrasoextraído de site terceiro.

## Saudi Exchange

[Sessões oficiais](https://www.saudiexchange.sa/wps/portal/saudiexchange/rules-guidance/capital-market-overview/trading-cycle-and-times?csrt=10820450772539872392&locale=en) conteúdo completo recuperado no índice e fetchHTML379linhas. Domingo–quinta; auction09:30–10:00; contínuo10–15; closing15–15:10; tradeatlast15:10–15:20; negotiateddeals15:20–16 separado. Abertura/fechamento variam dentro30s após10:00 e15:10. Representar as janelas explicitamente, sem assumir tickexato.

[Calendário oficial](https://www.saudiexchange.sa/wps/portal/saudiexchange/about-saudi-exchange/exchange-media-centre/saudi-exchange-holiday-calendar?csrt=7290425018528260842&locale=en) conteúdo indexado oficial lido; fetchdireto falhou. ListaFounding22/02, EidFitr17–23/03 (retorno24/03), EidAdha24–28/05 (retorno31/05), National23/09; nenhum restante2026. EidAdha é assinaladoUmmAlQura. [AvisoNationalDay02/09/2026](https://www.saudiexchange.sa/wps/portal/saudiexchange/newsandreports/issuer-news/news-detail-wcm/?locale=active&newsId=9568) conteúdo indexado confirma23/09 e retorno24/09. Isso melhora lacuna anterior, mas distinguir índice lido de calendário fetchintegral. Não foi usadaSAMA como calendário da bolsa.

## ASX

[Sessões](https://www.asx.com.au/markets/market-resources/trading-hours-calendar/cash-market-trading-hours) corpo HTML lido: pré07–09:59; OSPA começa em09:59–09:59:15, buffer mínimo30s; transição contínuo09:59:45 com random15s (earliest09:59:45). Contínuo até16:00; préCSPA16–16:10; CSPA começa16:10 com random30s e termina16:11; postclose16:11–16:21:30 negociável no preçoCSPA; fasesAdjust posteriores não são contínuo normal. Janelasambíguas devem ser auction/transição, não verde certo. Não usar antiga aberturaalfabética10–10:09.

[Anual](https://www.asx.com.au/markets/market-resources/trading-hours-calendar/cash-market-trading-hours/trading-calendar) corpo lido2026/2027. Restantes2026:25/12Christmas e28/12Boxing fechados;24/12 e31/12normaltrading cessa14:10. A fonte anual não fornece horários exatosdeauction/pós nesses meios pregões; não inventar14:10–14:20 etc por deslocamento das sessõesnormais. Até obter aviso, representarapós14:10 nesses dias como calendário de fases não confirmado, ou encerrar cobertura na véspera.

## Pendências que afetam implementação

1. Obter anexo SEBI15/10 e vigência; obtercashBSE vigente e anual deBSE. Downloads escalados já tentados:SEBItimeout30s, BSE403. Semrejeição deautoaprovação.
2. Abrir anualSZSE primário; annualKOSPI e eventual aviso19/11; preservar incógnita até chegar.
3. MuhuratNSE08/11 horários e ASXmeiospregõesfases finais ainda desconhecidos. Umaexceçãoparcialnãoéfechamentototal.
4. Para os horários herdados dos dois estudos prévios, conservarproveniênciaanterior: esta rodada não é nova leitura de todas asregras. Datasfora da cobertura não recebem estadoverde nem próximoevento inventado.
