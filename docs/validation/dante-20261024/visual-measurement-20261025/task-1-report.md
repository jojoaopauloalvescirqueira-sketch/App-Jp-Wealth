# Tarefa1 — medição visual agrupada

Veredito local: **PASS focal**, candidate congelado para crítica independente. Não equivale a all413, FULL102, zoom nativo ou aceite humano; coordenador executará essas etapas. Nenhum produto, dado, fórmula, gate, matriz ou ID foi editado por este implementador.

## Alvo e autorização

Raiz: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`. Branch `codex/dante-guia-20261024`, HEAD `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`. Contrato: `docs/work/CHG-JPW-VISUAL-MEASUREMENT-CONTROLS-20261025.md`, aprovação humana `call_2fef00bbd89f4bdf8537108cae962427`, tarefa delimitada no `task-1-brief.md`. O preflight sem `--allow-dirty` bloqueou sobre as alterações conhecidas; coordenador confirmou92 anteriores+CHG e ACTIVE-TASK. Audit/edit com `--allow-dirty` passaram, com aviso material preexistente preservado. Sem Git mutável, sinais, headed, instalações ou publicação.

Responsabilidade: `tools/` mede e julga geometria; a aplicação mantém seus bytes. O objetivo deste delta é obter as mesmas medidas reais em uma leitura após scroll/duploRAF, sem enfraquecer assertivas. Consumidores preservados: chamadas padrão de centered e controles de Planejamento. Contrato de equivalência restrito ao documento principal estável; coordenadas de iframe não foram homologadas.

## Delta autorizado

- `tools/ui_visual_quality_test.py`: patch revisado exato de centered/controls_geometry; SOURCE_FILES adiciona somente o novo helper; ação `counterproof-forecast-inner-text` agrega suas evidências, preservando as contraprovas anteriores.
- `tools/ui_visual_measurement_test.py`:282linhas, fonte completa no pacote; proxies delegam cada chamada ao browser. Referência do caminho anterior, orçamento real, equivalência,14contraprovas e protocolo do snapshot imediato.
- Snapshot não é cache: o chamador mede cada botão após seu próprio scroll/duploRAF. Nenhuma geometria positiva fabricada. Substituições deliberadas utilizam snapshots reais previamente medidos e somente testes negativos.

## RED/GREEN e comandos

Todos os comandos de browser foram encapsulados em `subprocess.run(..., timeout=900)`; arquivos `*-command.json` preservam argv literal, exit e tempo, e `*.log` preservam stdout/stderr. Runtime relativo à raiz: `.superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3`. Browser headless Chrome155.0.8059.86, contextos sintéticos novos com service_workers bloqueados; aplicação servida somente no loopback pelo BrowserFixtureServer existente.

1. **BASELINE_FAIL esperado / RED comportamental**, exit1: `python tools/ui_visual_measurement_test.py --budget-only --out /private/tmp/jpw-visual-measurement-20261025/budget-red-confirmed.json`, antes do patch. Exigência <=4RPC; medidos3botões×8RPC. Raw report classifica `TEST_HARNESS_FAIL` porque é asserção do juiz. Não foi falha de import/coleta/ambiente. `budget-red-command.json` confirma exit real1; primeiro invólucro com cat retornou0 e não foi usado como prova do exit.
2. **PASS / GREEN**, exit0: mesmo orçamento após patch (`budget-green.json`):3botões×4RPC. O helper recebeu depois reforços aditivos; a prova final abaixo mede novamente o mesmo orçamento nos bytes congelados.
3. **PASS / GREEN final**, exit0,4.449s de processo: `python tools/ui_visual_measurement_test.py --out /private/tmp/jpw-visual-measurement-20261025/permanent-app-green.json`.3controles sintéticos e12controles do formulário real: original8RPC/cada versus batched4RPC/cada. Comparação exata de outer,text,textRects,ink,label,svg,textAlign,inset,delta,isClose,cuts; decisões iguais tanto nos válidos quanto nas5violações geométricas. Writer_calls=[] e command_calls=[]. Medido desvio fresco de5CSSpx após mudar DOM.
4. **PASS wiring**, exit0,5.767s de processo: chamada headless direta de `counterproofs(browser,url,report)` com argv completo em `wiring-counterproofs-confirmed-command.json`.4IDs anteriores PASS e evidência `batched_measurement_counterproofs` presente no IDforecast. A primeira execução teve todos4IDsPASS, mas a asserção auxiliar scratch procurava `observed` em vez de `evidence`: **TEST_HARNESS_FAIL**, exit1/KeyError, preservado em `wiring-counterproofs.log/json`; corrigido só o leitor scratch e repetido o mesmo focal. Nenhuma falha foi apagada.
5. **PASS**, exit0,2.282s: `python tools/ui_visual_quality_test.py --case regressions --out /private/tmp/jpw-visual-measurement-20261025/impl-regressions`:3casos PASS. Já estava iniciado quando o coordenador pediu parar ampliações; nenhuma nova repetição foi iniciada.
6. **PASS estático/executável**: `task-1-static-receipt.json` registra AST, parse e `coverage_counterproof()` executado, incluindo negativas de gate/matriz. `git diff --check` exit0. O comando exploratório completo está no histórico de ferramentas; recibo é delimitado aos2arquivos.

Orçamento por botão inclui scroll evaluate, double-RAF page.evaluate, inspection evaluate e exact-count. Exclui setup/contagem do conjunto, reading_keyboard_order, selects e inputs (mesma exclusão no RED/GREEN). Contagem original delegada registrada individualmente, sem usar8 como resultado fabricado. Queda de chamadas não é alegação de ganho temporal de all.

## Contraprovas permanentes

Pelo controls_geometry real: texto+5px, SVG+5px, Fechar20px, corte de ancestral, conteúdo ausente; original e batched recusam pelo mesmo motivo. Também ausência de escopo e de botões. centered recusa zero/múltiplos tanto no caminho padrão quanto recebendo snapshot real. Nova inspeção após deslocar DOM mede+5px e recusa, sem aproveitar o resultado positivo anterior.

**Limite explícito de stale/wrong:** centered não autentica dict arbitrário como API pública. A instrumentação do teste observa a identidade do locator e do objeto retornado pela evaluate real, exige consumo imediato único e captura substituição stale/wrong como falha do protocolo do chamador. Isso testa o wiring privado atual; não promete impedir qualquer futuro consumidor malicioso de injetar dados. O patch aprovado não foi ampliado com contrato de identidade público.

## Preservação e limites

Todas as assertivas Python de centered/controls_geometry são AST-idênticas; CONTENT_GEOMETRY inalterada. Todas as outras funções são AST-idênticas exceto a adição interna a counterproofs. required_ids, validate_coverage, main, matrix, native_zoom, gate_counterproof e seus limites permanecem idênticos.413IDs,2CSSpx,102checks e cap900 preservados; gate tem hash idêntico ao baseline679. SOURCE_FILES160→161, sem remoção. Produto e os92pendentes preexistentes não são revertidos.

Nenhuma edição adicional após os hashes abaixo. Rollback: reverter somente `task-1-baseline-delta.patch`, preservando demais mudanças e histórico; baseline do juiz está em `ui_visual_quality_test.before.py`. Esse plano não autoriza remoção efetiva nem qualquer operação Git.

Autoavaliação SPEC:PASS focal para contrato delimitado;QUALITY:PASS local, sujeito à crítica independente. Mainframe sintético/Planejamento real cobertos; iframes,Safari,screenreader,toque físico,all/FULL/native200 e aceite humano **NOT_RUN por este subagente**. Não há promessa de all caber em900s.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: o juiz consumido pelo gate recebe helper versionado e hash novo; contagem e contrato de snapshot imediato mudam a representação de medição, sem alterar produto. CHG e reconciliação documental/IMPACT são responsabilidade do coordenador; este executor não editou docs do checkout.

## Artefatos congelados

- `tools/ui_visual_quality_test.py` — SHA256 `f5cee3d6442bbb95901afed953ca9ea504c6c30873fd6e0751a274c8b3c5c69c`
- `tools/ui_visual_measurement_test.py` — SHA256 `41f9d9be12248e7741cff20b8edc4d6beb8b0cd8674bc39fc175f43630d1b64e`
- `/private/tmp/jpw-visual-measurement-20261025/task-1-baseline-delta.patch` — SHA256 `6d6f92344c96c0b6c6e88fab1197cc8b217dac5683ddc57b272b4cd89d562767`

Pacote completo: `/private/tmp/jpw-visual-measurement-20261025/task-1-review-package/`. Patch revisável contra baseline da tarefa (inclui fonte nova integral): `task-1-baseline-delta.patch`; o git diff bruto contém alterações anteriores, por isso não substitui esse delta. Nenhum hash de relatório é apresentado como prova de produto ou de all.
