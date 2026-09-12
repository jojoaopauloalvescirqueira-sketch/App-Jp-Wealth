# DESIGN & EXPERIENCE 01 — campanha local delimitada

## Brief anterior à implementação

Autorização: objetivo ativo do proprietário “JP WEALTH — DESIGN & EXPERIENCE 01”,
em 2026-09-12. Permite redesign funcional, testes, derivados oficiais e contexto
diretamente afetado; branch/worktree própria. Não permite integração/publicação.
Risco **N1 / A2**, com FULL e auditoria pedidos expressamente. Nenhuma mudança de
persistência, control plane ou matemática. Este contrato registra autoridade; não a concede.

Raiz: /Users/joaopauloalves/.codex/design-campaigns/20260912/product.
Branch: codex/design-experience-01. Base Git:
689e8a8f6cc09db9109b52d505c4dcb66fc16be3; build 02eba740dcabc48b.
Árvore inicialmente limpa, 297 inputs, fingerprint de pacote (não commit)
74ebc79854fc3cbffb5e53007cf69daae27aeb5eb3d1fc81f1c71140f15e2237.
../evidence/intake.json, baseline.json e baseline.tar preservam baseline,
outras worktrees e stash. Aviso contextual anterior do preflight registrado,
não convertido em prova de contexto atualizado.

1. **Finalidade:** facilitar encontrar ações, ler fatos e comparar períodos no
   JP Wealth, sem acrescentar conclusões financeiras ou promessas de retorno.
2. **Responsabilidades:** 20-ui projeta read-models; index.html compõe áreas;
   40-app coordena interfaces. PF compara competências, Alladin apresenta fatos,
   Forex explicita prontidão/fechamentos e Research abriga estudos e experimento.
3. **Antes/depois observado:** série PF em grade textual; controles Lab após
   canvas; ferramentas secundárias antes de prontidão Forex; busca Settings
   estreita em 390px. Capturas em ../evidence/survey-baseline-01/ são observações
   do agente, não pesquisa ou aceite humanos.
4. **Consumidores:** pfCompSeries/pfCompCompare; envelope completo de
   leitura.ledger() antes do filtro visual; séries existentes do Forex.
   Shell, Editor, avisos e A10–A13 continuam compartilhados.
5. **Limites:** sem fórmulas, métricas primárias, gravações na navegação, schema,
   router ou sistema visual paralelo. Ausência/partial não viram zero; BRL_CENTS,
   moedas e datas mantêm significado. A12 parcial; OPEN-05/V11, AUD-05/P2 e demais
   dívidas preservadas. A13 mantém mesma simulação em RAM pausada até Continuar.
6. **Evidência:** mesmas fixtures/tarefas antes/depois, focais de interação e
   estado, regressões existentes, FULL final, audit independente e recuperação.
   Outros browsers e acessibilidade integral não são inferidos.

Fontes lidas na base: AGENTS, README, CONTEXT-MAP/PROJECT-CONTEXT/CHANGE-PROCESS/
QUALITY-GATES; X1 e filosofia v1.0, X2, contratos PF/Alladin/navegação; scripts e
fixtures correspondentes. Harness mestre v2 §§12–19,24–25,36–52, SHA-256
c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8.
Origem de cada afirmação distingue leitura, observação e execução.

## Plano finito e expectativas anteriores aos patches

| Lote | Tarefa e delta | Critério e preservação |
|---|---|---|
| D1 — piloto antes da propagação | PF Comparativo: evolução visual de 12 meses, métrica efêmera, valores/tabela legíveis | Exclusivamente dados canônicos; lacunas visíveis; zero explícito; tabela completa; teclado/toque; selecionar/navegar não grava; unidade desconhecida bloqueia números; revisar piloto antes de outros lotes |
| D2 | Acesso Dashboard mais direto; prontidão Forex antes de ferramentas secundárias; busca Settings responsiva | Mesmos destinos/IDs/valores; avisos globais e Sistema/atalhos; busca abre resultado e conserva foco; A10/A11 preservados |
| D3 | Alladin: busca efêmera de fatos; Forex: inspeção acessível das curvas | Envelope integral antes de filtrar; ordem econômica/datas/estorno; vazio filtrado distinto de indisponibilidade; datas e valores efetivos sem nova derivação financeira |
| D4 | Lab: controles antes do canvas e hierarquia concisa | Mesmos IDs/ações e matemática; navegação pausa/preserva; retorno exige Continuar; reset/finalização liberam recursos; Research sem faixa Forex |

Linhas respondem à evolução; barras à comparação; histogramas existentes à
distribuição. Composição patrimonial e dispersão não têm pergunta/dados
demonstrados neste recorte. Avaliação inicial de 3D: o Lab já representa duas
dimensões e histograma; profundidade não acrescenta variável canônica.
Não inserir 3D decorativo. Decisão final vinculada às evidências.

Fixar testes antes do renderer: tools/design_pf_comparison_test.py para D1,
tools/design_experience_test.py para D2–D4/compartilhados. Baseline sem capacidade
nova não é defeito financeiro. Preservar falhas e distinguir ajuste de fixture.
320/390/768/1440px, claro/escuro, zoom200%, reduced-motion, teclado/foco e estados
vazio/erro/sucesso pertinentes. Rede somente loopback com
browser_bootstrap_fixture.py e perfil existente loopback-only.sb. Preservar SW
nos testes PWA. Dados sintéticos. Tempos/heap observados não são benchmark
estatístico nem eficiência humana.

## CHG

```yaml
schema: jp-harness/chg/v1
change_id: CHG-DESIGN-EXPERIENCE-01-20260912
status: approved
objective: Entregar quatro lotes finitos de experiência e candidate local para revisão humana.
risk_level: N1
authority_required: A2
target:
  root: /Users/joaopauloalves/.codex/design-campaigns/20260912/product
  branch: codex/design-experience-01
  baseline_sha: 689e8a8f6cc09db9109b52d505c4dcb66fc16be3
scope:
  allowed_files:
    - index.html
    - src/styles/app.css
    - src/js/20-ui/20-finpes-comparison.js
    - src/js/20-ui/25-dash-macro.js
    - src/js/20-ui/24-alladin-views.js
    - src/js/20-ui/07-chart-crosshair-tooltip.js
    - src/js/40-app/09-settings-modal.js
    - src/js/40-app/18-galton-board/06-controller.js
    - src/js/manifest.json
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
    - tools/design_pf_comparison_test.py
    - tools/design_experience_test.py
    - README.md
    - docs/architecture/PERSONAL-FINANCE.md
    - docs/architecture/ALLADIN.md
    - docs/architecture/GALTON-BOARD.md
    - docs/architecture/CODE-MAP.md
    - docs/work/ACTIVE-TASK.md
    - docs/work/CHG-DESIGN-EXPERIENCE-01-20260912.md
    - docs/governance/CURRENT-STATE.md
    - SESSION_HANDOFF.md
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/**, .github/**, docs/normative/**, src/js/00-core/**, src/js/10-domain/**, src/js/30-accounting/**, tools/quality_gate.py, tools/validate_project.py, tools/rebuild_monolith.py, sw.js]
  allowed_actions: [quatro lotes acima, testes e fixtures sintéticos, derivados oficiais, evidências externas, contexto factual afetado]
  forbidden_actions: [staging, commit do produto, tag, push, PR, merge, deploy, reset Git, stash, migração, reindexação, dependências novas, APIs econômicas ao vivo]
  regressions_forbidden: [perda de dados e rascunhos, alteração financeira, duplicação de listeners e instâncias, controles enfraquecidos, alteração de persistência]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [Apple Developer e W3C públicos sem conteúdo privado, loopback em testes]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [Python e Chromium existentes, gerador oficial, Git read-only e branch/worktree autorizada, Git sintético em fixtures próprias sem remotos ou hooks]
acceptance_criteria: [D1 revisado antes de propagação, expectativas D1-D4, gates classificados, auditoria, recuperação, roteiro humano sem aceite presumido]
approved_tests: [focais D1-D4, regressões PF Alladin navegação gráficos Settings Galton, quality_gate full, reprodutibilidade e PWA existentes]
rollback:
  source: baseline.tar e baseline.json mais diff e snapshot finais em ../evidence; recuperar cópia e verificar hashes; somente delta após conferir trabalho posterior
  data: perfis sintéticos isolados; nenhum dado real ou migração
  environment: preservar outras worktrees e serviços existentes
  verification: comparar hashes e modos do snapshot recuperado
approved_by: proprietário no objetivo finito DESIGN & EXPERIENCE 01
approved_at: 2026-09-12
expires_on: [drift material, necessidade de mudar matemática persistência ou controles, dados reais, ampliação material]
```

Restrições internas: no crosshair não editar cálculos de renderDashCharts;
controller Galton somente panelHTML; manifest somente hashes sem reordenar.
Um escritor por componente.

## CTX e impacto delimitado

```yaml
schema: jp-harness/ctx/v1
context_change_id: CTX-DESIGN-EXPERIENCE-01-20260912
status: approved
root: /Users/joaopauloalves/.codex/design-campaigns/20260912/product
mode: CONCORRENTE
approved_branch: codex/design-experience-01
create: [docs/work/CHG-DESIGN-EXPERIENCE-01-20260912.md]
modify: [README.md, docs/architecture/PERSONAL-FINANCE.md, docs/architecture/ALLADIN.md, docs/architecture/GALTON-BOARD.md, docs/architecture/CODE-MAP.md, docs/work/ACTIVE-TASK.md, docs/governance/CURRENT-STATE.md, SESSION_HANDOFF.md]
preserve: [históricos, main, stash, outras worktrees, A10-A13, codex/nav-ref-context]
do_not_touch: [instruções e skills, normas, governança exceto cabeçalho factual CURRENT-STATE, índices e grafo]
source_of_truth: [código e contratos na base mais delta, autorização vigente do proprietário]
information_promotion: [somente comportamento implementado e evidência executada; sem aceite ou integração presumidos]
acceptance_criteria: [referências afetadas coerentes, dívida preservada, sem mudança de autoridade]
approved_by: proprietário no escopo de documentação afetada
approved_at: 2026-09-12
expires_on: [necessidade de control plane ou curadoria geral]
```

IMPACT/RECONCILE: contratos PF/Alladin/Galton, CODE-MAP/README são AFFECTED e
REQUIRED após implementação. CURRENT-STATE/ACTIVE-TASK/handoff: AFFECTED,
cabeçalho factual REQUIRED, histórico preservado. AGENTS/skills/roteamento/Atlas:
AFFECTED por referência, ação NOT_REQUIRED — responsabilidades e rotas não
mudam. Normas/gates/CI: NOT_AFFECTED. Índices antigos seguem sem demonstração
de frescor, nenhuma ação autorizada. Não é reconciliação global.
