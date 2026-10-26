# Triagem somente leitura — timeout de ui-visual-quality no FULL2

Nenhum navegador/teste foi iniciado por esta triagem. Nenhum arquivo oficial foi editado. Foram inspecionados argumentos, runner/script/helpers, recibo completo FULL1, timestamps dos artefatos FULL2, inventário de processos e hashes das fontes.

## Fatos confirmados

- quality_gate.py:run_check impõe900s ao processo inteiro de cada comando via subprocess.run(timeout=900). A entrada ui-visual-quality chama tools/ui_visual_quality_test.py --out <diretório>; sem --case, seleção defaultall. Não é timeout de um único caso nem indicação de uma assertiva financeira/visual específica.
- FULL1:ui-visual-quality PASS em774.978s do runner; relatório interno774.331s,370casosPASS,653.165s somados dentro de record() e~121.166s de setup/launch/cleanup entrecasos. Os SOURCE_FILES desse recibo coincidem integralmente com os arquivos atuais. Ambos usam Chromium148.0.7778.96, runtime/args iguais, diferenciando só diretório de saída.
- FULL2:runner relatou ENVIRONMENT_ERROR900.027s. Diretório tem32capturas calendar e8calendar-native200; falta ui-visual-quality-results.json. O script sógrava o JSON no finally; morte externa pelo teto impede esse recibo, portanto capturas não autorizam inferirPASS doscasos.
- Os481inputs congelados continuam iguais. Produto, scripts, critérios e timeout não foram alterados entre essas observações.

## Linha do tempo que distingue acúmulo de uma espera final isolada

Tempos desde início do comando/diretório, emsegundos, usando timestamps dos mesmos arquivos:

| Marco | FULL1 | FULL2 | Acréscimo |
|---|---:|---:|---:|
| Primeiro calendar320/sidebar/light |601.424|712.995|111.571|
| Último calendar1440x480/submenu/dark |672.615|829.892|157.278|
| Primeiro calendar-native200/sidebar/light |690.020|862.616|172.596|
| Último calendar-native200/submenu/dark |704.412|879.760|175.347|

Após o último marco, FULL2tinha20.240s do orçamento. No FULL1ainda foram necessários69.919s para planejamento nativo legacy, compact, closure e validação final de cobertura. Mantida apenas a cadência restante do FULL1, FULL2terminaria por volta de949.678s. A pastavisual-native200 remanescente nasceu~880.097s após início, coerente com interrupção durante essas etapasfinais. Isto comprova insuficiência do orçamento restante, sem provar a causa externa da lentidão acumulada.

## Onde há custo relevante já observado no FULL1

-80casos matrixlegacy:196.262s somados.
-80casos compactmatrix:177.158s somados.
-compact-month-details-complete:75.369s; verifica os120meses nosdoismodos reais, não sóamostra.
-8nativelegacy:32.856s;8compactnative:18.834s;8closurenative:4.174s, alémde setup/cleanup dosperfis.

O defaultexecuta serialmente regressões/contraprovas, matrizes completas, touch, notifications/calendar e cinco lançamentos de perfis nativos. Planning.setup tem timeout padrão15s por ação; record() captura falhas e continua. Assim, atrasos de ações ou falhas internas poderiam aumentar o total, mas sua ocorrência no FULL2não está demonstrada sem saída parcial detalhada.

As fases nativas usam headless=False, no_viewport e janela1440×1000; as matrizes anteriores usam browser headless. O acréscimo de111.571s já existia ao chegar ao primeiro calendar, anterior àsúltimasjanelas nativas. Portanto, atribuir tudo a foco/interação na última etapa seria causalmente incorreto.

## Limites e condição observada depois

O executor informou memórialivre32%, AC100%, sem aviso térmico e ausência de órfão UI após o timeout; estes são dados declarados pela raiz, não uma medição retrospectiva desta triagem. A inspeção deprocessos atual também não encontrou ui_visual_quality nem o perfilvisual-native200 antigo emexecução.

O usuário confirmou uso do Mac durante o FULL2 e ofereceu45min semuso. Interferênciaé possível; não está provada como causa. O executor preservou o parcial explícito full-second-interrupted.json/.log:25checkscompletos,24PASS/1ENVIRONMENT_ERROR, restanteNOT_RUN/interrompido, semJSONoficialFULL2. A saída porIDs docheckvisual estava no buffer do runner e não foi recuperada antesdeSIGINT; não reconstruir nem declarar que seuscasos passaram.

Foi iniciada uma única nova execuçãoFULL3 sob a condição declarada semuso, mesmo comando/900s/critério/fontes e semsuíte concorrente. Essa comparação tem condição externa diferente identificada e preserva asfalhas anteriores. FULL3precisa de resultado próprio; esta triagem não o antecipa. Se repetirENV, não tratar nova tentativa cega como diagnóstico nem relaxar matriz/oráculo/timeout para obterverde.

Veredito de triagem:ENVIRONMENT_ERROR por teto global confirmado; acúmulo de lentidão comprovado por marcos; causa da lentidão permanece indeterminada. Nenhuma alteração de produto ou juiz é indicada pelas evidências atuais.
