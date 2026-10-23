# Notificações — brief de implementação —22/10/2026

## Identidade e autorização

Branch `codex/notificacoes-acoes-20261022`, base `d517be0748f8`; raiz real CloudDocs/SOFTWARES & EAS/JP Wealth OS. Plano humano aprovado nesta conversa e branch especificamente autorizada. Produto N1/A2; verificadores em CHG N3/A4 dedicado conforme pedido explícito. Não inclui Git final/publicação, dependências, migração ou memória global. As14 alterações anteriores estão registradas e preservadas no baseline recuperável em `.superpowers/sdd/2026-10-22-notification-actions/`.

## Compreensão e fontes

1. JP Wealth organiza finanças locais/PWA; o sino deve dirigir a ação pertinente sem se tornar motor financeiro. Fonte: PROJECT-CONTEXT, finalidade Produto; NOTIFICATION-CENTER, finalidade e semântica.
2. A central projeta leituras canônicas; Planejamento comanda fatos e oferece consultas readonly. Fontes: `18-notification-center.js`, `06-planning/02-state.js`.
3. Antes: clearance sempre BLOCKED despeja todos motivos; leitura zera badge embora a causa continue; agenda/atividade/rascunhos são contados. Depois: somente ações ativas, agrupadas, contexto/CTA específico e detalhe progressivo; fonte sem verificação não parece saudável.
4. Afetados: sino, disponibilidade, queries Planning, guards de navegação, preferência de filtros mensais e distribuição. Consumidores antigos open/close/refresh/invalidate preservados; nova fonte planning e consulta pendingActions.
5. Preservar fórmulas/limites/clearance/eligibilidade financeiros, comandos e confirmações, rascunhos, dados reais, preferências, backup e três minigames/Bolsas Globais. Informações estáticas continuam nas origens. Sem novos escritores/normalização de leitura.
6. RED/GREEN de pertinência/contagem; consulta com zero/ausência/anulados/arquivados/invalidado/anterior bloqueante; browser real com zero writes/fetch; matriz visual e distribuições; contraprovas e revisão independente; FULL final estável. Evidências anteriores não são PASS atual.

## Plano e fronteiras

Contratos dedicados PRODUCT/TESTS listam os arquivos. Reutilizar script clássico e caches porfonte. Texto seguro via textContent/escape existente. Somente dados sintéticos em navegador novo. Invalidação após confirmação, observador isolado. Consulta pendências não roda timeline120. Fonte indisponível mantém último diagnóstico marcado não atual sem dupla contagem. Resolver/exibir aviso não executa comando financeiro. Guard de contexto revalida após consentimento sem escolher conta automaticamente.

## Contexto e controle

AGENTS, Harness §§11–16/19 e contratos pertinentes lidos; hashes do baseline e da fonte Harness abaixo. O aviso de frescor material ea15afc é preexistente; inspeção factual do estado atual não transforma documentos históricos em runtime. Este delta altera representação contratual da central: AGENTIC IMPACT DETECTED, alcance local em contrato/brief/registros desta tarefa, sem instruções/plugin/gates globais novos. ACTIVE-TASK recebe ponteiro focal, preservando histórico.

Rollback apenas do delta próprio com baseline; nunca reset/stash ou limpeza de preferências. Human acceptance e publicação permanecem separados.

Harness SHA256: `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`.
- `AGENTS.md`: `7a9b8d08e1bca6adc1c366a1872215bf3671aa9f9804cc702cfc94618063225e`.
- `docs/architecture/NOTIFICATION-CENTER.md`: `cd56a48c07ff25ff52eaf84d04159bf43cf30f696635e19fc362498c2bd6df70`.
- `src/js/40-app/18-notification-center.js`: `7f852a4f0f24c35fdb0cc48c73b0137ad229472eef7944799ad601df5fb022e4`.
- `src/js/30-accounting/06-planning/02-state.js`: `53287b45ad24bf12b2f8a6beac4b324225f24e5656e2f19492708863e2c0c6c2`.
