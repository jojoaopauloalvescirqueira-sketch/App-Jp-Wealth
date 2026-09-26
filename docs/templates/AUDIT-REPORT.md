# Relatorio de auditoria

- Data:
- Auditor:
- BASE_SHA / HEAD_SHA:
- Escopo e exclusoes:
- Fontes consultadas:
- Ambiente:

## Resumo

- Nota de qualidade:
- Estado: aprovado | aprovado com ressalvas | bloqueado

## Achados

| ID | Severidade | Local | Evidencia | Impacto | Correcao proposta | Nivel |
|---|---|---|---|---|---|---|

Para uso excepcional de `HISTORICAL_UNRESOLVED_FAILURE`, registrar um finding estruturado conforme Harness §19.1, sem alterar o schema `jp-harness/aud/v1` nem os recibos. Preencher todos os campos abaixo e anexar as evidências. Campos não observados permanecem explícitos; ausência material bloqueia a disposição.

```yaml
finding_type: HISTORICAL_UNRESOLVED_FAILURE
policy_version: jp-harness/historical-unresolved-failure/v1
policy_activation_record:
  path:
  sha256:
original_test_id:
original_receipt:
original_result: PRODUCT_FAIL
symptom:
missing_historical_observation:
candidate_identity:
  candidate:
  source_revision:
  build_id:
  fingerprint:
  artifacts: {}
subsequent_evidence: []
equivalence_assessment:
delta_relevance_assessment:
affected_property:
risk_level:
residual_risk:
reopening_triggers: []
auditor_identity:
final_disposition:
```

O gate bruto continua falho. Somente auditor independente pode emitir, no máximo, `AUDIT_PASS_WITH_DEBT`; Human Acceptance e autorizações de integração seguem pendentes.

## Evidencias de teste

| Comando | Resultado | Candidato | Observacao |
|---|---|---|---|

## Riscos residuais

-

## Decisoes humanas necessarias

-
