# GLOBAL TYPOGRAPHY, SPACING & PROPORTION CALIBRATION

## Brief / finalidade
JP Wealth apresenta organização financeira, risco e estudos a partir de fontes canônicas. CSS/index e renderizadores UI compõem o produto; esta campanha melhora sua geometria sem alterar os fluxos ou confirmar dados por aparência. O problema relatado em Configurações é tratado em todas as superfícies: escala, ritmo, leitura, controles e adaptação. X1 governa escolhas visuais, X2 revisa independentemente. Não é outro sistema visual, homologação financeira ou campanha de bugs.

Baseline main integrada PR18: 011e27512598b045df0c91b0480752cc6e43d4e5, build3caa2057e0f10f69; nova worktree limpa. Final-r3/303 inputs, evidências e recovery permanecem na pasta anterior. Preflight edit PASS com aviso contextual histórico: documentos do redesign descrevem candidate sobre fafb228; integração conferida no Git/recibos, sem mudança de instruções ou domínio. Não atualizar genericamente fontes históricas.

Fontes lidas: AGENTS; README; CONTEXT-MAP; PROJECT-CONTEXT; QUALITY-GATES; APPLE-EXPERIENCE-DIRECTION; X1/SKILL e filosofia composição/acessibilidade; X2/SKILL; Harness master §§12–20,31,36–48 (hash no recibo de fontes). Suas instruções não ampliam a autorização humana. O inventário textual inicial encontrou623 declarações font-size/77 expressões e468 gap/65 expressões; não é contagem de valores renderizados nem meta de redução.

## CHG
```yaml
schema: jp-harness/chg/v1
change_id: CHG-VISUAL-PROPORTION-CALIBRATION-20260913
status: approved
objective: Calibrar globalmente proporção tipográfica espacial e controles do design existente; entregar candidate local.
risk_level: N1
authority_required: A2
target:
  root: /Users/joaopauloalves/.codex/visual-calibration/20260913/product
  branch: codex/visual-proportion-calibration-20260913
  baseline_sha: 011e27512598b045df0c91b0480752cc6e43d4e5
scope:
  allowed_files: [src/styles/app.css, index.html, src/js/40-app/09-settings-modal.js, src/js/manifest.json, tools/visual_proportion_test.py, build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, docs/work/ACTIVE-TASK.md, docs/work/CHG-VISUAL-PROPORTION-CALIBRATION-20260913.md]
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/**, docs/normative/**, src/js/00-core/**, src/js/10-domain/**, src/js/30-accounting/**, .github/**, sw.js, tools/quality_gate.py, tools/validate_project.py, tools/rebuild_monolith.py]
  allowed_actions: [calibração CSS e markup de apresentação, teste focal, derivados oficiais, contrato e cabeçalho factual, evidências externas, branch e worktree expressamente autorizadas]
  forbidden_actions: [staging, commit do produto, tag, push, PR, merge, deploy, reset Git, stash, dados reais, nova persistência, dependências, reindexação]
  regressions_forbidden: [mudança financeira, perda de rascunhos ou preferências, alteração de rotas ou save, ocultação de alertas ou conteúdo essencial, duplicação de eventos, mudança de A10-A13 ou matemática Lab]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [Apple Developer público para referência, loopback de testes]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [Python Playwright Chromium existentes, gerador oficial, sandbox loopback existente, Git de leitura e branch/worktree autorizadas, fixtures Git descartáveis próprias sem remoto/hooks]
acceptance_criteria: [onze áreas e superfícies auxiliares examinadas, hierarquia contextual com tokens existentes, sem overflow material nos cenários, 320 390 768 1024 1440 claro escuro, zoom e texto longo, foco e controles acessíveis, nenhuma alteração de domínio, comparações before-after, auditoria independente, recovery e candidate identificado]
approved_tests: [visual_proportion_test, apple_experience_test, design_experience_test, focais pertinentes existentes, standard, full, reprodutibilidade e PWA existentes]
rollback:
  source: ../evidence/baseline.tar e baseline.json; restaurar em cópia, comparar hashes e reverter somente delta próprio quando autorizado; nunca reset amplo
  data: perfis sintéticos isolados
  environment: não modificar main outras worktrees stash ou evidências anteriores
  verification: recuperação de todos os inputs finais com hash e modo
approved_by: proprietário, prompt af4a3183 e AUTORIZAÇÃO ESPECÍFICA DE BRANCH
approved_at: 2026-09-13
expires_on: [mudança de domínio ou persistência necessária, conflito material, nova dependência, impossibilidade de isolamento]
```

## CTX delimitado
CHG autoriza apenas este contrato e cabeçalho de ACTIVE-TASK. Registro de entendimento, decisões, evidências e limites desta campanha; histórico anterior preservado. Demais mapas, Harness, skills e políticas não recebem edição. Manifest somente hashes se a fonte JS autorizada mudar; scripts/ordem permanecem.

## Expectativas fixadas antes do CSS
- Settings: título da janela e seção têm hierarquia discreta; headline interno menor que título de página; cards de navegação alinhados à esquerda com ícone subordinado. Busca e fechar acessíveis, sem faixa vazia imposta por altura mínima arbitrária.
- Títulos globais/página/painel distinguíveis; rótulos e metadados legíveis, preferência fs-scale aplicada uma única vez. Não reduzir tudo linearmente.
- Espaços estruturais reutilizam jp-space; entrelabel/controle menor que entreseções. Tabelas, texto narrativo, métricas e charts conservam densidades distintas.
- Matriz de telas e diálogos com mesmas fixtures antes/depois; capturar Settings aberto (a captura automática histórica após Escape não prova esse modal).
- Viewports320/390/768/1024/1440, temas, long labels/erros/números, teclado/retorno de foco, alvos>=24px salvo exceções reais; buscar44px em toque. Zoom CSS não será rotulado como zoom nativo; tentar mecanismo existente sem instalar nem ampliar permissões.
- Navegação repetida não muda S/armazenamento; botões e avisos continuam acessíveis. Focais e FULL existentes sem enfraquecer juiz/expectativas.
- Congelar após validações; revisão independente X2 e recovery; aceite humano permanece pendente.
