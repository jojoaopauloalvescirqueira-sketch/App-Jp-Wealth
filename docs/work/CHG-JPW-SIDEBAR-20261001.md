# CHG — Lateral padrão JP Wealth

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-SIDEBAR-20261001",
  "status": "approved",
  "objective": "Lateral padrão com exploração inline por hover/clique, overlay recolhido sem reflow, seleção azul fixa e acessibilidade",
  "risk_level": "N1",
  "authority_required": "A2",
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN (plano completo JP Wealth — aprimoramento da lateral padrão)",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06",
    "baseline_fingerprint": "5cb6611087b53f5fe1df57d14150bb3634e48ab5f3d5cb6e2237c8f9d1828a06"
  },
  "scope": {
    "allowed_files": [
      "src/js/40-app/11-operational-shell.js",
      "src/js/20-ui/12-nav-style.js",
      "src/js/20-ui/02-sidebar.js",
      "src/js/40-app/09-settings-modal.js",
      "src/js/40-app/01-navigation.js (somente adaptação do despacho se necessária)",
      "src/styles/app.css (sidebar somente)",
      "tools/navigation_sidebar_hover_test.py",
      "tools/smoke_test.py (somente pai disclosure e destino final, mantendo teste de ativacao)",
      "tools/dashboard_macro_test.py (somente aguardar transicao aprovada antes de medir gaveta lateral)",
      "tools/navigation_layout_choice_test.py",
      "tools/contextual_sidebar_test.py",
      "tools/navigation_local_contract_test.py",
      "tools/navigation_ia_test.py",
      "tools/exec_submenu_test.py",
      "tools/research_navigation_test.py",
      "tools/finpes_navigation_test.py",
      "tools/leverage_page_test.py (somente caminho de navegação UI aprovado)",
      "docs/architecture/NAVIGATION-HIERARCHY.md (complemento atual; preservar história)",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CHG-JPW-SIDEBAR-20261001.md",
      "docs/work/BRIEF-JPW-SIDEBAR-20261001.md",
      "docs/governance/CURRENT-STATE.md (nota focal da entrega, sem apagar história)"
    ],
    "forbidden_files": [
      "mt5/**",
      "downloads/**",
      "AGENTS.md",
      "skills/**",
      "docs/normative/**",
      "tools/quality_gate.py",
      "tools/agent_preflight.py",
      ".github/**",
      "sw.js",
      "src/js/00-core/**",
      "src/js/10-domain/**"
    ],
    "allowed_actions": [
      "bounded_edit",
      "synthetic_browser_tests",
      "official_generation",
      "independent_audit"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "publish",
      "read_real_account",
      "operational_MT5",
      "new_dependencies"
    ],
    "regressions_forbidden": [
      "topbar/glass/submenu layouts unchanged",
      "same route facade, aliases, guards and module availability",
      "no financial writes/render on hover",
      "preferences/drafts preserved"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "src/js/manifest.json (digest only)",
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "src/vendor/pdfjs/runtime-assets.js (official identical if emitted)"
    ],
    "generation_commands": [
      "Reconciliar somente SHA-256 das quatro fontes alteradas em src/js/manifest.json; preservar ordem e metadados (nao existe gerador dedicado desse input)",
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden for bundles; manifest digest-only computed from source bytes"
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "isolated localhost fixtures"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "acceptance_criteria": [
    "400ms hover, 300ms departure,180ms reduced-motion transition",
    "252/76 desktop,252 overlay no reflow;<=900 mobile min320,width-24",
    "parent toggle no navigation;leaf single guarded dispatch",
    "N3 and selected destination follow route, not exploration",
    "Tab/arrows/Escape, modal suspension, unique rail ownership",
    "classic/pill/kinetic keys preserved,sidebar magnetism disabled",
    "themes/32039010241440/200percent/synthetic guard scenarios"
  ],
  "approved_tests": [
    "new sidebar functional focal",
    "approved UI contract updates to existing functional focals only",
    "standard",
    "raw full",
    "independent interaction/design/scope audit"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-sidebar-20261001/baseline.tar.gz"
    ],
    "data": [
      "no financial schema,records or new persistent key"
    ],
    "verification": [
      "compare protected files to BASELINE.json; restore only task delta"
    ]
  },
  "harness": {
    "path": "/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/6C - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md",
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95"
  },
  "design_source": {
    "path": "skills/jpw-design/references/design-philosophy.md",
    "mode": "IMPLEMENTAR"
  },
  "inherited_limit": "SOURCE REVISION UNKNOWN; record unchanged, not approval"
}
```
