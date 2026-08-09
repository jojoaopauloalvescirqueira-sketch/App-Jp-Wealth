# Gates de qualidade e evidencia

## Taxonomia obrigatoria

- `PASS`: comando executado e criterio atendido.
- `PRODUCT_FAIL`: produto violou contrato valido.
- `TEST_HARNESS_FAIL`: teste, fixture ou expectativa esta incorreta.
- `ENVIRONMENT_ERROR`: ambiente impediu conclusao.
- `BASELINE_FAIL`: falha anterior ao diff, comprovada no baseline.
- `NOT_RUN`: verificacao omitida com justificativa.

## Tiers locais

### Fast

Para documentacao, governanca e iteracao curta:

- preflight auditavel;
- `validate_project.py`;
- `git diff --check`.

### Standard

Para N0-V e N1:

- tudo do fast;
- smoke test;
- testes focados da area;
- browser real nos fluxos e viewports afetados.

### Full

Para N2, N3, integracao ou candidato de release:

- tudo do standard;
- todos os testes `*_test.py` listados pelo gate;
- rebuild portatil e verificacao de drift;
- auditoria de seguranca e persistencia;
- revisao integral do diff final.

Execute com:

```bash
python3 tools/quality_gate.py --tier fast
python3 tools/quality_gate.py --tier standard
python3 tools/quality_gate.py --tier full
```

O gate grava relatorio local em `tools/.artifacts/`, que e ignorado pelo Git. O relatorio deve conter SHA, dirty state, comando, duracao, retorno e cauda da saida.

## Validade da evidencia

- Mudanca em runtime, teste, manifest, fixture ou configuracao invalida os gates afetados.
- Teste focado nao substitui o tier exigido.
- Resultado antigo pode ser citado como baseline, nunca como PASS atual.
- Teste que deixa de falhar apos afrouxar uma expectativa precisa de justificativa independente.
- CI verde nao substitui fluxo manual quando o criterio exige percepcao visual ou dados do navegador.
