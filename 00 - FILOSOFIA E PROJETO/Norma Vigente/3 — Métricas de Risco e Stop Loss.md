# LIVRO III

## Título 8 — Dimensionamento

**Artigo 8.1 — Ordem Gênese: Restrições Cumulativas**

A Ordem Gênese sujeita-se cumulativamente a três restrições independentes:

**I — Restrição de risco.** O risco financeiro máximo, apurado pelo produto da distância ao stop pelo volume, não excederá o percentual do Saldo Inicial de Referência definido no anexo paramétrico.

**II — Restrição de alavancagem.** A exposição nocional da Gênese não excederá o teto da Fase 1, definido na Matriz Hexafásica.

**III — Restrição de validação de stop.** A distância do stop observará o múltiplo mínimo de amplitude verdadeira estabelecido no artigo de validação. A projeção estatística de sobrevivência (modelo Raiz-N) possui função exclusivamente diagnóstica e não constitui restrição de admissão.

**§1º — Independência e prevalência.** As restrições são independentes e todas eliminatórias. A observância de uma não dispensa as demais, e prevalece sempre a que resultar em menor volume.
**§2º — Variável de ajuste.** Sendo incompatíveis a distância de stop tecnicamente exigida e o limite de risco financeiro, a variável de ajuste é o **volume**, jamais o stop. É vedado encurtar a distância do stop para acomodar volume pretendido.
**§3º — Teto de alavancagem como limite superior.** O teto de alavancagem da Fase 1 é limite máximo, e não dimensionamento de referência. Sua utilização integral pressupõe distância de stop compatível com o limite de risco, e não constitui alvo de dimensionamento.
**§4º — Impossibilidade de dimensionamento conforme.** Não sendo possível dimensionar volume que satisfaça simultaneamente as três restrições, a operação é vedada. A impossibilidade constitui indicação de que a estrutura técnica não comporta o instrumento na volatilidade vigente.
**§5º — Fundamento das restrições.** A restrição de risco delimita a perda da entrada. A restrição de alavancagem preserva capacidade de absorção para a construção subsequente e para a execução dos protocolos de desalavancagem. A restrição de validação assegura que a distância do stop seja tecnicamente sustentável, e não arbitrada para acomodar volume.
**§6º — Registro.** O dimensionamento é registrado com: risco financeiro apurado; exposição nocional resultante; distância do stop em unidades de preço e em múltiplos de amplitude verdadeira; restrição que efetivamente determinou o volume; e volume final executado.

--- 

**Artigo 8.2 — Determinação do Lote Operacional**
O volume de cada posição resulta da aplicação sequencial dos fatores deste artigo, prevalecendo sempre o que produzir menor volume.

**§1º — Fatores determinantes:**

**I — Equivalência financeira.** Valor nominal do contrato do instrumento, convertido à moeda de denominação da conta, de modo que movimentos equivalentes em diferentes instrumentos produzam impacto financeiro comparável.

**II — Distância do stop.** Distância entre o preço de execução e o stop validado, apurada em unidades de preço do instrumento.

**III — Limite de risco aplicável.** Percentual do Saldo Inicial de Referência admitido para a ordem, conforme sua natureza e a fase vigente.

**IV — Regime de volatilidade.** Classificação vigente da métrica de regime, com a conduta de redução correspondente.

**V — Fase vigente.** Teto de alavancagem da fase da Matriz Hexafásica.

**VI — Capacidade agregada remanescente.** Capacidade não consumida do Teto de Risco Agregado da Fase, apurada nos termos do Artigo 8.4.

**§2º — Sequência de cálculo.** O volume é apurado na seguinte ordem:

I — calcula-se o volume que consome integralmente o limite de risco aplicável, dados a distância do stop validado e a equivalência financeira do instrumento;  
II — verifica-se se a exposição nocional resultante observa o teto de alavancagem da fase; em caso negativo, reduz-se o volume até observá-lo;  
III — aplica-se a redução determinada pelo regime de volatilidade vigente;  
IV — apuram-se, em base pro forma, o Risco Comprometido da Operação e o Risco Aberto Agregado da Fase, e verifica-se se observam, respectivamente, o Orçamento de Risco da Operação e o Teto de Risco Agregado da Fase, nos termos do Artigo 8.4; em caso negativo, reduz-se o volume até observá-los.

**§3º — Prevalência do menor volume.** Cada etapa do §2º pode apenas reduzir o volume apurado na etapa anterior. É vedado o retorno a volume superior por reordenação das etapas ou por compensação entre fatores.
**§4º — Vedação de ajuste inverso.** É vedado alterar a distância do stop, a classificação de regime de volatilidade ou a apuração de fase com a finalidade de acomodar volume pretendido. A determinação é unidirecional: os fatores determinam o volume, e o volume não determina os fatores.
**§5º — Volume nulo.** Resultando das etapas do §2º volume inferior ao lote mínimo admitido pela instituição, a operação é vedada. É vedado o arredondamento para cima.
**§6º — Implementação em sistema.** O cálculo poderá ser executado por instrumento próprio da Holding, cuja divergência em relação a este artigo constitui defeito do instrumento. A sequência do §2º é vinculante para a implementação.
**§7º — Registro.** O dimensionamento é registrado com o valor apurado em cada etapa do §2º e a identificação da etapa que determinou o volume final.

---
**Artigo 8.3 — Position Size
O Position Sizing é a variável quantitativa que traduz o risco teórico em exposição real. Na JP Wealth, o tamanho da posição não é fixo; ele é ajustado dinamicamente para garantir que, independentemente do ativo ou da volatilidade, o impacto de um Stop Loss seja padronizado e contido pelo Firewall.

 **Alavancagem de Referência e Base de Cálculo**
Para instrumentos de Forex (pares de moedas com contrato padrão de 100.000 unidades), define-se o padrão:

- **Exposição Base:** 0,01 lote para cada US$ 2.000 de saldo.
- **Alavancagem Real:** ~0,5x por ordem.
- **Finalidade:** Este equilíbrio permite suportar o ruído estatístico do gráfico de H4 mantendo a conta em um regime de baixa pressão de margem.

 **Ajuste por Custo de Contrato (Equivalência Financeira)**
É obrigatória a correção do lote para ativos com valor de contrato anômalo. O risco financeiro deve ser idêntico ao Forex, independentemente do instrumento.

- **Caso XAU/USD (Ouro):** Devido ao valor do contrato (~US$ 308.000 por lote padrão), a exposição é 3x superior ao câmbio.
- **Regra de Correção:** Para XAUUSD, a alocação deve ser de 0,01 lote para cada US$ 6.000.
- **Protocolo:** Antes de operar qualquer ativo novo, o gestor deve realizar o cálculo de equivalência para garantir que a alavancagem real por ordem permaneça em 0,5x.

 **Ajuste por Volatilidade (O Filtro VRM)**
O índice Volatility Regime Metric (VRM) dita o fator de redução do lote. Se a amplitude do mercado aumenta, o lote deve diminuir para que o Stop Loss técnico (ajustado pelo ATR/Raiz-N) continue cabendo dentro do limite financeiro.

- **Regimes de Transição e de Alta Volatilidade:** O Position Size é reduzido de 0,5x para 0,25x por ordem (0,01 lote para cada $4.000).
- **Objetivo:** Garantir que o Stop Loss tenha espaço para respirar fora das zonas de ruído institucional sem ultrapassar os limites de risco aplicáveis à ordem, à Operação e à fase vigente.

 **Pilares de Influência do Position Size**
O cálculo final do lote de uma Ordem Gênese deve considerar obrigatoriamente:

1. **Valor Nominal do Contrato:** Padronização do risco por dólar exposto.
2. **Volatilidade Corrente (VRM):** Ajuste da distância técnica do stop.
### VRM (Volatility Regime Metric)

Para preservar a coerência entre a alavancagem real utilizada e a realidade estatística do mercado, define-se o VRM (Volatility Regime Metric) como o indicador oficial de classificação da volatilidade vigente. Ele define três regimes: normal, transição e alta volatilidade. No regime de transição o VRM nunca autoriza ampliação de risco e, na ausência de regra específica, aplica-se a restrição mais conservadora entre os regimes adjacentes.

```
              ATR H4 (55 períodos)
VRM  =  ─────────────────────────────
             ATR H4 (660 períodos)
```
​

Essa métrica compara a volatilidade recente do mercado (aproximadamente duas semanas, com base no ATR de 55 períodos no H4) com a volatilidade estrutural de longo prazo (cerca de seis meses, com base no ATR de 660 períodos no H4). O objetivo é identificar, de forma objetiva, se o mercado opera sob um regime de normalidade, alerta ou estresse.

A classificação de regimes segue a seguinte estrutura:

| Regime de Volatilidade      | Faixa de VRM | Alavancagem |
| --------------------------- | ------------ | ----------- |
| Regime Normal               | VRM < 1,20          | 0,5x        |
| Regime de Transição         | 1,20 ≤ VRM ≤ 1,50   | 0,25x — aplica-se a restrição mais conservadora entre os regimes adjacentes; vedada qualquer ampliação de risco |
| Regime de Alta Volatilidade | VRM > 1,50          | 0,25x       |

---
**Artigo 8.4 — Arquitetura de Limites de Risco**
O risco financeiro submete-se a três limites independentes e cumulativos: o Risco de Admissão da Ordem, o Risco Comprometido da Operação e o Risco Aberto Agregado da Fase. Os três empregam a mesma definição de risco financeiro e distinguem-se pelo objeto contabilizado e pela função do limite. Nenhum substitui os demais, e a observância de um não dispensa a observância dos outros.

**§1º — Definição canônica de risco financeiro.** O risco financeiro de uma ordem corresponde ao produto da distância entre o preço de execução e o stop válido vigente, na forma do Artigo 8.2, §1º, II, pelo volume remanescente, apurado na moeda de denominação da conta e nos termos do Artigo 4.5, §3º. Estando o stop válido em posição que assegure resultado não negativo em relação ao preço de execução, o risco financeiro da ordem é nulo. O risco financeiro não assume valor negativo.

**§2º — Invariância frente à marcação a mercado.** O risco financeiro não é reapurado a partir do preço corrente. Movimento de preço, adverso ou favorável, que não altere o volume remanescente nem o stop válido vigente, não modifica nenhuma das três grandezas deste artigo. O efeito patrimonial do movimento de preço é apurado pelo Equity, pelo drawdown, pela alavancagem e pelo nível de margem, nos termos dos institutos respectivos.

**§3º — Primeira camada: Risco de Admissão da Ordem.** Risco de Admissão da Ordem é o risco financeiro apurado no momento da admissão, sobre o volume pretendido, e verificado antes da execução. Observa o limite individual aplicável conforme a natureza da ordem e a fase vigente, nos termos do Artigo 8.2, §1º, III, e, quanto à Ordem Gênese, do Artigo 8.1, I. Movimento posterior do preço não altera retrospectivamente o valor registrado na admissão.

**§4º — Segunda camada: Risco Comprometido da Operação.** Risco Comprometido da Operação é a soma dos resultados realizados negativos atribuíveis à Operação, dos custos negativos atribuíveis à Operação, do risco financeiro das posições remanescentes e do risco reservado às ordens pendentes ampliadoras. Mede quanto do Orçamento de Risco da Operação foi consumido ou permanece comprometido, e representa o pior caso financeiro contratado, na hipótese de acionamento de todos os stops válidos sem descontinuidade de execução.

**§5º — Resultados realizados negativos.** Os resultados realizados negativos atribuíveis à Operação são computados sem compensação por resultados positivos e permanecem computados até o encerramento da Operação. Integram o Risco Comprometido em caráter definitivo, e sua realização não restaura capacidade.

**§5º-A — Custos negativos atribuíveis à Operação.** Integram o Risco Comprometido, pelo valor acumulado desde a Ordem Gênese e apurado na moeda de denominação da conta: o swap devedor, as comissões e os demais custos de execução efetivamente debitados e atribuíveis às posições da Operação. Custos são computados quando debitados e somam-se sem compensação: swap credor, resultado positivo ou qualquer outro crédito não abate custo negativo nem libera Orçamento de Risco. Enquanto não existir buffer homologado para descontinuidade de execução, o Risco Comprometido não constitui garantia de perda máxima: gap e deslizamento podem produzir perda superior ao risco apurado pelo stop, nos termos do §7º e do §25.

**§6º — Resultados realizados positivos.** Resultado realizado positivo não constitui parcela negativa do Risco Comprometido, não abate resultados realizados negativos e não cria capacidade, nos termos do Artigo 3.15, §§3º e 4º. Distingue-se a redução de risco decorrente do encerramento de volume, que é legítima e opera pela extinção do risco financeiro daquele volume, do financiamento de risco por resultado, que permanece vedado.

**§7º — Encerramento parcial.** O encerramento parcial extingue o risco financeiro do volume encerrado e acresce ao Risco Comprometido o resultado negativo eventualmente realizado. Disso decorre que o Risco Comprometido diminui quando o encerramento ocorre antes de consumido o risco que a parcela carregava; permanece inalterado quando o resultado realizado iguala aquele risco; e aumenta quando o resultado realizado o excede, por movimento descontínuo ou por deslizamento de execução.

**§8º — Vedação de liberação por deterioração.** A deterioração do preço, sem redução efetiva de exposição, não reduz o Risco Comprometido da Operação e não libera capacidade. Somente a redução efetiva de exposição extingue risco financeiro.

**§9º — Terceira camada: Risco Aberto Agregado da Fase.** Risco Aberto Agregado da Fase é a soma do risco financeiro das posições abertas e do risco reservado às ordens pendentes ampliadoras. Não compreende resultados realizados. Mede quanto risco financeiro permanece simultaneamente carregado.

**§10 — Orçamento de Risco da Operação.** Orçamento de Risco da Operação é o limite financeiro total declarado para uma Operação determinada, antes da execução da Ordem Gênese, e integra a declaração da Estrutura Operacional, na forma do Artigo 4.7. É específico da Operação para a qual foi declarado e não se amplia no curso dela, seja por resultado favorável, por realização de Lucro Técnico, por retorno a fase menos restritiva, por recomposição do Equity, por aporte de capital ou por decurso de tempo.

**§11 — Natureza declarada do Orçamento.** O Orçamento é teto interno declarado, e não autorização de consumo. Sua declaração não confere direito à utilização integral do valor declarado, e ele permanece subordinado aos limites institucionais da primeira e da terceira camadas. Prevalece sempre o menor entre o Orçamento declarado e o Teto de Risco Agregado da Fase vigente.

**§12 — Redução do Orçamento.** A redução do Orçamento é admitida desde que o novo valor não seja inferior ao Risco Comprometido da Operação apurado no momento da alteração. Pretendendo o Gestor orçamento inferior, reduz primeiro a exposição pelas condutas autorizadas e somente então registra o novo valor. A alteração escritural não constitui, por si, fundamento de redução compulsória.

**§13 — Teto de Risco Agregado da Fase.** Teto de Risco Agregado da Fase é o limite institucional aplicado ao Risco Aberto Agregado da Fase, específico da fase vigente. As três camadas são apuradas sobre o Saldo Inicial de Referência. Os valores das primeira e terceira camadas constam do anexo paramétrico; o Orçamento de Risco da Operação não constitui matéria paramétrica.

**§13-A — Limite prudencial de sobrevivência.** Independentemente da fase vigente, do Orçamento declarado e do Teto de Risco Agregado da Fase, o Risco Comprometido da Operação, apurado em base pro forma antes de qualquer nova ordem e reaferido continuamente, não excederá a capacidade prudencial restante até o limite operacional máximo de drawdown vigente, nos termos do Livro II, Artigo 6.1, deduzido o buffer de descontinuidade de execução quando homologado. O buffer de descontinuidade de execução (gap e deslizamento) é parâmetro PENDENTE de homologação; enquanto pendente, o cálculo deste parágrafo não inclui reserva quantitativa ex ante adicional para gap e deslizamento, e essa ausência é declarada como risco residual não coberto — não constituindo valor, fallback ou buffer provisório. O risco admissível efetivo para nova ordem é o menor entre a capacidade remanescente do Teto de Risco Agregado da Fase e a capacidade remanescente deste parágrafo, observados cumulativamente os demais limites deste artigo. Este parágrafo estabelece limite máximo, e não dimensionamento de referência: não autoriza consumir a capacidade que declara.

**§14 — Perfil entre fases.** O Teto de Risco Agregado da Fase 1 é igual ao da Fase 2, e o teto de cada fase seguinte não excede o da fase imediatamente anterior. A ampliação de capacidade admitida na transição do Nível 1, nos termos dos Artigos 6.3, §2º, e 7.1, §2º, alcança exclusivamente o teto de alavancagem e não se estende ao risco financeiro.

**§15 — Ordens pendentes ampliadoras e redutoras.** Ordem pendente ampliadora é aquela cuja execução aumentaria a exposição; sua capacidade é reservada e computada na segunda e na terceira camadas enquanto a ordem permanecer ativa. Ordem pendente redutora é aquela cuja execução apenas reduz ou encerra exposição, entre as quais o stop loss e o take profit; não consome reserva adicional. A obrigação de manter stop loss e take profit permanece integralmente aplicável.

**§16 — Ordens de execução mutuamente exclusiva.** Inexistindo garantia técnica auditável de exclusividade, reserva-se a soma dos riscos das ordens pendentes ampliadoras. Havendo exclusividade tecnicamente garantida e auditável, reserva-se o maior risco que possa materializar-se simultaneamente. A demonstração da exclusividade consta do controle operacional aplicável.

**§17 — Risco pro forma.** Antes da execução de qualquer nova ordem apuram-se, em base pro forma, o Risco de Admissão da Ordem, o Risco Comprometido da Operação e o Risco Aberto Agregado da Fase. A execução é vedada se qualquer deles exceder o limite que lhe é próprio.

**§18 — Capacidade remanescente.** A capacidade remanescente de cada camada corresponde à diferença entre o respectivo limite e a grandeza apurada, quando positiva, e a zero quando a grandeza igualar ou exceder o limite. Sua existência não constitui, por si, fundamento de nova ordem: a execução permanece condicionada cumulativamente à declaração prévia, ao teto de alavancagem da fase, ao regime de volatilidade vigente e aos demais protocolos aplicáveis.

**§19 — Reposicionamento do stop.** O reposicionamento do stop válido para posição mais distante do preço de execução eleva o risco financeiro da ordem e, por consequência, a segunda e a terceira camadas, observadas as vedações e os requisitos aplicáveis. O reposicionamento para posição mais próxima reduz o risco financeiro, sem que dessa redução decorra autorização automática de recomposição.

**§20 — Redução do risco e recomposição.** A redução de volume, a poda, o encerramento parcial e o encurtamento do stop podem reduzir o risco financeiro e produzir capacidade aritmética. Sua reutilização não é automática: subordina-se ao regime de Defesa Limitada do Artigo 3.17, ao Artigo 8.1, §2º, ao Artigo 3.16 e às demais vedações contra ajuste oportunista. É vedado invocar a mera existência de capacidade aritmética como fundamento de recomposição de exposição.

**§21 — Independência frente à alavancagem.** Risco financeiro e alavancagem são grandezas independentes, nos termos do Artigo 4.5, §3º, e sujeitam-se a limites próprios, aplicáveis cumulativamente, apurados sobre bases próprias. A observância do teto de alavancagem não supre a observância dos limites deste artigo, nem o inverso.

**§22 — Reaferição na transição de fase.** A transição para fase mais restritiva impõe a reaferição do Risco Aberto Agregado da Fase contra o teto da fase efetivamente atingida. A Operação somente se considera enquadrada na nova fase quando observar cumulativamente o teto de alavancagem da fase e o Teto de Risco Agregado da Fase.

**§23 — Ingresso em fase de ampliação vedada.** Ao ingresso em fase em que a ampliação é vedada, nos termos do Artigo 6.1, §5º, as ordens pendentes ampliadoras incompatíveis com a fase são canceladas ou reduzidas. As ordens pendentes redutoras permanecem ativas.

**§24 — Excesso na primeira camada.** Excedendo o Risco de Admissão da Ordem o limite individual aplicável, a ordem não é executável, e a variável de ajuste é o volume, nos termos do Artigo 8.1, §2º. É vedado alterar a distância do stop para acomodar volume pretendido.

**§25 — Excesso na segunda camada.** Excedendo o Risco Comprometido da Operação o Orçamento declarado, o Teto de Risco Agregado aplicável ou a capacidade prudencial do §13-A, fica vedada a assunção de novo risco ampliador até a regularização ou o encerramento da Operação, e procede-se, nesta ordem: ao cancelamento ou à redução das ordens pendentes ampliadoras; ao recálculo das grandezas deste artigo; e, subsistindo o excesso na parcela correspondente ao risco financeiro das posições abertas, à poda das posições na forma do Protocolo de Desalavancagem Tática, até a observância simultânea de todos os limites aplicáveis. A parcela do excesso correspondente a resultados realizados negativos e a custos já debitados não é regularizável por redução de exposição nem por nova exposição; permanece registrada, e a Operação admite exclusivamente condutas de contenção, redução, proteção e encerramento. Decorrendo o excesso exclusivamente de movimento descontínuo, de deslizamento de execução ou de outro evento de execução não controlável, o fato é registrado como incidente operacional e não constitui, por si, infração, sem prejuízo da redução devida.

**§25-A — Reaferição da segunda camada na transição de fase.** A transição para fase mais restritiva impõe a reaferição do Risco Comprometido da Operação contra os limites aplicáveis na fase atingida, em conjunto com a reaferição do §22. Verificado excesso, aplica-se o §25 na primeira janela disponível, observada a prevalência da proteção de margem.

**§26 — Excesso na terceira camada.** Excedendo o Risco Aberto Agregado da Fase o teto da fase vigente, procede-se, nesta ordem: ao cancelamento ou à redução das ordens pendentes ampliadoras incompatíveis; ao recálculo das grandezas deste artigo; e, subsistindo o excesso, à poda das posições abertas na forma do Protocolo de Desalavancagem Tática, até a observância do teto. É vedado realizar prejuízo em posição aberta para preservar ampliação ainda não executada, quando o cancelamento desta for suficiente.

**§27 — Ordem remanescente única.** Remanescendo apenas a Ordem Gênese e subsistindo excesso, admite-se a redução parcial de seu volume para enquadramento. Sendo a zeragem integral da exposição a única forma de enquadrar, procede-se a ela. A zeragem não extingue a Operação, nos termos dos Artigos 4.2, §3º, e 4.4, e eventual reingresso permanece subordinado ao Orçamento vigente, às três camadas deste artigo, à fase, ao teto de alavancagem e ao regime de Defesa Limitada.

**§28 — Prevalência.** Sendo aplicáveis simultaneamente mais de um dos limites deste artigo, prevalece o que resultar em menor volume, na forma do Artigo 8.2, §3º.

**§29 — Registro.** São registrados: o Orçamento de Risco da Operação declarado e suas alterações; o Risco de Admissão de cada ordem; o Risco Comprometido e o Risco Aberto Agregado no momento de cada dimensionamento; os valores pro forma apurados; a capacidade remanescente de cada camada; os cancelamentos de ordens pendentes ampliadoras; e a reaferição realizada em cada transição de fase.

## Título 9 — Stop Loss
### Artigo 9.1 — Distribuição de Exposição na Estrutura
A construção da estrutura observa distribuição escalonada de exposição ao longo da zona operacional, com concentração progressiva nas regiões de confluência técnica mais próximas ao ponto de reversão esperado.

**§1º — Fundamento aritmético.** Ordem posicionada mais próxima ao stop admite volume superior sob idêntico risco financeiro, dado que a distância até a invalidação é menor. A elevação da alavancagem nocional nessas ordens não corresponde a elevação do risco financeiro da estrutura.
**§2º — Distinção entre alavancagem e risco.** Esta é a única hipótese admitida neste Livro em que a alavancagem nocional de uma ordem atinge níveis elevados. A admissibilidade decorre exclusivamente da compensação pela proximidade do stop, e não constitui autorização para elevar exposição por qualquer outro fundamento.
**§3º — Finalidade.** A distribuição visa concentrar exposição em regiões de maior exaustão técnica do movimento, ampliando a assimetria da estrutura sem elevar o risco financeiro total previamente estabelecido.
**§4º — Limite da estrutura.** O somatório do risco financeiro de todas as ordens da estrutura observa o Teto de Risco Agregado da Fase, na forma do Artigo 8.4. A compensação do §1º opera dentro desse teto, jamais como exceção a ele.
**§5º — Declaração prévia.** As zonas de ampliação, o volume previsto em cada uma e a exposição nocional máxima projetada são declarados antes da execução da Ordem Gênese, nos termos do artigo de construção tática.
**§6º — Vedação de concentração não prevista.** É vedada a colocação de ordem de volume superior ao declarado na zona correspondente, ainda que o risco financeiro individual permaneça dentro do limite.

**Nota Explicativa — o movimento do preço médio**
Durante o curso da Operação, parte das ordens da estrutura poderá gerar resultado realizado em movimentos corretivos favoráveis. Esse resultado, definido como Lucro Técnico, é empregado nas finalidades taxativas do artigo respectivo — entre elas, a amortização de ordens deficitárias posicionadas em níveis anteriores.
O efeito prático é o deslocamento do preço médio consolidado. Quando o mercado se move contra a estrutura, o preço médio é trazido para mais próximo do preço corrente; quando se move a favor, a realização o afasta. É essa dinâmica que a gestão denomina o ciclo entre defesa, ataque e gerenciamento.
Registra-se que o emprego do Lucro Técnico observa integralmente a hierarquia de finalidades e as vedações do Título 3, e que o prolongamento de permanência é a última das finalidades admitidas.
## Artigo 9.2 — Modelo de Alocação Escalonada
A estrutura é construída por alocação assimétrica em degraus, com volume crescente à medida que o preço se aproxima da zona de invalidação.

|Ordem|Posição na estrutura|Volume relativo|
|---|---|---|
|Gênese|Topo da estrutura|Leve|
|Intermediária|Zona intermediária|Médio|
|Estrutural|Zona de stop técnico e reversão provável|Pesado|

**§1º — Fundamento da progressão.** A progressão de volume decorre da compensação pela distância: ordem mais próxima ao stop admite volume superior sob idêntico risco financeiro. A assimetria de volume corresponde à assimetria de distância, e não a elevação do risco.
**§2º — Concentração em zona de exaustão.** A distribuição concentra exposição nas regiões de maior agressão do preço, onde a estrutura técnica indica maior probabilidade de reversão. A avaliação de probabilidade é qualitativa e estrutural, não constituindo afirmação quantitativa nos termos da vedação aplicável.
**§3º — Limite do somatório.** O somatório do risco financeiro de todas as ordens da estrutura observa o Teto de Risco Agregado da Fase, na forma do Artigo 8.4. Ordem pesada próxima ao stop não excepciona o teto: ela cabe nele por construção, ou não é executada.
**§4º — Número de degraus.** O número de ordens da estrutura e a distribuição de volume entre elas constam da declaração prévia da Operação e observam os limites do anexo paramétrico.
**§5º — Vedação de degrau não declarado.** É vedada a colocação de ordem em zona não prevista na declaração prévia. Ordem nessas condições constitui ampliação autônoma, sujeita a justificativa técnica escrita e registro próprio.

---
## Artigo 9.3 — Distinção frente a Preço Médio Irrestrito e Martingale
A alocação escalonada deste Título não se confunde com as técnicas de preço médio irrestrito e de progressão geométrica de exposição, reconhecidas como de risco patrimonial elevado.

**§1º — Elementos distintivos.** A distinção decorre da presença cumulativa dos seguintes elementos, cuja ausência descaracteriza o modelo:

**I** — Orçamento de Risco da Operação, declarado antes da execução da Ordem Gênese e não ampliável no curso dela, na forma do Artigo 8.4, §10;

**II** — zonas de ampliação, volumes e exposição máxima projetada declarados previamente, vedada a improvisação de degrau;

**III** — Teto de Risco Agregado da Fase, observado pelo risco comprometido da Operação, na forma do Artigo 8.4, §13;

**IV** — decaimento obrigatório de alavancagem ao longo das fases, que reduz a exposição admitida à medida que a deterioração avança;

**V** — teto de Defesa Limitada, que torna irreversível cada redução de exposição executada;

**VI** — limite absoluto de drawdown, que encerra a Operação independentemente de convicção, contexto ou expectativa de reversão.

**§2º — Natureza da distinção.** A distinção é estrutural, e não de intenção. Reside nos mecanismos enumerados no §1º, e não na avaliação do Gestor sobre a qualidade da tese ou sobre a diferença entre a própria conduta e as técnicas mencionadas.
**§3º — Perda da distinção.** Suprimido, flexibilizado ou descumprido qualquer dos elementos do §1º, a estrutura passa a constituir preço médio irrestrito para todos os efeitos deste Estatuto, independentemente da denominação empregada e do resultado obtido.
**§4º — Vedação de invocação.** É vedado invocar este artigo como fundamento de conduta. Ele descreve por que o modelo se distingue; não autoriza ampliação, não flexibiliza limite e não constitui salvaguarda contra o descumprimento dos artigos que estabelecem os elementos enumerados.

---
### Artigo 9.4 — Protocolo de Validação do Stop
O Stop Loss é o elemento fundante da Operação. A partir dele definem-se a construção da estrutura de ordens, o espaço de distribuição, o risco financeiro e a margem estatística que sustentará a posição em volatilidade adversa.

**§1º — Primazia da análise técnica.** A definição do stop cabe à análise técnica, por topos, fundos, confluências estruturais ou demais referências do método. A validação estatística não substitui a análise técnica: seleciona, entre as referências tecnicamente válidas, aquela de maior robustez frente à volatilidade histórica do instrumento.
**§2º — Finalidade da validação.** A validação destina-se a evitar que stops tecnicamente bem posicionados sejam acionados por oscilação natural do mercado, preservando simultaneamente a lógica técnica e a integridade da estrutura.
**§3º — Stop Loss Mínimo.** Define-se como Stop Loss Mínimo a menor distância percentual admissível entre o ponto de entrada e o stop, apurada pelo múltiplo de amplitude verdadeira, nos termos do Artigo 9.5. O modelo de dispersão acumulada (Raiz-N) é referência diagnóstica complementar e não integra o Stop Loss Mínimo.
**§4º — Ordem de precedência.** A análise técnica precede a validação. É vedado definir stop a partir do resultado dos indicadores quantitativos e buscar, posteriormente, referência técnica que o justifique.

---
### Artigo 9.5 — Múltiplo de Amplitude Verdadeira

O múltiplo de ATR mede a distância do stop em unidades da oscilação média do instrumento.

**§1º — Base de apuração.** Emprega-se a amplitude verdadeira média apurada no horizonte decisório, com o período constante do anexo paramétrico. O período adotado capta a oscilação média de aproximadamente duas semanas úteis, alinhando-se ao horizonte operacional e à sensibilidade exigida pelo perfil swing.
**§2º — Conversão percentual.** Para comparabilidade com a distância do stop, a amplitude verdadeira é convertida em percentual:

```
ATR percentual (%) = ( ATR / Preço atual ) × 100
```

**§3º — Apuração do múltiplo.**

```
                    Stop Técnico (percentual)
Múltiplo de ATR = ──────────────────────────────
                       ATR (percentual)
```

**§4º — Classificação estratificada:**

|Faixa|Classificação|Interpretação|
|---|---|---|
|< 1,0x|Frágil|Altamente exposto ao ruído|
|1,0 – 2,0x|Levemente frágil|Inadequado para maturação longa|
|2,0 – 3,5x|Mínimo realista|Inadequado para maturação longa|
|3,5 – 5,0x|Normal|Mínimo aceitável|
|5,0 – 7,0x|Conservador|Operações de longa duração ou instrumentos de cauda longa; exige alvo proporcional|
|> 7,0x|Zona segura|Exige alvo proporcional|

**§5º — Limiar operacional.** Considerado o horizonte ordinário de maturação da Operação, a classificação de mínimo aceitável constitui o limiar admitido para abertura. Classificação inferior veda a operação.
**§6º — Alvo proporcional.** Stop classificado como conservador ou superior exige alvo proporcional à distância adotada, de modo que a relação risco-retorno permaneça compatível com a estrutura. Distância ampliada sem alvo correspondente não constitui conservadorismo, mas degradação da assimetria.
**§7º — Os limiares deste artigo constam do anexo paramétrico.**

---

### Artigo 9.6 — Integração com a Distribuição da Estrutura

**§1º — Funções distintas.** O múltiplo de amplitude define o espaço natural de oscilação do instrumento. O stop define a profundidade estrutural da Operação. A distribuição define a resposta da gestão ao movimento do mercado.
**§2º — Natureza da distância ampliada.** Stop de múltiplo elevado não constitui, por si, risco elevado. Constitui profundidade estatística e espaço de desenvolvimento, desde que o volume seja reduzido na proporção correspondente, mantendo o risco financeiro constante.
**§3º — Condição da afirmação anterior.** O disposto no §2º pressupõe o cumprimento integral do dimensionamento por risco. Distância ampliada com volume mantido eleva o risco financeiro proporcionalmente, e nesse caso a profundidade estatística converte-se em exposição ampliada.

---
## Modelo de Stop Mínimo Estatístico por ATR Raiz-N

Para garantir que o Stop técnico resista a oscilações médias por pelo menos uma semana de candles H4 (aproximadamente 30 velas), utilizamos um modelo derivado da teoria de dispersão acumulada (movimento browniano), comum em cálculos de desvio padrão aplicado ao tempo.

```
Stop Estatístico (Stop Mínimo Recomendado) em % = ATR(%) × √N × F
```

**Onde:**

- **ATR(%)** = ATR(55) convertido em percentual;
- **N** = número de candles H4 (ex: 55 = ~2 semanas);
- **F** = Fator de ajuste conservador para cauda estatística — valor pendente de homologação (Anexo C, item 1); o intervalo 1,5 a 2,0 é referência histórica sem efeito operacional.

Esse modelo estima a expansão estatística da faixa de oscilação semanal, e estabelece um limite mínimo abaixo do qual o stop estaria exposto a ser atingido por ruído natural com alta frequência.

Esta métrica oferece uma referência quantitativa diagnóstica para o dimensionamento da distância do stop em função do período planejado. Não existe eficácia nem probabilidade de resistência demonstrada; a métrica não possui força normativa e não autoriza afirmação de grau de confiança.

 **Determinando o Fator N (Número de Candles)**
O fator N representa a quantidade de candles H4 ao longo da qual se espera que a operação evolua até seu desfecho. Ele deve ser estimado com base na média histórica de duração das operações da estratégia, nas características de maturação do setup e no regime de volatilidade atual.
Valores típicos situam-se entre 12 e 50 candles H4. O fator N é estimado caso a caso pelo Gestor, na forma do parágrafo anterior: não existe valor padrão homologado, e o fator não constitui parâmetro de calibração delegado à governança paramétrica.

**Fator de ajuste F**
Utilizado na fórmula do Stop Estatístico, o fator F representa uma ampliação conservadora da dispersão média do ativo, com o objetivo de proteger a operação contra ruídos extremos e oscilações fora da curva ao longo do tempo planejado. Este fator de ajuste se baseia em dois fundamentos estatísticos consolidados:

 **Volatilidade acumulada no tempo**
A fórmula do modelo Raiz-N deriva da lógica do movimento browniano, onde a dispersão esperada de um ativo cresce proporcionalmente à raiz quadrada do tempo (√N). Isso reflete o comportamento observado na projeção de volatilidade futura:

```
σt = σ1 × √N
```

Quando projetamos a dispersão de um ativo ao longo do tempo, o desvio padrão cresce proporcionalmente à raiz quadrada do tempo. Portanto aplicaremos diretamente a dispersão cumulativa do movimento browniano, com N como o número de candles e F como o fator de ajuste conservador para cauda longa.
#### Intervalos de confiança estatística (múltiplos de σ)
Em distribuições normais, múltiplos de desvio padrão (σ) delimitam zonas de probabilidade:

|Múltiplo|Cobertura|
|---|---|
|1σ|68,2% dos casos|
|1,5σ|~86,6%|
|2σ|~95,4%|

Como o ATR representa uma média suavizada da amplitude de movimento (não uma dispersão pura dos retornos), e os mercados reais apresentam distribuições com cauda longa, é necessário aplicar um fator de ajuste empírico que compense esse desvio da normalidade.

O intervalo **F = 1,5 a 2,0**, historicamente empregado, é descrito como:

- Um ajuste conservador da dispersão média, sem cobertura probabilística demonstrada;
- Um parâmetro cujo valor vigente é pendente de homologação (Anexo C, item 1) e, até lá, sem efeito operacional; o intervalo 1,5–2,0 é referência histórica de redação.
### Exemplo Aplicado — Validação Estatística no XAU/USD (EXEMPLO HISTÓRICO, NÃO OPERACIONAL — instrumento vedado pelo Art. 22.2; mantido apenas como memória de cálculo)

```
Stop Estatístico Raiz-N (%) = 0,817% × √30 × 1,8

Stop Estatístico = 8,04%
```

**Interpretação**

Para que o stop sobreviva estatisticamente a uma semana de oscilação média do XAU/USD, o valor mínimo recomendado é de 8,04% de distância em relação à entrada.

Se o stop técnico estiver abaixo disso (ex.: 4% ou 5%), ele estará posicionado dentro da zona estatística de ruído, e poderá ser acionado mesmo em operações corretamente direcionadas. Portanto a gestão não abre mão da análise técnica para definir suas zonas de stop loss técnico, porém utiliza deste filtro quantitativo para definir a distância mínima a buscar sua referência.

---

### Aplicação dos Modelos Múltiplo de ATR e Raiz-N na Gestão

A forma como a gestão posiciona o stop loss é definida por dois modelos que verificamos nos trechos anteriores. No entanto, a maneira como sintetizamos na tomada de decisão é conjugada, o que traz redundância do correto posicionamento quantitativo do distanciamento do Stop.

**Etapa 1** — Price Action, Stop Técnico.
**Etapa 2** — Cálculo do múltiplo de ATR do Stop.
**Etapa 3** — Cálculo do stop mínimo do modelo Raiz-N, dado o tempo esperado da operação (ex.: 55 candles H4 para 1 semana).
**Etapa 4** — O stop observa obrigatoriamente o múltiplo mínimo de amplitude verdadeira (Art. 9.5); o resultado do modelo Raiz-N é registrado como diagnóstico e não veda a operação.

#### Exemplo de Caso Aplicado (EXEMPLO HISTÓRICO, NÃO OPERACIONAL — instrumento vedado pelo Art. 22.2)

Operação planejada no XAU/USD, com ATR(55) em 0,82%, e expectativa de maturação de 8 dias úteis. O gestor posiciona o stop técnico em 5%. Após calcular:

- **Múltiplo de ATR ≈ 6,1x** → conservador, porém estatisticamente coerente.
- **Modelo Raiz-N indica stop mínimo ≈ 8%** → ainda abaixo.

**Decisão:** manter o stop técnico com alvo maior, aceitando um risco estatístico sob controle, mas ciente da menor probabilidade de resistir ao ruído por 7+ dias sem ser acionado.

> **Nota:** Nem todo stop técnico precisa alcançar o valor do Stop Estatístico. O importante é que, ao estar abaixo dele, a gestão tenha plena consciência de que está operando dentro da zona estatística de vulnerabilidade — e que compensações táticas sejam estruturadas.

### Considerações
O Stop Loss não é apenas uma medida de proteção, mas a base sobre a qual toda a estrutura da operação é desenhada. Não buscamos abandonar a análise técnica, mas refiná-la, selecionando entre as zonas técnicas possíveis aquela que melhor protege a operação de ser "stopada" por ruído estatístico. A validação estatística eleva o nível de precisão, confiança e resiliência da nossa estratégia, atuando como filtro adicional de qualidade operacional.