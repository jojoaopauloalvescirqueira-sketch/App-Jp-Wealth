# CHG-JPW-EMPTY-FIRST-USE-TESTS-20261024

Records human authorization; grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/primeiro-acesso-vazio-20261024",
    "baseline_sha": "a4bf278cd4dc38bbaa5b905ed17a79e33684fb67"
  },
  "approved_by": "human user",
  "approved_at": "2026-10-24",
  "approval": {
    "evidence": "PLEASE IMPLEMENT THIS PLAN: JP Wealth — primeiro acesso realmente vazio; Autorizar essa branch e preservar todas as alterações",
    "limits": "Only approved plan, preserve existing candidate and saved data; no commit/merge/push/publication/dependencies/formula changes."
  },
  "rollback": {
    "source": "/private/tmp/jpw-empty-first-use-20261024/baseline.json; baseline-pending.zip; baseline-sources; reverse own delta only"
  },
  "harness_source": {
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "sections": "12-14,19,24,28-30,36-49"
  },
  "approved_tests": [
    "empty_first_use_test.py",
    "affected accumulated focals",
    "quality_gate.py --tier full"
  ],
  "acceptance_criteria": [
    "No pre-created user facts/answers on clean first use",
    "Explicit null differs from zero and malformed/missing input",
    "Saved bases/history/guards preserved",
    "Current RED/GREEN, counterproofs, independent review and full gate"
  ],
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "explicit null accepted for documented absent values; no automatic data deletion"
  },
  "forbidden_actions": [
    "commit",
    "merge",
    "push",
    "publication",
    "real-data mutation",
    "global-memory mutation",
    "dependency installation"
  ],
  "change_id": "CHG-JPW-EMPTY-FIRST-USE-TESTS-20261024",
  "objective": "Protect clean boot and compatibility; make fixtures explicit without weakening accumulated assertions",
  "risk_level": "N3",
  "authority_required": "A4",
  "scope": {
    "allowed_files": [
      "tools/empty_first_use_test.py",
      "tools/*_test.py only affected explicit fixture setup or deliberately replaced null rejection",
      "tools/empty_first_use_fixture.py",
      "tools/regression-memory.json",
      "docs/validation/empty-first-use-20261024/"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "tools/quality_gate.py",
      ".github/",
      "docs/normative/"
    ]
  },
  "test_contract": "Only null rejection is replaced by accepted documented absence; missing/string/boolean/fraction/out-of-range remain rejected. Legacy tests may get explicit synthetic accounts/capital/checklist fixtures preserving their oracles. New boot proof must not inject financial state. No thresholds/skips/timeouts lowered. Dedicated focused command additional to unchanged full runner; independent counterproof/review required."
}
```

## Inicializador de cadastro — reconciliação delimitada

EMPTY-CREATE-01 demonstrou por UI que cadastro sem observação gravava sini/satu0. O contrato aprovado usa null para saldos não informados; fx_account_registration_test.py conserva seus cenários e substitui somente as três expectativas estruturais0→null de criação/recadastro. Contas legadas com zero explícito devem permanecer zero e têm contraprova no focal novo. Não altera ativo, período, rascunho, histórico nem regra financeira.

## Fixtures de preservação de sessão — reconciliação delimitada

O FULL2 terminou com 100 PASS e dois PRODUCT_FAIL brutos, preservados nos recibos. A triagem independente demonstrou uma pré-condição ausente em `alladin_finalize_preservation_test.py` (C8/C11/C14) e `session_write_serialization_test.py`: ambos tratavam contas vazias como prova de perda, mas não criavam uma conta. O produto corretamente começava com zero contas.

A correção instala uma conta sintética explicitamente identificada apenas nesses testes, sem alterar produto, sequência, prazos, runner ou asserções anteriores. C8/C11/C14 também exigem igualdade integral antes/depois. A causalidade foi demonstrada por vazio 0→0, fixture preservada 1→1 e mutante destrutivo 1→0 rejeitado. A revisão independente aprovou os patches exatos; focais e novo FULL permanecem obrigatórios. Essa adaptação está contida na autorização original para substituir fixtures implícitas sem enfraquecer suas proteções.
