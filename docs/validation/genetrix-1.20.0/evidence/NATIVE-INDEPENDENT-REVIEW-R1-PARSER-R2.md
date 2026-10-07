# Revisão independente — compilação nativa GENETRIX 1.20.0 R1

Revisor: `hud_acceptance`. Data: 06/10/2026. Estado: **NATIVE_COMPILATION_DEMONSTRATED_33_OF_33**.

Conferidos exatamente **33 alvos, 33 logs adjacentes e 33 EX5 novos**, com geração de código e resultado final **0 errors, 0 warnings, X64 Regular**. O log geral contém os mesmos 33 caminhos. Inputs e outputs não mudaram durante esta revisão.

- Freeze candidato: `6ca7c179be25adc2146a27a35d23fb7dfa128f525659facf5d760cd2934910e0`.
- Freeze nativo anterior: `5c4dee2ba88561c18f882c3803edf89399d7a60a196d62e99a8e7f820c2480c4`.
- MQL/source+resource fingerprint: `1290186a730aaaf8f1d5645318ff8c814a7dc821e419d9eb3c16015cadf1d783`.
- Build ID do candidato: `8a01094f354dc52ed37e14d585b6625d11dc62614a5019aa74d5dc8da7497f1e`.
- Compilador: SHA-256 `68d8f87dcdb443cb851a75839ae68ed606b0b661995cde8218156778db5244c2`, idêntico ao arquivo instalado e congelado. PE **5.0.0.6230**, build **6230**, lido sem executar. Assinatura Authenticode `NOT_VERIFIED`; About `NOT_OBSERVED`.
- Auxiliar: SHA-256 `74c2210a09563b98278a38decef0ca75d2a1d2b03f18153353c82e79631a887b`.
- 735 entradas anteriores conferidas: 349 arquivos efetivos e 386 AppleDouble de metadados; 112 fontes/recursos MQL e 235 includes padrão. Os 120 arquivos do freeze candidato também foram conferidos no host.
- Intervalo observado: 2026-10-06T12:47:22.980000+00:00 a 2026-10-06T12:50:33.440000+00:00. Logs/EX5 ausentes no inventário anterior e gravados no intervalo da chamada correspondente.

Retornos brutos **1 em 33/33 chamadas**, preservados sem usar esse código isoladamente como sucesso. A conclusão usa os logs atuais completos, EX5 novos e integridade dos inputs. Não se transferiu evidência de 1.19.0. FINISHED indica despacho concluído, sem aprovar os componentes; código final do auxiliar não observado.

| Alvo | EX5 bytes | Resultado nativo | Retorno bruto |
|---|---:|---|---:|
| `Experts/JPWealth/JPW_Alavancagem_Observer.mq5` | 283550 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Experts/JPWealth/JPW_Genetrix_Accountant.mq5` | 103238 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Experts/JPWealth/JPW_Genetrix_Monitor.mq5` | 439222 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Experts/JPWealth/JPW_Genetrix_Supervisor.mq5` | 122728 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Indicators/JPWealth/JPW_Alavancagem_Atual.mq5` | 1002050 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Indicators/JPWealth/JPW_NoCuda_Channels.mq5` | 459246 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Consultar_MDD.mq5` | 42776 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Diagnostics_Tests.mq5` | 39828 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Genesis_Store_Tests.mq5` | 52004 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Genesis_Tests.mq5` | 15104 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Metrics_Tests.mq5` | 61048 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Observer_Tests.mq5` | 39344 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Panel_Tests.mq5` | 9426 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Positions_Tests.mq5` | 52748 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Profile_Tests.mq5` | 39710 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_RaizN_Config_Tests.mq5` | 105846 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_RaizN_Factor_Tests.mq5` | 54816 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_RaizN_Horizon_Tests.mq5` | 21050 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_RaizN_Live_Tests.mq5` | 23320 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_RaizN_Store_Tests.mq5` | 101872 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_RaizN_Tests.mq5` | 7626 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_StopRisk_Tests.mq5` | 51716 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Tests.mq5` | 65570 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Alavancagem_Verificar_USC.mq5` | 72318 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Genetrix_Ledger_Tests.mq5` | 38948 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_Genetrix_Risk_Tests.mq5` | 36340 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_NoCuda_Core_Tests.mq5` | 10428 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_NoCuda_Fibo_Lab.mq5` | 34860 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_NoCuda_Fibo_Tests.mq5` | 32502 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_NoCuda_Projection_Tests.mq5` | 19960 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_NoCuda_Store_Tests.mq5` | 47662 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_PersonalHistory_Tests.mq5` | 20100 | 0 erros / 0 avisos · X64 Regular | 1 |
| `Scripts/JPWealth/JPW_SignalCopy_Tests.mq5` | 76572 | 0 erros / 0 avisos · X64 Regular | 1 |

Nenhum caminho de include nos logs saiu do namespace isolado. O JSON conserva hashes, caminhos, tempos, resultado completo e gates. O revisor leu os resultados; não executou Windows nem alterou produto, VM ou instalação operacional.

**Limite:** Scripts Tests foram compilados, não executados. Runtime, interface, migração, alertas, som, aceitação financeira e operacional permanecem `NOT_RUN` por esta evidência. Compilação comprovada não é aprovação do funcionamento.

Leitura PE conforme [VS_FIXEDFILEINFO](https://learn.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo) e [VS_VERSIONINFO](https://learn.microsoft.com/en-us/windows/win32/menurc/vs-versioninfo), documentação Microsoft consultada em 06/10/2026.
