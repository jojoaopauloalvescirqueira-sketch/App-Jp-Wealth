# CHG-FOREX-V11-CENTRAL-20260914 / CTX-FOREX-V11-CENTRAL-20260914

## Autoridade e identidade
N3 financeiro / A4. Pedido FOREX-V11-CENTRAL-01 e autorização específica de isolamento de 2026-09-14 na sessão atual: implementação integral, migrações sintéticas, testes, documentação técnica, build, auditoria e candidate local. Sem commit, publicação ou deploy.
ROOT: /Users/joaopauloalves/.codex/forex-v11/20260914/product
BRANCH: codex/forex-v11-central-engine-20260914
BASE_SHA: edcdd82fee5a220fcee282552a5b607cec563d3f
BASE_TREE: 81801da10214a4b730cc89a772576ea5ee32e037
BASE_BUILD: 154676b1f178260d
Main remota conferida igual antes da criação. Worktree nova limpa, sem trabalho preexistente.

## Brief / compreensão
Forex registra fatos de ordens, contas, reservas, contabilidade e projeções. Legado: quatro fases, DD por perdas/risco e guards espalhados. Resultado: registry versionado, funções puras, read-model único, seis fases por equity e atos explícitos auditáveis. Registro desconforme continua possível; gravar não autoriza execução. UI consome domínio. Dados, aliases, rascunhos, histórico, locks, epoch, UNKNOWN e recuperação precisam sobreviver.
Fontes, consumidores, escopo e oráculos completos em ../evidence/PROPOSAL.md, preimplementation-package.json, TASK-BRIEF-preimplementation.json e reference-oracles-before-implementation.json. São preparação, não validação do produto.

## Fontes e decisões
Harness MASTER SPECIFICATION SHA256 c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8.
Constituição I.6/I.7 > PDF V11 SHA256 2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769 > Anexo JPW-ANNEX-T03 SHA256 6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23 nos elementos delegados. Exemplares e linhas no pacote externo.
Preservar conflitos: FCR capital nominal Mestre versus SI; FEO/apuração/homologação; agregado inclui pendentes ampliadoras; canonicidade não homologa. DD>=22 tem precedência. P14/P17/P18/P10/P30 e demais lacunas não admitem zero/fallback. Não adotar outro Livro IV por inferência. Valores históricos não alimentam política vigente.

## Limites
Preservar principal, Notas, conflitos/staged/stash, recuperação, outras worktrees, SESSION_HANDOFF, CURRENT-STATE, ACTIVE-TASK e NAV-REF. Autorização atual prevalece sobre ACTIVE-TASK sugerido na skill/proposta. Sem AGENTS, CLAUDE, skills, policies, SECURITY-MODEL, gates, CI, dependências ou correções adjacentes. Documentar segurança implementada somente no documento técnico do motor. Nenhuma senha fornecida em fonte, hash fixo, estado, log ou fixture. Client-side não representa autenticação contra o dono da origem.
Scripts clássicos, protocolos de persistência, key e proteção de dados preservados. Migração explicitamente versionada; legado não é reescrito/reinterpretado. ACTUAL nunca é sobrescrito por projeção. Calendário mantém fonte única.

## Caminhos diretamente necessários
- `src/js/00-core/01-risk-profiles.js`
- `src/js/00-core/03-default-state.js`
- `src/js/00-core/04-persistence.js`
- `src/js/10-domain/01-risk-instruments.js`
- `src/js/10-domain/02-risk-calculations.js`
- `src/js/10-domain/03-phase-transitions.js`
- `src/js/10-domain/04-stop-statistics.js`
- `src/js/10-domain/06-quarantine.js`
- `src/js/10-domain/07-reserve-requirements.js`
- `src/js/10-domain/11-operation-lifecycle.js`
- `src/js/20-ui/01-header-readout.js`
- `src/js/20-ui/03-main-render.js`
- `src/js/20-ui/04-operational-clearance.js`
- `src/js/20-ui/05-execution-clearance.js`
- `src/js/20-ui/08-input-bindings.js`
- `src/js/20-ui/11-phase-posture.js`
- `src/js/20-ui/13-exec-views.js`
- `src/js/20-ui/16-operation-history.js`
- `src/js/20-ui/25-dash-macro.js`
- `src/js/30-accounting/01-daily-ledger.js`
- `src/js/30-accounting/02-accounting-engine.js`
- `src/js/30-accounting/05-fx-planning/01-fx-model.js`
- `src/js/30-accounting/05-fx-planning/02-fx-engine.js`
- `src/js/30-accounting/05-fx-planning/03-fx-state.js`
- `src/js/30-accounting/05-fx-planning/04-fx-charts.js`
- `src/js/30-accounting/05-fx-planning/05-fx-ui.js`
- `src/js/40-app/01-navigation.js`
- `src/js/40-app/02-reset.js`
- `src/js/40-app/04-onboarding.js`
- `src/js/40-app/06-boot.js`
- `src/js/40-app/07-finalize-session.js`
- `src/js/40-app/09-settings-modal.js`
- `src/js/40-app/11-operational-shell.js`
- `src/js/40-app/12-global-dashboard.js`
- `src/js/40-app/13-dashboard-layout.js`
- `src/js/40-app/18-notification-center.js`
- `src/js/manifest.json`
- `index.html`
- `src/styles/app.css`
- `sw.js`
- `build-id.js`
- `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`
- `tools/order_guards_test.py`
- `tools/phases_visibility_test.py`
- `tools/state_integrity_test.py`
- `tools/operation_identity_test.py`
- `tools/operation_wiring_test.py`
- `tools/operation_finalize_test.py`
- `tools/operation_history_test.py`
- `tools/operation_copy_test.py`
- `tools/forex_persistence_contract_test.py`
- `tools/fx_planning_test.py`
- `tools/navigation_ia_test.py`
- `tools/navigation_local_contract_test.py`
- `tools/exec_submenu_test.py`
- `tools/dashboard_macro_test.py`
- `tools/dashboard_forex_relocation_test.py`
- `tools/settings_modal_test.py`
- `tools/import_xss_security_test.py`
- `tools/notification_center_test.py`
- `docs/architecture/CODE-MAP.md`
- `docs/architecture/STATE-SCHEMA.md`
- `docs/architecture/FX-PLANNING.md`
- `docs/architecture/NAVIGATION-HIERARCHY.md`
- `docs/architecture/DB-STORAGE-GOVERNANCE.md`
- `README.md`
- `src/js/30-accounting/04-patrimonial-simulation.js`
- `tools/backup_reliability_test.py`
- `tools/storage_governance_test.py`
- `tools/finalize_session_test.py`
- `tools/navigation_order_test.py`
- `tools/navigation_layout_choice_test.py`
- `tools/forex_context_bar_test.py`
- `src/js/00-core/00-forex-policy.js`
- `src/js/10-domain/00-forex-engine.js`
- `src/js/20-ui/26-forex-engine-views.js`
- `tools/forex_v11_engine_test.py`
- `tools/forex_v11_journey_test.py`
- `docs/architecture/FOREX-V11-ENGINE.md`
- `docs/work/CHG-FOREX-V11-CENTRAL-20260914.md`

Outros arquivos técnicos/testes diretamente necessários podem ser registrados antes da edição conforme autorização explícita; nenhuma ampliação material implícita.

## Validação
Caracterizar APIs atuais antes da transformação, usando baseline fiel e dados sintéticos. Expectativas antigas ficam preservadas como evidência histórica; alterá-las só para comportamento expressamente substituído pela V11. Casos independentes já fixados no JSON de oráculos.
Focais: fronteiras DD, H4/histerese, conta/grade, min(SI,equity), VRM/stop/três riscos, reservas, PENDING, registro BLOCKED e correção/anulação; projeção, rebase e cenários sem escrita em ACTUAL; editor/sessão/expiração/audit sem segredo estático.
Persistência: vazio, legado, inválido, quota/recusa, UNKNOWN, reload, roundtrip, extensões, concorrência e recuperação. Navegador isolado, fixtures sintéticas, sem APIs econômicas ao vivo; sete rotas, aliases, conta, Settings, calendário, teclado, celular/desktop, claro/escuro.
FULL existente obrigatório no final. Build/manifest/portátil pelo processo oficial. Não mudar gates, remover asserts válidos ou transformar NOT_RUN em PASS. Freeze deve vincular hashes/modos, build, diff, testes, auditorias independentes e recovery. Nenhum aceite/homologação/validação empírica presumidos.

## CTX
Documentação técnica apenas diretamente afetada; agregadores protegidos permanecem intocados, com divergências registradas, sem reindexação. Evidência externa é mecanismo de campanha, não altera autoridade.

## Recuperação
../evidence/baseline-edcdd82.tar e baseline-inputs.json preservam base. Recuperação final nova não sobrescreve estes registros. Rollback limitado ao próprio delta nesta worktree, sem reset, stash, clean ou mudanças nas demais.

## Estado
IMPLEMENTATION_AUTHORIZED — nenhum candidate validado ainda. CI de Notas é evidência da base, não prova da V11.

## Localização adicional diretamente necessária — 2026-09-14
- `src/js/10-domain/00-forex-state.js`: adapter do domínio, observações com proveniência, comandos, migração explícita e sessão local de propostas. Separado das funções puras; não cria outro store financeiro ou backend.
- `src/js/00-core/05-helpers.js`: representar valores ausentes como indisponíveis nos formatadores existentes, mantendo a saída dos números válidos; não calcular finanças na apresentação.
- `tools/forex_v11_ledger_planning_test.py`: prova focal do ledger, cenários, rebase e origem do realizado, fora da definição dos gates.

Complemento de caminhos diretamente necessários: `tools/forex_recording_test.py` caracteriza registro explícito sob BLOCKED e sua persistência. O teste pertence ao produto, não altera os gates.

Testes focais adicionais diretamente necessários: `tools/forex_v11_state_test.py` (atos/segurança/migração) e `tools/forex_v11_journey_test.py` (formulários/rotas/derivados/teclado/responsividade). Oráculos fixados antes da execução de navegador; fixtures nominais existentes e nenhuma alteração de gate.

Consumidor real adicional: `src/js/40-app/05-wipe-all.js`, exclusivamente o binding de `quarantineConfirmBtn` em bindConfig. Remove o prazo fixo de 90 dias e registra o evento via comando Forex com motivo/rollback. Nenhuma alteração no wipe, backup, proteção, locks ou importação desse arquivo.

### Focal adicional de associação e projeção
`tools/forex_v11_read_model_test.py`: contraprova anterior à correção e regressão de pendência sem estado, conta/período/moeda, capitais conflitantes e origem do risco de admissão. Escopo N3 já autorizado; somente dados sintéticos, Node VM existente, sem gravação/rede. Rollback restrito ao teste e delta de read-model/sonda associado.

### Consumidores de navegação diretamente afetados
`tools/contextual_sidebar_test.py` e `tools/forex_context_bar_test.py` complementam os testes já listados de navegação para sete destinos, Contabilidade e a projeção única de equity. Preservar atomicidade, preferências, aliases, teclado, foco, métricas, ausência de escrita e recursos. Oráculos substituídos somente após falha observada e vínculo com o contrato deliberadamente alterado. Sem alterar o gate.

### Aviso documental dentro do runtime
`tools/statute_documentary_test.py`: somente o oráculo da frase externa ao leitor é atualizado de motor legado ainda não adaptado para motor V11 em validação. Mantidos hashes do texto integral, originais offline, consentimento explícito/versionado, não homologação, não autorização e ausência de escrita por leitura. `04-onboarding.js` não altera o texto integral do Estatuto/Anexo. Valores de reserva em branco continuam ausentes e a projeção consome somente observações conciliadas da conta/período.

### Contraprovas focais do histórico e unidade
`tools/forex_v11_history_test.py` acrescenta observações Node/Chromium dos consumidores de `src/js/20-ui/16-operation-history.js`, junto à regressão `tools/operation_copy_test.py`. Preservar moeda e contexto efetivamente capturados; resultados desconhecidos não viram zero e dados atuais não completam registros antigos. Totais de moedas diferentes ficam indisponíveis. `01-risk-instruments.js` vincula os adapters à conta/período/moeda do fato; as três falhas anteriores e os 17 resultados posteriores estão nos recibos read-model-order-scope.
A revisão focal identificou duas falhas antes do freeze: pico de fase omitido na confirmação de equity e ciclo/histórico sem unidade segregada. A confirmação explícita inclui o pico da operação no rollback delimitado; nenhuma leitura passa a gravar. Novas operações V11 registram resultado/contexto no histórico, preservando o acumulado LEGACY sem somá-lo a outra moeda/período. Focais de recusa, UNKNOWN, idempotência e contexto cobrem o delta. Rollback somente desses arquivos/delta próprio; nenhum histórico real é migrado ou reescrito.

### Cobertura normativa pré-freeze — orçamento e traço
O escopo original de sequência risco→fase→VRM→orçamento/agregado é completado nos mesmos `00-forex-engine.js`, `00-forex-state.js`, `02-risk-calculations.js`, `26-forex-engine-views.js` e seus testes focais. PDF p66 Art8.2§2–7 e p71 Art8.4§10–13: o orçamento é declaração factual específica, não parâmetro N3; aumentos são recusados, reduções exigem RC conhecido compatível. Versões, autoria declarada e associação à operação permanecem auditáveis. Declaração anterior ao primeiro registro local não prova execução prévia no mercado. P14/P18 impedem a etapa inicial do dimensionamento: volume final null, dependências NOT_EVALUATED, sem lote mínimo ou arredondamento falsamente validados. P2 do firewall corrigida com contraprova independente: margem superior ao limite não representa teto admissível zero. N3/A4 e proibições anteriores preservados; nenhum parâmetro foi preenchido ou ativado.

### Carregamento e status explícito de ordens
A recarga não transforma rascunho preenchido em ordem aberta, nem converte `Active` legado em fato V11. A contraprova executou o `migrate()` completo com dados sintéticos e comprovou a promoção antiga; a revisão remove apenas essa inferência. Atividade legada sem status conciliado permanece intacta e produz `ORDER_STATUS_UNRESOLVED`/NOT_COMPUTABLE no agregado, nunca risco zero presumido. Rascunhos explicitamente identificados ficam fora da exposição. O focal inclui recarga real, além da contraprova isolada; evidências antes/depois são preservadas no diretório da campanha.

### Revisão final V3 — contradições de fatos e oráculos de integração
V2 e seu FULL bruto (53 PASS, 2 PRODUCT_FAIL) permanecem congelados externamente. A auditoria e a contraprova de 24 cenários identificaram em `src/js/10-domain/02-risk-calculations.js` dois limites do mesmo adapter: `draft` contraditório com status operacional não pode ocultar um fato; resultado fechado sem contexto monetário conciliado não pode ser formatado na moeda selecionada. Corrigir somente seleção/projeção, preservando os fatos, a exclusão de draft explícito sem status e de voided, e o zero factual conciliado. `tools/forex_v11_read_model_test.py` recebe os cinco casos previamente capturados, sem alterar equações ou reconciliação normativa.

`tools/usd_brl_quote_test.py`: o scanner atual confunde três ocorrências exatas e públicas de “authorization” no portátil com credenciais. Aplicar somente a distinção textual revisada, limitada a essas linhas únicas e ao portátil; manter os oito marcadores, arquivos e verificações de cache. As 169 contraprovas de cabeçalhos, tokens, linhas modificadas/duplicadas e alvos incorretos continuam exigidas. Não alterar código do produto para contornar o scanner.

`tools/import_xss_security_test.py`, já previsto no contrato: investigar o oráculo da denominação canônica LEGACY (FASE antiga versus GRADE LEGADA), preservando injeções, escape, importação, reload e proteção. Ajustar somente expectativas incompatíveis demonstradas com o contrato atual, após revisão focal; não flexibilizar validação de payload.

Classificação e autoridade N3/A4 anteriores preservadas. CTX limitado a este complemento; nenhuma fonte geral atualizada. Regenerar somente manifest/hash e derivados oficiais após as correções. Executar focais afetados, novo FULL obrigatório sob a barreira loopback existente, auditoria focal, identificação e recovery V3. Rollback exclusivamente do delta próprio destes caminhos e derivados, usando as cópias V2 preservadas; sem reset, stash ou intervenção em outras árvores. V3 terá identidade distinta e não herdará aprovação de FULL da V2.
