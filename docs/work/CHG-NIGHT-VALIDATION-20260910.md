# CHG-NIGHT-VALIDATION-20260910 — complemento de avaliação

Autorização específica recebida após escolha A. Não é aceite do candidate nem publicação. Contrato anterior à instrumentação/ajustes desta rodada. V2 e relatório anteriores ficam preservados. ACTIVE-TASK/contexto canônico não serão editados, prevalecendo o escopo humano sobre a sugestão da skill.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-NIGHT-VALIDATION-20260910",
  "status": "approved",
  "objective": "Concluir avaliação dos sete checks falhos, sem modificar runtime/build/quatro correções.",
  "risk_level": "N3",
  "authority_required": "A4",
  "risk_basis": "Trilha dedicada de avaliação: risco de falsa evidência em testes críticos de persistência/PWA; classificação conservadora, sem autorização financeira ou Git.",
  "target": {
    "root": "/Users/joaopauloalves/.codex/night-reviews/20260910/product",
    "branch": "codex/night-review-20260910",
    "baseline_sha": "4cb2e2a24c58a714b9909df6dd6f0415097480e2"
  },
  "scope": {
    "allowed_files": [
      "tools/smoke_test.py",
      "tools/settings_modal_test.py",
      "tools/statute_documentary_test.py",
      "tools/galton_board_test.py",
      "tools/finalize_session_test.py",
      "tools/storage_governance_test.py",
      "tools/mvp_notes_test.py",
      "tools/dashboard_macro_test.py",
      "tools/browser_bootstrap_fixture.py",
      "docs/work/CHG-NIGHT-VALIDATION-20260910.md",
      "docs/audit/NIGHT-VALIDATION-20260910.md"
    ],
    "allowed_actions": [
      "observação desde primeira carga",
      "ajuste mínimo de fixtures/initialização/helper dos sete checks",
      "cópias equivalentes sintéticas e controles negativos externos",
      "focais e FULL existente",
      "relatórios/auditoria/freeze no destino durável"
    ],
    "forbidden_actions": [
      "edição runtime/build/manifest/artefatos",
      "produto/norma/schema/dados reais/dependências",
      "Harness/gates/CI/agentes/Atlas/contexto canônico",
      "alterar política loopback-only.sb",
      "commit produto/push/PR/merge/deploy",
      "retries sem aprendizado"
    ],
    "regressions_forbidden": [
      "remover/filtrar assertions/console",
      "JSON genérico para qualquer recurso",
      "perda SW nos testes controller/offline",
      "reset ou alteração de dados originais"
    ]
  },
  "external_side_effects": {
    "network": "forbidden",
    "allowed_targets": [
      "loopback conforme perfil existente cf35cca89f2e1b677995e788c0fe365bf627c641f260a3e4ea80cbde31a0c60e"
    ],
    "temporary_artifacts": "allowed",
    "destinations": [
      "/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910",
      "tools/.artifacts"
    ]
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "derived_artifacts": {
    "allowed": [],
    "generation_commands": [],
    "manual_edit": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python/Playwright/Chromium/Node existentes",
      "sandbox-exec perfil inalterado",
      "Git somente leitura; init/add/commit só fixtures próprias autorizadas no FULL"
    ]
  },
  "acceptance_criteria": [
    "causa por check demonstrada ou lacuna específica",
    "cenários interrompidos concluídos ou bloqueio",
    "V2 e histórico preservados",
    "mesma configuração de testes por comparação de produtos",
    "novas fixtures específicas continuam detectando erros",
    "FULL no freeze final, não a cada tentativa",
    "runtime/build e originais intactos"
  ],
  "approved_tests": [
    "sete focais before em baseline e candidate com trace somente",
    "contraprova SW context.route real instalada",
    "sete focais after nas duas versões com mesma configuração",
    "controles negativos sintéticos de recurso/console/documento",
    "regressões quatro correções via FULL final",
    "auditoria independente focal de delta de avaliação"
  ],
  "rollback": {
    "source": [
      "restaurar somente delta de avaliação comparado às cópias preserved-v2/candidate-before; preservar correções noturnas"
    ],
    "application_state": [
      "não tocar dados reais"
    ],
    "environment": [
      "nenhuma mudança global; encerrar só processos próprios"
    ],
    "verification": [
      "hashes V2 e entrega; original/stash/PF; perfil de rede"
    ]
  },
  "approved_by": "proprietário, resposta sim à escolha A deste complemento",
  "approved_at": "2026-09-10T13:06:04.717156+00:00",
  "expires_on": [
    "drift material",
    "runtime/permission/schema change required",
    "files/effects beyond scope"
  ]
}
```

Compreensão: JP Wealth é local-first financeiro; erro de fixture não pode ocultar erro de persistência nem produzir falsa aprovação. As quatro correções seguem byte-idênticas. Os sete testes têm guardas de console e alguns importam o boot Dashboard; três falhas já identificam FF, quatro precisam URL desde início. FX escreve instrumentos/save no boot, FF grava cache próprio; estabilização deve preceder snapshots, sem filtrar gravações posteriores. Documental e run_cache de finalização precisam SW real.

Fontes: AGENTS/CHANGE-PROCESS/QUALITY-GATES, competências do projeto, sete fontes de testes, ffNewsSanitizeEvents e fetchOneRate, triagemV2 e relatório noturno, skills preflight/change-control/test-triage/browser/data-safety/security/post-change. Harness A0 hash c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8, §§12–16,27–28,48,53–56. Preflight audit/edit PASS com14alterações conhecidas e aviso histórico de contexto; não autoriza reconciliação automática.

Plano causal: primeiro instrumentar cópias dos sete scripts (e helper importado) para eventos contexto/request/response/requestfailed/console antesgoto/set_content. Nenhuma rota/oráculo muda nessa comparação. Depois de identificar incompatibilidade, fixture comum pequena para URLs econômicas exatas, sem novo framework. Unknown resources seguem falhando. Manter taxas já usadas na finalização e demais testes; estabilizar bootstrap antes do estado-base quando necessário. Helper opcional Dashboard somente para consumidor documental, preservando default/CTAs. Verificar suporte real a context.route no SW instalado; a documentação antiga e implementação atual divergem e não bastam sem contraprova. Duas tentativas sem aprendizado bloqueiam o item.

## Ajuste focal após avaliação V3a, antes do freeze final

As14comparações before falharam; as14afterV3a passaram com mesma configuração por produto. Captura desde início identifica feed+oitoFX, com requisições do SW em Notas/Estatuto. SWproof comprovou context.route no worker instalado. Quatro negativos rejeitaram recurso desconhecido, erroconsole, PDFcom1bytealterado emresposta e feedinválido; arquivosoriginais preservados.

Auditoria inicial detectou P2: a guarda de recursos desconhecidos só era chamada no wait inicial. Acrescentar sua chamada explícita nas fronteiras de fechamento existentes dos setechecks mantém detectável request tardia sódoSW, semdependência de erroconsole da página. Não mudaroráculos existentes. PreservarV3a/recibos e repetirfocaisafetados sob revisãoV3b, depoisFULLúnico. Controle novo usará consent_case original e request inesperada apósboot, suprimindo somente o console do probe deliberadamente para isolar a nova guarda; isso não é configuração dos testespositivos.
