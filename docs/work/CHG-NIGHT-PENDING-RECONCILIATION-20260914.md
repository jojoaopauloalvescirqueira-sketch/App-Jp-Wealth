# NIGHT PENDING RECONCILIATION — contrato e brief

Autorização vigente: anexo 72ee72b7-8737-48c0-9f4b-34676428202f. Um lead/escritor coordena os lotes; análises e auditoria independentes não editam produto. A origem exata foi reproduzida antes desta escrita: 309 inputs, build7432a52edd5a00be, fingerprint70577cf6c710d02fb2b9a1868dc4cdb01522be764676c7c447c26270c64bfaff. Os 17 deltas herdados pertencem ao snapshot autorizado, não são autoria desta campanha.

## Compreensão e decisão delimitada

JP Wealth organiza registros financeiros locais; perder dados ou anunciar confirmação inexistente viola sua finalidade. Notas organiza texto/rascunhos; core mantém gates e estado; daily-ledger orquestra export/import; Settings, Dashboard e calendário projetam estados. O backup clona S completo e remove segredos; a pasta escolhida é destino de exportação, não banco primário. A confirmação de backup atual muta backup/log antes de ignorar save, e o Dashboard ignora UNKNOWN e vencimento. Reutilizaremos o lote Notas final-r1 já entregue somente onde compatível com a origem309, sem incluir silenciosamente a Central de Notificações posterior.

Lote A: reaproveitamento rastreável de janela/ícone/posição e regressões, mantendo fontes canônicas de dados. Lote B: guardas e rollback delimitados à confirmação, estado de persistência e freshness compartilhados, cobertura explícita, export por fase, fronteira de importação e avisos do calendário. Lote C: interferências, FULL, freeze, revisão independente e recovery.

O parser de importação distinguirá agregado ausente legado de agregado explicitamente incompatível, antes da troca, conforme autorização atual. Não muda migrate nem fórmulas. Metadados descritivos de cobertura/build podem usar extensão compatível do envelope existente, sem novo schema financeiro, mantendo seus campos e aceitação histórica; incompatibilidade real exige parada do item. Export iniciado por download não será tratado como arquivo fisicamente salvo; erro indeterminado não habilita tentativa cega nem Finalizar. Nenhuma mudança no protocolo crítico de sessão ou filesystem é autorizada por esta implementação: lacuna nessa fronteira será delimitada.

Oráculos fixos: recusa mantém disco e confirmação/log anteriores; save posterior não ressuscita confirmação recusada; UNKNOWN não anuncia salvo; 30 dias segue DG_BACKUP_DUE_DAYS, sem novo limite; raw inválido não substitui estado; legacy ausente continua aceito; dados válidos round-trip semanticamente; perfil/foto/posição/cache/handles/segredos excluídos. No contexto de testes, inicialização normal é estabilizada antes do checkpoint para não atribuir normalização antiga ao delta.

Preflight edit sem allow-dirty bloqueou os 17 caminhos herdados; autoria/escopo provados pelo recibo origin-reproduction. Usar a opção existente --allow-dirty para esse snapshot identificado, sem mudar o gate. Advertência temporal de contexto é preservada; CTX apenas documental focal. Aceite humano e publicação permanecem separados.

Fontes lidas: AGENTS; CONTEXT-MAP; PROJECT-CONTEXT/CURRENT-STATE históricos; DB-STORAGE-GOVERNANCE; STATE-SCHEMA; DATA-RECOVERY; SECURITY-MODEL; QUALITY-GATES; skills preflight/change-control/data-safety/X1/X2/browser/test-triage/security/post-change e impacto agêntico. Harness master hash c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8, §§12–16,24,27 e instruções pertinentes. Fontes de código examinadas pela base reproduzida; relatório backup-review é diagnóstico, não patch.

## CHG

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-NIGHT-PENDING-RECONCILIATION-20260914",
  "status": "approved",
  "objective": "Concluir Notas e confiabilidade de backup/storage/avisos in-app em um candidate local, reutilizando deltas comprovados.",
  "risk_level": "N2",
  "authority_required": "A3",
  "target": {
    "root": "/Users/joaopauloalves/.codex/night-pending-reconciliation/20260914/product",
    "branch": "codex/night-pending-reconciliation-20260914",
    "baseline_sha": "5f0c9680bdd9a93e9d184ca751999c70193a72aa"
  },
  "scope": {
    "allowed_files": [
      "index.html",
      "src/styles/app.css",
      "src/js/40-app/07-finalize-session.js",
      "src/js/40-app/09-settings-modal.js",
      "src/js/40-app/14-mvp-notes.js",
      "src/js/00-core/04-persistence.js",
      "src/js/30-accounting/01-daily-ledger.js",
      "src/js/40-app/12-global-dashboard.js",
      "src/js/40-app/15-ff-news.js",
      "src/js/40-app/16-storage-governance.js",
      "src/js/40-app/17-economic-calendar.js",
      "src/js/20-ui/25-dash-macro.js",
      "src/js/manifest.json",
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "tools/notes_experience_test.py",
      "tools/notes_launcher_test.py",
      "tools/mvp_notes_test.py",
      "tools/finalize_session_test.py",
      "tools/studies_notes_persistence_contract_test.py",
      "tools/storage_governance_test.py",
      "tools/ff_news_cache_test.py",
      "tools/backup_reliability_test.py",
      "README.md",
      "docs/architecture/CODE-MAP.md",
      "docs/architecture/DB-STORAGE-GOVERNANCE.md",
      "docs/architecture/STATE-SCHEMA.md",
      "docs/recovery/DATA-RECOVERY.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CHG-NIGHT-PENDING-RECONCILIATION-20260914.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/**",
      ".github/**",
      "docs/normative/**",
      "src/js/00-core/03-default-state.js",
      "src/js/00-core/06-storage-fs.js"
    ],
    "allowed_actions": [
      "single-author scoped edits",
      "existing local tests",
      "synthetic Chromium",
      "official derived build",
      "external evidence",
      "independent audit"
    ],
    "forbidden_actions": [
      "staging",
      "commit",
      "push",
      "PR",
      "merge",
      "deploy",
      "tag",
      "reset",
      "stash",
      "cleanup of other worktrees"
    ],
    "regressions_forbidden": [
      "financial rules",
      "domain schema",
      "secrets exposure",
      "draft loss",
      "false success",
      "preference reset",
      "live economic APIs"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "loopback only, existing economic fixtures"
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
      "existing Python/Playwright/Chromium",
      "local server",
      "read-only Git",
      "authorized branch/worktree creation already performed"
    ]
  },
  "acceptance_criteria": [
    "origin 309 exact before implementation",
    "Notes centered, icon, responsive, same instance and persisted normalized launcher position",
    "backup coverage explicit and compatible envelope",
    "refused confirmation not retained",
    "UNKNOWN never saved/healthy",
    "freshness shared across consumers",
    "safe import and synthetic multimodule round-trip",
    "coherent calendar and recovery notices",
    "full pass, no material audit blocker, reproducible delta recovery",
    "human review prepared without acceptance"
  ],
  "approved_tests": [
    "existing Notes experience and launcher focals reused code but rerun on this target",
    "backup_reliability_test.py characterization then candidate",
    "storage_governance_test.py",
    "ff_news_cache_test.py",
    "studies_notes_persistence_contract_test.py",
    "quality_gate.py --tier full",
    "cross-cutting isolated UI and independent audit"
  ],
  "rollback": {
    "source": [
      "origin-reproduction.json + preserved recovery-notes-r2; own delta only in fresh recovery destination"
    ],
    "application_state": [
      "disposable synthetic browser context only"
    ],
    "data": [
      "no real data"
    ],
    "environment": [
      "preserve all original worktrees, stash, checkpoints"
    ],
    "verification": [
      "hashes/modes of inherited 309 and each protected candidate"
    ]
  },
  "approved_by": "owner: attached explicit NIGHT PENDING RECONCILIATION request",
  "approved_at": "2026-09-14",
  "expires_on": [
    "material scope/identity drift",
    "new permissions or financial change needed"
  ]
}
```

## CTX

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-NIGHT-PENDING-RECONCILIATION-20260914",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/night-pending-reconciliation/20260914/product",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/night-pending-reconciliation-20260914",
  "create": [
    "docs/work/CHG-NIGHT-PENDING-RECONCILIATION-20260914.md"
  ],
  "modify": [
    "README.md",
    "docs/architecture/CODE-MAP.md",
    "docs/architecture/DB-STORAGE-GOVERNANCE.md",
    "docs/architecture/STATE-SCHEMA.md",
    "docs/recovery/DATA-RECOVERY.md",
    "docs/work/ACTIVE-TASK.md"
  ],
  "preserve": [
    "all prior contracts and evidence",
    "ACTIVE-TASK historical body",
    "old Notes and notification candidates"
  ],
  "do_not_touch": [
    "CURRENT-STATE.md",
    "SESSION_HANDOFF.md",
    "Harness",
    "AGENTS",
    "skills",
    "indices",
    "financial norms"
  ],
  "source_of_truth": {
    "storage": "src/js/00-core/04-persistence.js",
    "backup": "src/js/30-accounting/01-daily-ledger.js",
    "notes": "src/js/40-app/14-mvp-notes.js"
  },
  "acceptance_criteria": [
    "only factual directly affected docs",
    "no inferred acceptance or integration"
  ],
  "approved_by": "owner: attached explicit NIGHT PENDING RECONCILIATION request",
  "approved_at": "2026-09-14"
}
```

Consumidor adicional confirmado antes da escrita: `src/js/20-ui/25-dash-macro.js` projeta o calendário no Dashboard. Incluído exclusivamente para consumir o mesmo estado de atualização, sem mudar dados, consultas ou regras.

## Complemento autorizado — unificação final, 2026-09-14

Autorização: attachment 6883fa39-0280-49b8-8d0c-fcfbafb6bc96. Preservado final-r5 (312 inputs/build834192ce7d6f988d/fingerprint4b497eb4efb02f4134c387fd0c4b38cd94fd0b00702b67e90d898f6531cbc9fc). Nova revisão cumulativa, não byte-idêntica. N2 produto e exceção N3/A4 exclusivamente diagnóstico do workflow. Git autorizado após gates, sem deploy/limpeza.

CHG/CTX: preservar Notes/Backup da revisão posterior e incorporar Notifications final de272b1d5, reconciliando consumers de status. Caminhos adicionais: .github/workflows/quality-gate.yml; src/js/40-app/18-notification-center.js; docs/architecture/NOTIFICATION-CENTER.md; docs/work/CHG-NOTIFICATIONS-CENTER-20260914.md (proveniência); tools/notification_center_test.py; sw.js; tools/apple_experience_test.py; tools/smoke_test.py. Demais caminhos afetados já delimitados: index.html,src/styles/app.css,src/js/manifest.json,build-id.js,dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html,tools/finalize_session_test.py,tools/notes_launcher_test.py,README.md,CODE-MAP,ACTIVE-TASK e este contrato. Alterações de causa demonstrada limitadas a estes consumidores e testes; sem nova regra financeira.

O produto mantém dados locais, drafts e bloqueios; comunicação in-app lê as mesmas fontes, não cria segunda verdade. Verificação: focais Notes/Backup/Notifications/Settings/Finalizar,200%dark,responsivo,standard/FULL e auditoria independente; CI diagnóstico não altera oráculos. Recovery somente delta em destino vazio; não restaurar outras worktrees. Inventário, overlaps e evidências em ../evidence/unification-ci (externo à árvore). Aceite anterior não é prova do novo source; nenhuma conferência manual é inventada.


Complemento causal da revisão unificada: adapter Notifications preserva dgBackupStatus().due e atenção unknown, sem cobrança em base vazia. Reprodução negativa e regressão distinguem base inativa/ativa/current/overdue/data inválida. Teste do launcher captura gesto por alvo/pointerId, eventos/viewport/foco/hit target e classifica interrupção não comandada como precondição interrompida (ENVIRONMENT_ERROR não-PASS, causa externa não presumida). Abertura de gesto estável permanece obrigatória; cenário nativo de resize exige cancelamento sem gravação e próximo clique/teclado funcional. Contraprovas sintéticas impedem abertura e consomem clique posterior, devendo produzir PRODUCT_FAIL. Nenhuma alteração no runtime launcher. Resultado histórico18PASS/1PRODUCT_FAIL preservado, causa retroativa inconclusiva; FULL remoto diagnóstico não reproduziu a antiga falha54/55. Rollback somente este delta contra recovery final-v1, sem restaurar worktrees alheias. Autoridade causal de teste coberta pelas seções5/6 do pedido6883fa39, sem alteração dos gates.
