# Stoikus — escopo como projeto independente para MetaTrader 5

- Data: 2026-10-22
- Status: aprovada
- Responsavel pela aprovacao: proprietário do JP Wealth
- Nivel: arquitetura (delimitação documental, N0-D)
- Fonte normativa relacionada: nenhuma alterada; Estatuto JP Wealth como base normativa compartilhada

## Contexto

O nome "Stoikus" designava duas coisas: a suíte MQL5 em `mt5/jpw-alavancagem-atual/` (Monitor, Conta, NoCuda, Abrir Painéis) e o botão "Stoikus ▾" do Planejamento patrimonial, um menu de ações do aplicativo web sem relação com MQL5. O proprietário pediu uma delimitação clara.

## Decisao

**Stoikus é um projeto independente do JP Wealth para MetaTrader 5, escrito em MQL5, que complementa o JP Wealth OS.**

- **O que é:** o sistema de gerenciamento e monitoramento de conta no MT5. Componentes atuais: Monitor da conta (observador, não negocia), Stoikus · Conta, NoCuda · Gráficos, Abrir Painéis e o Supervisor opcional de proteção 7x. NoCuda é componente do Stoikus e conserva nome e identidade visual próprios.
- **Independência:** versão própria (hoje 1.23.0, produto C5, cálculo 1.9.0), separada do build do aplicativo web; ciclo próprio, em que fontes, compilação, distribuição e aceite são estados distintos dos do aplicativo; instruções e harness próprios em `mt5/jpw-alavancagem-atual/AGENTS.md`, subordinados às regras do repositório; execução no MT5, nunca no navegador. O aplicativo não executa, compila nem certifica o Stoikus.
- **Complementaridade:** o aplicativo explica e distribui o Stoikus (área "Stoikus — MT5", downloads e instalador). Ambos partilham a base normativa do Estatuto JP Wealth; o Stoikus usa definições do Estatuto, mas não comprova conformidade de operações nem substitui o motor Forex do aplicativo, e esse motor não executa o Stoikus. Hoje não há troca de dados em execução entre os dois; qualquer integração futura, como importar leituras do MT5 no aplicativo, exige contrato próprio e autorização do proprietário.
- **Localização:** `mt5/jpw-alavancagem-atual/` (nome de pasta legado), no mesmo repositório. Separar em repositório próprio seria decisão posterior.
- **Exceção de nome:** o botão "Stoikus ▾" do Planejamento patrimonial é um menu do aplicativo web e não pertence a este projeto. O proprietário escolheu manter o nome e documentar a exceção.

## Alternativas consideradas

- Renomear o menu do Planejamento para "Ações ▾": recusada pelo proprietário nesta decisão.
- Tratar NoCuda como sistema separado: recusada; NoCuda é componente do Stoikus.
- Repositório próprio para o Stoikus: não decidida; fora do escopo.

## Consequencias e riscos

Agentes e documentação passam a tratar o Stoikus como projeto complementar, fora da tabela dos cinco módulos do aplicativo. As instruções locais `mt5/jpw-alavancagem-atual/AGENTS.md` ainda abrem com o mapa "GENETRIX 1.20.0"; sua atualização é alteração de control plane (N3) e permanece pendente, fora desta decisão.

## Exemplos e casos-limite

- Pedido sobre o painel C5, o Monitor ou o NoCuda no MT5: escopo Stoikus.
- Pedido sobre a página "Stoikus — MT5" ou os downloads no site: aplicativo web, como distribuidor do Stoikus.
- Pedido sobre o botão "Stoikus ▾" do Planejamento: aplicativo web, módulo Planejamento.

## Impacto em codigo, dados e testes

Nenhum. Somente documentação: esta decisão, `docs/governance/PROJECT-CONTEXT.md`, `docs/governance/CONTEXT-MAP.md` e `docs/architecture/PLANNING.md`. Fórmulas, código, interface, dados e nomes de pastas permanecem inalterados.

## Plano de migracao/rollback

Sem migração. Rollback: reverter os quatro arquivos documentais.

## Evidencia de aprovacao

Conversa com o proprietário em 22/10/2026: respostas "Manter e só documentar" (menu do Planejamento) e "Componente do Stoikus" (NoCuda); em seguida, "quero definir dentro do projeto, o escopo do stoikus, ele é um projeto independente para metatrader 5 que complementara o jp os" e a aprovação do texto proposto, "Aprovo o novo texto de escopo do Stoikus como projeto independente dentro do repositório".
