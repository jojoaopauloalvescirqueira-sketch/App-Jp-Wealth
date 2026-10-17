# REF3608–4103 — batch12: cobertura parcial honesta

Leitura semântica integral da camada textual de **REF3608–3768 (161 páginas físicas)**. **REF3769–4103 (335 páginas) permanece NÃO_LIDO** neste registro. Limite de contexto impede completar496p numa só passagem; não se declara leitura do intervalo inteiro.

Fonte: corpus-fast/REF/pages.jsonl e index.json. Lotes00–09 em `/private/tmp/ref12`, cada um<=29000caracteres, expostos integralmente via ferramenta com max_output_tokens20000. Agregação de saída no lote08 truncou parte3742–3744; as três páginas foram expostas e relidas integralmente em chamada separada, reparando o corte. Demais lotes sem truncamento. Lista exata e hashes originais no ledger.

Limites: leitura textual inclui exemplos, parâmetros, avisos e rodapés; fórmulas/imagens ausentes da extração e gráficos não foram inspecionados visualmente. Código com linha horizontalmente cortada na fonte extraída não foi reconstruído. MQL/MetaEditor/MT5/EX5/StrategyTester: **NOT_RUN**. Nenhum produto, manual, harness, Git ou instrução foi alterado. Aplicações abaixo são propostas ou ausência de uso atual demonstrado, nunca normas JPW nem fatos de implementação do Stoikus.

## Conhecimento e cuidados de integração

As famílias repetem contratos escalares e arrays: NaN/error_code difere de bool/result[]. Densidade contínua não é massa discreta; valores de acumulada e quantil dependem de tail/log_mode. Mesmo que uma função devolva quatro momentos, a leitura não estabelece que eles existam em todos os parâmetros ou sejam finitos; não substituir erro por zero.

Os exemplos gráficos semeiam com GetTickCount(), geram amostras grandes e reescalam histogramas pelo pico teórico. Isso ilustra forma, não fornece teste de aderência, evidência de rentabilidade nem reprodutibilidade. Proposta futura: sementes e dados fixos, checagem dos retornos antes de ArrayMaximum, validação de limites e finitude e comparações independentes.

Erros editoriais observados: quantis array com retorno double apesar de narrativa bool; MathMoments das distribuições double versus narrativa true/false; data_count const descrito[out]; F não central com MathQuantileF e overload sem sigma; parâmetros Weibull shape/scale invertidos; vários analogs de R copiados de outras distribuições. Conferir headers e compilação nativa antes de produzir exemplo utilizável. MathArctan2 também traz ordem escalar/array diferente e regras(0,0) conflitantes.

## Registro de todos os IDs que cruzam3608–4103

Entradas NÃO_LIDO são filas explícitas; títulos/limites vêm apenas do catálogo e não são síntese semântica. Pais maiores são parciais mesmo quando toda a interseção local foi lida.

### REF-0001 — MQL5 Reference

Catálogo PDF74–7284; texto lido neste registro:3608–3768; status:PARTIAL_FULL_TEXT_READ.

Contêiner geral: leitura somente da interseção3608–3768; não cobre o restante do livro. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1136 — Standard Library

Catálogo PDF3484–7007; texto lido neste registro:3608–3768; status:PARTIAL_FULL_TEXT_READ.

Biblioteca padrão: interseção estatística e funções auxiliares aqui lida; nenhuma conclusão sobre demais classes ainda não lidas. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1137 — Mathematics

Catálogo PDF3485–3935; texto lido neste registro:3608–3768; status:PARTIAL_FULL_TEXT_READ.

Matemática: nesta interseção há famílias de distribuições e início de Subfunctions; não há prova de leitura das partes posteriores. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1138 — Statistics

Catálogo PDF3486–3843; texto lido neste registro:3608–3768; status:PARTIAL_FULL_TEXT_READ.

Estatística: densidades/massas, acumuladas, quantis, geradores e momentos; distinguir escalar NaN/erro de arrays bool e não assumir aderência dos dados de mercado. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1202 — Noncentral F-distribution

Catálogo PDF3606–3617; texto lido neste registro:3608–3617; status:PARTIAL_FULL_TEXT_READ.

Somente3608–3617: final de exemplo/histograma e contratos F não central. Histograma usa centros, exige cells>1 e size>=cells*10, evita largura zero e limita bin superior. Início3606–3607 fica fora desta leitura. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1203 — MathProbabilityDensityNoncentralF

Catálogo PDF3610–3611; texto lido neste registro:3610–3611; status:FULL_TEXT_READ.

Densidade da distribuição F não central; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: nu1 e nu2 são graus de liberdade; sigma é não centralidade. Pesquisa futura de razões de variâncias sob hipótese explícita; sem uso atual demonstrado.

### REF-1204 — MathCumulativeDistributionNoncentralF

Catálogo PDF3612–3613; texto lido neste registro:3612–3613; status:FULL_TEXT_READ.

Acumulada F não central; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: nu1 e nu2 são graus de liberdade; sigma é não centralidade. Pesquisa futura de razões de variâncias sob hipótese explícita; sem uso atual demonstrado.

### REF-1205 — MathQuantileNoncentralF

Catálogo PDF3614–3615; texto lido neste registro:3614–3615; status:FULL_TEXT_READ.

Inversa da acumulada F não central; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência; catálogo MathQuantileNoncentralF contrasta com título/protótipos MathQuantileF e última assinatura sem sigma. Parâmetros: nu1 e nu2 são graus de liberdade; sigma é não centralidade. Pesquisa futura de razões de variâncias sob hipótese explícita; sem uso atual demonstrado.

### REF-1206 — MathRandomNoncentralF

Catálogo PDF3616–3616; texto lido neste registro:3616–3616; status:FULL_TEXT_READ.

Gerador pseudoaleatório F não central; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: nu1 e nu2 são graus de liberdade; sigma é não centralidade. Pesquisa futura de razões de variâncias sob hipótese explícita; sem uso atual demonstrado.

### REF-1207 — MathMomentsNoncentralF

Catálogo PDF3617–3617; texto lido neste registro:3617–3617; status:FULL_TEXT_READ.

Quatro momentos teóricos F não central, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: nu1 e nu2 são graus de liberdade; sigma é não centralidade. Pesquisa futura de razões de variâncias sob hipótese explícita; sem uso atual demonstrado.

### REF-1208 — T-distribution

Catálogo PDF3618–3629; texto lido neste registro:3618–3629; status:FULL_TEXT_READ.

Família t com nu; exemplo nu=10, milhão de amostras e51bins, MathSrand(GetTickCount()). Curva e histograma escalados por máximos, não teste de aderência; erros de geração/histograma não são checados antes do uso. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1209 — MathProbabilityDensityT

Catálogo PDF3622–3623; texto lido neste registro:3622–3623; status:FULL_TEXT_READ.

Densidade da distribuição t de Student; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: nu é graus de liberdade. Pesquisa futura de distribuições e quantis sob hipótese testada; sem uso atual demonstrado.

### REF-1210 — MathCumulativeDistributionT

Catálogo PDF3624–3625; texto lido neste registro:3624–3625; status:FULL_TEXT_READ.

Acumulada t de Student; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: nu é graus de liberdade. Pesquisa futura de distribuições e quantis sob hipótese testada; sem uso atual demonstrado.

### REF-1211 — MathQuantileT

Catálogo PDF3626–3627; texto lido neste registro:3626–3627; status:FULL_TEXT_READ.

Inversa da acumulada t de Student; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: nu é graus de liberdade. Pesquisa futura de distribuições e quantis sob hipótese testada; sem uso atual demonstrado.

### REF-1212 — MathRandomT

Catálogo PDF3628–3628; texto lido neste registro:3628–3628; status:FULL_TEXT_READ.

Gerador pseudoaleatório t de Student; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: nu é graus de liberdade. Pesquisa futura de distribuições e quantis sob hipótese testada; sem uso atual demonstrado.

### REF-1213 — MathMomentsT

Catálogo PDF3629–3629; texto lido neste registro:3629–3629; status:FULL_TEXT_READ.

Quatro momentos teóricos t de Student, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: nu é graus de liberdade. Pesquisa futura de distribuições e quantis sob hipótese testada; sem uso atual demonstrado.

### REF-1214 — Noncentral t-distribution

Catálogo PDF3630–3641; texto lido neste registro:3630–3641; status:FULL_TEXT_READ.

Família t não central com nu/delta; exemplo30/5, milhão de amostras51bins; reutiliza escala por máximos e guards do histograma. Não transforma demonstração gráfica em inferência de mercado. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1215 — MathProbabilityDensityNoncentralT

Catálogo PDF3634–3635; texto lido neste registro:3634–3635; status:FULL_TEXT_READ.

Densidade da distribuição t não central; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: nu é graus de liberdade; delta é não centralidade. Pesquisa futura de testes sob alternativas especificadas; sem uso atual demonstrado.

### REF-1216 — MathCumulativeDistributionNoncentralT

Catálogo PDF3636–3637; texto lido neste registro:3636–3637; status:FULL_TEXT_READ.

Acumulada t não central; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: nu é graus de liberdade; delta é não centralidade. Pesquisa futura de testes sob alternativas especificadas; sem uso atual demonstrado.

### REF-1217 — MathQuantileNoncentralT

Catálogo PDF3638–3639; texto lido neste registro:3638–3639; status:FULL_TEXT_READ.

Inversa da acumulada t não central; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: nu é graus de liberdade; delta é não centralidade. Pesquisa futura de testes sob alternativas especificadas; sem uso atual demonstrado.

### REF-1218 — MathRandomNoncentralT

Catálogo PDF3640–3640; texto lido neste registro:3640–3640; status:FULL_TEXT_READ.

Gerador pseudoaleatório t não central; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: nu é graus de liberdade; delta é não centralidade. Pesquisa futura de testes sob alternativas especificadas; sem uso atual demonstrado.

### REF-1219 — MathMomentsNoncentralT

Catálogo PDF3641–3641; texto lido neste registro:3641–3641; status:FULL_TEXT_READ.

Quatro momentos teóricos t não central, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: nu é graus de liberdade; delta é não centralidade. Pesquisa futura de testes sob alternativas especificadas; sem uso atual demonstrado.

### REF-1220 — Logistic distribution

Catálogo PDF3642–3653; texto lido neste registro:3642–3653; status:FULL_TEXT_READ.

Família logística mu/sigma; exemplo6/2, milhão de amostras51bins, eixoY fixado0…theor_max. Operação de distribuição não equivale a regressão logística. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1221 — MathProbabilityDensityLogistic

Catálogo PDF3646–3647; texto lido neste registro:3646–3647; status:FULL_TEXT_READ.

Densidade da distribuição logística; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: mu é localização denominada mean e sigma é escala. Pesquisa futura de distribuição de dados; não equivale a regressão logística nem modelo ML atual.

### REF-1222 — MathCumulativeDistributionLogistic

Catálogo PDF3648–3649; texto lido neste registro:3648–3649; status:FULL_TEXT_READ.

Acumulada logística; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: mu é localização denominada mean e sigma é escala. Pesquisa futura de distribuição de dados; não equivale a regressão logística nem modelo ML atual.

### REF-1223 — MathQuantileLogistic

Catálogo PDF3650–3651; texto lido neste registro:3650–3651; status:FULL_TEXT_READ.

Inversa da acumulada logística; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: mu é localização denominada mean e sigma é escala. Pesquisa futura de distribuição de dados; não equivale a regressão logística nem modelo ML atual.

### REF-1224 — MathRandomLogistic

Catálogo PDF3652–3652; texto lido neste registro:3652–3652; status:FULL_TEXT_READ.

Gerador pseudoaleatório logística; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: mu é localização denominada mean e sigma é escala. Pesquisa futura de distribuição de dados; não equivale a regressão logística nem modelo ML atual.

### REF-1225 — MathMomentsLogistic

Catálogo PDF3653–3653; texto lido neste registro:3653–3653; status:FULL_TEXT_READ.

Quatro momentos teóricos logística, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: mu é localização denominada mean e sigma é escala. Pesquisa futura de distribuição de dados; não equivale a regressão logística nem modelo ML atual.

### REF-1226 — Cauchy distribution

Catálogo PDF3654–3665; texto lido neste registro:3654–3665; status:FULL_TEXT_READ.

Família Cauchy a/b; exemplo-2/1 e milhão de amostras51bins. Calculador imprime extremos e depois força min=-20/max=20, usa MathRound e só conta índices válidos: extremos são descartados. Gráfico recortado não valida caudas nem momentos. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1227 — MathProbabilityDensityCauchy

Catálogo PDF3658–3659; texto lido neste registro:3658–3659; status:FULL_TEXT_READ.

Densidade da distribuição Cauchy; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: a é denominado mean na documentação e b é escala; essa nomenclatura não estabelece existência de média teórica. Pesquisa futura de cenários de caudas; não converter a em média amostral nem presumir momentos finitos.

### REF-1228 — MathCumulativeDistributionCauchy

Catálogo PDF3660–3661; texto lido neste registro:3660–3661; status:FULL_TEXT_READ.

Acumulada Cauchy; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: a é denominado mean na documentação e b é escala; essa nomenclatura não estabelece existência de média teórica. Pesquisa futura de cenários de caudas; não converter a em média amostral nem presumir momentos finitos.

### REF-1229 — MathQuantileCauchy

Catálogo PDF3662–3663; texto lido neste registro:3662–3663; status:FULL_TEXT_READ.

Inversa da acumulada Cauchy; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: a é denominado mean na documentação e b é escala; essa nomenclatura não estabelece existência de média teórica. Pesquisa futura de cenários de caudas; não converter a em média amostral nem presumir momentos finitos.

### REF-1230 — MathRandomCauchy

Catálogo PDF3664–3664; texto lido neste registro:3664–3664; status:FULL_TEXT_READ.

Gerador pseudoaleatório Cauchy; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: a é denominado mean na documentação e b é escala; essa nomenclatura não estabelece existência de média teórica. Pesquisa futura de cenários de caudas; não converter a em média amostral nem presumir momentos finitos.

### REF-1231 — MathMomentsCauchy

Catálogo PDF3665–3665; texto lido neste registro:3665–3665; status:FULL_TEXT_READ.

Quatro momentos teóricos Cauchy, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: a é denominado mean na documentação e b é escala; essa nomenclatura não estabelece existência de média teórica. Pesquisa futura de cenários de caudas; não converter a em média amostral nem presumir momentos finitos.

### REF-1232 — Uniform distribution

Catálogo PDF3666–3677; texto lido neste registro:3666–3677; status:FULL_TEXT_READ.

Uniforme com limites a/b; exemplo0…10, milhão de amostras51bins. Histograma usa centros e limita máximo no último bin; escala por pico não é densidade estimada por contagem/(n*largura). Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1233 — MathProbabilityDensityUniform

Catálogo PDF3670–3671; texto lido neste registro:3670–3671; status:FULL_TEXT_READ.

Densidade da distribuição uniforme; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: a é limite inferior e b é limite superior. Proposta de dados sintéticos limitados para testes, com limites e semente fixados; não é política de risco JPW.

### REF-1234 — MathCumulativeDistributionUniform

Catálogo PDF3672–3673; texto lido neste registro:3672–3673; status:FULL_TEXT_READ.

Acumulada uniforme; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: a é limite inferior e b é limite superior. Proposta de dados sintéticos limitados para testes, com limites e semente fixados; não é política de risco JPW.

### REF-1235 — MathQuantileUniform

Catálogo PDF3674–3675; texto lido neste registro:3674–3675; status:FULL_TEXT_READ.

Inversa da acumulada uniforme; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: a é limite inferior e b é limite superior. Proposta de dados sintéticos limitados para testes, com limites e semente fixados; não é política de risco JPW.

### REF-1236 — MathRandomUniform

Catálogo PDF3676–3676; texto lido neste registro:3676–3676; status:FULL_TEXT_READ.

Gerador pseudoaleatório uniforme; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: a é limite inferior e b é limite superior. Proposta de dados sintéticos limitados para testes, com limites e semente fixados; não é política de risco JPW.

### REF-1237 — MathMomentsUniform

Catálogo PDF3677–3677; texto lido neste registro:3677–3677; status:FULL_TEXT_READ.

Quatro momentos teóricos uniforme, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: a é limite inferior e b é limite superior. Proposta de dados sintéticos limitados para testes, com limites e semente fixados; não é política de risco JPW.

### REF-1238 — Weibull distribution

Catálogo PDF3678–3689; texto lido neste registro:3678–3689; status:FULL_TEXT_READ.

Weibull a/b; exemplo1/5, milhão de amostras51bins, eixoX min…max. Histograma descreve centros mas usa min+i*width(limites inferiores); parâmetros shape/scale contraditórios nas listas exigem verificação de header. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1239 — MathProbabilityDensityWeibull

Catálogo PDF3682–3683; texto lido neste registro:3682–3683; status:FULL_TEXT_READ.

Densidade da distribuição Weibull; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: protótipos indicam a=shape e b=scale, mas listas Parameters trocam os papéis. Pesquisa futura de durações, condicionada a conferir os headers e testar parâmetros assimétricos; sem uso atual demonstrado.

### REF-1240 — MathCumulativeDistributionWeibull

Catálogo PDF3684–3685; texto lido neste registro:3684–3685; status:FULL_TEXT_READ.

Acumulada Weibull; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: protótipos indicam a=shape e b=scale, mas listas Parameters trocam os papéis. Pesquisa futura de durações, condicionada a conferir os headers e testar parâmetros assimétricos; sem uso atual demonstrado.

### REF-1241 — MathQuantileWeibull

Catálogo PDF3686–3687; texto lido neste registro:3686–3687; status:FULL_TEXT_READ.

Inversa da acumulada Weibull; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: protótipos indicam a=shape e b=scale, mas listas Parameters trocam os papéis. Pesquisa futura de durações, condicionada a conferir os headers e testar parâmetros assimétricos; sem uso atual demonstrado.

### REF-1242 — MathRandomWeibull

Catálogo PDF3688–3688; texto lido neste registro:3688–3688; status:FULL_TEXT_READ.

Gerador pseudoaleatório Weibull; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: protótipos indicam a=shape e b=scale, mas listas Parameters trocam os papéis. Pesquisa futura de durações, condicionada a conferir os headers e testar parâmetros assimétricos; sem uso atual demonstrado.

### REF-1243 — MathMomentsWeibull

Catálogo PDF3689–3689; texto lido neste registro:3689–3689; status:FULL_TEXT_READ.

Quatro momentos teóricos Weibull, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: protótipos indicam a=shape e b=scale, mas listas Parameters trocam os papéis. Pesquisa futura de durações, condicionada a conferir os headers e testar parâmetros assimétricos; sem uso atual demonstrado.

### REF-1244 — Binomial distribution

Catálogo PDF3690–3700; texto lido neste registro:3690–3700; status:FULL_TEXT_READ.

Binomial n/p; exemplo40/0.75, milhão de amostras20bins; curva teórica em inteiros0…n e LinesSmooth(true), enquanto bins têm largura amostral. Suavização não torna variável contínua; normalização é por pico. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1245 — MathProbabilityDensityBinomial

Catálogo PDF3693–3694; texto lido neste registro:3693–3694; status:FULL_TEXT_READ.

Massa de probabilidade da distribuição binomial; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: n é número de testes e p é probabilidade por teste. Pesquisa futura de contagens de sucesso, sem interpretar acerto como rentabilidade ou norma JPW.

### REF-1246 — MathCumulativeDistributionBinomial

Catálogo PDF3695–3696; texto lido neste registro:3695–3696; status:FULL_TEXT_READ.

Acumulada binomial; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: n é número de testes e p é probabilidade por teste. Pesquisa futura de contagens de sucesso, sem interpretar acerto como rentabilidade ou norma JPW.

### REF-1247 — MathQuantileBinomial

Catálogo PDF3697–3698; texto lido neste registro:3697–3698; status:FULL_TEXT_READ.

Inversa da acumulada binomial; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: n é número de testes e p é probabilidade por teste. Pesquisa futura de contagens de sucesso, sem interpretar acerto como rentabilidade ou norma JPW.

### REF-1248 — MathRandomBinomial

Catálogo PDF3699–3699; texto lido neste registro:3699–3699; status:FULL_TEXT_READ.

Gerador pseudoaleatório binomial; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: n é número de testes e p é probabilidade por teste. Pesquisa futura de contagens de sucesso, sem interpretar acerto como rentabilidade ou norma JPW.

### REF-1249 — MathMomentsBinomial

Catálogo PDF3700–3700; texto lido neste registro:3700–3700; status:FULL_TEXT_READ.

Quatro momentos teóricos binomial, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: n é número de testes e p é probabilidade por teste. Pesquisa futura de contagens de sucesso, sem interpretar acerto como rentabilidade ou norma JPW.

### REF-1250 — Negative binomial distribution

Catálogo PDF3701–3711; texto lido neste registro:3701–3711; status:FULL_TEXT_READ.

Binomial negativa r/p; exemplo usa n_par=40 rotulado número de testes, enquanto contratos dizem número de sucessos. Gera milhão de amostras19bins e curva0…n_par; não tomar esse limite gráfico como suporte completo. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1251 — MathProbabilityDensityNegativeBinomial

Catálogo PDF3704–3705; texto lido neste registro:3704–3705; status:FULL_TEXT_READ.

Massa de probabilidade da distribuição binomial negativa; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: r é número de sucessos e p é probabilidade de sucesso; x é inteiro. Pesquisa futura de contagens sob parâmetro explicitamente definido; sem uso atual demonstrado.

### REF-1252 — MathCumulativeDistributionNegativeBinomial

Catálogo PDF3706–3707; texto lido neste registro:3706–3707; status:FULL_TEXT_READ.

Acumulada binomial negativa; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: r é número de sucessos e p é probabilidade de sucesso; x é inteiro. Pesquisa futura de contagens sob parâmetro explicitamente definido; sem uso atual demonstrado.

### REF-1253 — MathQuantileNegativeBinomial

Catálogo PDF3708–3709; texto lido neste registro:3708–3709; status:FULL_TEXT_READ.

Inversa da acumulada binomial negativa; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: r é número de sucessos e p é probabilidade de sucesso; x é inteiro. Pesquisa futura de contagens sob parâmetro explicitamente definido; sem uso atual demonstrado.

### REF-1254 — MathRandomNegativeBinomial

Catálogo PDF3710–3710; texto lido neste registro:3710–3710; status:FULL_TEXT_READ.

Gerador pseudoaleatório binomial negativa; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: r é número de sucessos e p é probabilidade de sucesso; x é inteiro. Pesquisa futura de contagens sob parâmetro explicitamente definido; sem uso atual demonstrado.

### REF-1255 — MathMomentsNegativeBinomial

Catálogo PDF3711–3711; texto lido neste registro:3711–3711; status:FULL_TEXT_READ.

Quatro momentos teóricos binomial negativa, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: r é número de sucessos e p é probabilidade de sucesso; x é inteiro. Pesquisa futura de contagens sob parâmetro explicitamente definido; sem uso atual demonstrado.

### REF-1256 — Geometric distribution

Catálogo PDF3712–3723; texto lido neste registro:3712–3723; status:FULL_TEXT_READ.

Geométrica p; exemplo0.2, milhão de amostras47bins, curva0…ncells. Histograma usa limites inferiores apesar de comentário centros; código gera step mas sequência usa passo1. Convenção de contagem precisa ser conferida antes de aplicação. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1257 — MathProbabilityDensityGeometric

Catálogo PDF3716–3717; texto lido neste registro:3716–3717; status:FULL_TEXT_READ.

Massa de probabilidade da distribuição geométrica; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: p é probabilidade de evento em um teste e x é inteiro. Pesquisa futura de espera em contagens, exigindo validar convenção zero/um no header; sem uso atual demonstrado.

### REF-1258 — MathCumulativeDistributionGeometric

Catálogo PDF3718–3719; texto lido neste registro:3718–3719; status:FULL_TEXT_READ.

Acumulada geométrica; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: p é probabilidade de evento em um teste e x é inteiro. Pesquisa futura de espera em contagens, exigindo validar convenção zero/um no header; sem uso atual demonstrado.

### REF-1259 — MathQuantileGeometric

Catálogo PDF3720–3721; texto lido neste registro:3720–3721; status:FULL_TEXT_READ.

Inversa da acumulada geométrica; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: p é probabilidade de evento em um teste e x é inteiro. Pesquisa futura de espera em contagens, exigindo validar convenção zero/um no header; sem uso atual demonstrado.

### REF-1260 — MathRandomGeometric

Catálogo PDF3722–3722; texto lido neste registro:3722–3722; status:FULL_TEXT_READ.

Gerador pseudoaleatório geométrica; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: p é probabilidade de evento em um teste e x é inteiro. Pesquisa futura de espera em contagens, exigindo validar convenção zero/um no header; sem uso atual demonstrado.

### REF-1261 — MathMomentsGeometric

Catálogo PDF3723–3723; texto lido neste registro:3723–3723; status:FULL_TEXT_READ.

Quatro momentos teóricos geométrica, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: p é probabilidade de evento em um teste e x é inteiro. Pesquisa futura de espera em contagens, exigindo validar convenção zero/um no header; sem uso atual demonstrado.

### REF-1262 — Hypergeometric distribution

Catálogo PDF3724–3735; texto lido neste registro:3724–3735; status:FULL_TEXT_READ.

Hipergeométrica m/k/n; exemplo60/30/30, milhão de amostras15bins, curva0…n, suavizada. Contratos especificam inteiros em parâmetros double; não misturar número de objetos e retiradas. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1263 — MathProbabilityDensityHypergeometric

Catálogo PDF3728–3729; texto lido neste registro:3728–3729; status:FULL_TEXT_READ.

Massa de probabilidade da distribuição hipergeométrica; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: m é total de objetos, k os que têm característica desejada, n o número de retiradas; todos são inteiros ainda que parâmetros double. Pesquisa futura com população finita e contagens identificadas; sem uso atual demonstrado.

### REF-1264 — MathCumulativeDistributionHypergeometric

Catálogo PDF3730–3731; texto lido neste registro:3730–3731; status:FULL_TEXT_READ.

Acumulada hipergeométrica; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: m é total de objetos, k os que têm característica desejada, n o número de retiradas; todos são inteiros ainda que parâmetros double. Pesquisa futura com população finita e contagens identificadas; sem uso atual demonstrado.

### REF-1265 — MathQuantileHypergeometric

Catálogo PDF3732–3733; texto lido neste registro:3732–3733; status:FULL_TEXT_READ.

Inversa da acumulada hipergeométrica; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: m é total de objetos, k os que têm característica desejada, n o número de retiradas; todos são inteiros ainda que parâmetros double. Pesquisa futura com população finita e contagens identificadas; sem uso atual demonstrado.

### REF-1266 — MathRandomHypergeometric

Catálogo PDF3734–3734; texto lido neste registro:3734–3734; status:FULL_TEXT_READ.

Gerador pseudoaleatório hipergeométrica; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: m é total de objetos, k os que têm característica desejada, n o número de retiradas; todos são inteiros ainda que parâmetros double. Pesquisa futura com população finita e contagens identificadas; sem uso atual demonstrado.

### REF-1267 — MathMomentsHypergeometric

Catálogo PDF3735–3735; texto lido neste registro:3735–3735; status:FULL_TEXT_READ.

Quatro momentos teóricos hipergeométrica, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: m é total de objetos, k os que têm característica desejada, n o número de retiradas; todos são inteiros ainda que parâmetros double. Pesquisa futura com população finita e contagens identificadas; sem uso atual demonstrado.

### REF-1268 — Poisson distribution

Catálogo PDF3736–3747; texto lido neste registro:3736–3747; status:FULL_TEXT_READ.

Poisson lambda; exemplo10 com100mil amostras13bins, sequência inteira0…ceil(max), eixoY0…NormalizeDouble(theor_max,2). Escala por máximos e curva suavizada são visualização; nenhum resultado executado foi comprovado. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1269 — MathProbabilityDensityPoisson

Catálogo PDF3740–3741; texto lido neste registro:3740–3741; status:FULL_TEXT_READ.

Massa de probabilidade da distribuição Poisson; log_mode=true devolve log natural; escalar double com error_code retorna NaN em erro e arrays bool escrevem result[]. Parâmetros: lambda é parâmetro de média e x é inteiro. Pesquisa futura de contagens por janela; janela e adequação dos dados precisam de justificativa; sem uso atual demonstrado.

### REF-1270 — MathCumulativeDistributionPoisson

Catálogo PDF3742–3743; texto lido neste registro:3742–3743; status:FULL_TEXT_READ.

Acumulada Poisson; tail=true calcula probabilidade de variável não exceder x; log_mode devolve log natural da probabilidade; escalar double/NaN com error_code e arrays bool com saída result[]. Parâmetros: lambda é parâmetro de média e x é inteiro. Pesquisa futura de contagens por janela; janela e adequação dos dados precisam de justificativa; sem uso atual demonstrado.

### REF-1271 — MathQuantilePoisson

Catálogo PDF3744–3745; texto lido neste registro:3744–3745; status:FULL_TEXT_READ.

Inversa da acumulada Poisson; tail=false usa1-probabilidade e log_mode=true interpreta Exp(probabilidade); overload array com flags aparece double apesar de narrativa false, exigindo conferência. Parâmetros: lambda é parâmetro de média e x é inteiro. Pesquisa futura de contagens por janela; janela e adequação dos dados precisam de justificativa; sem uso atual demonstrado.

### REF-1272 — MathRandomPoisson

Catálogo PDF3746–3746; texto lido neste registro:3746–3746; status:FULL_TEXT_READ.

Gerador pseudoaleatório Poisson; versão escalar double/NaN com error_code, versão array bool com data_count e result[]; data_count é const entrada apesar de rotulado[out]. Parâmetros: lambda é parâmetro de média e x é inteiro. Pesquisa futura de contagens por janela; janela e adequação dos dados precisam de justificativa; sem uso atual demonstrado.

### REF-1273 — MathMomentsPoisson

Catálogo PDF3747–3747; texto lido neste registro:3747–3747; status:FULL_TEXT_READ.

Quatro momentos teóricos Poisson, saídas mean/variance/skewness/kurtosis e error_code; protótipo double contradiz retorno narrado true/false. Parâmetros: lambda é parâmetro de média e x é inteiro. Pesquisa futura de contagens por janela; janela e adequação dos dados precisam de justificativa; sem uso atual demonstrado.

### REF-1274 — Subfunctions

Catálogo PDF3748–3843; texto lido neste registro:3748–3768; status:PARTIAL_FULL_TEXT_READ.

Leitura parcial3748–3768: catálogo3748–3752 lista subfunções de operações, sequências, ordenação, bits, cumulativas, trigonometria, estatísticas, correlações e empíricas. Só contratos3753–3768 foram lidos aqui; mera aparição de função no catálogo não cobre sua seção detalhada. Aplicação Stoikus: proposta de pesquisa; sem uso atual demonstrado por esta leitura.

### REF-1275 — MathRandomNonZero

Catálogo PDF3753–3753; texto lido neste registro:3753–3753; status:FULL_TEXT_READ.

Retorna double aleatório descrito como intervalo0.0 a1.0; o texto não esclarece inclusão das extremidades apesar do nome NonZero. Proposta: conferir implementação antes de usar em logaritmos ou inversão. Não há semente neste contrato.

### REF-1276 — MathMoments

Catálogo PDF3754–3754; texto lido neste registro:3754–3754; status:FULL_TEXT_READ.

MathMoments recebe array double e quatro saídas por referência; start=0 e count=WHOLE_ARRAY delimitam recorte; retorna bool. Proposta: estatística descritiva em janela explicitada, com falha e amostra vazia tratados; esta página não fornece fórmula ou convenção de curtose.

### REF-1277 — MathPowInt

Catálogo PDF3755–3755; texto lido neste registro:3755–3755; status:FULL_TEXT_READ.

MathPowInt(x,power) recebe double e expoente int, retorna double elevado à potência. Sem uso atual demonstrado; proposta de cálculo auxiliar sujeita a testes de domínio e overflow.

### REF-1278 — MathFactorial

Catálogo PDF3756–3756; texto lido neste registro:3756–3756; status:FULL_TEXT_READ.

MathFactorial recebe int e retorna double. A página não especifica teto seguro ou erro; sem uso atual demonstrado, não extrapolar precisão para fatoriais grandes.

### REF-1279 — MathTrunc

Catálogo PDF3757–3757; texto lido neste registro:3757–3757; status:FULL_TEXT_READ.

MathTrunc oferece escalar double, array de entrada const com saída separada e array alterado no lugar; versões array retornam bool. Proposta: não truncar dados monetários originais em cálculos de risco sem política de arredondamento definida.

### REF-1280 — MathRound

Catálogo PDF3758–3759; texto lido neste registro:3758–3759; status:FULL_TEXT_READ.

MathRound arredonda para digits casas decimais e possui escalar, array com saída separada e array no lugar; arrays retornam bool. Proposta: separar apresentação e cálculo, preservar entradas; a página não documenta desempate de meios.

### REF-1281 — MathArctan2

Catálogo PDF3760–3761; texto lido neste registro:3760–3761; status:FULL_TEXT_READ.

MathArctan2 escalar usa ordem(y,x); assinatura array mostra(x[],y[],result[]). Retorna radianos[-pi,pi] e documenta quadrantes/eixos. Lista(0,0) tanto em y=0/x não negativo→0 como em regra própria→-pi/2, exigindo conferência. NaN ou infinito em argumento retorna NaN. Sem uso atual; teste de orientação obrigatório antes de adoção.

### REF-1282 — MathGamma

Catálogo PDF3762–3762; texto lido neste registro:3762–3762; status:FULL_TEXT_READ.

MathGamma(x) recebe real e retorna valor gamma double; não se veem domínio, erro ou polos nesta página. Sem uso atual; proposta matemática exige validação explícita.

### REF-1283 — MathGammaLog

Catálogo PDF3763–3763; texto lido neste registro:3763–3763; status:FULL_TEXT_READ.

MathGammaLog(x) retorna logaritmo da gamma para argumento real. Sem uso atual; candidato a cálculos em log, mas esta página não estabelece tratamento de sinal/polos.

### REF-1284 — MathBeta

Catálogo PDF3764–3764; texto lido neste registro:3764–3764; status:FULL_TEXT_READ.

MathBeta(a,b) retorna beta double de dois argumentos reais. Sem uso atual; não é distribuição beta nem teste de aderência por si só.

### REF-1285 — MathBetaLog

Catálogo PDF3765–3765; texto lido neste registro:3765–3765; status:FULL_TEXT_READ.

MathBetaLog(a,b) retorna logaritmo da beta. Sem uso atual; proposta de preservar escala numérica precisa de testes de domínio e precisão.

### REF-1286 — MathBetaIncomplete

Catálogo PDF3766–3766; texto lido neste registro:3766–3766; status:FULL_TEXT_READ.

MathBetaIncomplete(x,p,q) exige p>0 e q>0; retorna double. A página não explicita normalização nem intervalo de x. Sem uso atual; conferir header antes de fórmula estatística.

### REF-1287 — MathGammaIncomplete

Catálogo PDF3767–3767; texto lido neste registro:3767–3767; status:FULL_TEXT_READ.

MathGammaIncomplete(x,alpha) retorna double e descreve argumento/parâmetro sem explicitar domínio nem normalização. Sem uso atual; não substituir variantes regularizadas por suposição.

### REF-1288 — MathBinomialCoefficient

Catálogo PDF3768–3768; texto lido neste registro:3768–3768; status:FULL_TEXT_READ.

MathBinomialCoefficient(int n,int k) retorna long e documenta n!/(k!*(n-k)!), número de combinações. Sem uso atual; proposta deve testar limites long e entradas inválidas; não inferir precisão ilimitada.

### REF-1289 — MathBinomialCoefficientLog

Catálogo PDF3769–3769; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1290 — MathHypergeometric2F2

Catálogo PDF3770–3770; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1291 — MathSequence

Catálogo PDF3771–3771; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1292 — MathSequenceByCount

Catálogo PDF3772–3772; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1293 — MathReplicate

Catálogo PDF3773–3773; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1294 — MathReverse

Catálogo PDF3774–3774; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1295 — MathIdentical

Catálogo PDF3775–3775; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1296 — MathUnique

Catálogo PDF3776–3776; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1297 — MathQuickSortAscending

Catálogo PDF3777–3777; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1298 — MathQuickSortDescending

Catálogo PDF3778–3778; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1299 — MathQuickSort

Catálogo PDF3779–3779; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1300 — MathOrder

Catálogo PDF3780–3780; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1301 — MathBitwiseNot

Catálogo PDF3781–3781; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1302 — MathBitwiseAnd

Catálogo PDF3782–3782; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1303 — MathBitwiseOr

Catálogo PDF3783–3783; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1304 — MathBitwiseXor

Catálogo PDF3784–3784; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1305 — MathBitwiseShiftL

Catálogo PDF3785–3785; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1306 — MathBitwiseShiftR

Catálogo PDF3786–3786; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1307 — MathCumulativeSum

Catálogo PDF3787–3787; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1308 — MathCumulativeProduct

Catálogo PDF3788–3788; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1309 — MathCumulativeMin

Catálogo PDF3789–3789; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1310 — MathCumulativeMax

Catálogo PDF3790–3790; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1311 — MathSin

Catálogo PDF3791–3791; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1312 — MathCos

Catálogo PDF3792–3792; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1313 — MathTan

Catálogo PDF3793–3793; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1314 — MathArcsin

Catálogo PDF3794–3794; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1315 — MathArccos

Catálogo PDF3795–3795; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1316 — MathArctan

Catálogo PDF3796–3796; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1317 — MathSinPi

Catálogo PDF3797–3797; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1318 — MathCosPi

Catálogo PDF3798–3798; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1319 — MathTanPi

Catálogo PDF3799–3799; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1320 — MathAbs

Catálogo PDF3800–3800; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1321 — MathCeil

Catálogo PDF3801–3801; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1322 — MathFloor

Catálogo PDF3802–3802; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1323 — MathSqrt

Catálogo PDF3803–3803; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1324 — MathExp

Catálogo PDF3804–3804; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1325 — MathPow

Catálogo PDF3805–3805; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1326 — MathLog

Catálogo PDF3806–3806; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1327 — MathLog2

Catálogo PDF3807–3807; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1328 — MathLog10

Catálogo PDF3808–3808; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1329 — MathLog1p

Catálogo PDF3809–3809; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1330 — MathDifference

Catálogo PDF3810–3811; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1331 — MathSample

Catálogo PDF3812–3814; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1332 — MathTukeySummary

Catálogo PDF3815–3815; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1333 — MathRange

Catálogo PDF3816–3816; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1334 — MathMin

Catálogo PDF3817–3817; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1335 — MathMax

Catálogo PDF3818–3818; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1336 — MathSum

Catálogo PDF3819–3819; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1337 — MathProduct

Catálogo PDF3820–3820; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1338 — MathStandardDeviation

Catálogo PDF3821–3821; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1339 — MathAverageDeviation

Catálogo PDF3822–3822; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1340 — MathMedian

Catálogo PDF3823–3823; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1341 — MathMean

Catálogo PDF3824–3824; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1342 — MathVariance

Catálogo PDF3825–3825; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1343 — MathSkewness

Catálogo PDF3826–3826; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1344 — MathKurtosis

Catálogo PDF3827–3827; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1345 — MathExpm1

Catálogo PDF3828–3828; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1346 — MathSinh

Catálogo PDF3829–3829; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1347 — MathCosh

Catálogo PDF3830–3830; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1348 — MathTanh

Catálogo PDF3831–3831; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1349 — MathArcsinh

Catálogo PDF3832–3832; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1350 — MathArccosh

Catálogo PDF3833–3833; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1351 — MathArctanh

Catálogo PDF3834–3834; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1352 — MathSignif

Catálogo PDF3835–3836; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1353 — MathRank

Catálogo PDF3837–3837; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1354 — MathCorrelationPearson

Catálogo PDF3838–3838; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1355 — MathCorrelationSpearman

Catálogo PDF3839–3839; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1356 — MathCorrelationKendall

Catálogo PDF3840–3840; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1357 — MathQuantile

Catálogo PDF3841–3841; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1358 — MathProbabilityDensityEmpirical

Catálogo PDF3842–3842; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1359 — MathCumulativeDistributionEmpirical

Catálogo PDF3843–3843; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1360 — Fuzzy Logic

Catálogo PDF3844–3935; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1361 — Membership functions

Catálogo PDF3845–3904; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1362 — CConstantMembershipFunction

Catálogo PDF3847–3849; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1363 — GetValue

Catálogo PDF3849–3849; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1364 — CCompositeMembershipFunction

Catálogo PDF3850–3853; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1365 — CompositionType

Catálogo PDF3852–3853; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1366 — MembershipFunctions

Catálogo PDF3852–3853; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1367 — GetValue

Catálogo PDF3852–3853; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1368 — CDifferencTwoSigmoidalMembershipFunction

Catálogo PDF3854–3858; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1369 — A1

Catálogo PDF3856–3856; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1370 — A2

Catálogo PDF3856–3856; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1371 — C1

Catálogo PDF3857–3857; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1372 — C2

Catálogo PDF3857–3857; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1373 — GetValue

Catálogo PDF3858–3858; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1374 — CGeneralizedBellShapedMembershipFunction

Catálogo PDF3859–3862; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1375 — A

Catálogo PDF3861–3861; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1376 — B

Catálogo PDF3861–3861; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1377 — C

Catálogo PDF3862–3862; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1378 — GetValue

Catálogo PDF3862–3862; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1379 — CNormalCombinationMembershipFunction

Catálogo PDF3863–3867; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1380 — B1

Catálogo PDF3865–3865; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1381 — B2

Catálogo PDF3865–3865; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1382 — Sigma1

Catálogo PDF3866–3866; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1383 — Sigma2

Catálogo PDF3866–3866; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1384 — GetValue

Catálogo PDF3867–3867; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1385 — CNormalMembershipFunction

Catálogo PDF3868–3871; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1386 — B

Catálogo PDF3870–3870; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1387 — Sigma

Catálogo PDF3870–3870; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1388 — GetValue

Catálogo PDF3871–3871; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1389 — CP_ShapedMembershipFunction

Catálogo PDF3872–3876; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1390 — A

Catálogo PDF3874–3874; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1391 — B

Catálogo PDF3874–3874; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1392 — C

Catálogo PDF3875–3876; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1393 — D

Catálogo PDF3875–3876; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1394 — GetValue

Catálogo PDF3875–3876; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1395 — CProductTwoSigmoidalMembershipFunctions

Catálogo PDF3877–3881; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1396 — A1

Catálogo PDF3879–3879; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1397 — A2

Catálogo PDF3879–3879; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1398 — C1

Catálogo PDF3880–3880; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1399 — C2

Catálogo PDF3880–3880; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1400 — GetValue

Catálogo PDF3881–3881; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1401 — CS_ShapedMembershipFunction

Catálogo PDF3882–3885; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1402 — A

Catálogo PDF3884–3884; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1403 — B

Catálogo PDF3884–3884; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1404 — GetValue

Catálogo PDF3885–3885; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1405 — CSigmoidalMembershipFunction

Catálogo PDF3886–3889; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1406 — A

Catálogo PDF3888–3888; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1407 — C

Catálogo PDF3888–3888; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1408 — GetValue

Catálogo PDF3889–3889; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1409 — CTrapezoidMembershipFunction

Catálogo PDF3890–3894; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1410 — X1

Catálogo PDF3892–3892; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1411 — X2

Catálogo PDF3892–3892; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1412 — X3

Catálogo PDF3893–3893; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1413 — X4

Catálogo PDF3893–3893; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1414 — GetValue

Catálogo PDF3894–3894; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1415 — CTriangularMembershipFunction

Catálogo PDF3895–3899; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1416 — X1

Catálogo PDF3897–3897; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1417 — X2

Catálogo PDF3897–3897; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1418 — X3

Catálogo PDF3898–3899; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1419 — ToNormalMF

Catálogo PDF3898–3899; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1420 — GetValue

Catálogo PDF3898–3899; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1421 — CZ_ShapedMembershipFunction

Catálogo PDF3900–3903; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1422 — A

Catálogo PDF3902–3902; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1423 — B

Catálogo PDF3902–3902; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1424 — GetValue

Catálogo PDF3903–3903; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1425 — IMembershipFunction

Catálogo PDF3904–3904; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1426 — GetValue

Catálogo PDF3904–3904; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1427 — Fuzzy systems rules

Catálogo PDF3905–3917; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1428 — CMamdaniFuzzyRule

Catálogo PDF3906–3907; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1429 — Conclusion

Catálogo PDF3906–3906; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1430 — Weight

Catálogo PDF3907–3907; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1431 — CSugenoFuzzyRule

Catálogo PDF3908–3909; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1432 — Conclusion

Catálogo PDF3908–3909; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1433 — CSingleCondition

Catálogo PDF3910–3912; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1434 — Not

Catálogo PDF3910–3910; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1435 — Term

Catálogo PDF3911–3912; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1436 — Var

Catálogo PDF3911–3912; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1437 — CConditions

Catálogo PDF3913–3914; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1438 — ConditionsList

Catálogo PDF3913–3913; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1439 — Not

Catálogo PDF3914–3914; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1440 — Op

Catálogo PDF3914–3914; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1441 — CGenericFuzzyRule

Catálogo PDF3915–3917; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1442 — Conclusion

Catálogo PDF3915–3915; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1443 — Condition

Catálogo PDF3916–3917; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1444 — CreateCondition

Catálogo PDF3916–3917; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1445 — Fuzzy systems variables

Catálogo PDF3918–3924; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1446 — CFuzzyVariable

Catálogo PDF3919–3922; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1447 — AddTerm

Catálogo PDF3920–3920; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1448 — GetTermByName

Catálogo PDF3920–3920; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1449 — Max

Catálogo PDF3920–3920; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1450 — Min

Catálogo PDF3921–3922; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1451 — Terms

Catálogo PDF3921–3922; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1452 — Values

Catálogo PDF3921–3922; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1453 — CSugenoVariable

Catálogo PDF3923–3924; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1454 — Functions

Catálogo PDF3923–3923; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1455 — GetFuncByName

Catálogo PDF3924–3924; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1456 — Values

Catálogo PDF3924–3924; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1457 — Fuzzy terms

Catálogo PDF3925–3926; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1458 — MembershipFunction

Catálogo PDF3926–3926; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1459 — Fuzzy systems

Catálogo PDF3927–3935; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1460 — Mamdani system

Catálogo PDF3928–3931; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1461 — AggregationMethod

Catálogo PDF3928–3928; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1462 — Calculate

Catálogo PDF3929–3929; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1463 — DefuzzificationMethod

Catálogo PDF3929–3929; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1464 — EmptyRule

Catálogo PDF3929–3929; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1465 — ImplicationMethod

Catálogo PDF3929–3929; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1466 — Output

Catálogo PDF3930–3931; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1467 — OutputByName

Catálogo PDF3930–3931; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1468 — ParseRule

Catálogo PDF3930–3931; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1469 — Rules

Catálogo PDF3930–3931; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1470 — Sugeno system

Catálogo PDF3932–3935; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1471 — Calculate

Catálogo PDF3932–3932; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1472 — CreateSugenoFunction

Catálogo PDF3933–3933; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1473 — EmptyRule

Catálogo PDF3934–3934; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1474 — Output

Catálogo PDF3934–3934; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1475 — OutputByName

Catálogo PDF3934–3934; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1476 — ParseRule

Catálogo PDF3934–3934; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1477 — Rules

Catálogo PDF3935–3935; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1478 — OpenCL

Catálogo PDF3936–3957; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1479 — BufferCreate

Catálogo PDF3938–3938; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1480 — BufferFree

Catálogo PDF3939–3939; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1481 — BufferFromArray

Catálogo PDF3940–3940; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1482 — BufferRead

Catálogo PDF3941–3941; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1483 — BufferWrite

Catálogo PDF3942–3942; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1484 — Execute

Catálogo PDF3943–3943; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1485 — GetContext

Catálogo PDF3944–3944; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1486 — GetKernel

Catálogo PDF3945–3945; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1487 — GetKernelName

Catálogo PDF3946–3946; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1488 — GetProgram

Catálogo PDF3947–3947; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1489 — Initialize

Catálogo PDF3948–3948; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1490 — KernelCreate

Catálogo PDF3949–3949; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1491 — KernelFree

Catálogo PDF3950–3950; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1492 — SetArgument

Catálogo PDF3951–3951; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1493 — SetArgumentBuffer

Catálogo PDF3952–3952; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1494 — SetArgumentLocalMemory

Catálogo PDF3953–3953; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1495 — SetBuffersCount

Catálogo PDF3954–3954; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1496 — SetKernelsCount

Catálogo PDF3955–3955; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1497 — Shutdown

Catálogo PDF3956–3956; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1498 — SupportDouble

Catálogo PDF3957–3957; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1499 — Basic Class CObject

Catálogo PDF3958–3969; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1500 — Prev

Catálogo PDF3959–3959; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1501 — Prev

Catálogo PDF3960–3960; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1502 — Next

Catálogo PDF3961–3961; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1503 — Next

Catálogo PDF3962–3962; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1504 — Compare

Catálogo PDF3963–3964; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1505 — Save

Catálogo PDF3965–3966; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1506 — Load

Catálogo PDF3967–3968; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1507 — Type

Catálogo PDF3969–3969; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1508 — Data Collections

Catálogo PDF3970–4368; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1509 — CArray

Catálogo PDF3971–3983; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1510 — Step

Catálogo PDF3973–3973; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1511 — Step

Catálogo PDF3974–3974; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1512 — Total

Catálogo PDF3975–3975; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1513 — Available

Catálogo PDF3976–3976; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1514 — Max

Catálogo PDF3977–3977; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1515 — IsSorted

Catálogo PDF3978–3978; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1516 — SortMode

Catálogo PDF3979–3979; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1517 — Clear

Catálogo PDF3980–3980; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1518 — Sort

Catálogo PDF3981–3981; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1519 — Save

Catálogo PDF3982–3982; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1520 — Load

Catálogo PDF3983–3983; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1521 — CArrayChar

Catálogo PDF3984–4020; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1522 — Reserve

Catálogo PDF3986–3986; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1523 — Resize

Catálogo PDF3987–3987; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1524 — Shutdown

Catálogo PDF3988–3988; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1525 — Add

Catálogo PDF3989–3989; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1526 — AddArray

Catálogo PDF3990–3990; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1527 — AddArray

Catálogo PDF3991–3992; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1528 — Insert

Catálogo PDF3993–3993; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1529 — InsertArray

Catálogo PDF3994–3994; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1530 — InsertArray

Catálogo PDF3995–3996; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1531 — AssignArray

Catálogo PDF3997–3997; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1532 — AssignArray

Catálogo PDF3998–3999; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1533 — Update

Catálogo PDF4000–4000; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1534 — Shift

Catálogo PDF4001–4001; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1535 — Delete

Catálogo PDF4002–4002; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1536 — DeleteRange

Catálogo PDF4003–4003; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1537 — At

Catálogo PDF4004–4005; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1538 — CompareArray

Catálogo PDF4006–4006; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1539 — CompareArray

Catálogo PDF4007–4007; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1540 — InsertSort

Catálogo PDF4008–4008; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1541 — Search

Catálogo PDF4009–4009; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1542 — SearchGreat

Catálogo PDF4010–4010; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1543 — SearchLess

Catálogo PDF4011–4011; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1544 — SearchGreatOrEqual

Catálogo PDF4012–4012; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1545 — SearchLessOrEqual

Catálogo PDF4013–4013; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1546 — SearchFirst

Catálogo PDF4014–4014; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1547 — SearchLast

Catálogo PDF4015–4015; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1548 — SearchLinear

Catálogo PDF4016–4016; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1549 — Save

Catálogo PDF4017–4017; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1550 — Load

Catálogo PDF4018–4019; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1551 — Type

Catálogo PDF4020–4020; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1552 — CArrayShort

Catálogo PDF4021–4059; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1553 — Reserve

Catálogo PDF4024–4024; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1554 — Resize

Catálogo PDF4025–4025; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1555 — Shutdown

Catálogo PDF4026–4026; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1556 — Add

Catálogo PDF4027–4027; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1557 — AddArray

Catálogo PDF4028–4028; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1558 — AddArray

Catálogo PDF4029–4030; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1559 — Insert

Catálogo PDF4031–4031; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1560 — InsertArray

Catálogo PDF4032–4032; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1561 — InsertArray

Catálogo PDF4033–4034; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1562 — AssignArray

Catálogo PDF4035–4035; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1563 — AssignArray

Catálogo PDF4036–4037; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1564 — Update

Catálogo PDF4038–4038; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1565 — Shift

Catálogo PDF4039–4039; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1566 — Delete

Catálogo PDF4040–4040; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1567 — DeleteRange

Catálogo PDF4041–4041; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1568 — At

Catálogo PDF4042–4043; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1569 — CompareArray

Catálogo PDF4044–4044; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1570 — CompareArray

Catálogo PDF4045–4045; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1571 — InsertSort

Catálogo PDF4046–4046; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1572 — Search

Catálogo PDF4047–4047; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1573 — SearchGreat

Catálogo PDF4048–4048; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1574 — SearchLess

Catálogo PDF4049–4049; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1575 — SearchGreatOrEqual

Catálogo PDF4050–4050; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1576 — SearchLessOrEqual

Catálogo PDF4051–4051; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1577 — SearchFirst

Catálogo PDF4052–4052; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1578 — SearchLast

Catálogo PDF4053–4053; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1579 — SearchLinear

Catálogo PDF4054–4054; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1580 — Save

Catálogo PDF4055–4056; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1581 — Load

Catálogo PDF4057–4058; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1582 — Type

Catálogo PDF4059–4059; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1583 — CArrayInt

Catálogo PDF4060–4098; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1584 — Reserve

Catálogo PDF4063–4063; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1585 — Resize

Catálogo PDF4064–4064; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1586 — Shutdown

Catálogo PDF4065–4065; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1587 — Add

Catálogo PDF4066–4066; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1588 — AddArray

Catálogo PDF4067–4067; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1589 — AddArray

Catálogo PDF4068–4069; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1590 — Insert

Catálogo PDF4070–4070; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1591 — InsertArray

Catálogo PDF4071–4071; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1592 — InsertArray

Catálogo PDF4072–4073; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1593 — AssignArray

Catálogo PDF4074–4074; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1594 — AssignArray

Catálogo PDF4075–4076; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1595 — Update

Catálogo PDF4077–4077; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1596 — Shift

Catálogo PDF4078–4078; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1597 — Delete

Catálogo PDF4079–4079; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1598 — DeleteRange

Catálogo PDF4080–4080; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1599 — At

Catálogo PDF4081–4082; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1600 — CompareArray

Catálogo PDF4083–4083; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1601 — CompareArray

Catálogo PDF4084–4084; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1602 — InsertSort

Catálogo PDF4085–4085; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1603 — Search

Catálogo PDF4086–4086; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1604 — SearchGreat

Catálogo PDF4087–4087; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1605 — SearchLess

Catálogo PDF4088–4088; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1606 — SearchGreatOrEqual

Catálogo PDF4089–4089; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1607 — SearchLessOrEqual

Catálogo PDF4090–4090; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1608 — SearchFirst

Catálogo PDF4091–4091; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1609 — SearchLast

Catálogo PDF4092–4092; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1610 — SearchLinear

Catálogo PDF4093–4093; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1611 — Save

Catálogo PDF4094–4095; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1612 — Load

Catálogo PDF4096–4097; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1613 — Type

Catálogo PDF4098–4098; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1614 — CArrayLong

Catálogo PDF4099–4137; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1615 — Reserve

Catálogo PDF4102–4102; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.

### REF-1616 — Resize

Catálogo PDF4103–4103; texto lido neste registro:nenhuma; status:NOT_READ.

NÃO_LIDO: título e limites vistos apenas no catálogo; conhecimento concreto e aplicação Stoikus não avaliados. Retomar texto integral antes de qualquer síntese.
