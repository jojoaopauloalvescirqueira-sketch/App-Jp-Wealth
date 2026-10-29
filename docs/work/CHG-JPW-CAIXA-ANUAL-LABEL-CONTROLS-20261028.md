# CHG-JPW-CAIXA-ANUAL-LABEL-CONTROLS-20261028

```json
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-CAIXA-ANUAL-LABEL-CONTROLS-20261028",
  "status": "approved",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "human user",
  "approval": "call_04e699dcb5fb4ad5ace8760f62dafd8c explicitly includes literal-label expectations in three tests, reviewed patch",
  "allowed_files": [
    "tools/portfolio_management_navigation_test.py",
    "tools/management_annual_ui_test.py",
    "tools/management_dashboard_notes_test.js"
  ],
  "allowed_change": "Only Contabilidade / Contabilidade anual / Gerenciamento · Contabilidade expected literals become Caixa Anual equivalents",
  "forbidden": [
    "gate catalog or IDs or commands changed",
    "financial assertions altered",
    "limits/timeouts/tolerances changed",
    "skipping cases",
    "repairing discovered financial/presentation defects to make rename tests green"
  ],
  "proof": "RED with new expected name on original product; GREEN on renamed product; same judge rejects old-label counterproof; independent source review plus full",
  "historical_failures": "Retain raw Hedge full4/full5 and new UI review PRODUCT_FAIL findings; no audit exception or universal readiness"
}
```

## Ampliação específica autorizada — quarta expectativa

call_ca4bee2bb5904219b50f6cd1762a1791 aprovou SIDEBAR-NAME.patch, uma única constante no caso lifecycle de tools/contextual_sidebar_test.py:363. O RED original demonstrou o breadcrumb correto do produto recusado pelo nome antigo esperado; revisão independente por AST preservou toda a outra sintaxe. Mesma rota e asserção, sem mudança de limites, catálogo ou produto. A quarta expectativa tem contraprova própria e passa pela mesma suíte acumulada.
