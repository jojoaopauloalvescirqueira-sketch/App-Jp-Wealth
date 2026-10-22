# F1 — expectativa antiga de localização no teste de UI

O FULL congelado registrou `PRODUCT_FAIL` em `planning-ui` (45,23 s); esse resultado bruto será preservado. A reprodução isolada, nos mesmos bytes, terminou com saída real 1 em `current_month_journey`, `tools/planning_ui_test.py:169`: `Locator.inner_text` aguardou 30 s pela nona célula `td.nth(8)` de uma linha que agora tem seis células de dados. A verificação seguinte também procurava a situação do custo na linha principal, embora o contrato aprovado a mova para detalhes.

[Log integral da reprodução](PLANNING-UI-TRIAGE.log) e [processo/identidades](PLANNING-UI-TRIAGE-COMMAND.json). A classificação diagnosticada é **expectativa obsoleta do Harness**; não modifica a classificação bruta registrada pelo runner nem aprova esta rodada.

O plano humano já autoriza “adaptar a expectativa antiga de 18 colunas”, preservando os demais critérios. A proposta delimitada abre os detalhes pelo controle real, lê o único aporte e a situação do custo no campo correspondente, mantendo os valores US$ 100/20, os textos qualificadores, os resultados US$ 1.050/1.030, a confirmação explícita e a ausência de gravação anterior à confirmação.

A inclusão desse arquivo no CHG dedicado e no escopo será reconciliada antes da aplicação. Proposta, contraprovas e revisão independente precedem a alteração. O candidato permanece congelado até concluir esta rodada; depois será necessário novo freeze e novo FULL integral. Não se troca o check por um focal nem se remove qualquer dos 96 checks.
