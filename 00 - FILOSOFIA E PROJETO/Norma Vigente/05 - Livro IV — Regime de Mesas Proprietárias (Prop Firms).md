---
tipo_nota: norma
dominio: jp_wealth
documento: JPW-GOV-001
versao: "10.0"
status: vigente
livro: "IV"
titulos: "19–22"
aliases:
  - "Livro IV — Regime de Mesas Proprietárias (Prop Firms)"
  - "Livro IV"
---

# Livro IV — Regime de Mesas Proprietárias (Prop Firms)

> Títulos 19 a 22 · Artigos 19.1 a 22.5

## Título 19 — Adaptação do Modelo e Revogações

### Artigo 19.1 — Migração Integral para a Arquitetura V9.0+

Este Livro substitui integralmente o Estatuto Normatizado para Mesas Proprietárias anterior. Ficam expressamente revogados, por incompatibilidade com a Arquitetura de Risco Vertical: o regime de DDR de 12%; a tolerância a duas ou três operações simultâneas; e os fatores de correção de 66%, 50% e 33% (substituídos pelo Título 10 do Livro II). As contas de prop firm operam sob a mesma Operação Única Exclusiva da Conta Mestre, replicada pelo Firewall Assimétrico.

### Artigo 19.2 — Regras Contratuais de Referência (FTMO / The5%ers / The Trading Pit)

- Challenge em duas fases: meta de 10% (Fase 1) e 5% (Fase 2), com perda diária de 5% e perda máxima de 10%; mínimo de 4 dias operacionais;
- Maximum Daily Loss: 5% do saldo inicial, recalculado diariamente sobre o maior valor entre balance e equity no início do dia — regra mais crítica do regime, cuja violação, mesmo por flutuação momentânea de equity, encerra a conta sem recurso;
- Maximum Loss: 10% do saldo inicial, fixo; violação implica encerramento definitivo;
- Saques a cada 15–30 dias, com reembolso da taxa após aprovação; divisão de lucros 80/20, elevável a 90/10;
- Inatividade: ausência de operações por mais de 30 dias pode encerrar a conta;
- Vedações comportamentais: variações abruptas de risco sem consistência histórica; comportamento de pass-through não institucional; padrões estatísticos incompatíveis com trading humano.

## Título 20 — Salvaguardas Internas

### Artigo 20.1 — Daily Loss Interno de 4%

O limite interno de perda diária das contas financiadas é de 4% — mais rígido que o contratual de 5% —, implementado por monitoramento automatizado 24/7 (Traders Connect), com encerramento das operações e desativação automática do copy ao acionamento.

### Artigo 20.2 — Reingresso após Daily Loss

**§1º** — Conta cortada por daily loss NÃO reingressa na Operação em andamento da Conta Mestre. Seu reacoplamento ao sistema de cópia ocorrerá somente na próxima Ordem Gênese.

**§2º** — Se o corte decorreu de erro de gestão (e não de travessia ordenada de fases), aplica-se adicionalmente período de espera de 1 semana, destinado a reavaliação de estratégia, recomposição emocional e ajuste do plano.

### Artigo 20.3 — Retenção Estratégica de Lucros

Política de represamento dos primeiros 3% de lucro de cada conta financiada, elevando o colchão efetivo frente ao Maximum Loss; retenção mínima mensal de 2% de lucro; revisão a cada ciclo.

**§1º** — Esta política protege contra a eliminação contratual da conta satélite e não constitui, em hipótese alguma, autorização para ampliar alavancagem, alargar stops ou flexibilizar a Matriz Quadrifásica — vedação do Art. 12.2 integralmente aplicável.

### Artigo 20.4 — Ressincronização

Técnica de realinhamento entre balance e equity (fechar e reabrir posições no mesmo ponto) para conter o descolamento contábil que fragiliza a conta frente ao daily loss recalculado. Política: ressincronizar sempre que o drawdown diário estiver abaixo de 4% no dia seguinte ao recálculo. Custos reconhecidos: slippage e spreads/comissões adicionais.

### Artigo 20.5 — Simulação Obrigatória Fases × Daily Loss

Antes da ativação de qualquer conta em perfil Longevity, o Compliance Board validará simulação da interação entre travessia rápida de fases da Conta Mestre e o daily loss interno de 4%, certificando que a poda LIFO compulsória não colide com o corte automático de copy [Anexo C].

## Título 21 — Estrutura de Contas e Perfis

### Artigo 21.1 — Segregação

As contas não serão unificadas via merge account, preservando a diversificação tática entre perfis (Longevity, High Longevity, High Longevity Plus) conforme Título 10 do Livro II e o princípio deliberado: quanto maior o risco do perfil, menor o teto de participação na carteira.

### Artigo 21.2 — Estrutura Planejada de Adesão

| **#** | **Instituição** | **Capital** | **Perfil** |
| --- | --- | --- | --- |
| 1 | FTMO | $100.000 | Longevity |
| 2 | FTMO | $100.000 | Longevity |
| 3 | FTMO | $100.000 | High Longevity |
| 4 | FTMO | $100.000 | High Longevity Plus |
| 5 | The5%ers | $100.000 | High Longevity |
| 6 | The Trading Pit | $100.000 | High Longevity |

## Título 22 — Instrumentos, Tetos e Atividade

### Artigo 22.1 — Tetos de Exposição por Instrumento (conta de referência JP Wealth MAM)

| **Instrumento** | **Teto (lote)** | **Status** |
| --- | --- | --- |
| EUR/USD | 0,05 | Ativo |
| GBP/USD | 0,04 | Ativo |
| AUD/USD | 0,09 | Ativo |
| NZD/USD | 0,09 | Ativo |
| USD/JPY | 0,05 | Ativo |
| USD/CHF | 0,05 | Ativo |
| USD/CAD | 0,05 | Ativo |
| AUD/CAD | 0,11 | Ativo |
| US500 | — | SUSPENSO — fora do escopo Forex vigente [ratificar exclusão definitiva, Anexo C] |
| XAU/USD e demais metais | — | VEDADO — proibição permanente por decreto do Gestor (Art. 22.2) |

**§1º** — Tabela revisada nesta consolidação (base anterior: 07/07/2025). A cada conta satélite aplica-se o fator do respectivo perfil sobre estes tetos, após normalização por saldo. Revisão obrigatória a cada alteração relevante de valor nominal dos contratos.

### Artigo 22.2 — Vedação Permanente de Metais

Fica terminantemente proibida a operação de XAU/USD e demais metais, em qualquer conta da estrutura. Registro de fundamento: o histórico documentado da gestão demonstra que as perdas de mesas proprietárias e parcela relevante dos prejuízos pessoais decorreram da operação de ouro sob viés de teimosia ("o ouro me deve algo"). A vedação é comportamental e definitiva; sua remoção exigiria emenda formal com justificativa quantitativa, parecer da Auditoria e deliberação unânime do Compliance Board.

### Artigo 22.3 — Diferenças Estruturais Reconhecidas

As mesas proprietárias impõem limites inflexíveis e absolutos que exigem: redução da alavancagem real frente ao padrão institucional; monitoramento da velocidade de flutuação (o risco de violação é temporal, não apenas financeiro); e aceitação do snapshot contábil diário, inexistente no ambiente institucional.

### Artigo 22.4 — Destino dos Saques

Por deliberação do Gestor Geral (Anexo B, D-1), 100% dos saques líquidos das prop firms, após encargos, destinam-se ao Caixa Central da Holding, sob os critérios macro do Livro V. A Auditoria atua como custodiante e executora da transferência, sem poder de destinação. Fica revogada a autonomia de destinação anteriormente atribuída à supervisora.

### Artigo 22.5 — Operação Simbólica de Atividade

A cada 15 dias sem novas ordens, a Auditoria executará operação simbólica de lote mínimo (0,01), aberta e imediatamente fechada, exclusivamente para reiniciar o contador de inatividade.

**§1º** — Exceção formal à exclusividade do Art. 5.1: a operação simbólica é permitida mesmo com Operação ativa, desde que em ativo distinto, com duração inferior a 60 segundos e registro obrigatório.

**§2º** — Para não constituir padrão estatístico detectável, horário, ativo e intervalo exato serão variados dentro da janela regulamentar.

---

## Navegação

- Índice: [[JP Wealth OS/00 - FILOSOFIA E PROJETO/Norma Vigente/00 - Estatuto V10]]
- Anterior: [[JP Wealth OS/00 - FILOSOFIA E PROJETO/Norma Vigente/04 - Livro III — Governança, Funções e Controles Humanos]]
- Próximo: [[JP Wealth OS/00 - FILOSOFIA E PROJETO/Norma Vigente/06 - Livro V — Alocação Patrimonial, Tesouraria e Distribuição]]
