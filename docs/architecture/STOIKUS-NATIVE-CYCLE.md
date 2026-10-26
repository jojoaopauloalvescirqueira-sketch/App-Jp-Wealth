# Stoikus — ciclo nativo MT5

Camada nativa do harness do Stoikus. A suíte host (`tools/leverage_suite.py`) prova a lógica com a API do MT5 simulada; este ciclo prova compilação e execução no MT5 real. Uma não substitui a outra, e nenhuma substitui o ensaio visual e o aceite humano. Contrato e autorização: [CHG-STOIKUS-NATIVE-CYCLE-20261026](../work/CHG-STOIKUS-NATIVE-CYCLE-20261026.md).

## Como funciona

```
Mac (repositório)                            Windows (VM Parallels, usuário comum mt5lab)
tools/stoikus_native_runner.py               C:\MT5Lab\
  1 congela os fontes (hashes, identity)       bin\     agente PowerShell, versão pinada
  2 monta payload.zip + identity.json          golden\  MT5 portable de referência, nunca escrito
  3 ssh: mkdir runs\<run_id>\inbox             runs\<run_id>\
    scp: payload.zip + identity.json             inbox\     o que o Mac enviou
  4 ssh: schtasks /create /it /f + /run  ──►     tarefa na sessão interativa do mt5lab:
                                                   valida o payload (NativeKit.Core)
                                                   terminal\ = cópia do golden só desta execução
                                                   compila os 34 com o MetaEditor da cópia
                                                   roda cada *_Tests.mq5 (terminal64 /portable /config)
                                                   results.zip, depois done.json (por último)
  5 ssh: type done.json até existir  ◄──
    scp: results.zip
  6 confere hashes, classifica, grava o recibo
```

- **Transporte:** OpenSSH com chave dedicada (`~/.ssh/jpw_mt5_lab`), usuário Windows sem administrador, rede interna do Parallels. Nenhuma senha passa pelo fluxo; todo comando SSH roda com a entrada fechada, para um pedido de senha falhar na hora em vez de travar.
- **Onde o agente roda:** na sessão interativa do `mt5lab`, por tarefa agendada (`schtasks /create /it /f` e `/run`). A sessão SSH é um logon de rede: nela o WMI (usado pelo Core para validar caminhos locais), a lista de processos de outras sessões e o desktop são negados. `schtasks /change` pede a senha do usuário e nunca é usado. A VM precisa manter a sessão do `mt5lab` aberta.
- **Isolamento:** cada execução tem pasta própria e cópia própria do terminal; o MetaEditor e o terminal usados são os da cópia, porque o MetaEditor grava logs e configurações na pasta de onde roda. O golden e o MT5 de uso diário nunca são escritos: o recibo compara o fingerprint de conteúdo do golden antes e depois.
- **Compilação:** reaproveita `NativeKit.Core.ps1` do kit C5-D1 byte a byte. Um programa só compila com sucesso se o log tiver exatamente um resultado com 0 erro e 0 aviso, aceito pela gramática estrita do Core, e o EX5 for novo; o código de retorno do MetaEditor não conta (ele sai com 1 mesmo nos sucessos).
- **Execução dos testes:** `[StartUp] Symbol=EURUSD Period=H1 Script=JPWealth\<script>` e `ShutdownTerminal=1`, sem login. O agente guarda as linhas novas do log de experts (`MQL5\Logs`) e do diário (`logs`) de cada script.
- **Protocolo de término:** o agente grava sempre, num bloco `finally`, o `agent-receipt.json`, o `results.zip` (entradas com `/`) e por último o `done.json` com o SHA-256 do ZIP. O Mac confere esse hash, recusa entradas perigosas e confere que o agente validou o mesmo payload enviado.

Comandos (no Mac, na raiz do repositório):

```bash
python3 tools/stoikus_native_runner.py --install-agent
```
```bash
python3 tools/stoikus_native_runner.py --self-test
```
```bash
python3 tools/stoikus_native_runner.py --scope all
```
- **Classificação dos testes:** cada script tem um parser do seu resumo (`tools/stoikus_native_parsers.py`). Falhas > 0 → PRODUCT_FAIL; o próprio script declarar NOT_RUN → NOT_RUN; resumo ausente ou ilegível → ENVIRONMENT_ERROR. Nunca PASS sem resumo reconhecido com 0 falhas.

## Recibo

Suíte `MT5_NATIVE`, com: candidato (commit, fingerprint, hashes dos fontes, entradas inalteradas), ambiente (Windows, MetaEditor e terminal com versão e SHA-256), `compile[]` (fonte, log, EX5, erros, avisos), `tests[]` (script, resultado, linha de resumo, hash do trecho do log), inventário do golden antes/depois e:

| Gate nativo | Medido por este ciclo |
|---|---|
| `compilation` | Sim |
| `test_scripts` | Sim |
| `tester`, `terminal_interaction`, `alerts_sound`, `installation` | Não: permanecem NOT_RUN |

## Laboratório: preparação única

Feita pelo proprietário, uma vez, no Windows do Parallels. Nenhum passo usa conta real.

1. **Servidor OpenSSH** (PowerShell como administrador):
   ```powershell
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
   Start-Service sshd
   Set-Service -Name sshd -StartupType Automatic
   Set-NetFirewallRule -Name OpenSSH-Server-In-TCP -RemoteAddress 10.211.55.0/24
   ```
   A última linha limita o acesso à rede interna do Parallels. Confira a faixa com `ipconfig` (adaptador do Parallels).
2. **Usuário comum `mt5lab` e a pasta do laboratório** (mesma janela de administrador; a senha é digitada por você e não é registrada em lugar nenhum):
   ```powershell
   $senha = Read-Host -AsSecureString 'Senha do mt5lab'
   New-LocalUser -Name mt5lab -Password $senha -FullName 'MT5 Lab'
   Add-LocalGroupMember -SID S-1-5-32-545 -Member mt5lab
   New-Item -ItemType Directory C:\MT5Lab
   icacls C:\MT5Lab /grant 'mt5lab:(OI)(CI)F'
   ```
3. **Entrar uma vez como `mt5lab`** e deixar essa sessão aberta (troca rápida de usuário). O terminal dos testes roda nela.
4. **MT5 golden:** instale o MetaTrader 5 como `mt5lab`, sem login (o spike mostrou que não é necessário). O instalador pode ignorar a pasta escolhida e gravar em `C:\Users\mt5lab\AppData\Roaming\MetaTrader 5`; nesse caso, com o MT5 e o MetaEditor fechados, o agente copia essa instalação para `C:\MT5Lab\golden` e a abre uma vez com `/portable`, até a recompilação inicial terminar (`full recompilation has been finished`).
5. **Chave do Mac:** na sessão do `mt5lab`, em PowerShell comum, cole a linha pública que o Claude fornecer:
   ```powershell
   New-Item -ItemType Directory -Force "$env:USERPROFILE\.ssh"
   Add-Content "$env:USERPROFILE\.ssh\authorized_keys" '<chave pública jpw_mt5_lab>'
   ```
6. **IP da VM:** informe o IPv4 do adaptador do Parallels (`ipconfig`), para a entrada `jpw-mt5-lab` no `~/.ssh/config` do Mac.

Desfazer: remover `C:\MT5Lab`, o usuário `mt5lab` e, se quiser, o recurso OpenSSH Server; no Mac, `~/.ssh/jpw_mt5_lab*` e a entrada `jpw-mt5-lab`.

## Primeira execução (26/10/2026)

Fontes idênticos ao C5 (`79160d9`), MT5 e MetaEditor 5.0.0.6286, 15 minutos: 56 PASS, 3 PRODUCT_FAIL, 1 ENVIRONMENT_ERROR. Compilação: 33 de 34 aceitos; o `JPW_Stoikus_Abrir_Paineis` compilou com 0 erros e 0 avisos, mas a gramática do Core recusa duas linhas informativas `tester_indicator` do build 6286. Testes: 21 de 24 PASS; `JPW_Alavancagem_Diagnostics_Tests`, `JPW_Alavancagem_RaizN_Config_Tests` e `JPW_Alavancagem_RaizN_Store_Tests` falham no MT5 nativo (persistência) e passam na suíte host. Golden intacto, entradas inalteradas. A segunda execução (`run2-20261026T175454Z`), com o agente corrigido após a auditoria independente, reproduziu exatamente as mesmas falhas e classificou o `Abrir_Paineis` como TEST_HARNESS_FAIL. Evidência: [`docs/validation/stoikus-native-20261026/`](../validation/stoikus-native-20261026/); achados em `tools/regression-memory.json`.

## Limites

- O ciclo não instala nada no MT5 de uso, não envia ordens e não arma o Supervisor.
- A tarefa agendada é criada com `/sc once /st 23:59` (exigência do `schtasks`) e o Mac a apaga assim que o `done.json` aparece, ou quando a espera termina sem ele (`lab_task_cleanup` no recibo). Se algum disparo indevido ocorrer, o agente e o autoteste saem sem escrever nada numa execução já usada.
- Isolamento por execução, não por script: os 24 scripts de uma execução compartilham a mesma cópia do terminal e a mesma `MQL5\Files`.
- `JPW_PersonalHistory_Tests` e `JPW_Stoikus_Ledger_Tests` só imprimem a contagem de falhas, sem o total de asserções; para eles, a proteção contra "0 asserções" não se aplica.
- Uma compilação com 0 erros e 0 avisos que a gramática congelada do Core recusa é classificada TEST_HARNESS_FAIL (a primeira execução, anterior a essa regra, registrou ENVIRONMENT_ERROR). O código de saída do terminal e o diário servem de diagnóstico; o veredito do script vem só do resumo no log de experts.
- Prova nativa não é aceite: o ensaio visual (painel, cliques, dois gráficos) continua manual.
- Os testes MQL5 não são alterados para servir ao executor; qualquer ajuste neles é mudança de produto com CHG próprio.
