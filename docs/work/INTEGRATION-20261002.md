# Integração JP Wealth — 2026-10-02

Autorização humana: “faça push, merge coomit de todas as atualizações”. A ação cobre commit, merge na main e push; não cobre instalação no MT5, armamento, negociação ou publicação do site.

## Fontes preservadas

- Base remota: `deffc5061fe2eff3d83b6f6e742fa105ac9c5b06`.
- Site e Execution Board: checkpoint `4d89afa`.
- Genetrix Risk/Ledger 1.17.0: checkpoint `9000e26`.
- Genetrix Histórico Pessoal 1.18.0: checkpoint `91d4aaf`.
- As duas frentes MT5 carregavam um site anterior; o merge mantém os fontes web mais recentes e os módulos MT5 1.18.0. Manifesto, pacote, portátil e cache são derivados dos geradores oficiais.
- Alterações de links feitas pelo vault e duplicações ` 2` na main foram preservadas em snapshot e stash, sem introduzir regressões no produto. Outputs locais com bancos/executáveis sintéticos não entram no Git.

## Limites e dívida preservada

O site congelado anterior registrou standard 46 PASS e full 57 PASS. A auditoria de fronteiras financeiras encontrou 72 PRODUCT_FAIL em 1.080 casos, incluindo o DD matemático de 22% e fronteiras de fase. Esses defeitos não são corrigidos ou reclassificados pela integração. O problema do tratamento de timeout no executor geral e as divergências documentais continuam registrados na auditoria externa.

O MT5 permanece com compilação, interação, EX5 e prontidão operacional NOT_RUN/bloqueados. O Supervisor separado contém envio de ordens exclusivamente em demo hedging explicitamente armada, com padrão OBSERVE; nenhuma ativação é realizada aqui. A presença dos fontes não homologa parâmetros ou implementa integralmente o Estatuto.

Os resultados dos checks dos bytes combinados e a identidade final de Git serão registrados no recibo externo de integração. CI é uma verificação separada e não cobre automaticamente todas as novas suítes Genetrix.

## Recuperação

Há snapshots independentes das quatro worktrees e seus diffs antes da integração. O rollback de código deve usar revert dos commits/merges autorizados, preservando os registros e dados do usuário; não usar reset destrutivo. O stash da main conserva as alterações do vault separadamente para consulta, sem reaplicação automática sobre a versão integrada.
