# Tarefa ativa — Candidate documental V11 isolado

Classe M3. Atualizado em 2026-09-08.
Fonte humana: pedido explícito para isolar a adoção V11 e abrir somente Draft PR.

```yaml
schema: jp-harness/chg/v1
change_id: CHG-2026-0908-V11-ISOLATION
status: approved
objective: reconstruir somente a adoção documental V11 sobre a main limpa, validar e publicar uma única mudança em Draft PR
risk_level: N3
authority_required: A4
approved_by: proprietário, pedido explícito desta tarefa
target:
  branch: codex/statute-v11-documental
  baseline_sha: 02d3a6991fe82569c1fe232722d9b8566fc62ecd
scope:
  allowed_files:
    - docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf
    - docs/normative/ANEXO_PARAMETRICO_CANONICO.md
    - docs/normative/README.md
    - 00 - FILOSOFIA E PROJETO/Norma Vigente (18 remoções verificadas)
    - 00 - FILOSOFIA E PROJETO/Antigo Estatuto (2 remoções verificadas)
    - AGENTS.md (referência normativa, sem enfraquecer autoridade)
    - docs/governance/PROJECT-CONTEXT.md
    - docs/governance/CONTEXT-MAP.md
    - docs/governance/CURRENT-STATE.md
    - docs/work/ACTIVE-TASK.md
    - SESSION_HANDOFF.md
    - README.md (somente V11 e validação relacionada)
    - CHANGELOG.md (somente entrada desta adoção)
    - docs/decisions/README.md (propostas V10 históricas)
    - docs/architecture/PWA-UPDATE-LIFECYCLE.md (somente entrega dos documentos)
    - docs/audit/STATUTE-V11-ISOLATION-2026-09-08.md
    - index.html (somente transparência/referência normativa)
    - src/js/40-app/04-onboarding.js (leitor e consentimento por versão)
    - src/js/40-app/09-settings-modal.js (links e transparência)
    - src/js/manifest.json (somente hashes onboarding/settings)
    - sw.js (somente cache e atendimento dos dois documentos)
    - tools/rebuild_monolith.py
    - tools/build_reproducibility_test.py
    - tools/statute_documentary_test.py
    - tools/quality_gate.py (acrescentar teste documental, sem relaxar gates)
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
  forbidden_actions: [modificar_worktree_original, alterar_formulas, alterar_parametros, alterar_schema, migrar_dados, alterar_dashboard_anterior, alterar_galton, alterar_finalizacao, merge, marcar_pr_ready, deploy]
data:
  test_policy: synthetic_only
  credentials: never_read_or_display
acceptance_criteria:
  - V11 e Anexo byte-idênticos às fontes fornecidas
  - leitor integral, documentos e downloads corretos online/offline
  - SW nunca entrega shell em lugar dos dois documentos
  - portátil inclui os originais
  - novo aceite explícito sem promover versão histórica
  - motor identificado como legado; FCR/FEO e PENDING preservados como conflitos
  - nenhuma mudança de fórmula, parâmetro ou comportamento financeiro
  - nenhum hunk local anterior do Dashboard
  - remoções recuperáveis por hash e Git blob
  - source, build e runtime identificados; ausência de segredo e drift
  - testes próprios no candidate e auditoria independente após freeze
authorized_git: [um_commit_se_gates_passarem, push_somente_branch_candidata_se_nao_afetar_producao, draft_pr_para_main]
forbidden_git: [reset, clean, stash, force_push, merge]
```

## Preservação e proveniência

A worktree `codex/dashboard-complete` é somente origem de leitura e permanece
intacta; não recebe edições, testes com rebuild, stash ou limpeza. Seu fingerprint
inicial e diff completo foram registrados fora dos repositórios antes de agir.
Esta worktree foi criada sobre a revisão exata solicitada, inicialmente limpa.
Os hunks compartilhados serão reexpressos sobre essa base; o Dashboard já integrado
na main permanece, e suas melhorias locais anteriores não entram nesta mudança.

## Topologia e autoridade

O proprietário confirmou nesta tarefa: “Não foque no netlify por hora, ele ainda
não está em uso”. Há apenas configuração declarativa Netlify e workflow de qualidade;
site, produção e SHA publicada não foram identificados. Nenhum deploy é
autorizado. A confirmação permite prosseguir com o candidate GitHub documental,
condicionado aos testes/auditoria e sem merge ou deploy.

## Validação e rollback

Build oficial, teste documental focal, reprodutibilidade, full e fast na nova
worktree, segurança/higiene, auditoria independente e conferência de preservação
da origem. Resultados anteriores são históricos e não comprovam este candidate.
A falha intermitente Finalizar Sessão/Galton permanece registrada; não será corrigida
neste escopo. Em falha material, parar sem publicar. A origem não precisa de
rollback porque não será modificada; a branch isolada pode permanecer para revisão.

## Resultado

Checkpoint pré-freeze: build isolado1ee88bab37539798, focal documental PASS,
full 55/55 PASS e fast final 4/4; evidências e histórico das triagens na auditoria.
A publicação depende da auditoria independente posterior ao freeze.
Os identificadores posteriores de commit/push/Draft PR e resultado da auditoria
serão registrados no relatório externo e no PR, sem antecipação neste checkpoint.
Não declarar READY_FOR_NEXT_DEVELOPMENT_CYCLE. O próximo gate humano é revisar o
Draft PR documental; resolver contratos normativos exige trabalho próprio.
Merge e deploy exigem outra autorização explícita.
