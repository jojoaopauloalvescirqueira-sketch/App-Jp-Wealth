# CHG-JPW-ALAVANCAGEM-LABEL-EN-20260928 — painel v1.1.2

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-LABEL-EN-20260928
status: approved
objective: Tornar a linha do indicador menor e autoexplicativa, com rótulo Leverage e estados em inglês.
risk_level: N1
authority_required: A2
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
  derived_from: jpw-alavancagem-atual-20260928-r3
  r3_fingerprint: f2a3b60099fe019a1207299edf9c532a1563c579a5250048097efcca1656f610
scope:
  allowed_files: [mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5, mt5/jpw-alavancagem-atual/README.md, downloads/jpw-alavancagem-atual/manifest.json, downloads/jpw-alavancagem-atual/JPW_Alavancagem_Atual_Fontes_v1.1.2.zip, index.html, tools/leverage_panel_test.py, tools/leverage_page_test.py, docs/work/CHG-JPW-ALAVANCAGEM-LABEL-EN-20260928.md, docs/work/ACTIVE-TASK.md, build-id.js, sw.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  forbidden_files: [mt5/jpw-alavancagem-atual/MQL5/Include/, mt5/jpw-alavancagem-atual/MQL5/Scripts/, src/js/00-core/, src/js/10-domain/, docs/normative/, docs/decisions/, tools/quality_gate.py, .github/]
  allowed_actions: [local copy and appearance edit, synthetic tests, official generation, independent review]
  forbidden_actions: [commit, push, merge, deploy, trade, operational-terminal installation, real-account collection]
data:
  test_policy: synthetic_only
  schema_change: forbidden
acceptance_criteria:
  - Linha em cinza fonte 8 com prefixo JPW: Leverage e estado Current ou Estimated em inglês.
  - Indisponibilidade e preparação não exibem número antigo; dica completa permanece acessível.
  - Fórmula, leitura, conversões, perfil USC, scripts e includes permanecem idênticos ao r3.
  - Site, README, manifesto, ZIP e artefatos gerados descrevem a mesma versão 1.1.2.
approved_tests: [focal do painel com dados sintéticos, pacote e página, validação estrutural, standard, revisão independente]
rollback:
  source: [Restaurar o candidate r3 preservado externamente.]
  data: [Nenhum estado financeiro ou preferência afetado.]
  verification: [Comparar hashes dos componentes financeiros com o r3 e conferir pacote gerado.]
approved_by: Proprietario, pedido nesta conversa para Leverage em inglês e fonte menor
approved_at: 2026-09-28 America/Sao_Paulo
```

## Decisão proporcional

A captura enviada pelo proprietário mostra o r3 instalado, próximo ao cabeçalho nativo, ainda grande para a preferência visual dele e sem nome da métrica. A captura contém dados operacionais reais e não será copiada para o candidate nem usada nos testes. O novo texto será `JPW: Leverage 2,75x · Current`, `JPW: Leverage ≈2,75x · Estimated` ou `JPW: Leverage N/A`, preservando o separador decimal da leitura. Estados de espera passam a `Loading` e `Updating`. O tamanho padrão cai de 10 para 8, mantendo cor #767676 e posição X16/Y40; templates antigos podem exigir Redefinir nas Entradas.

Esta é apenas a projeção visual de um número calculado pelo mesmo código financeiro. A legenda e a dica não transformam uma estimativa em dado atual. A versão 1.1.2 separa os novos bytes da 1.1.1 que o proprietário mostrou no MT5. Os testes e falhas anteriores são preservados; resultados nativos do r3 não são herdados como validação da nova versão.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. O contrato de exibição e o pacote distribuído mudam; página, README, manifesto e artefatos derivados serão reconciliados. O aplicativo web continua somente como guia/download, sem cálculo ou dados de conta. O control plane, main e evidências anteriores permanecem intocados.

## Resultado da revisão 1.1.2

- Build gerado: `70d9444f960966d9`.
- ZIP de fontes: `JPW_Alavancagem_Atual_Fontes_v1.1.2.zip`, 37.782 bytes, SHA-256 `cc725f1ea413434a1cb1e08eb29f56dbc07ae8a50db1d4975bd9378677f7752b`. O manifesto, o ZIP e os artefatos portátil e offline apontam à mesma revisão. Não há EX5 1.1.2.
- Focais de painel e pacote: PASS. Página: PASS por HTTP, arquivo local, portátil e PWA offline; quatro layouts e larguras 1440, 390 e 320 px foram exercitados com dados sintéticos. Validação estrutural e `git diff --check`: PASS.
- Gate `standard`, uma execução: **44 PASS / 2 PRODUCT_FAIL**. `finpes-backup-roundtrip` excedeu a espera de inicialização antes do cenário; `finpes-navigation` levantou `TypeError` em `26-forex-engine-views.js:145` durante a navegação. Recibo integral: `tools/.artifacts/quality-20260928T124505-standard.json`, com cópia externa no pacote de entrega. Não houve mudança de Finanças Pessoais ou Forex nesta revisão, mas a causa das falhas não foi atribuída ao ambiente nem reclassificada.
- Auditoria independente read-only: sem defeito estático novo identificado no delta visual. Os três includes e três scripts MT5 conservam os hashes do r3; tooltip, `JPWRefresh` e `JPWCollectReading` não mudaram. O parecer não converte os focais em validação nativa ou gate aprovado.
- **NOT_RUN / pendente:** compilação completa da 1.1.2 no MetaEditor X64 Regular, execução/inspeção da linha menor no gráfico MT5 em DPI e temas relevantes e verificação de sobreposição. A captura enviada pelo usuário pertence ao r3, não comprova a versão nova. O candidate de fontes e página está pronto para revisão, sem homologação operacional ou aceite humano.
