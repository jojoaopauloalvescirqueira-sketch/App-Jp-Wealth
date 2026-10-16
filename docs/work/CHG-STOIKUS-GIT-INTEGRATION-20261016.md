# Integração Stoikus 1.23.0/R5 ao JP Wealth atual

Autorização humana: integrar a última versão do Stoikus e executar commit, push e merge (2026-10-16). Reutilizar codex/stoikus-continuity-20261014, sem nova branch. Base remota main confirmada: 2b22175a4f3f47b1f289deca65366c4dc0445dca. Snapshot anterior em /private/tmp/jpw-stoikus-git-integration-20261016/pre-integration-snapshot.zip.

## Contrato
Preservar exatamente os fontes e ZIPs selados R5-R3, cálculo 1.9.0 e arquivos históricos. Integrar a interface, orientação e distribuição source-only 1.23.0, preservando melhorias da main (downloads lazy, MiniGames e demais módulos). Compilação, execução, instalação MT5 e aceite humano permanecem NOT_RUN. Não incluir correção F01 da worktree de segurança. Não publicar no GPT Sites nem atualizar instalador nesta ação.

## Trilhas revisáveis
1. Catálogo de distribuição e verificadores: acrescentar contrato R5 selado; preservar R4 e casos negativos/oráculos financeiros. Sem alterar CI, gates, AGENTS ou normas.
2. Página, download lazy e SW: preservar main, atualizar versão e instruções R5, hashes exatos e validação de integridade.
3. Validação final: leverage_suite --scope all, quality_gate --tier full, identidade, reprodução, revisão independente e GitHub CI antes do merge.

## Estado inicial
Reconciliação dos arquivos da main aplicada na working tree (sem commit); conflitos de apresentação e gerador pendentes. Nenhum envio remoto ainda. Git mantém HEAD 0037bd3. Todos os bytes MQL R5 conferidos antes da integração.

## Movimentação externa do repositório
O diretório canônico foi movido durante a tarefa para `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`. O Git reparou os apontadores das worktrees registradas pelo comando oficial `git worktree repair`, sem alterar código/dados/HEAD. Base main e a separação da correção F01 foram revalidadas.

## Correção de control plane histórica transportada
A integração conserva a correção já documentada em `docs/work/CHG-STOIKUS-DIDACTIC-20261015.md` para diferenciar links de navegação de dependências remotas em `tools/validate_project.py`. Sua regressão independente `tools/validate_external_resources_test.py` deve acompanhar o delta. Não remover controles de recursos externos nem ampliar exceções para fazer a integração passar. O runner quality_gate.py e os critérios financeiros da main permanecem iguais.
