# Aparato local de testes (opt-in)

`sidecar/sitecustomize.py` registra entrega de recursos e ciclo do servidor/browser nos testes locais. Sua fila HTTP de loopback é 128 quando ativada. Sem `JPW_INFRA_MODE`, ele não interfere; o aplicativo, o gate e seus critérios não o importam diretamente. `validate_trace.py` produz um recibo de observabilidade separado do resultado canônico do gate.

Execute a partir da raiz do repositório, com Python/Playwright já configurados, e grave artefatos fora da árvore de produto:

```sh
export PYTHONPATH="$(pwd)/tools/test_infra/sidecar${PYTHONPATH:+:$PYTHONPATH}"
export JPW_INFRA_MODE=full-local
export JPW_INFRA_BACKLOG=128
export JPW_INFRA_TRACE=/caminho/externo/full-local.jsonl
python3 tools/quality_gate.py --tier full --artifact /caminho/externo/full-local.artifact.json
python3 tools/test_infra/validate_trace.py \
  --trace /caminho/externo/full-local.jsonl \
  --root "$(pwd)" \
  --out /caminho/externo/full-local.infra.json
```

O validador pode produzir `OBSERVABILITY_INCOMPLETE` mesmo quando o gate passa: service workers em teardown e servidores HTTP customizados têm limites de proveniência descritos no [CHG de integração](../../docs/work/CHG-TEST-INFRA-INTEGRATION-20260923.md). Não converter esse laudo em `INFRA_OK` nem usar a fila 128 como prova da causa histórica da intermitência. Para reverter a instrumentação, execute os testes sem essas variáveis; não há serviço ou instalação permanente.

Proveniência: sidecar v3 SHA-256 `6347bac648cf6094e8d5f74f50fc588344da42764a79a943874ae341b3cf9e2a`; validador v5 SHA-256 `30610b0e3e2faccba26d636aa2748e435dcf5f97e821f00e1b21496f548174a0`. Os recibos, a auditoria e o histórico de falhas originais permanecem em `/Users/joaopauloalves/.codex/jpw-test-infra/20260923/`.
