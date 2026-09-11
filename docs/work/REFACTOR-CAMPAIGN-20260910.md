# Campanha finita de refatoração — 20260910

## Compreensão, autoridade e baseline

JP Wealth é PWA financeira local: capital, integridade e evidência fiel prevalecem. A campanha melhora manutenção das decisões de apresentação e separa efeitos em fronteiras existentes; não muda finalidade, regras, dados ou arquitetura. Base integrada e770e1b66a87e93f52f40eab83479d7a26be2cd4 (PR #11), build inicial f4adcd1cc131c623. NAV-REF-01 está encerrado e não será refeito.

Fonte de autoridade: objetivo vigente do proprietário, que autoriza campanha finita N1/N2, branch/worktree própria, testes/fixtures e derivados. Os quatro lotes selecionados são N1: nenhum writer, fórmula ou contrato persistente é modificado. A autorização mais ampla N2 não obriga criar um lote de maior risco. Harness §§12–16,23–25,31,36–48; revisão/hash em evidence/baseline-inputs.json. AGENTS e fontes roteadas foram consultados; contextos históricos não provam estado atual. Apenas o coordenador escreve; três agentes fizeram inventário seletivo read-only, sem atribuir teste à leitura.

## Fase 1 — inventário e decisão

| Área / cobertura examinada | Decisão | Fonte e fundamento |
|---|---|---|
| Dashboard: métricas, composição, foco e agendamento; shell/realocação/preferências | Manter | 20-ui/25-dash-macro.js:155,331; 40-app/12-global-dashboard.js:16 e13-dashboard-layout.js:479. Métricas canônicas e guardas por módulo; atualização/foco já separados. Consumidor indireto do lote Alladin. |
| PF: receitas/despesas inline | Refatorar L1 | 20-ui/18-finpes-budget.js:298,346. Duas cópias do mesmo protocolo parsing→ato→restauração→feedback. |
| PF: ghosts, recorrência, status, parcelas, destinações; views/dívidas/cenários/comparação/overview | Manter | 17–22-finpes*.js e domínio12-personal-finance.js. Materialização, nulidade e efeitos diferem; não consolidar fórmulas, pfMutate ou protocolos distintos. |
| Alladin: rótulos de caixas | Refatorar L2 | 20-ui/24-alladin-views.js:181–204; seis consumidores (ledger,saldos,posições,seletor,estorno,Dashboard). Separar só desambiguação pura, mantendo interleaving das leituras. |
| Alladin: guards, read-models, CRUD e ledger/escritor | Manter | 10-domain/13-alladin.js e20-ui/24-alladin-views.js:168,468. Sentinelas/dados/portas econômicas têm diferenças materiais; zero alteração normativa ou persistente. |
| Compartilhados: busca Configurações | Refatorar L3 | 40-app/09-settings-modal.js:341–346. Seleção concentra filtro/dedupe/prioridade/corte no render. |
| Compartilhados: boot, ajuda, fonte, navegação, storage/PWA | Manter | 40-app/06-boot.js;20-ui/09-contextual-help.js e10-font-scale.js;01-navigation.js já NAV-REF-01. Ciclos distintos; contratos críticos/security não entram. |
| Forex: ativação visual do Planejamento overview | Refatorar L4 | 30-accounting/05-fx-planning/05-fx-ui.js:664–709. Entry point despacha/renderiza e ainda instala efeitos exclusivos do overview; separar essa ativação preservando os ifs seguintes. |
| Forex: clearance, preparação, conta, operação/motor, apuração | Manter / decisão específica para mudança material | 20-ui/04-operational-clearance.js e05-execution-clearance.js;10-domain/04-stop-statistics.js;30-accounting/01-daily-ledger.js e02-accounting-engine.js. Mistura regras, credencial, proteções e efeitos; não transformar em lote N1 por rótulo. |
| Forex: histórico e demais modos de Planejamento | Manter | 20-ui/16-operation-history.js já separa snapshot/filtros/repintura/foco; prévias e realizado FX envolvem fórmulas/mutações excluídas. |
| Research: navegação e placeholders, Calendário, NoCoda, Pivots | Manter | 20-ui/23-research-views.js;40-app/17-economic-calendar.js e15-ff-news.js;20-ui/14-nocoda-studies.js e15-pivot-studies.js. Pipeline compartilhado, filtros/lifecycle distintos e projeções que preservam foco. Atlas parcial só orientou localização, não comprova eficácia. |

Cobertura: leitura seletiva das funções citadas, contratos e consumidores, não revisão exaustiva de cada função nem auditoria matemática. Fonte física mantém diretórios existentes; único novo teste fica em tools/*_test.py, contrato em docs/work, derivados em dist pelo gerador. Sem reorganização física, novo router, API pública criada só para teste ou avaliador genérico.

## Fase 2 — plano fechado, dependências e provas

Ordem L1→L2→L3→L4, com um escritor. Lotes independentes em código, acumulados no mesmo candidate; não avançar sobre regressão própria. Baseline recuperável e770… em ../evidence/baseline.tar. Cada lote conserva patch e identidade intermediária externos. Novo teste focal comum usa o padrão já existente de Chromium/DOM/scripts reais e oráculo literal; cobre quatro áreas por opção, sem alterar gates. Expectativas são escritas ANTES de mudar source; consumidores reais são exercitados pelas suítes existentes, sem confundir spy com integração.

| Lote | Transformação exata | Expectativas antes/depois e regressão |
|---|---|---|
| L1 PF | Uma função interna de binding para receitas/despesas; adaptadores fi/fe explícitos no evento. Não capturar ato/ID antes do change. | Textos crus; seis campos monetários; null/zero/inválido/negativo; prevval ausente/vazio; restauração antes do feedback; contagem/ordem; recusa e exceção, repetição/rebind. Parser e atos intactos. Focal + finpes_budget/overview/comparison e Dashboard. |
| L2 Alladin | Somente legível/contagem→caixas em helper puro; wrapper mantém accounts→processamento→instruments→processamento→cashAccounts. | Rótulos literais únicos/colisões entre contas, inativos, ausências/fallback/IDs, texto cru/escape posterior; snapshots congelados, ordem/contagem/throws, zero writes; ledger/saldos/posições/seletor/estorno/Dashboard. |
| L3 Configurações | Extrair filtro/dedupe/prioridade/limite de entradas com path; índice/mapeamento de paths, root/query/HTML/listeners ficam no render. | pt-BR, acentos preservados, primeira ocorrência vence antes do sort, estabilidade e18/19, correspondência clique/resultado, ausente/vazio/semresultado, escape e ausência de dados privados. Focal + settings_modal. |
| L4 FX | Bloco overview para função local fxpActivateOverview(root,live), chamado no mesmo if. Expressões, seletores, ifs seguintes e exceções intactos. | API existente/quatro views/plano ausente; wire/bind/refresh/charts na mesma ordem; reentrância e leitor ausente; janela visual/mode, largura/summary, botões e zero writes. Focal + fx_planning/usd_brl_quote/submenus/PWA. |

Fases3–5: caracterizar baseline → transformar/medir/verificar cada lote → atualizar somente CTX afetado → manifest hash e rebuild oficiais → freeze → focais finais/consumidores/FULL existente (inclui reprod/PWA) → auditoria independente → recuperação em cópia. Status/resultados posteriores ao freeze permanecem nas evidências externas. Gate necessário falho é classificado, não relaxado.

## Contratos canônicos

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-REFACTOR-CAMPAIGN-20260910",
  "status": "approved",
  "objective": "Campanha finita de quatro refatorações locais de apresentação/orquestração; comportamento preservado, lotes validados e checkpoint recuperável para revisão humana.",
  "risk_level": "N1",
  "authority_required": "A2",
  "target": {
    "root": "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product",
    "branch": "codex/refactor-campaign-20260910",
    "baseline_sha": "e770e1b66a87e93f52f40eab83479d7a26be2cd4"
  },
  "scope": {
    "allowed_files": [
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/src/js/20-ui/18-finpes-budget.js",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/src/js/20-ui/24-alladin-views.js",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/src/js/40-app/09-settings-modal.js",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/src/js/30-accounting/05-fx-planning/05-fx-ui.js",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/src/js/manifest.json",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/build-id.js",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/tools/presentation_refactor_contract_test.py",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/docs/work/REFACTOR-CAMPAIGN-20260910.md",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/docs/work/ACTIVE-TASK.md",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/docs/governance/CURRENT-STATE.md",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/SESSION_HANDOFF.md",
      "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/docs/architecture/CODE-MAP.md"
    ],
    "allowed_actions": [
      "four scoped source refactors",
      "focused product characterization test",
      "official manifest source hash update only",
      "official rebuild",
      "bounded non-normative CTX updates",
      "isolated synthetic testing and recovery",
      "one explicitly authorized campaign branch/worktree"
    ],
    "forbidden_actions": [
      "product staging/commit/tag/push/PR/merge/deploy",
      "reset/stash/cleanup of other work",
      "financial formulas or normative changes",
      "schema/migration or material persistence contract change",
      "security/permission changes",
      "new dependencies",
      "Harness/skills/CI/gates/index changes",
      "redesign or new features"
    ],
    "regressions_forbidden": [
      "same return values/refusals/exceptions",
      "same field IDs and identities",
      "same data/preferences/drafts",
      "same reads and effect order/count",
      "same focus/UI",
      "no new writes/network requests"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html"
    ],
    "generation_commands": [
      "/private/tmp/jpw-dashboard-official-venv/bin/python tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "official GitHub read-only checks as needed",
      "application and test traffic loopback only, existing loopback-only.sb"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": false
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "existing Python3.12.14/Playwright/Chromium",
      "existing sandbox-exec loopback profile",
      "existing product tests/quality_gate/rebuild",
      "Git read operations; fixture init/add/commit with own Git and no remotes/hooks"
    ]
  },
  "acceptance_criteria": [
    "four selected lots executed with meaningful structural gains",
    "identical literal-oracle baseline/candidate observations on existing APIs/DOM",
    "consumer regressions and mandatory FULL with truthful classification",
    "freeze before final gates; identified revision if later change",
    "independent audit and recovery verified in copy",
    "main/stash/other task and 8bd6d028 candidate preserved",
    "no user acceptance or integration inferred"
  ],
  "approved_tests": [
    "tools/presentation_refactor_contract_test.py (new ordinary focal product test following navigation_local_contract_test.py pattern; not new evaluator/gate)",
    "existing finpes_budget/overview/comparison; alladin_ui_readonly/ledger/tx_write/tx_reverse; settings_modal; fx_planning/usd_brl_quote; dashboard_macro",
    "existing navigation_local_contract/contextual_sidebar/navigation_layout_choice/dashboard_forex_relocation and operation_history as adjacent consumers",
    "tools/quality_gate.py --tier full (contains standard, reprod and PWA)",
    "tools/build_reproducibility_test.py and service_worker_upgrade_test.py via existing FULL",
    "recovery copy: git apply --check, apply approved patch and byte-hash comparison; official build if pertinent"
  ],
  "rollback": {
    "source": [
      "evidence/baseline.tar plus baseline-inputs.json",
      "per-lot patches/snapshots outside product",
      "revert only own delta after checking later work; no reset/stash or branch/worktree removal"
    ],
    "application_state": [
      "no real data read or changed; isolated browser contexts"
    ],
    "environment": [
      "no dependencies/configuration globally changed; stop only own test servers/processes"
    ],
    "verification": [
      "recover candidate in copy from exact baseline + final diff; compare all allowed paths and derived hashes"
    ]
  },
  "approved_by": "Proprietário — objetivo ativo de campanha finita N1/N2, fornecido nesta sessão; executor delimita os quatro lotes cobertos, não concede autoaprovação",
  "approved_at": "2026-09-10T23:57:23.130168-03:00",
  "expires_on": [
    "material target/base drift",
    "need to change financial/critical contract",
    "new permissions/dependencies/N3/material architecture",
    "own regression not resolved"
  ],
  "human_result_acceptance": "PENDING; distinct from execution authorization"
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-REFACTOR-CAMPAIGN-20260910",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/refactor-campaign-20260910",
  "create": [
    "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/docs/work/REFACTOR-CAMPAIGN-20260910.md"
  ],
  "modify": [
    "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/docs/work/ACTIVE-TASK.md",
    "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/docs/governance/CURRENT-STATE.md",
    "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/SESSION_HANDOFF.md",
    "/Users/joaopauloalves/.codex/refactor-campaigns/20260910/product/docs/architecture/CODE-MAP.md"
  ],
  "preserve": [
    "full prior headers/history",
    "global source revision/last_verified unchanged outside examined recut",
    "NAV-REF-01 checkpoint and merged source",
    "codex/nav-ref-context frozen candidate and evidence",
    "main/stash/other worktrees"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "skills/",
    "docs/normative/",
    "docs/governance policies",
    "tools existing gates or instruction tests",
    "graphs/indices"
  ],
  "source_of_truth": {
    "execution": "docs/work/REFACTOR-CAMPAIGN-20260910.md",
    "inputs": "evidence/baseline-inputs.json and eventual candidate manifest outside worktree",
    "past_NAV_integration": "PR #11/e770e1b; not repeated"
  },
  "information_promotion": [
    {
      "from": "inspected source and per-lot receipts",
      "to": [
        "docs/work/ACTIVE-TASK.md",
        "docs/governance/CURRENT-STATE.md",
        "SESSION_HANDOFF.md",
        "docs/architecture/CODE-MAP.md"
      ],
      "reason": "Bounded operational context and code responsibility mapping, with coverage and unreconciled historical metadata explicit."
    }
  ],
  "privacy_actions": [
    "synthetic data only, no real backups/credentials/caches copied"
  ],
  "acceptance_criteria": [
    "local campaign represented without false integration/acceptance",
    "source paths resolve and history preserved",
    "no authority/gate weakening or global freshness claim"
  ],
  "approved_by": "Proprietário — objetivo ativo de campanha finita N1/N2, fornecido nesta sessão; executor delimita os quatro lotes cobertos, não concede autoaprovação",
  "approved_at": "2026-09-10T23:57:23.130168-03:00"
}
```

## Preservação e pendências

O candidate documental 8bd6d02844685b44b7c832b4346cf865bd5ed3b8e4400cc07f008481885e098c permanece em codex/nav-ref-context. Seu fast autorizado foi executado em cópia fiel com HEAD+delta:4/4 PASS; reconstrução oficial só na cópia e outputs idênticos. Isso não é aceite nem altera freeze. Evidências em /Users/joaopauloalves/.codex/refactor-campaigns/20260910/evidence/context-fast*. Não transferir suas alterações para esta branch por conveniência.

AUD-05/P2, estrutural V4 CHG/CTX root mismatch bruto, limitações de PyYAML/Claude/descoberta/índices, Galton, defeitos anteriores de confirmação NoCoda/cache de calendário e conflitos FCR/FEO permanecem registrados, sem conversão a PASS. Manter uma área não significa auditar todas suas propriedades. Sem promessa de desempenho, segurança integral, aprovação de regras financeiras, teste manual, aceite humano ou integração.

## Registro anterior ao freeze — fases 3 e 4

L1–L4 implementados. Oráculo v1:88 observações PASS antes da fonte; revisão
independente identificou lacunas de fixture/cobertura, preservadas em evidência.
Oráculo v2:93 PASS na cópia de fontes e770 e 93 idênticas no conjunto transformado;
o teste é o mesmo nas duas condições. Sem alteração de expectativa para ocultar
falha. Cada lote tem patch e recibo; consumidores e gates finais são etapas
separadas, registradas externamente após freeze.

Ganho: PF passa de dois protocolos equivalentes para um; Alladin separa projeção
de leitura; Configurações explicita seleção independente do DOM; renderer FX
passa de52 para20 linhas com ativação overview local. Não há promessa de velocidade,
redução geral de bugs nem benefício financeiro. Build oficial: `e5caefeada66ab35`.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED.
BASIS: os contratos funcionais externos permanecem, mas a tarefa local e as
responsabilidades internas são consumidas como contexto por agentes. CHG/CTX
permite somente a reconciliação informativa abaixo, não mudança do control plane.
Análise em modo IMPACT do procedimento existente; magnitude baixa das representações,
com fontes de produto transformadas e contexto reconciliatório, sem nova autoridade.

| Categoria/representação | Impacto | Ação local | Base e decisão |
|---|---|---|---|
| AGENTS/CLAUDE, bootstrap e preflight | AFFECTED | NOT_REQUIRED | Mandam consultar mapas/estado atuais; herdam referências, não duplicar instruções |
| Skills e routing/registry | AFFECTED | NOT_REQUIRED | Skills existentes cobrem leitura, teste, auditoria; nenhuma invocação, autoridade ou feature nova |
| ACTIVE-TASK/CURRENT-STATE/handoff | AFFECTED | REQUIRED | Cabeçalhos da campanha local, limites e evidência externa; história preservada |
| CODE-MAP | AFFECTED | REQUIRED | Recorte das quatro responsabilidades acima; ordem global não muda |
| CONTEXT-MAP/PROJECT-CONTEXT/FEATURE-ATLAS | AFFECTED | NOT_REQUIRED | Finalidades/consumidores externos e caminhos continuam; mapa remete ao código e ao estado, Atlas é piloto parcial |
| Contratos do lote | AFFECTED | REQUIRED | Este CHG/CTX registra execução, critérios e recuperação, sem autoaceite |
| Normas e decisões financeiras | NOT_AFFECTED | NOT_REQUIRED | Nenhuma fórmula/parametrização/schema/capacidade de domínio muda |
| Gates/CI/segurança/permissões | NOT_AFFECTED | NOT_REQUIRED | Nenhuma política/exigência ou implementação dessas superfícies mudou |
| Histórico/changelog/auditorias anteriores | NOT_AFFECTED | NOT_REQUIRED | Registro verdadeiro do período não deve ser atualizado retrospectivamente |
| Grafo/índices/memórias | UNKNOWN | NOT_REQUIRED neste lote | Índice histórico permanece não validado/desatualizado; sem consulta que grave ou reindexação autorizada |

Reconciliação limitada: cabeçalhos e CODE-MAP passam a representar o recorte local;
consumidores por referência não precisam edição. Não declarar SYSTEM RECONCILED
universal, carregamento em Claude ou indexação. INDEX BLOCKED neste escopo: não
há autorização para atualizar índice antigo; a recuperação em arquivos é mantida.

### Complemento focal antes do freeze

Revisão intermediária L1 encontrou lacuna no teste de integração do input real:
atos/render eram spies no focal e as suítes de orçamento chamavam o domínio
diretamente. O mesmo teste focal autorizado recebeu `pf-live`: oito observações
por teclado nos campos de receita/despesa, gravação real em storage sintético,
rebind, inválido e recusa do domínio. Fixtures serve/bootstrap existentes, nenhuma
infraestrutura nova. A baseline e770 passou nas101 observações (93+8); replay do
candidate final fica na evidência externa. Não impor retenção de foco inédita nem
confundir comparação de foco observado com correção de foco legado.
