# Brief — Lateral padrão JP Wealth

N1/A2. Solicitação humana atual: implementar o plano completo aprovado; somente sidebar. Raiz e branch no CHG. Baseline preservada com639 arquivos e138 entradas dirty, originadas de tarefas anteriores conhecidas nesta conversa; não serão sobrescritas fora da allowlist. Snapshot externo BASELINE.json e baseline.tar.gz. Preflight audit PASS; edit inicialmente BLOCKED por dirty não confirmado, depois PASS com --allow-dirty após confirmação/hash. SOURCE REVISION UNKNOWN permanece explícito.

## Compreensão

1. JP Wealth organiza gestão financeira e leitura de risco; esta tarefa torna sua navegação previsível sem alterar mensuração.
2. O shell coordena apresentação e foco; o resolver central possui rotas, guards e ownership. Estilos/sidebar/preferences pertencem à UI, fora de S.
3. Hoje N2 segue apenas a rota e pai navega. Depois hover/pai exploram qualquer grupo sem navegar; somente folha passa pela fachada.
4. Consumidores: quatro layouts, N3 local, Configurações que empresta railToggle, Notas/modais, deep links Genetrix, preferências/backup e focais de navegação.
5. Preservar fórmulas, schema, registros, MT5/ZIP, disponibilidade, rascunhos, guards, IDs e aliases. Não clonar nós, criar preferências ou alterar gates/Harness.
6. Provar zero navegação/guard/storage/render de domínio em exploração, despacho único em folha, N3 intacto, overlay sem reflow, clique/teclado/mobile e todos layouts/temas.

## Fontes e evidência

AGENTS.md, README, CONTEXT-MAP, PROJECT-CONTEXT e CURRENT-STATE lidos no bootstrap; skills preflight/change-control/design/browser/test-triage/security/post-change e feature-atlas lidas. Atlas parcial não substitui originais. NAVIGATION-HIERARCHY descreve contrato histórico sem hover; complemento atual aprovado explicitará mudança. 01-navigation listener direto usa shellHandlePrimaryIntent; 11-operational-shell listener delegado também processa pais e acopla contextos à exploração; 09-settings empresta railToggle. Hashes exatos de cada fonte no BASELINE.json. Harness disponível no caminho real do CHG, hash conferido; caminho antigo de AGENTS foi localizado pela fonte atual da tarefa anterior, sem reconstrução por memória. X1 é síntese autoral, não especificação Apple.

## Delta e segurança

Estado de exploração privado/efêmero. Tema restrito à sidebar/#navLocalSlot. Sem novo HTML externo, URL, rede, storage financeiro, dependência, executor ou credenciais. Controle compartilhado restaurado conforme owner; cancelar timers em modais/layout/breakpoint. Dados e browser exclusivamente sintéticos. Focais poderão mudar expectativas de pai/hover somente pela decisão humana explícita, sem enfraquecer guardas ou reclassificar falhas.

## Agentic IMPACT

Mudança material do contrato de apresentação consumido por agentes em NAVIGATION-HIERARCHY; reconciliar com complemento datado e ACTIVE-TASK/nota focal CURRENT-STATE. Não mudar instruções, routing, registry, autoridade, gates, schemas ou reindexar. Historia correta preservada. Auditor deverá conferir fechamento semântico do complemento e leitores existentes.

## Delegação e aceite

Root: controlador/coordenação/CHG/derivados. Design: somente CSS. Testes: novo focal e expectativas funcionais aprovadas. Revisão independente sem escrita no produto depois do freeze. Critérios detalhados no CHG/plano humano; gate standard e full brutos, capturas, relatório/fingerprint/rollback externos. Candidate local não significa aceite, integração ou publicação.
