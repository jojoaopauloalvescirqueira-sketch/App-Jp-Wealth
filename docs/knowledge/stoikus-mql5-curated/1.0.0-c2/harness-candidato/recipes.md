# Receitas das suítes existentes

Rodar a partir da raiz REPO escolhida, em cópia de trabalho controlada. Leia cabeçalho e dependências de cada script antes: alguns testes host usam Node; indisponibilidade é DEPENDENCY_MISSING. Nenhuma destas receitas foi executada apenas por constar aqui.

```sh
python3 -B tools/jpw_stoikus_monitor_state_test.py
python3 -B tools/jpw_stoikus_risk_test.py
python3 -B tools/jpw_stoikus_ui_test.py
python3 -B tools/stoikus_daily_package_test.py
python3 -B tools/stoikus_window_package_test.py
```

Monitor state examina contratos host do estado; risk cobre oráculos host financeiros conforme o próprio script; UI verifica comportamentos disponíveis no runner; daily/window package cobrem coerência dos respectivos pacotes. Leia o output e registre o nome e quantidade reais; não reutilize a etiqueta histórica de 48 host + 6 grupos UI como contagem nova.

Nativo separado: em terminal autorizado, compilar candidato exato com MetaEditor; registrar versão/build, command line, log completo, warnings, hash EX5 e hash de todos os includes/recursos. Executar scripts JPW_Stoikus_Ledger_Tests.mq5 e JPW_Stoikus_Risk_Tests.mq5 somente no ambiente autorizado, preservar Journal e dados de teste. Nenhuma execução aqui concede permissão para instalar, armar Supervisor ou operar conta. Tester e chart real têm contextos diferentes; relatório deve descrever qual foi utilizado.
