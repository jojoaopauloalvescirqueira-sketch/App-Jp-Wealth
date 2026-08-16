---
tipo_nota: norma
dominio: jp_wealth
documento: JPW-GOV-001
versao: "10.0"
status: vigente
livro: "I"
titulos: "1–4"
aliases:
  - "Livro I — Hierarquia Normativa e Definições"
  - "Livro I"
---

# Livro I — Hierarquia Normativa e Definições

> Títulos 1 a 4 · Artigos 1.1 a 4.6

## Título 1 — Natureza e Escopo

### Artigo 1.1 — Objeto

Este Código rege integralmente a atividade de gestão e alocação de capital da JP Wealth Holding nos mercados de Câmbio (Forex) e Contratos por Diferença (CFDs), abrangendo: princípios e filosofia de gestão; limites de risco e exposição; protocolos de execução, desalavancagem e proteção patrimonial; estrutura de governança e funções; regime de mesas proprietárias; alocação patrimonial e tesouraria; e método de análise e execução técnica.

### Artigo 1.2 — Vinculação

Este documento constitui referência obrigatória para todas as decisões operacionais. Nenhuma convicção analítica, resultado isolado ou circunstância de mercado autoriza sua flexibilização. Em caso de conflito entre convicção e protocolo, prevalece o protocolo; entre lucro potencial e preservação patrimonial, prevalece a preservação.

## Título 2 — Hierarquia Normativa e Resolução de Conflitos

### Artigo 2.1 — Hierarquia Interna

As normas deste Código organizam-se na seguinte ordem de precedência:

- **1º — Livro I** (Disposições Fundamentais e Definições) e Cláusulas Pétreas de qualquer Livro;
- **2º — Livro II** (Estatuto Operacional e Arquitetura Quadrifásica de Risco);
- **3º — Livro III** (Governança e Funções);
- **4º — Livros IV e V** (Mesas Proprietárias; Alocação Patrimonial e Tesouraria);
- **5º — Livro VI** (Método e Execução Técnica);
- **6º** — Anexos e documentos operacionais derivados (planilhas, painéis, templates de sinal).

**§1º** — Norma de nível superior prevalece sobre norma de nível inferior, sem exceção.

**§2º** — Havendo conflito entre normas do mesmo nível, prevalece a interpretação mais restritiva em risco (menor exposição, menor alavancagem, encerramento mais rápido), até resolução formal pelo Compliance Board.

**§3º** — Todo conflito identificado deverá ser registrado por escrito e resolvido por emenda formal na revisão seguinte deste Código. A existência de conflito não suspende a operação: aplica-se o §2º.

### Artigo 2.2 — Revogação dos Instrumentos Anteriores

Ficam revogados, na data de ratificação deste Código, todos os instrumentos normativos anteriores da JP Wealth, cujo conteúdo vigente encontra-se integralmente incorporado a este documento. Referências externas a tais instrumentos entendem-se remetidas aos Livros correspondentes deste Código.

## Título 3 — Princípios e Cultura de Gestão

### Artigo 3.1 — Pilares Operacionais

A consistência operacional é sustentada por quatro pilares:

- **Planejamento** (definição prévia de cenários, critérios e objetivos);
- **Filosofia e Mindset** (aceitação da incerteza e da natureza probabilística dos resultados);
- **Execução Operacional** (reação disciplinada às informações do mercado, sem antecipações preditivas); e
- **Gerenciamento** (aplicação rigorosa dos limites de risco).

### Artigo 3.2 — Bússola Estratégica Operacional

Toda alocação de risco direcional exige alinhamento simultâneo de quatro critérios:

- **Padrão** (estrutura operacional clara e documentável compatível com o método);
- **Tendência** (alinhamento ao fluxo predominante);
- **Amplitude** (espaço técnico suficiente para relação risco-retorno adequada); e
- **Confluência** (múltiplos fatores independentes de validação).

### Artigo 3.3 — Hierarquia Permanente de Prioridades

Todas as decisões operacionais respeitarão a seguinte ordem:

- **Preservação do Capital;**
- **Sobrevivência Operacional da Conta;**
- **Cumprimento Integral dos Protocolos de Risco;**
- **Qualidade da Execução;**
- **Consistência de Longo Prazo;**
- **Rentabilidade.**

### Artigo 3.4 — Natureza Probabilística

Nenhum modelo analítico é capaz de prever com certeza o comportamento futuro dos preços. Todas as operações constituem decisões probabilísticas. O objetivo da gestão não é eliminar perdas, mas controlar sua magnitude e preservar capacidade operacional ao longo de centenas de ciclos de decisão. Este Código não contém, e proíbe que documentos derivados contenham, afirmações quantitativas de probabilidade de ruína ou de retorno sem memória de cálculo formalmente publicada.

## Título 4 — Definições Formais (Glossário Normativo)

Para todos os efeitos deste Código, aplicam-se as seguintes definições, vinculantes para interpretação humana e para implementação em sistemas automatizados:

### Artigo 4.1 — Drawdown Operacional (DD)

Medida oficial de deterioração que rege a Matriz Quadrifásica:

```
DD(t) = max( 0 ; ( Saldo_Inicial_Ciclo − Equity(t) ) / Saldo_Inicial_Ciclo )

Equity(t) = patrimônio flutuante da conta (saldo + resultado aberto), tick a tick
Saldo_Inicial_Ciclo = saldo de referência fixado na abertura do ciclo anual (Catraca Patrimonial)
```

**§1º** — O DD é medido sobre equity flutuante, em base contínua (tick a tick), tendo como referência exclusiva o Saldo Inicial do Ciclo. Lucros acumulados no ciclo não alteram a referência (regime DDC, Art. 12.3 do Livro II).

**§2º** — A transição para fase mais restritiva é efetivada no instante em que o DD rompe o limite superior da fase vigente. A adequação de exposição deve iniciar imediatamente, observado o Protocolo de Desalavancagem Tática.

**§3º** — Histerese de retorno: o retorno a uma fase menos restritiva somente ocorre quando o DD recuar para valor inferior ao limite da fase em pelo menos 0,50 ponto percentual, sustentado pelo fechamento de ao menos 1 (um) candle H4 completo.

A poda LIFO executada não é revertida; nova exposição somente por ordens novas, conformes aos limites da fase restaurada.

### Artigo 4.2 — Operação

Conjunto de ordens pertencentes à mesma tese operacional, executadas no mesmo ativo e na mesma direção. Inicia-se com a execução da Ordem Gênese e encerra-se quando não houver qualquer posição aberta vinculada à tese, confirmado o encerramento pelo protocolo do Art. 4.4.

### Artigo 4.3 — Ordem Gênese

Primeira ordem de uma Operação Única, identificada objetivamente pela conjunção de dois critérios:

- posição líquida do ativo igual a zero no momento da execução; e
- sinalização expressa da flag GÊNESE no template de sinal. Ausente a flag, a ordem não será executada pela Auditoria até esclarecimento.

### Artigo 4.4 — Encerramento de Operação

Estado em que a posição líquida do ativo retorna a zero E o Gestor confirma o encerramento mediante o protocolo de dupla confirmação (registro escrito "FECHADO" no template de saída).

Zeragem tática sem confirmação de encerramento não extingue a Operação; contudo, eventual reingresso permanece sujeito aos limites da fase vigente e não constitui nova Gênese.

### Artigo 4.5 — Alavancagem

```
Alavancagem(t) = Σ │exposição nocional das posições abertas│ / Saldo_Inicial_Ciclo
```

Calculada sobre o valor nocional bruto, sem compensação entre posições, tendo por denominador o Saldo Inicial do Ciclo.

### Artigo 4.6 — Demais Definições

- **Tese Operacional:** hipótese técnica documentada que fundamenta a Operação, registrada no template de sinal. Para sistemas automatizados, a proxy observável da tese é o par {ativo, direção} sob regime de exclusividade.
- **Lucro Técnico:** resultado obtido pela liquidação parcial de posições defensivas em movimentos corretivos favoráveis, utilizável para redução de exposição líquida, melhoria de preço médio, redução de margem ou encerramento parcial de posições deficitárias.
- **DDI (Drawdown Inicial):** período em que a conta opera exclusivamente com o capital-base do ciclo, sem amortecimento de resultados acumulados.
- **DDC (Drawdown Compensado):** situação em que resultados positivos do ciclo geram margem patrimonial sobre o saldo de referência. Natureza exclusivamente contábil; não amplia limites de risco.
- **Fase da Conta vs. Fase da Grade Ativa:** a Fase da Conta decorre do DD nos termos do Art. 4.1; a Fase da Grade Ativa reflete a estrutura de posições remanescente após podas. A Fase da Conta rege limites; a Fase da Grade rege reconstrução.
- **VRM (Volatility Regime Metric):** razão ATR(55)/ATR(660), calculada no gráfico H4, com recálculo semanal no fechamento de sexta-feira [parâmetro sujeito a ratificação — Anexo C].

---

## Navegação

- Índice: [[JP Wealth OS/00 - PROJECT/Norma Vigente/00 - Estatuto V10]]
- Anterior: [[JP Wealth OS/00 - PROJECT/Norma Vigente/01 - Preâmbulo Institucional]]
- Próximo: [[JP Wealth OS/00 - PROJECT/Norma Vigente/03 - Livro II — Estatuto Operacional — Arquitetura Quadrifásica de Risco Vertical]]
