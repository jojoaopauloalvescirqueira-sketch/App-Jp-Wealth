# CHG-JPW-ALAVANCAGEM-PAINEL-COMPACTO-20260928 — 1.1.1

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-PAINEL-COMPACTO-20260928
status: approved
objective: Apresentar a alavancagem em uma linha discreta junto ao cabeçalho do gráfico MT5, com detalhes acessíveis sob demanda.
risk_level: N1
authority_required: A2
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
  derived_from: jpw-alavancagem-atual-20260927-r2
  r2_fingerprint: 5035c508e3efa5850634d4962f75768c6f0e55ac6a5d09de5b6d08b44970693d
scope:
  allowed_files: [mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5, mt5/jpw-alavancagem-atual/README.md, downloads/jpw-alavancagem-atual/manifest.json, downloads/jpw-alavancagem-atual/JPW_Alavancagem_Atual_Fontes_v1.1.1.zip, index.html, tools/leverage_panel_test.py, docs/work/CHG-JPW-ALAVANCAGEM-PAINEL-COMPACTO-20260928.md, docs/work/ACTIVE-TASK.md, build-id.js, sw.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  forbidden_files: [mt5/jpw-alavancagem-atual/MQL5/Include/, mt5/jpw-alavancagem-atual/MQL5/Scripts/, src/js/00-core/, src/js/10-domain/, docs/normative/, docs/decisions/, tools/quality_gate.py, skills/, .github/]
  allowed_actions: [local visual implementation, synthetic tests, official generation, independent review]
  forbidden_actions: [commit, push, merge, deploy, trade, operational-terminal installation, real-account collection]
data:
  test_policy: synthetic_only
  schema_change: forbidden
acceptance_criteria:
  - Uma linha cinza e pequena, alinhada ao nome nativo do instrumento sem o sobrepor; valores atuais e estimados explicitamente distintos.
  - Motivo, data da cotação mais antiga e base do equity permanecem disponíveis na dica do indicador.
  - Falhas e estados sem valor retiram o número anterior; gráfico pequeno não mostra número sem estado.
  - Fórmula, leitura de posições, conversões, perfil USC e relógio permanecem byte a byte iguais aos do r2.
  - Fonte, manifesto, ZIP, build, portátil e cache são regenerados pelos comandos oficiais; versão anterior preservada.
approved_tests: [focal de qualidade e geometria do painel com dados sintéticos, pacote, pagina e downloads, estrutural, standard, revisao independente do diff]
rollback:
  source: [Voltar ao candidate r2 preservado fora da worktree.]
  data: [Nenhum estado financeiro ou preferencia afetado.]
  verification: [Comparar hashes do nucleo e dos adapters com r2; conferir manifesto e ZIP derivados.]
approved_by: Proprietario, pedido nesta conversa para compactar a aparencia do indicador
approved_at: 2026-09-27 America/Sao_Paulo
```

## Compreensão e decisão

O JP Wealth distribui orientações e fontes; o cálculo ocorre exclusivamente no MT5. O pedido corrige ocupação excessiva do gráfico, observada na captura operacional enviada pelo proprietário: o r2 mostra marca, leitura e estado/horário em três ou mais linhas, com fonte 14 e Y50. O valor de 2,75x foi conferido com os dados visíveis da captura, mas a fonte r2 continua sem homologação geral e com full 53 PASS / 4 PRODUCT_FAIL. Capturas e dados da conta não entram nesta mudança ou nos testes.

A documentação oficial do MT5 não oferece contrato para inserir texto dentro do nome nativo do par. Um `OBJ_LABEL` será colocado logo abaixo dele, no mesmo alinhamento horizontal, com fonte 10 e pequeno afastamento. `OBJPROP_TOOLTIP` conterá o estado extenso. O código não altera `Comment()` compartilhado, o nome nativo do par nem o shortname a cada atualização. A apresentação inclui a qualidade perto do número: `JPW 2,75x · atual`, `JPW ≈2,75x · estim.` ou `JPW N/D`. A posição vertical é ajustável em Entradas; a sobreposição real depende de revisão no MT5 com temas, símbolos e DPI distintos.

Partes protegidas: `JPWRefresh`, `JPWCollectReading`, Core, Terminal, Profile, testes de matemática e scripts. A menor mudança é a projeção `JPWRender`, seus parâmetros visuais e a descrição de uso no site/README. Troca de versão para 1.1.1 separa os bytes novos da 1.1.0 instalada manualmente; nenhum EX5 antigo será rotulado como novo.

Fontes consultadas: `AGENTS.md`, `README.md`, `docs/governance/CONTEXT-MAP.md`, `PROJECT-CONTEXT.md`, `QUALITY-GATES.md`, `docs/work/CHG-JPW-ALAVANCAGEM-USC-20260927.md` e código r2. API MetaQuotes: https://www.mql5.com/en/docs/constants/objectconstants/enum_object/obj_label, https://www.mql5.com/en/docs/constants/objectconstants/enum_object_property, https://www.mql5.com/en/docs/constants/chartconstants/enum_chart_property, https://www.mql5.com/en/docs/objects/textsetfont. O Harness externo mantém o hash documentado no CHG r2; esta alteração não muda fórmula ou controle de aprovação.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. O contrato visual e o pacote distribuído mudam; README, página, manifesto e ACTIVE-TASK serão reconciliados. O estado integrado da main e o control plane não mudam. Auditoria final deste candidate e validação nativa serão distinguidas dos recibos r2.

## Implementação e validação local

Versão derivada 1.1.1, build `2e84435381d063ed`. A linha usa fonte 10, cor `#767676`, X16/Y40, com qualidade junto ao número e detalhes no tooltip. `0,00x` confirmado inclui a base do equity na dica. O indicador mantém `JPWRefresh` e todas as rotinas financeiras byte a byte iguais ao r2; os três includes e três scripts também são idênticos. O ZIP de fontes v1.1.1 foi regenerado pelo gerador oficial, SHA-256 `a10dd241ba07324b79b723c2e9bff149247469c8870f43c3f0a1b0ddff6c1654`, 37.729 bytes. Portátil e build foram regenerados por `tools/rebuild_monolith.py`; o ZIP 1.1.0 permanece preservado.

- Focal do painel: PASS, expressões reais da projeção testadas com estados sintéticos, tooltip, largura estreita e ciclo de vida. Não substitui execução MQL5.
- Pacote: PASS, extração, hashes, determinismo e recusa de EX5 sem evidência. Estrutura: PASS no ambiente autorizado.
- Página: download HTTP, arquivo local, portátil e seis geometrias sidebar passaram; depois o teste retornou falha com quatro `jpwWorkspaceDraftProviders is not defined`. A execução permanece falha. Uma observação passiva separada recebeu integralmente `07-workspace-backup.js` com status 200, expôs o símbolo e abriu a rota, sem explicar a primeira falha.
- Gate standard único: 44 PASS / 2 PRODUCT_FAIL. `research-navigation` falhou antes do cenário com `$ is not defined` em `closeModal`; `alladin-ui-crud` registrou `render is not defined`. Sem reclassificação por resultados focais.
- Revisão independente: sem achado estático novo no delta visual após a correção da dica de zero e do texto de compilação. O alinhamento junto ao título, o tooltip e a ausência de sobreposição sob DPI, ticker e painel de negociação exigem inspeção nativa.

Compilação 1.1.1 em X64 Regular, EX5, execução de testes MQL5 e inspeção do painel no MT5 continuam pendentes. A entrega é fonte e página examináveis, não homologação operacional. A falha do teste da página e os dois PRODUCT_FAIL do standard permanecem registrados, sem presumir causa ambiental.
