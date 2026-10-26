# CHG-STOIKUS-NATIVE-CYCLE-20261026 — ciclo nativo MT5 do Stoikus

Status: **ACCEPTED_BY_OWNER** (26/10/2026; antes: A4_APPROVED_FOR_IMPLEMENTATION). Risco N3 de control plane (ferramenta que decide PASS/FAIL do Stoikus). Aprovação do proprietário em 26/10/2026, na conversa: "Aprovo em A4 o CHG-STOIKUS-NATIVE-CYCLE-20261026 como está. Pode implementar a parte do Mac enquanto eu preparo o laboratório." A aprovação cobre a implementação deste contrato; auditoria independente, comparação antes/depois e aceite humano continuam pendentes. Commit, push, PR e merge são autorizações separadas.

## Autoridade e escopo

- Pedido humano de 26/10/2026: "Quero que seja desenvolvido a arquitetura desse funcionamento e a implementação", seguido da aprovação do plano `quero-que-seja-desenvolvido-floofy-conway.md`. A aprovação autorizou: branch `claude/stoikus-ciclo-nativo-20261026` e worktree `/private/tmp/jpw-stoikus-ciclo-nativo-20261026` a partir do main `a4bf278`; geração do par de chaves `~/.ssh/jpw_mt5_lab` e da entrada `jpw-mt5-lab` no `~/.ssh/config`; execução no laboratório (só `C:\MT5Lab`, conta demo, sem ordens).
- Fontes conferidas: Master Specification do Harness SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95` (§§12–14, 19, 28–30, 36–48); harness interno `mt5/jpw-alavancagem-atual/harness/JPW_GENETRIX_MT5_ENGINEERING_HARNESS_v1.0.md` SHA-256 `a0e6b6776c237899c048cd460ccb44ac3e916a0a6cd9958577884c42b03f70c9` (§§7–9, ENG-AC12); `NativeKit.Core.ps1` do kit C5-D1 SHA-256 `2dba568c184e31f1e28814c706d3e6a9459fe4e45524e33b52db14c0776ed542`, igual ao `$PinnedCoreSha256` do kit.
- Arquivos permitidos: `tools/stoikus_native_runner.py`, `tools/stoikus_native_parsers.py`, `tools/stoikus_native_runner_test.py`, `tools/stoikus_native_parsers_test.py` (acrescentado na implementação: os testes dos parsers ficaram em arquivo próprio), `tools/stoikus_native/windows/*.ps1`, `docs/architecture/STOIKUS-NATIVE-CYCLE.md`, este CHG, `docs/validation/stoikus-native-*/`, e os acréscimos mínimos em `tools/leverage_suite.py` (registro append-only do teste host) e `tools/regression-memory.json` (bloco `protection.mt5_native`).
- Proibido: MQL5 (inclusive `#property script_show_inputs`), fórmulas, pacotes e pins selados em `downloads/`, `quality-gate.yml`, `mt5-host.yml`, Quality Gate, renomeação da pasta, MT5 de uso diário do proprietário, contas reais, envio de ordens, armamento do Supervisor.

## Compreensão (TASK-BRIEF)

1. **Finalidade:** o JP Wealth trata capital com rastreabilidade; o Stoikus é o projeto MT5 independente que o complementa (decisão de 22/10). Esta tarefa fecha a lacuna de prova nativa: hoje só existe prova host.
2. **Responsabilidade da área:** `tools/` guarda as ferramentas de teste; a suíte host `tools/leverage_suite.py` prova a lógica com API simulada. O novo executor prova compilação e execução no MT5 real, sem substituir a suíte host.
3. **Hoje e depois:** hoje, compilação MetaEditor e os 24 `*_Tests.mq5` estão NOT_RUN; o kit Windows é interativo e compila só 4 programas. Depois: um comando no Mac compila os 34 programas e roda os 24 scripts num MT5 portable isolado, e devolve recibo com hashes.
4. **Afetados:** recibos e `regression-memory` (novo bloco); fingerprint da suíte host (novos arquivos `tools/stoikus_*`); nenhum consumidor do app ou do produto MT5.
5. **Invariantes:** bytes do MQL5, dos pacotes selados e do `NativeKit.Core.ps1` reutilizado; expectativas dos testes existentes; golden do laboratório nunca escrito; nenhuma credencial no repositório.
6. **Prova sem regressão:** testes host do executor; suíte host completa com o novo check; contraprovas; primeira execução real sobre os fontes do C5 `79160d9`; auditoria independente.

## Problema e comparação antes/depois

| Item | Antes | Depois |
|---|---|---|
| Compilação nativa | NOT_RUN; kit interativo, 4 programas | 34 programas por comando, log estrito (0 erro, 0 aviso), cadeia fonte → log → EX5 com hashes |
| Execução dos 24 testes MQL5 | NOT_RUN | Cada script rodado no terminal portable via `[StartUp]`, resultado lido do log por parser próprio |
| Evidência | Prosa "NOT_RUN" | Recibo `MT5_NATIVE` com `native_gates` separados |
| Suíte host | 62 checks | 64 checks (+ testes host dos parsers e do executor) |

## Critérios congelados

- Payload determinístico; identity no schema `JPW_STOIKUS_UI_NATIVE_COMPILE_IDENTITY`; o agente recusa qualquer divergência de hash antes de compilar.
- `NativeKit.Core.ps1` reutilizado byte a byte (SHA-256 acima), conferido pelo runner antes do envio.
- Compilação aceita só pelo `Test-CompileLog` do Core; código de retorno do MetaEditor não prova sucesso.
- Resultado de cada script: resumo com falhas > 0 → PRODUCT_FAIL; linha NOT_RUN do próprio script → NOT_RUN; resumo ausente ou ilegível → ENVIRONMENT_ERROR; nunca PASS sem resumo reconhecido com 0 falhas.
- `native_gates`: `compilation`, `test_scripts` medidos; `tester`, `terminal_interaction`, `alerts_sound`, `installation` permanecem NOT_RUN.
- Entradas inalteradas durante a execução; inventário do golden igual antes e depois.
- Expectativas existentes não são enfraquecidas; o registro na suíte host é só acréscimo.

## Portão de viabilidade (spike)

Antes do agente PowerShell definitivo: confirmar no laboratório (a) SSH com chave; (b) `metaeditor64 /compile` numa sessão SSH; (c) `terminal64 /portable /config` via tarefa agendada interativa rodando um teste e fechando sozinho; (d) efeito do `script_show_inputs`; (e) gráfico disponível sem login. Falha em (c), (d) ou (e) para o trabalho dependente e volta ao proprietário com alternativas.

Achados (26/10/2026, VM `JOOPAULOCIR1828`, 10.211.55.3):

- (a) **PASS.** `ssh jpw-mt5-lab` entra como `joopaulocir1828\mt5lab` só com a chave `jpw_mt5_lab` (BatchMode). Preparação feita pelo proprietário: OpenSSH Server instalado; regra `OpenSSH-Server-In-TCP` estendida a Private e Public, restrita a `10.211.55.0/24` (a rede do Parallels é classificada Public); usuário comum `mt5lab`; `C:\MT5Lab` com controle total do `mt5lab`.
- **Achado de arquitetura:** numa sessão SSH (logon de rede), o WMI recusa o `mt5lab` (`Get-CimInstance: Access denied`). O `Assert-LocalWindowsPath` do Core usa WMI, então o agente não pode validar caminhos dentro da sessão SSH. Na sessão interativa o WMI responde. Sonda por tarefa agendada (`schtasks /create /it`, criada pelo próprio `mt5lab`, sem administrador): usuário `mt5lab`, sessão 2, interativa, `Win32_LogicalDisk` C: = 1, resultado da tarefa 0. A tarefa de sonda foi removida.
- **Decisão decorrente (dentro do contrato):** o agente inteiro, compilação e terminal, roda na sessão interativa do `mt5lab` por tarefa agendada; o SSH só transporta arquivos, dispara a tarefa e espera o marcador de conclusão. O Core continua byte a byte. Isso também elimina a dúvida (b), porque a compilação deixa de rodar na sessão SSH.
- Golden: o instalador gravou o MT5 em `C:\Users\mt5lab\AppData\Roaming\MetaTrader 5`, ignorando a pasta escolhida. Com o MT5 fechado pelo proprietário, a instalação foi copiada (robocopy, 583 arquivos, 0 falhas) para `C:\MT5Lab\golden` e aberta com `/portable` pela tarefa interativa: MT5 x64 build 6286, sem login, `MQL5\Include\Object.mqh` criado, recompilação inicial concluída (`full recompilation has been finished: 34 file(s) compiled`).
- (b) **PASS na sessão interativa** (spike 2, payload SHA-256 `8331217e921e1e836c890247a2755a3abff6bc1894270dcfff03d7f371da17e6`): `JPW_Alavancagem_Panel_Tests` e `JPW_Alavancagem_Tests` com `Result: 0 errors, 0 warnings`, cpu `X64 Regular`, EX5 gerado. O MetaEditor saiu com código 1 nos dois casos de sucesso: confirma que o código de retorno não prova nada.
- (c) **PASS:** o terminal da cópia abriu com `/portable /config`, rodou o script, fechou sozinho (`closes terminal with code 0`, `shutdown with 0`).
- (d) **PASS:** o `script_show_inputs` do `JPW_Alavancagem_Tests` não bloqueou o `[StartUp]`.
- (e) **PASS:** sem login, o gráfico EURUSD H1 existiu e os scripts rodaram.
- Primeiros resultados nativos de runtime: `JPW_Alavancagem_Panel_Tests PASS: 673 asserts; 0 failures`; `JPW_Alavancagem_Tests PASS: 235 asserts` (cenários r1 117 PASS / 0 FAIL). Os parsers classificaram as linhas reais como PASS (673/0 e 235/0). Spike, não recibo final.
- Limitações observadas e decisões do agente: pela sessão SSH, `tasklist`, `taskkill`, `Get-ScheduledTask` e WMI dão Access denied; `schtasks /change` pede a senha do `mt5lab` (nunca usado; a tarefa é recriada com `/create /f`, que não pede). O MetaEditor grava em `logs` e configurações da pasta de onde roda; por isso cada execução copia o golden e usa o MetaEditor e o terminal da cópia, mantendo o golden sem escrita. Os resultados sempre são gravados num bloco `finally`, porque um script de espera do spike morreu sem deixar resultado.

## Preservação e rollback

- Antes do commit: descartar a branch e o worktree. Depois: reverter o commit; nenhum dado de produto ou de usuário é afetado.
- Laboratório: apagar `C:\MT5Lab\runs\*` e `C:\MT5Lab\bin`; o golden e o MT5 de uso nunca são tocados. Chave: remover `~/.ssh/jpw_mt5_lab*`, a entrada `jpw-mt5-lab` e a linha no `authorized_keys` do mt5lab.

## Evidências

Parte do Mac (26/10/2026, worktree sem commit, Python 3.9.6 do sistema e venv com `requirements-dev.txt`):

| Verificação | Resultado |
|---|---|
| `tools/stoikus_native_parsers_test.py` (14 testes; vermelho antes, verde depois) | PASS |
| Contraprova: âncora inexistente no `.mq5` faz o teste de âncoras falhar | PASS |
| `tools/stoikus_native_runner_test.py` (15 testes com transporte simulado na primeira versão; vermelho antes, verde depois) | PASS |
| `tools/leverage_suite.py --scope all`: 64 checks (62 anteriores + 2 novos), entradas inalteradas | PASS |
| `tools/jp_engineering_integration_test.py` | PASS |
| `NativeKit.Core.ps1` copiado byte a byte do kit C5-D1 (SHA-256 `2dba568c…`) | PASS |

Laboratório e agente (26/10/2026):

| Verificação | Resultado |
|---|---|
| Spike (a)–(e), detalhado no portão de viabilidade | PASS |
| Testes host após a mudança para tarefa agendada e `done.json` (17 do runner, 14 dos parsers) | PASS |
| `--install-agent`: 3 arquivos em `C:\MT5Lab\bin` conferidos por SHA-256 no Windows (agente `ef963087…`, autoteste `d9a459d9…`, Core `2dba568c…`) | PASS |
| `--self-test` na sessão interativa: 8/8 (pin do Core, WMI, golden, parser de log aceita limpo e recusa aviso/erro/truncado, payload adulterado recusado) | PASS |
| Primeira execução nativa `--scope all` (run `20261026T172957Z`, fontes = C5 `79160d9`, MetaEditor/terminal 5.0.0.6286, 15 min) | PRODUCT_FAIL bruto: 56 PASS, 3 PRODUCT_FAIL, 1 ENVIRONMENT_ERROR |

Detalhe da primeira execução nativa (recibo em `docs/validation/stoikus-native-20261026/mt5-native.json`; logs copiados; `SHA256SUMS-original.txt` cobre os 118 arquivos originais, inclusive os 34 EX5, que não foram versionados):

- Golden intacto (fingerprint igual antes e depois); entradas inalteradas; integridade dos resultados PASS.
- Compilação: 33 de 34 aceitos. `JPW_Stoikus_Abrir_Paineis`: `Result: 0 errors, 0 warnings`, mas `Test-CompileLog` do Core recusa (`UNRECOGNIZED_OR_FOREIGN_BODY_LINE`) duas linhas informativas `info property tester_indicator ... implicitly added ... iCustom`. Classificado ENVIRONMENT_ERROR, não PASS; o kit selado reprovaria o mesmo programa. Ampliar a gramática é decisão do proprietário, fora deste CHG.
- Scripts de teste: 21 de 24 PASS. PRODUCT_FAIL nativos, todos em persistência e todos PASS na suíte host: `JPW_Alavancagem_Diagnostics_Tests` (5 passed; 13 failed), `JPW_Alavancagem_RaizN_Config_Tests` (4 of 72), `JPW_Alavancagem_RaizN_Store_Tests` (40 of 82 asserts). Os stores declaram não usar `FILE_COMMON`. Causa não diagnosticada; correção é mudança de produto com CHG próprio.
- Memória de regressões: 4 entradas novas (3 `open_incident`, 1 `baseline_limitation`). Desvio do plano: em vez de um bloco `mt5_native` nas entradas do painel C5, os achados nativos receberam entradas próprias, por serem incidentes distintos.

### Auditoria independente e correções

Auditor separado, somente leitura, sem autoria do código: veredito **CHANGES_REQUIRED** por um item MAJOR, mais notas MINOR. Escopo confirmado: `NativeKit.Core.ps1` idêntico ao do kit, nenhuma mudança em `mt5/`, `downloads/` ou `.github/`, registro na suíte host só acrescentado, contagens do recibo conferidas, sem falso PASS e sem senha no fluxo.

| Achado | Ação |
|---|---|
| MAJOR: a tarefa `/sc once /st 23:59` nunca era apagada; um disparo às 23:59 reexecutaria o último RunId e sobrescreveria a evidência no laboratório | As tarefas existentes foram apagadas no laboratório na hora. O Mac apaga a tarefa assim que o `done.json` aparece ou a espera termina (`lab_task_cleanup` no recibo); o agente e o autoteste saem sem escrever nada numa execução já usada. Testes host novos cobrem a remoção, inclusive no timeout |
| MINOR: compilação 0/0 recusada pela gramática classificada ENVIRONMENT_ERROR | Passa a TEST_HARNESS_FAIL, com teste |
| MINOR: o Mac não conferia o hash do fonte compilado | Confere contra o identity; divergência dá TEST_HARNESS_FAIL, com teste |
| MINOR: o autoteste do payload adulterado aceitava qualquer exceção | Controle positivo com o hash certo e exigência da mensagem `Frozen entry SHA-256 mismatch` |
| MINOR: faltavam testes para erro do agente, Core divergente e linha ausente | Acrescentados (22 testes no executor) |
| MINOR: PersonalHistory e Ledger sem total de asserções | Limite documentado na arquitetura; os testes MQL5 não foram alterados |
| MINOR: "maioria das asserções" e contagens contraditórias | Corrigido para 40 of 82, 64 checks e as versões dos testes |
| MINOR: desvio da memória de regressões após o A4 | Registrado acima; precisa do reconhecimento do proprietário |

### Execução final (agente corrigido)

`--install-agent` (agente `6ac065cc…`, autoteste `3d62afb2…`, Core `2dba568c…`, conferidos no Windows) e `--self-test` 8/8 PASS. Segunda execução completa `20261026T175454Z`, recibo `docs/validation/stoikus-native-20261026/run2-20261026T175454Z/mt5-native.json` (SHA-256 `c5b11d324abe8a349f3cc3028116d52bd94cecb5235be873fa1a0faefb7226de`): 56 PASS, 3 PRODUCT_FAIL, 1 TEST_HARNESS_FAIL. Resultado idêntico ao da primeira execução, com a nova classificação do `Abrir_Paineis`: as três falhas de persistência são determinísticas (13/18, 4/72, 40/82). Golden intacto, entradas inalteradas, `lab_task_cleanup: DELETED`, nenhuma tarefa Stoikus restante no laboratório. A primeira execução fica preservada como tentativa histórica.

### Gates sobre o candidato final

| Verificação | Resultado |
|---|---|
| `tools/leverage_suite.py --scope all` (venv com `requirements-dev.txt`): 64 checks, entradas inalteradas | PASS 64/64 |
| `tools/stoikus_native_runner_test.py` (22) e `tools/stoikus_native_parsers_test.py` (14) | PASS |
| `tools/jp_engineering_integration_test.py` (95 entradas) e `git diff --check` | PASS |
| `tools/quality_gate.py --tier full` (bruto: 86 PASS, 4 PRODUCT_FAIL, 12 ENVIRONMENT_ERROR) | Não verde; nenhuma falha atribuível a esta mudança |

Classificação das falhas do full, sem alterar o resultado bruto:

- 12 ENVIRONMENT_ERROR: 11 por ausência do Node.js neste Mac (`No such file or directory: 'node'`); `ui-visual-quality` pelo timeout de 900 s já diagnosticado no `main`.
- `notification-efficiency` e `consolidated-efficiency`: o gate rotula PRODUCT_FAIL, mas a causa é a variável `JP_WEALTH_CHROMIUM` ausente (`KeyError`); ambiental.
- `calendar-agenda`: falha também no `main` (worktree `jpw-stoikus-mt5-all-registro-20261024`, código do app idêntico), no caso `calendar-edges-320-light`. BASELINE_FAIL.
- `navigation-ia` (`focusInside: False` a 390 px após abrir o Alladin): no `main`, 1 PASS e 2 FAIL em três execuções; no candidato, 3 FAIL. Intermitente e preexistente. BASELINE_FAIL.
- `git diff main --name-only` no candidato: só `tools/leverage_suite.py` e `tools/regression-memory.json` entre os rastreados; nenhum arquivo do app web mudou.

Pela política do projeto, um commit com gate aplicável falhando exige pedido explícito do proprietário para preservar o vermelho preexistente, identificado como tal. Os logs em `docs/validation/stoikus-native-20261026/` são ignorados por `*.log` no `.gitignore` e precisam de `git add -f`.

### Aceite

Proprietário, 26/10/2026, na conversa: "Aceito o ciclo nativo como está, reconheço o desvio da memória de regressões e autorizo o commit na branch claude/stoikus-ciclo-nativo-20261026, preservando o vermelho preexistente identificado no gate full." O aceite cobre o ciclo e o commit nesta branch; push, PR, merge e publicação continuam como autorizações separadas. Fora deste CHG ficam o diagnóstico das três falhas nativas de persistência (sessão própria, só diagnóstico) e a decisão sobre a gramática de log do Core para as linhas `tester_indicator`.
