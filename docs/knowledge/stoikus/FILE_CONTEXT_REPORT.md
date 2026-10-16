# Stoikus — contexto de arquivos para IAs

Este relatório complementa o relatório nativo do Graphify: a apresentação nativa filtra nós de inventário de arquivos e stubs, exibindo duas comunidades conceituais. Os JSONs/HTMLs mantêm todas as 28 comunidades do mapa geral. As contagens abaixo são de relações de arquivos; grau elevado pode decorrer de hashes de recibos, sem implicar cobertura ou relevância funcional.

## Mapas

| Mapa | Nós | Pares de relações |
| --- | ---: | ---: |
| arquitetura | 125 | 228 |
| fluxos | 104 | 172 |
| testes-evidencias | 225 | 983 |
| master | 301 | 1144 |

## Impacto de mudanças

A direção de includes é consumidor → dependência. A lista a seguir usa apenas entradas EXTRACTED de includes_file; referências de teste são separadas. Abra o arquivo antes de decidir a alteração.

### JPW_PersonalHistory_Store.mqh

Consumidores diretos: `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_Controller.mqh`, `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_Export.mqh`.

Referências em testes/facetas: `tools/jpw_personal_history_test.py`, `tools/leverage_package_test.py`, `tools/personal_history_host/continuity_cases.cpp`, `tools/personal_history_host/controller_cases.cpp`, `tools/personal_history_host/export_cases.cpp`, `tools/personal_history_host/store_cases.cpp`, `tools/personal_history_host/ui_cases.cpp`.

### JPW_NoCuda_Channels.mq5

Consumidores diretos: nenhum include de entrada neste mapa; programa é entrypoint.

Referências em testes/facetas: `tools/jpw_nocuda_fibo_controller_test.py`, `tools/jpw_nocuda_integration_test.py`, `tools/jpw_nocuda_lifecycle_test.py`, `tools/leverage_package_test.py`, `tools/stoikus_daily_package_test.py`, `tools/stoikus_startup_test.py`.

### JPW_Stoikus_Monitor.mq5

Consumidores diretos: nenhum include de entrada neste mapa; programa é entrypoint.

Referências em testes/facetas: `tools/jpw_stoikus_monitor_state_test.py`, `tools/leverage_package_test.py`, `tools/stoikus_daily_package_test.py`, `tools/stoikus_startup_test.py`.

### JPW_Alavancagem_Version.mqh

Consumidores diretos: `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5`, `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Accountant.mq5`, `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5`, `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Diagnostics_Core.mqh`, `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Observer_Presence.mqh`, `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Fibo_Controller.mqh`, `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_PersonalHistory_Terminal.mqh`, `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Accountant_Runtime.mqh`, `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Brand.mqh`, `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Monitor_Status.mqh`, `mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5`, `mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5`, `mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Consultar_MDD.mq5`, `mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Diagnostics_Tests.mq5`, `mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Stoikus_Abrir_Paineis.mq5`.

Referências em testes/facetas: `tools/leverage_package_test.py`, `tools/stoikus_daily_package_test.py`, `tools/stoikus_startup_test.py`.

## Contratos e estados

As receitas Q01–Q08 ligam os quatro papéis, continuidade auditada, cancelamento, ownership, cálculo1.9.0 e distinção entre teste host e prova MT5. Referências do design permanecem contratos; recibos são snapshots identificados por hash. Cálculo, código, fontes e grafos históricos não foram alterados.

Nativo/instalação/aceite: NOT_RUN. Consumo de tokens do host: indisponível. Consultas de navegação 8/8 verificadas; qualidade ou eficiência das respostas de IA não medida.
