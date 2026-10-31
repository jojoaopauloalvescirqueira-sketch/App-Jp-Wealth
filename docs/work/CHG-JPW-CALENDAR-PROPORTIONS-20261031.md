# Calendário — proporções e estados — 31/10/2026

## Autoridade e identidade

O proprietário pediu explicitamente a implementação do plano das quatro frentes nesta conversa e autorizou quatro worktrees isoladas. Branch desta frente: `codex/calendario-proporcoes-20261031`; BASE_SHA `69b6cb677de2486be5c30681e4b2e02d4180d704`. O checkout original estava limpo. Commit, merge, push e publicação novos não integram esta autorização de implementação.

O Harness externo referenciado no AGENTS não foi encontrado na migração. O proprietário autorizou usar os contratos e controles versionados nesta implementação, preservando os gates. Isso não altera AGENTS, autoridade futura nem a política do Harness.

## Compreensão e contrato

O JP Wealth organiza dados e análises financeiras locais. O calendário oferece consulta econômica e agenda pessoal nas superfícies do cabeçalho e workspace; o delta apenas melhora a legibilidade dos estados, sem alterar fontes, fatos ou comandos.

Fontes examinadas na base: `AGENTS.md` (qualidade e autoridade); `docs/governance/UI-VISUAL-QUALITY.md` (2 px, teclado, zoom e estados); `docs/architecture/CALENDAR-AGENDA.md` (grade de 44 px, marcadores, consultas sem gravação); renderizador19 e estilos locais. O commit histórico `c69b199` foi examinado como evidência e reaproveitado parcialmente; seu sublinhado de hoje não corresponde ao plano atual e foi substituído por numeral vermelho/negrito.

Produto N0-V/N1: hoje em vermelho e peso700, sem contorno; seleção em disco azul32x32 dentro do alvo44x44, numeral branco; hoje selecionado mantém peso700 e aria-current. Pontos econômicos vermelhos e pessoais azuis permanecem fora do disco. Capitalização de frase em mês/dia, sem text-transform capitalize. Foco de teclado continua no alvo externo, distinto dos estados de data.

Invariantes: tabelas econômicas de sete campos, fonte/ausências e detalhes, filtros, APIs/identidades da agenda, escritores/estado, preferências, rascunhos, ordem dos127scripts e ciclo PWA. Proibida limpeza/importação de dados reais.

## Controles e escopo

A alteração deliberada da expectativa antiga de contorno é parte expressa do plano aprovado. Controles de geometria são N3 de control plane e ficam identificados separadamente do produto neste contrato; nenhuma entrada obrigatória, tolerância ou prazo do runner é retirada ou reduzida. `calendar_proportions_contract.py` mede disco32/alvo44, cores, centro do conteúdo, marcadores e as duas superfícies, com violações representativas rejeitadas. Os testes existentes conservam as demais expectativas e incluem o novo oráculo.

Arquivos permitidos: JS19, CSS restrito a calendário, quatro testes de calendário/qualidade pertinentes, novo oráculo, índice de regressões, este contrato/brief, contexto factual desta frente e derivados oficiais. Gerados somente por `tools/rebuild_monolith.py --refresh-manifest`.

## Evidência e limites

Preflight audit/edit executados. Primeira tentativa de Chromium no sandbox: ENVIRONMENT_ERROR na inicialização, não RED. Execução com perfil sintético fora do sandbox reproduziu PRODUCT_FAIL de32px/capitalização/seleção/hoje na base anterior à correção. Recibos atuais ficam fora do repositório em `work/implementation/calendar-*` no workspace Codex; nenhuma passagem histórica equivale à validação nova.

Focais de geometria e contraprovas, matriz32casos, distribuições, FULL vigente e revisão independente precedem prontidão técnica. Aceite humano de Safari/toque/compreensão é separado. Rollback: reverter apenas este delta, reconstruir derivados e preservar dados/cache do proprietário; sem migração reversa.
