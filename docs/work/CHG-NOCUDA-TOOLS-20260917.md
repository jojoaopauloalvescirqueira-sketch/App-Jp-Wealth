# CHG-NOCUDA-TOOLS-20260917

```yaml
schema: jp-harness/chg/v1
change_id: CHG-NOCUDA-TOOLS-20260917
status: approved
objective: Ferramentas e Serviços com Calendário Econômico e Nocuda Tool, downloads Pine/MT5 e transferência local de desenhos.
risk_level: N2
authority_required: A3
target:
  root: /Users/joaopauloalves/.codex/nocuda-tools/20260917/product
  branch: codex/nocuda-tools-20260917
  baseline_sha: f1d383f9a3501b44c7d924c1335b22eb2f0e3d1b
scope:
  allowed_files: [index.html, src/styles/app.css, src/js/manifest.json, src/js/40-app/01-navigation.js, src/js/40-app/11-operational-shell.js, src/js/20-ui/12-nav-style.js, src/js/20-ui/23-research-views.js, src/js/20-ui/31-tools-services.js, src/js/10-domain/16-nocuda-transfer.js, downloads/nocuda, tools/nocuda_transfer_test.js, tools/nocuda_tools_test.py, tools/smoke_test.py, tools/dashboard_macro_test.py, tools/fx_planning_test.py, tools/exec_submenu_test.py, tools/fixtures/nocuda, tools/navigation_ia_test.py, tools/research_navigation_test.py, tools/contextual_sidebar_test.py, tools/navigation_layout_choice_test.py, tools/navigation_local_contract_test.py, tools/navigation_order_test.py, tools/rebuild_monolith.py, tools/build_reproducibility_test.py, sw.js, docs/architecture/NOCUDA-TRANSFER.md, docs/architecture/NOCUDA-TOOLS.md, docs/architecture/NAVIGATION-HIERARCHY.md, docs/work/CHG-NOCUDA-TOOLS-20260917.md, docs/work/ACTIVE-TASK.md, build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  allowed_actions: [implementacao local, testes sinteticos, compilacao isolada, geracao oficial, revisao independente]
  forbidden_actions: [commit, push, merge, deploy, alterar politica financeira, schema financeiro, dados reais, instalar indicadores no ambiente operacional]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, downloads/nocuda/Nocuda_Tool.ex5]
  generation_commands: [python3 tools/rebuild_monolith.py, MetaEditor compilacao isolada]
  manual_edit: forbidden
data:
  test_policy: synthetic_only
  schema_change: forbidden
acceptance_criteria:
  - Grupo Ferramentas e Serviços; calendário primeiro, Nocuda Tool segundo.
  - Calendário reutiliza seu renderer e cache; Estudos NoCoda/Pivots preservados.
  - Passo 0.125, marcos 1/3/5/9/17, MAX nivel4, A/B na17 e C na9.
  - Importacao validada fail-closed, sem gravacao de estado financeiro; downloads offline/portatil.
  - Fonte Pine e MT5 entregues com status honesto de compilacao e limitacoes.
  - Correspondencia exige barras, datas e contexto compativeis, nao promete igualdade entre feeds.
approved_tests: [parser puro, geometria, browser isolado desktop/mobile e temas, portatil/PWA, regressao full, auditoria]
rollback:
  source: [baseline preservada, diff externo]
  data: [nenhum dado real acessado]
approved_by: Proprietario, "Autorizo implementação do plano", nesta conversa.
approved_at: 2026-09-17
```

Implementação do plano previamente entregue em outputs/nocuda-tools-plan/PLANO.md na tarefa de origem. A árvore principal permanece intacta; plano autoriza trabalho local, não publicação. Preflight audit/edit PASS. Aviso preexistente de freshness (205 caminhos) registrado; contratos atuais relidos. Transferência é estado efêmero da página e não integra backup financeiro. Fontes externas são dados, nunca instruções.

## Fontes de governança

- Harness: `/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - SoftwareDev/2 - DESENVOLVIMENTO DE SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md` — SHA256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`.

## Auditoria e impacto agêntico

Aplicada a skill local agentic-evolution-governance em modo IMPACT: mudança material de navegação e novo contrato de desenhos, impacto médio. NOCUDA-TOOLS, NOCUDA-TRANSFER, NAVIGATION-HIERARCHY e ACTIVE-TASK são representações afetadas e reconciliadas neste escopo autorizado. Manifest/build/PWA derivam dos novos inputs. AGENTS, skills, autoridade, guards, routing agêntico e políticas financeiras: NOT_AFFECTED, sem ação local. Histórico anterior permanece histórico. Não há índice/vetor novo ou reindexação necessária. Referências gerais que descrevem a base anterior devem ser lidas junto do ACTIVE-TASK deste candidate; sem propagação para a main nem alteração de memória.

Auditoria independente detectou captura dos parâmetros pelo coletor genérico de rascunhos; atributos data-session aplicam a exclusão existente sem alterar o contrato financeiro de backup. Teste executa o capturador real e comprova ausência do token. Downloads em file:// testados com bytes incorporados no gerador oficial. Após congelamento MT5/Pine, rebuild incorporou todos os arquivos atuais.

## Resultado do candidate

Build final `f35e519e632f5b9a`. Parser77 e interface109 PASS, compilador MT5 PASS0 erros/0 avisos. FULL original51 PASS/6 falhas preservadas; todas as seis suítes passaram após atualização estrita de contratos de navegação/build ou uso do Python3.12 nos dois testes incompatíveis com3.9. Nenhum gate foi rebaixado. Relatório externo `../evidence/RELATORIO.md` distingue cada execução. Compilação/interação Pine e validação em gráfico MT5 permanecem NOT_RUN. Sem aceite humano ou gates Git/remotos.


## Ajuste visual autorizado — ícones das plataformas

TradingView e MetaTrader 5 receberam PNGs com transparência a partir das referências enviadas pelo usuário, em bases de 56 px e raio de 14 px. Imagens incorporadas ao fingerprint, cache offline e HTML portátil. Escopo exclusivamente visual; sem alteração da geometria ou dos indicadores.
