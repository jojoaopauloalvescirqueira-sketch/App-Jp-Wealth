# Brief — evolução da conta e risco visual no Forex

## Identidade e autorização

Base main ac3a2faffeb398357ff105adbf1d47f70ca309bd, preservada em baseline.tar.gz e baseline.json fora do candidate. Candidate isolado codex/forex-visual-risk-20261005. Pedido humano vigente aprova implementação local; CHG produto N1/A2 e teste N3/A4 separado. Sem commit, integração, publicação ou leitura de perfil financeiro real.

## Compreensão e fontes

1. JP Wealth organiza registros e leitura de risco; esta tarefa melhora a comparação dos dados existentes, sem criar autorização operacional.
2. UI 28-fx-consolidated recebe series/metrics de 17-fx-consolidated-model; UI 30-execution-board consome 18-execution-board-model. Domínio continua único produtor dos valores.
3. Base tem crescimento duplicado, SVG esticado e eixo por índice; candidate deve ter curva única, escala temporal verificável, teclado/toque e tabela. Operação recebe barras dos valores confirmados já usados na grade.
4. Conta consultada da Visão geral difere da operacional do Board; fontes MT5/Manual nunca se fundem. Barras usam operationalRisk, percentual book, não risk percentual SI. Pendentes separadas; rascunhos não alteram dados confirmados.
5. Preservar 20 colunas, 14/36 desktop e 16/48 toque, guardas, explicit save, unidade, contexto, schemas, política/engine, MT5, distribuição/cache e quatro layouts. Equity vazia não vira curva. Ausência não vira zero. Falha DD14 permanece PRODUCT_FAIL.
6. Focais sintéticos em domain real, tasks/drafts/resize, escala temporal irregular/fallback, 1/10/30 ordens, teclado/toque e zoom nativo. Depois standard/full bruto e auditor independente; nenhuma evidência anterior aceita novos bytes.

Fontes lidas: AGENTS.md; README; CONTEXT-MAP; PROJECT-CONTEXT; CURRENT-STATE; ACTIVE-TASK histórico; FOREX-V11-ENGINE; FOREX-EXECUTION-BOARD; FOREX-CONSOLIDATED; skills preflight/change-control/design/browser-verification/post-change-audit/agentic-evolution-governance. Fontes locais são da base acima, hashes em baseline.json. Harness canônico localizado em 2 - TRABALHO/7C - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md (caminho antigo do AGENTS está indisponível); SHA256 b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95, §§12–19: autorização, freeze, evidência e bloqueio. Sem alteração dessas fontes.

## Delta, segurança e evidência

Apresentação pura das séries/métricas, classes locais, gráficos sem biblioteca externa. Escapar textos e identidades. Estado visual só RAM. Render/hover/foco não escrevem dados. Sinais financeiros e cores existentes preservados; não calcular limites ou inferir rentabilidade.

Delegação separa UI Overview, UI Board, juiz focal e auditor independente; root integra CSS, derivados, documentação e gates. Browser sintético descartável, execução sequencial. Fontes e juízes congelados antes de evidência final. Alteração posterior invalida recibo afetado.

Rollback: restaurar somente delta a partir do snapshot externo; sem migração financeira, sem tocar dados reais. Revisão independente e aceite humano separados; pronto para visualização não significa aprovação financeira ou publicação.
