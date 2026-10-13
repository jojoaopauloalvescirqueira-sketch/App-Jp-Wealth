# Stoikus 1.22.0 — mapa de renomes e compatibilidade

Revisão candidata de 12/10/2026, implementada sob a autorização atual do proprietário para a renomeação delimitada. Produto **1.22.0**, MQL **1.220**, cálculo **1.9.0**. Marca pública **Stoikus**; o prefixo `JPW_Stoikus_` identifica arquivos técnicos. A logo JP Wealth, o slogan “Da origem da operação à leitura do risco.” e o nome independente **NoCuda** permanecem.

Contrato e fronteira de escrita: [CHG/CTX autorizado](../../docs/work/CHG-STOIKUS-RENAMING-20261012.md) e [brief](../../docs/work/BRIEF-STOIKUS-RENAMING-20261012.md). Base `0f247215cc20829fdba40c3b33458ee976c17ea1`; candidato na branch `codex/stoikus-renaming-20261012`. Este manual registra o escopo; não concede novas permissões.

## Componentes e nomes estáveis

| Uso | Componente atual | Contrato preservado |
| --- | --- | --- |
| Stops, histórico pessoal e ciclos da conta | `JPW_Stoikus_Monitor` | Núcleo observador em gráfico de apoio; não negocia. |
| Resumo e Cockpit | `JPW_Alavancagem_Atual` — Stoikus · Conta | Indicador; nome técnico conservado. |
| Estudos no gráfico | `JPW_NoCuda_Channels` — NoCuda · Gráficos | Indicador independente; sem autorização operacional pelo desenho. |
| Proteção adicional em 7x | `JPW_Stoikus_Supervisor` | Separado e opcional; conserva o contrato de observação e armamento explícito em demo. Não é requisito das leituras. |

`JPW_Alavancagem_Observer` e o Accountant separado ficam preservados para compatibilidade e rollback. Não executar esses produtores junto ao Monitor. O gráfico de apoio precisa permanecer aberto; fechar o Cockpit não encerra o núcleo. No MT5, anexar outro EA ao mesmo gráfico substitui o anterior.

## Mapa exato de arquivos MQL e recursos — 29 entradas

Caminhos relativos a `mt5/jpw-alavancagem-atual/` na raiz do repositório. O mapa inclui programas, bibliotecas, oito bitmaps e sua proveniência. Renomear um recurso não redesenha a logo.

| Antes | Depois |
| --- | --- |
| `MQL5/Experts/JPWealth/JPW_Genetrix_Accountant.mq5` | `MQL5/Experts/JPWealth/JPW_Stoikus_Accountant.mq5` |
| `MQL5/Experts/JPWealth/JPW_Genetrix_Monitor.mq5` | `MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5` |
| `MQL5/Experts/JPWealth/JPW_Genetrix_Supervisor.mq5` | `MQL5/Experts/JPWealth/JPW_Stoikus_Supervisor.mq5` |
| `MQL5/Images/JPWealth/JPW_Genetrix_Logo.provenance.md` | `MQL5/Images/JPWealth/JPW_Stoikus_Logo.provenance.md` |
| `MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_100.bmp` | `MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_100.bmp` |
| `MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_125.bmp` | `MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_125.bmp` |
| `MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_150.bmp` | `MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_150.bmp` |
| `MQL5/Images/JPWealth/JPW_Genetrix_Logo_Dark_200.bmp` | `MQL5/Images/JPWealth/JPW_Stoikus_Logo_Dark_200.bmp` |
| `MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_100.bmp` | `MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_100.bmp` |
| `MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_125.bmp` | `MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_125.bmp` |
| `MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_150.bmp` | `MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_150.bmp` |
| `MQL5/Images/JPWealth/JPW_Genetrix_Logo_Light_200.bmp` | `MQL5/Images/JPWealth/JPW_Stoikus_Logo_Light_200.bmp` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Accountant_Runtime.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Accountant_Runtime.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Brand.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Brand.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Bridge.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Bridge.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Core.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Core.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Preparation.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Preparation.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Store.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Store.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Terminal.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Ledger_Terminal.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Monitor_Core.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Monitor_Core.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Monitor_Status.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Monitor_Status.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Monitor_UI.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Monitor_UI.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Observer_Runtime.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Observer_Runtime.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Risk_Core.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Risk_Core.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Risk_Store.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Risk_Store.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_Risk_Terminal.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_Risk_Terminal.mqh` |
| `MQL5/Include/JPWealth/JPW_Genetrix_UI.mqh` | `MQL5/Include/JPWealth/JPW_Stoikus_UI.mqh` |
| `MQL5/Scripts/JPWealth/JPW_Genetrix_Ledger_Tests.mq5` | `MQL5/Scripts/JPWealth/JPW_Stoikus_Ledger_Tests.mq5` |
| `MQL5/Scripts/JPWealth/JPW_Genetrix_Risk_Tests.mq5` | `MQL5/Scripts/JPWealth/JPW_Stoikus_Risk_Tests.mq5` |

## Mapa de ferramentas host — cinco entradas

Caminhos relativos à raiz do repositório. Esta trilha mantém critérios, fixtures e oráculos financeiros originais; mudar o nome do verificador não transforma falha histórica em aprovação.

| Antes | Depois |
| --- | --- |
| `tools/jpw_genetrix_brand_test.py` | `tools/jpw_stoikus_brand_test.py` |
| `tools/jpw_genetrix_ledger_test.py` | `tools/jpw_stoikus_ledger_test.py` |
| `tools/jpw_genetrix_oracle_test.py` | `tools/jpw_stoikus_oracle_test.py` |
| `tools/jpw_genetrix_risk_test.py` | `tools/jpw_stoikus_risk_test.py` |
| `tools/jpw_genetrix_ui_test.py` | `tools/jpw_stoikus_ui_test.py` |

## Compatibilidade e dados

A troca de marca e dos 34 nomes não altera fórmulas, unidades, agrupamento, ordenação, limites, parâmetros, tipos, funções, macros, APIs ou portas de escrita. Schemas, bancos, caminhos de dados, chaves persistidas, locks, titularidade de publicador, inputs e preferências mantêm seus contratos. Nomes internos legados podem permanecer por compatibilidade; sua presença não indica uma segunda política financeira.

As pastas `mt5/jpw-alavancagem-atual/`, `downloads/jpw-alavancagem-atual/`, `MQL5/Include/JPWealth/` e os namespaces financeiros existentes permanecem. Não fazer substituição global de GENETRIX em nomes persistidos, diretórios, JSON, bancos ou variáveis de terminal. Não apagar locks nem recriar registros para forçar a troca de programa.

Os manuais `GENETRIX_*.md`, o harness, o AGENTS do componente, os pacotes anteriores e seus recibos permanecem como documentos históricos. O README acrescenta somente a camada atual Stoikus acima do corpo original. As referências normativas e os estados `PENDING`, `NOT_HOMOLOGATED`, `BLOCKED`, `Partial` e `N/A` não recebem nova interpretação pela renomeação.

## Distribuição e transição futura

O pacote atual é `JPW_Stoikus_Fontes_v1.22.0.zip`, **somente de fontes**, sem EX5. Para preparar uma futura instalação autorizada, usar o conjunto completo de fontes, includes e recursos da mesma revisão em ambiente isolado. Não copiar somente um MQ5 nem misturar arquivos de versões diferentes.

**Não renomear EX5 antigos para Stoikus.** Um binário GENETRIX não se torna 1.22.0 pela troca do nome. É necessário compilar os bytes exatos e registrar o vínculo fonte/build/log/hash do EX5 antes de tratar o artefato como correspondente à revisão.

Em futura transição operacional explicitamente autorizada, preservar o conjunto anterior coerente e os registros, encerrar normalmente e retirar dos gráficos os componentes legados antes de iniciar os correspondentes Stoikus. Um binário antigo pode não reconhecer o novo nome de apresentação; não confiar nessa compatibilidade para impedir duas instâncias. Conferir indicadores e produtores existentes, sem remover bancos, chaves ou locks. Observer e Accountant separados não devem concorrer com o Monitor. Esta tarefa não realiza instalação, retirada no terminal, armamento ou negociação.

## Evidência e limites atuais

Host/web e integridade do pacote estão **em validação**; os resultados pertencem aos recibos do candidato exato em [INTEGRATION 1.22.0](../../docs/validation/stoikus-1.22.0/INTEGRATION.md). Este manual não declara execução de testes, compilação ou aprovação.

Compilação e interação nativas no MT5, instalação e aceite operacional: **NOT_RUN**. Recibos de versões anteriores permanecem históricos e não comprovam execução, prontidão ou homologação destes fontes. Uma alteração material posterior exige nova identificação e repetição das verificações afetadas.

Rollback restaura somente o delta autorizado e o conjunto anterior coerente, com a operação Git pertinente autorizada separadamente, regeneração pelos processos oficiais e conferência de hashes. Não envolve restaurar ou apagar dados financeiros. Commit, push, integração e publicação continuam gates humanos próprios.
