# CI — display e runtime — 01/11/2026

N3 de control plane. A4 específico na conversa: “Aprovar patch de runtime e continuar”, para o patch apresentado em outputs/proposta-ci-runtime.patch (question call_4c2c9843f1304208ade7e63eab71a532). Base `9e050a1cf832ce52aa69e4b72680686f1faf6a66`; branch autorizada `codex/backup-unificado-20261031`, limpa antes da edição. Autorização anterior para usar contratos versionados nesta implementação permanece; Harness externo ausente não foi reconstruído. Git autorizado anteriormente; sem publicação de site ou exclusões.

## Compreensão e contrato delimitado

O app organiza registros financeiros; esta alteração cuida exclusivamente da infraestrutura que verifica o artefato web. `.github/workflows/quality-gate.yml` instala Playwright1.60/Chromium148 mas os launchers priorizam `/usr/bin/chromium` quando JP_WEALTH_CHROMIUM está ausente. Os checks obrigatórios Hedge e Gerenciamento incluem zoom nativo200% com janela; o Linux do workflow não tinha servidor X ativo. Dados/finanças, fontes do app, testes e seus oráculos não podem mudar.

Alterar somente a etapa Run quality gate: obter executável instalado pelo Playwright, registrar versão e executar o mesmo comando sob Xvfb1440×1000×24. Antes SHA256 `0e171b0a0b7a5f7c61e3f97fb13ed93c9d14fe46c0ed247e3acbd3edfc1dafc4`; depois `e9d5dcbd6fcf8301b37893398dbcc19e0eaaaf4eb31dc5cc1122c89ec4b3eb87`. Preservar todos os checks, assertivas, zoom nativo,900segundos/check,90minutos totais, retenção7dias, triggers, concurrency, permissions e pins. Não trocar por CSS zoom, headless ou skip.

Fontes vigentes: AGENTS.md (Classificação/Git/Validação), docs/governance/CHANGE-PROCESS.md (§§2,5–7), QUALITY-GATES.md (Full), e implementação `tools/notes_launcher_test.py::launch_options`, `tools/hedge_prop_browser_test.py::native_zoom`, `tools/management_visual_quality_test.py::native_cases`; fingerprints pertinentes em runtime-source-fingerprints.json junto ao recibo. Finalidade/consumidores globais lidos em PROJECT-CONTEXT e CONTEXT-MAP. Nenhum parâmetro financeiro ou formato de dados é afetado.

## Evidências e limites

Run41257986724 completou após31min:68PASS,2PRODUCT_FAIL,1NOT_RUN. Hedge e Gerenciamento registram Missing X server or $DISPLAY nos recibos filhos; classificação bruta preservada. Matriz UI: timeout900.009s,309 linhas PASS e uma PRODUCT_FAIL inline-review-input-opening no trecho retido, sem recibo final da matriz. Causa desse foco/timeout permanece aberta; não presumir lentidão como única causa. Base69b6 já registrava os dois primeiros sintomas históricos de Hedge/timeout; nenhuma dispensa de gate decorre disso.

Reprodução local direcionada TZ=UTC:25/25 inline-regressions PASS, fontes estáveis, incluindo review nos3viewports; não reproduz nem corrige Linux. Registros brutos do CI e do foco local em docs/validation/ci-runtime-20261101/. A correção do display reutiliza casos nativos existentes em standard/full; GREEN do mesmo estímulo no runner Linux ainda depende do próximo CI. Não declarar incidente fechado por resultado local ou retry.

Aceite: patch literal e auditoria independente; FULL local do candidate, execução remota com versão registrada, casos nativos realmente executados e resultados brutos preservados. Falhas remanescentes bloqueiam aprovação integral, sem enfraquecer testes. Comando FULL local: python tools/quality_gate.py --tier full. Não há rebuild porque nenhum input do gerador foi alterado.

Rollback: reverter somente este delta e seus registros, preservar fontes/dados e diagnósticos; não há migração reversa ou limpeza. Security review: nenhuma permissão de workflow, segredo, action, dependência ou envio adicional; Xvfb local ao runner e Chromium já instalado. Auditoria independente e execução Linux são provas distintas, registradas externamente.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: a seleção de runtime/display do pipeline consumido por agentes mudou; IMPACT do procedimento agentic-evolution-governance delimita atualização a este CHG, tarefa/estado e memória factual. Autoridade, AGENTS, skills, routing, registries, validadores, índices e normas preservados. Nova revisão material: sim, somente CI. Não há reconciliação global do aviso histórico do preflight nem reindexação.


Validação local final do candidate combinado: FULL116/116PASS eUI413/413PASS, fontes estáveis, concluída31/10/2026às23:26-03:00. Recibos em docs/validation/ci-runtime-20261101/. PrimeiroFULLinterrompido e resultadosCIanteriores preservados separadamente. Próxima ação: branchpush autorizada eCI Linux do mesmoSHA antes de integrar este ajuste àmain; não declarar GREEN remoto ou foco/timeout resolvido sem prova.
