# CHG — integração do aparato local de validação (2026-09-23)

**Classificação:** N3/A4, control plane de testes. **Autorização:** pedido explícito do usuário para commit, push, merge e integração completa após a auditoria do candidate visual e da frente separada de confiabilidade. Este CHG é distinto dos CHGs de cabeçalho/navegação.

## Alvo e risco

Integrar, em commit separado do recorte visual, somente `tools/usd_brl_quote_test.py`, `tools/test_infra/sidecar/sitecustomize.py`, `tools/test_infra/validate_trace.py` e `tools/test_infra/README.md`. O teste USD/BRL bloqueia service workers em seu contexto para que a rota sintética do provedor seja determinística; casos, valores, timeouts e asserções não mudam. O sidecar e o validador são cópias byte-idênticas das versões externas auditadas v3/v5, carregadas apenas por `PYTHONPATH` e `JPW_INFRA_MODE`. Não modificar runtime, SW, gate, classificador, Harness ou CI.

O sidecar altera a fila do servidor HTTP local de testes para 128 quando explicitamente ativado e registra eventos servidor/navegador. Isso pode alterar timing e não estabelece a causa histórica da intermitência. A auditoria externa classificou o envelope do candidate como `AUDIT_PASS_WITH_DEBT`: full de 57 PASS/0 FAIL, 514/514 bootstraps do documento principal verificados, mas laudo global `OBSERVABILITY_INCOMPLETE` por telemetria de service worker no teardown e servidor PWA customizado. Esse resultado não é reclassificado como aprovação universal do aparato. Recibos anteriores permanecem em `/Users/joaopauloalves/.codex/jpw-test-infra/20260923/`.

## Validação e reversão

Conferir SHA-256 das duas ferramentas e o diff de uma linha da fixture contra a cópia auditada; executar focal USD/BRL e gate full sobre a árvore integrada, com instrumentação opt-in e recibos externos. Confirmar que execução comum sem variáveis `JPW_INFRA_*` não carrega o sidecar. Revisar diff e status antes de merge/push. Para reverter, remover `PYTHONPATH`/`JPW_INFRA_*`; o commit de aparato pode ser revertido independentemente do visual. Nenhum dado financeiro ou preferência é migrado.
