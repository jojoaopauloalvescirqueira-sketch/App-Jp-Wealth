# Revisão noturna — conclusão da validação

## CONFIRMADO

Os sete checks anteriormente interrompidos concluíram seus cenários. O **FULL local final passou: 55 checks PASS, zero nas demais classes, retorno 0**, em 10/09/2026, 10:25:57–10:35:22 −03:00. Esta é uma execução nova do gate existente; não é CI remoto, contagem de asserções ou aceite humano. [Resultado por check e saídas capturadas](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/full-final/quality.json); [comando, PID e retorno](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/full-final/receipt.json).

Candidate **V3**, fingerprint SHA-256 — **não commit Git**:
`66fa5d9cd6f7ffd66c216e5bcdebfd0be6d83342f23da2785478039cf8c89fa4`.

- Raiz: `/Users/joaopauloalves/.codex/night-reviews/20260910/product`.
- Branch: `codex/night-review-20260910`.
- HEAD/base preservado: `4cb2e2a24c58a714b9909df6dd6f0415097480e2`.
- Build preservado: `60463a994a0068f8`.
- V2 anterior: `b2f11151e5838eb60a33a1409295af10d2b6b9d88eec78b1ce51e52738781f8e`.

V3 contém o delta de validação; **não é byte-idêntica à V2**. As quatro correções noturnas, runtime, manifest e artefatos são idênticos aos da V2. O freeze inclui 23 caminhos alterados e 270 arquivos/links inventariados. Este relatório é somente resultado posterior ao freeze, previsto no manifesto, com identidade de entrega separada. [Manifesto V3](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/candidate-v3.json); [diff completo](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/candidate-v3.diff); [diff exclusivo da validação](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/validation-only.diff).

### Check → observação → ajuste → resultado → lacuna

Todos os caminhos de testes abaixo estão em `tools/`. Antes e depois, cada par usou os mesmos testes nas duas versões de produto: baseline build `88c0cb1ce5520311` e candidate build `60463a994a0068f8`. A baseline foi copiada de 4cb2, com testes V2 sobrepostos; não foi apresentada como execução dos testes nativos antigos.

| Check / arquivo | Impedimento identificado na reprodução | Ajuste de avaliação | Resultado final / limite |
|---|---|---|---|
| smoke / `smoke_test.py` | Oito cotações FX e feed FF sem fixture; falhas DNS | Fixture específica, espera do bootstrap, SW bloqueado onde dispensável | PASS pareado e FULL; sem API ao vivo |
| settings / `settings_modal_test.py` | Feed FF não atendido; FX já simulado | Completar bootstrap antes dos snapshots | PASS pareado e FULL; estado/foco mantidos |
| statute-documentary / `statute_documentary_test.py` | Fetch econômico do SW não atendido pelas rotas de página | Rotas no contexto, SW real, estabilização e guarda final | PASS pareado e FULL; recursos auxiliares abaixo continuam registrados |
| galton-board / `galton_board_test.py` | Feed global falhava antes dos cenários posteriores | Fixture e bootstrap; nenhuma mudança matemática/física | PASS pareado e FULL; não elimina intermitência histórica |
| session-finalization / `finalize_session_test.py` | Feed FF interrompia a guarda de console | Completar fixture, conservar taxas TEST_FX_RATES; SW real em run_cache | PASS pareado e FULL; finalização, recarga e caches exercitados |
| storage-governance / `storage_governance_test.py` | Oito FX e feed sem fixture | Estabilizar antes dos checkpoints; preservar conflitos entre abas | PASS pareado e FULL; não altera persistência |
| mvp-notes / `mvp_notes_test.py` | Feed e fetch econômico via SW; 37 eventos para nove URLs | Fixture, bootstrap e guardas nas fronteiras de fechamento | PASS pareado e FULL; recusa de gravação OPEN-04 continua fora desta suíte |

Novo helper: `tools/browser_bootstrap_fixture.py`. `tools/dashboard_macro_test.py` recebeu callback opcional de preparação do contexto para o consumidor documental; os quatro oráculos de atalhos anteriores foram mantidos. Feed sintético segue version1/events; FX segue URL/par e taxa válida. Recursos externos desconhecidos são recusados, sem resposta JSON genérica. O [CHG específico](/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/CHG-NIGHT-VALIDATION-20260910.md) delimita N3/A4, arquivos, efeitos e rollback somente deste delta.

### Evidências e auditoria

- Antes: **14 execuções com retorno 1**, sete por produto, com captura desde o início. Depois V3a: **14 com retorno 0**.
- A auditoria inicial apontou uma guarda incompleta para requisições desconhecidas tardias. V3b ligou a guarda aos encerramentos; os **14 focais foram executados novamente e passaram**. V3 final conserva esses mesmos bytes.
- Quatro controles negativos V3a são reaproveitados para a fixture inalterada: recurso desconhecido, erro de console, PDF corrompido somente na resposta e feed inválido foram rejeitados. Um negativo novo V3b comprovou a rejeição no `finally` real do teste documental, isolando o erro de console somente nesse controle externo.
- Os 1.010 nós Python Assert originais permanecem; isso é verificação estrutural, não 1.010 testes aprovados. Houve também prova dinâmica de interceptação de nove respostas no SW real instalado.
- O FULL V3 inclui as regressões das quatro correções: PF, foco Alladin, atalhos Dashboard e orientação do Calendário. A reprodutibilidade reconstruiu exclusivamente cópias temporárias pelo processo existente.

[Índice dos recibos](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/results-index.json); [auditoria focal V3b aprovada](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/audit-fixtures-v3b.md); [auditoria da comparação causal](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/audit-comparison.md).

Parecer independente final: **EVALUATION_DELTA_APPROVED — FULL_LOCAL_PASS**, limitado aos ajustes de avaliação e à ligação candidate → execução. O auditor conferiu fontes, hashes e registros; não declarou ter executado os testes. [Auditoria final](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/audit-final.md). A [identidade da entrega](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/delivery-final.json) inclui este relatório sem confundi-lo com os inputs testados.

Os FULL anteriores permanecem reprovados em seus registros originais, inclusive **48 PASS / 7 PRODUCT_FAIL brutos da V2**. A classificação causal adicional não reescreve esses resultados nem atribui URLs novas a logs antigos incompletos. O P2 da fixture desta rodada é distinto de AUD-05/P2 da reconciliação de instruções.

### Preservação e efeitos

Após o FULL: **270/270 inputs congelados iguais**, original **266/266**, tarefa PF anterior **6/6** e V2 protegida **259/259**, excluindo precisamente oito testes com backups conferidos. HEAD, branch, stash e relatórios anteriores preservados; nenhum staged ou conflito. Perfil de rede loopback e Harness mestre mantêm seus hashes. Não houve alteração de permissões globais. [Conferência final](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/preservation-final.json).

O FULL utilizou sete repositórios sintéticos próprios: 11 commits locais e operações auxiliares; os 11 processos automáticos de manutenção Git também ficaram nessas fixtures, conforme SID/def_repo. Sem commit do produto, push, PR, merge ou deploy nesta tarefa. Não se afirma consulta remota nova. [Trace verificado](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/full-final/git-synthetic-verification.json); [manutenção automática das fixtures](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/validation-complement-20260910/full-final/git-auto-maintenance.json).

## INFERÊNCIA

A reprodução pareada, os recursos identificados e a conclusão dos cenários sem mudança de runtime sustentam deficiência das fixtures/inicialização como causa dos sete bloqueios reproduzidos. O pacote não isola o efeito individual de cada linha nem prova inexistência de defeitos financeiros.

## NÃO VERIFICADO

PASS documental não significa zero falha de recurso: por execução posterior há dois cancelamentos do viewer PDF, um favicon durante offline e três assets locais ausentes no portátil standalone. A causa interna dos cancelamentos não foi provada; os assets ausentes são falhas reais fora do oráculo documental preservado. Não foram corrigidos.

Continuam os seis achados OPEN-01…06 do relatório noturno: persistência Forex, NoCoda, Pivots e Notas, divergência de Reservas e datas Alladin. Também permanecem as limitações históricas de Galton, Atlas/Claude/AUD-05/P2, contexto desatualizado, APIs ao vivo e cobertura fora dos cenários existentes. Não se declara auditoria integral de segurança, filesystem ou software sem defeitos.

## RECOMENDAÇÃO

Submeter V3 e suas evidências à revisão humana. Este complemento resolve a validação delimitada, sem conceder aceite ou autorizar integração. Tratar os achados de produto em escopos próprios. Recomenda-se atualização posterior das fontes canônicas de contexto; nenhuma foi aplicada nesta rodada.
