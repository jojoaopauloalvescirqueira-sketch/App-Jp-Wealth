---
tipo_nota: norma
dominio: jp_wealth
documento: JPW-GOV-001
versao: "10.0"
status: vigente
livro: "II"
titulos: "5–13"
aliases:
  - "Livro II — Estatuto Operacional — Arquitetura Quadrifásica de Risco Vertical"
  - "Livro II"
---

# Livro II — Estatuto Operacional — Arquitetura Quadrifásica de Risco Vertical

> Títulos 5 a 13 · Artigos 5.1 a 13.3

## Título 5 — Estrutura Operacional

### Artigo 5.1 — Modelo de Risco Vertical

A gestão opera sob o regime de **Operação Única Exclusiva**: toda a exposição é concentrada em uma **única tese operacional** por vez, sujeita a **mecanismos progressivos de controle,** desalavancagem e proteção patrimonial. Fica revogado, em caráter definitivo, o modelo de risco horizontal (múltiplas operações simultâneas), bem como os indicadores de correlação ICCO e ICFO a ele associados.

**§1º** — É permitida apenas uma Operação ativa por conta gerenciada. Enquanto houver Operação em andamento, é proibida a abertura de posições em qualquer outro ativo, ressalvada exclusivamente a Operação Simbólica de Atividade (Art. 22.5, Livro IV).

### Artigo 5.2 — Horizonte Temporal

O gráfico de 4 horas (**H4**) é o horizonte principal para análise estrutural, contexto e construção de teses, com gatilho de execução em H1, conforme Livro VI.

### Artigo 5.3 — Ciclo Operacional e Catraca Patrimonial

O ciclo de gestão possui duração de **12 meses**, contados da fixação do Saldo Inicial de Referência. Lucros consolidados de exercícios anteriores integram reservas segregadas e não ampliam o risco do ciclo vigente. Risco máximo, limites de drawdown e dimensionamento são calculados exclusivamente sobre o Saldo Inicial de Referência do ciclo ativo.

## Título 6 — Matriz Quadrifásica de Risco

### Artigo 6.1 — Limite Máximo e Fases

O limite máximo de drawdown da Conta Mestre é fixado em **15,00%,** distribuído em **quatro fases** operacionais:

| **Fase** | **Faixa de DD** | **Alav. Máx.** | **Regime e Diretrizes** |
| --- | --- | --- | --- |
| 1 — Exposição Inicial | 0,00% – 4,00% | 4,0x | Ordem Gênese; construção da grade conforme critérios técnicos; execução da tese em parâmetros normais. |
| 2 — Restrição Moderada | 4,01% – 8,00% | 2,0x | Reconhecimento formal de deterioração; redução obrigatória de exposição; prioridade à proteção patrimonial e recuperação técnica. |
| 3 — Restrição Avançada | 8,01% – 12,00% | 1,0x | Tendência adversa confirmada; proibição de novas ampliações agressivas; correções usadas exclusivamente para reduzir exposição. Aciona o Protocolo de Emergência. |
| 4 — Salvaguarda Final | 12,01% – 15,00% | 0,4x | Congelamento da atividade discricionária; manutenção apenas da exposição residual; única exceção: Defesa Final (Art. 9.3). Preparação para encerramento compulsório. |

**§1º** — Considera-se "ampliação agressiva", para fins da Fase 3, qualquer ordem que eleve a exposição nocional total acima da exposição vigente no momento do ingresso na fase, ainda que dentro do teto de alavancagem.

**§2º** — **Protocolo de Gap**: se abertura de mercado ou movimento descontínuo deslocar o DD através de uma ou mais fases sem janela de poda, aplica-se imediatamente o teto da fase efetivamente atingida, com adequação compulsória na primeira liquidez disponível. Se o gap conduzir o DD a nível igual ou superior a 15,00%, aplica-se o encerramento compulsório integral a mercado, executado pela Auditoria ou pelo **Equity Protector,** o que ocorrer primeiro.

### Artigo 6.2 — Hierarquia de Disjuntores

| **Nível** | **Acionamento** | **Medida** |
| --- | --- | --- |
| 1 — Restrição Moderada | DD > 4,00% | Alavancagem máxima reduzida a 2,0x; início da poda LIFO. |
| 2 — Emergência Operacional | DD > 8,00% | Alavancagem máxima 1,0x; ativação do Protocolo de Emergência. |
| 3 — Congelamento Operacional | DD > 12,00% | Suspensão da atividade discricionária; exposição residual apenas; exceção única: Defesa Final (Art. 9.3). |
| 4 — Encerramento Compulsório | DD ≥ 15,00% | Liquidação integral e imediata; início da Quarentena Operacional. |

> [!danger] Cláusula de Penalidade Fiduciária
> *O descumprimento, hesitação ou tentativa de burla à Hierarquia de Disjuntores — incluindo remoção temporária de ordens stop no terminal ou atraso intencional da poda LIFO em janelas de pullback — constitui falta gravíssima de conformidade, sujeita ao Art. 17.6 (Livro III).*

## Título 7 — Protocolo de Desalavancagem Tática (PDT / LIFO)

### Artigo 7.1 — Regra Geral

A **transição para fase mais restritiva** impõe **redução imediata da exposição** ao novo teto, pelo método LIFO (Last In, First Out): encerram-se prioritariamente as posições mais recentes da estrutura, preservando a eficiência do preço médio e reduzindo pressão sobre margem.

**§1º** — Sempre que tecnicamente possível, a **poda será executada em movimentos corretivos favoráveis** (retrações observadas em M15/H1).

**§2º** — Gatilho compulsório: **inexistindo movimento corretivo, a poda torna-se compulsória e imediata quando o DD avançar 1,00 ponto percentual além do limite superior da fase rompida**. A inexistência de retrações não suspende nem posterga a obrigação de adequação.

**§3º** — Se o nível de margem da conta indicar risco de stop-out técnico (Tabela do Art. 18.4, Livro III) antes do gatilho do §2º, a proteção de margem prevalece: executa-se a redução necessária de imediato, mantendo a ordem LIFO.

### Artigo 7.2 — Revogação da Exceção Direcional

Fica revogado qualquer mecanismo que permita manter posições além dos limites deste Código com base em convicções subjetivas ou expectativa de reversão. **O limite máximo de drawdown é critério objetivo e definitivo de encerramento compulsório.**

## Título 8 — Dimensionamento e Métricas de Risco

### Artigo 8.1 — Ordem Gênese: Dupla Restrição

A Ordem Gênese está sujeita, cumulativamente, a duas restrições independentes:

- Restrição de risco: o risco financeiro máximo (distância ao stop × volume) não excederá 1,00% do Saldo Inicial, equivalente a 25% da capacidade de absorção da Fase 1;
- Restrição de alavancagem: a exposição nocional da Gênese não excederá 0,4x, preservando capacidade financeira para absorção de volatilidade e execução dos protocolos subsequentes.

### Artigo 8.2 — Fatores do Lote Operacional

O volume final de cada posição decorre de:

I — valor nominal do contrato (equivalência financeira entre ativos);

II — regime de volatilidade (VRM);

III — fase vigente da Matriz Quadrifásica;

IV — distância do stop estatístico.

### Artigo 8.3 — VRM e Regimes de Volatilidade

| **VRM = ATR(55)/ATR(660) em H4** | **Regime** | **Conduta** |
| --- | --- | --- |
| < 1,20 | Normal | Parâmetros padrão da fase vigente. |
| 1,20 – 1,50 | Transição | Cautela; revisão de amplitude e stop. |
| > 1,50 | Alta Volatilidade | Redução obrigatória de exposição conforme parâmetros da gestão. |

### Artigo 8.4 — Validação do Stop

O Stop Técnico deve observar simultaneamente estrutura de Price Action, múltiplo de ATR e validação estatística.

A distância do stop, expressa em múltiplos do ATR(55):

| **Distância do Stop (× ATR55)** | **Classificação** |
| --- | --- |
| < 2,0 | Estrutura inadequada — operação vedada. |
| 2,0 – 3,5 | Estrutura mínima aceitável. |
| 3,5 – 5,0 | Estrutura ideal. |
| > 5,0 | Estrutura conservadora. |

### Artigo 8.5 — Projeção Estatística de Sobrevivência (Raiz-N)

```
Stop_estatístico = ATR(55) × √N × F

N = horizonte projetado da operação, em candles H4  (padrão: 55)
F = fator de segurança  (padrão: 1,25 — sujeito a ratificação, Anexo C)
```

**§1º** — Se o Stop Técnico for inferior ao Stop Estatístico, a operação é classificada como Estrutura de Vulnerabilidade Elevada, e todas as decisões de gestão priorizarão redução de risco.

## Título 9 — Construção Tática da Posição

### Artigo 9.1 — Estrutura Escalonada

A posição poderá compor-se de Ordem Gênese, ordens intermediárias de ajuste e ordens de posicionamento estrutural, distribuídas em zonas técnicas previamente definidas. **Toda ampliação permanece subordinada aos limites da fase vigente.**

### Artigo 9.2 — Lucro Técnico

O Lucro Técnico (Art. 4.6) será empregado exclusivamente para: redução da exposição líquida; melhoria do preço médio consolidado; redução de exigência de margem; ou encerramento parcial de posições deficitárias. É vedado seu uso para ampliar limites de risco.

### Artigo 9.3 — Defesa Final da Estrutura

A Defesa Final é o mecanismo excepcional e único de exposição nova permitido na Fase 4, destinado exclusivamente à melhoria técnica das condições de encerramento — jamais à ampliação de risco direcional ou ao prolongamento indefinido da Operação.

**§1º** — Exposição máxima: 1,00% do Saldo Inicial do Ciclo.

**§2º** — Procedimento obrigatório:

- solicitação formal escrita do Gestor, com justificativa técnica, registrada no canal oficial;
- execução exclusiva pela Auditoria — o Gestor não possui meios de execução direta;
- direito de veto pleno da Auditoria, com fundamentação escrita;
- limite de uma única Defesa Final por Operação;
- registro em ata do Compliance Board.

**§3º** — O congelamento da Fase 4 permanece íntegro para qualquer outra forma de atividade discricionária. A Defesa Final não suspende o encerramento compulsório aos 15,00%.

## Título 10 — Firewall Assimétrico e Replicação para Contas Satélites

### Artigo 10.1 — Fórmula Normativa de Replicação

A replicação de ordens da Conta Mestre para contas satélites observará, obrigatoriamente, a normalização por saldo previamente à aplicação do fator de perfil:

```
Lote_satélite = Lote_mestre × ( Saldo_satélite / Saldo_mestre ) × Fator_perfil

DD%_satélite_projetado = DD%_mestre × Fator_perfil
```

**§1º** — É expressamente vedada a aplicação de fator de lote fixo sem normalização por saldo, por produzir risco proporcional incorreto entre contas de saldos distintos. A redação anterior ("fator de multiplicação de lote fixado em 1/3") fica revogada e substituída pela fórmula deste artigo.

### Artigo 10.2 — Invariante de Segurança do Fator

```
Fator_perfil ≤ ( MaxLoss_conta − 2,00 p.p. ) / 15,00%
```

Nenhum perfil poderá adotar fator que, no cenário de utilização integral do limite de 15,00% da Conta Mestre, projete drawdown na conta satélite superior ao seu limite contratual de perda máxima deduzido de margem mínima de segurança de 2,00 pontos percentuais.

### Artigo 10.3 — Perfis de Correção por Função da Conta

Por deliberação do Gestor Geral (Anexo B, D-3), o fator de correção é definido pela função estratégica da conta, observados o invariante do Art. 10.2 e o princípio de que quanto maior o fator de risco do perfil, menor o teto de participação da conta na carteira de satélites:

| **Perfil** | **Fator (novo)** | **Fator revogado** | **DDR-alvo** | **DD no cenário 15%** | **Alav./ordem** | **Teto de participação\*** |
| --- | --- | --- | --- | --- | --- | --- |
| Longevity | 53% | 66% | 8,0% | 7,95% | 0,21x | ≤ 1/3 das contas satélites |
| High Longevity | 40% | 50% | 6,0% | 6,00% | 0,16x | ≤ 1/2 das contas satélites |
| High Longevity Plus | 27% | 33% | 4,0% | 4,05% | 0,11x | Sem teto; mínimo de 1 conta ativa |

*\* Tetos de participação: proposta em ratificação (Anexo C). Os fatores anteriores (66/50/33%) foram calibrados sobre o DDR de 12% da V8.0; sob o limite de 15% da V9.0, o fator de 66% projetaria 9,9% de drawdown na satélite — margem nula frente ao Maximum Loss contratual de 10% —, razão pela qual sua revogação é compulsória e não discricionária.*

### Artigo 10.4 — Faixas de Fase nas Satélites

As faixas de drawdown de cada fase nas contas satélites correspondem às faixas da Conta Mestre multiplicadas pelo Fator_perfil, conforme tabela consolidada no Anexo A.

### Artigo 10.5 — Rotatividade de Perfis

Perfis não são fixos: são atribuídos pela função estratégica da conta no momento. Contas escaladas migram para perfis mais defensivos. Em caso de perda de conta-base por violação de drawdown, outra conta ativa poderá ser promovida ao papel de perfil-base, e nova conta adquirida no perfil mais conservador. Contas High Longevity Plus são estáticas por princípio, salvo esgotamento extremo das demais.

## Título 11 — Protocolo de Emergência, Encerramento e Quarentena

### Artigo 11.1 — Acionamento

O Protocolo de Emergência é automaticamente acionado quando o DD atinge a Fase 3 (8,01%–12,00%), independentemente de interpretação ou convicção. Medidas obrigatórias: adequação imediata ao teto da fase; aplicação do PDT/LIFO; proibição de ampliações agressivas; suspensão de novas teses; reavaliação integral do contexto antes de qualquer ajuste permitido.

### Artigo 11.2 — Encerramento Compulsório e Quarentena

Atingido DD ≥ 15,00%: liquidação integral e imediata das posições e suspensão da atividade, iniciando-se Quarentena Operacional mínima de 90 dias.

**§1º** — Execução do encerramento: pela Auditoria, mediante alerta automático; e, em paralelo, pelo Equity Protector permanentemente armado (Art. 18.6, Livro III), prevalecendo o que ocorrer primeiro. O Gestor não executa o encerramento.

**§2º** — Durante a quarentena, o Gestor elaborará relatório de incidente com análise de causas, avaliação de falhas e propostas de correção.

**§3º** — Autoridade de retorno: o reinício das atividades exige deliberação conjunta e registrada do Compliance Board (Gestor Geral + Auditoria), lavrada em ata, após conclusão do relatório e revalidação dos protocolos. É vedada a auto-revalidação unilateral pelo Gestor.

### Artigo 11.3 — Recuperação de Estado Inválido

Constatado erro de apuração de fase ou de DD (falha de dado, cálculo ou registro), a operação é imediatamente enquadrada na fase correta apurada; excessos de exposição são adequados pelo PDT na primeira liquidez; o incidente é registrado e reportado ao Compliance Board em até 48 horas.

## Título 12 — Regimes Patrimoniais do Ciclo

### Artigo 12.1 — DDI

Durante o Drawdown Inicial, exige-se aderência integral aos critérios de validação operacional. O acionamento do limite máximo implica os protocolos do Título 11.

### Artigo 12.2 — Drawdown Compensado (DDC)

O Drawdown Compensado possui natureza exclusivamente patrimonial e contábil. Lucro acumulado amplia a margem livre da fase, mas não autoriza ampliação de limites absolutos, alteração de tetos de alavancagem, flexibilização da Matriz.

> [!warning] Aviso do Auditor — A Ilusão do DDC
> *O regime DDC não compra indulgência técnica. O DDC protege o saldo final e a estrutura; não protege egos feridos que se recusam a executar o corte tático LIFO.*

### Artigo 12.3 — Proibição Absoluta de Merge

É terminantemente proibida a fusão de riscos ou compensação cruzada de saldos. Lucros de operações liquidadas ou margens livres de subcontas não estendem os limites verticais de fase. Cada ciclo da Operação Única nasce, respira e morre sob os limites matemáticos estritos de sua fase vigente.

## Título 13 — Reservas Segregadas

### Artigo 13.1 — FCR (Fundo de Contingência e Reconstituição)

Volume mínimo: **15,00% do capital nominal da Conta Mestre**.

Finalidade exclusiva: recomposição do capital operacional após atingimento do limite máximo de drawdown.

Natureza: reserva segregada de liquidez imediata (D+0/D+1).

O acionamento do FCR não altera quarentena, auditoria ou revalidação. Após uso, todos os recursos líquidos gerados destinam-se prioritariamente à sua recomposição integral; enquanto não recomposto, é vedada distribuição de dividendos ou retiradas extraordinárias.

### Artigo 13.2 — FEO (Fundo de Estabilidade Operacional)

Volume mínimo: 6 meses das despesas pessoais, operacionais e administrativas da estrutura.

Finalidade: continuidade financeira durante baixa rentabilidade, drawdowns prolongados, interrupções ou quarentena.

Liquidez de até D+2. Vedada a transferência de recursos do FEO para corretoras, prop firms ou ampliação de risco.

### Artigo 13.3 — Hierarquia de Capitalização

Todo fluxo financeiro gerado pela atividade observará a ordem:

I — recomposição integral do FCR;

II — constituição/recomposição integral do FEO;

III — reservas estratégicas adicionais;

IV — distribuição de dividendos ou realocação patrimonial. A relação entre estes fundos e o bloco macro de 15% da alocação patrimonial rege-se pelo Art. 26.2 (Livro V).

> [!abstract] Cláusula Pétrea das Reservas
> *A manutenção do FCR e do FEO é requisito obrigatório para a continuidade do modelo de gestão. A preservação da estrutura financeira da Holding possui prioridade sobre qualquer expectativa de crescimento, retorno ou expansão.*

---

## Navegação

- Índice: [[JP Wealth OS/00 - PROJECT/Norma Vigente/00 - Estatuto V10]]
- Anterior: [[JP Wealth OS/00 - PROJECT/Norma Vigente/02 - Livro I — Hierarquia Normativa e Definições]]
- Próximo: [[JP Wealth OS/00 - PROJECT/Norma Vigente/04 - Livro III — Governança, Funções e Controles Humanos]]
