# Instalador Stoikus — candidato R4 — 18/10/2026

O R4 corrige uma fragilidade comprovada pela revisão independente do R3: arquivos regulares do stage podiam mudar entre compilações e ser instalados com um hash recém-calculado, sem corresponder ao payload ou ao EX5 reconhecido. O produto continua **Stoikus 1.23.0/R5**, cálculo **1.9.0**, instalador **1.0.0-beta.1**, beta local sem assinatura digital e sem download público. R1/R2/R3, seus recibos, binários e fontes permanecem históricos; a aprovação do parser ou do build R3 não aprova sua transação.

## Identidade do candidato

| Artefato | Identidade |
|---|---|
| EXE privado `Stoikus_Setup_1.0.0-beta.1_win-x64.exe` | **117.149.237 bytes**, SHA-256 `7ae3785c4c45e2bb65b9ee6e0f2a57fc1ffff07fca1303958cc0ec686006754b` |
| Core Release incorporado, bytes exatos no EXE | **89.088 bytes**, SHA-256 `441b907b4f10bfef3835a31ba1eacbe30b06d53ee001f6dc86a76fa7a516e0d3` |
| Payload diário preservado | **469.034 bytes**, 86 membros/quatro programas, SHA-256 `0bc6c856410b576ebf0412aa341056e8e02463c8f848fe34d2bd4e983ae5f7a3` |
| Manifesto do payload preservado | SHA-256 `0b43fb7d5d68281d2ff041aca499cf4ac633fc8290540040bac293c647cfc0a8` |
| Construção | SDK .NET10.0.402, Release win-x64 autocontido, arquivo único, sem trimming/AOT |

O PE é AMD64; isso não comprova arquitetura de EX5 nem execução Windows. Não há EX5 incorporado. [Metadados e estados próprios](candidate-R4.json).

## Defeito reproduzido e correção

As contraprovas trocaram fonte já compilada, EX5 aceito, include JPWealth, include padrão e log durante a compilação seguinte. No R3 os cinco casos retornaram sucesso e fizeram nove escritas no destino sintético. Alterar a fonte durante compilação ou o stage após as quatro compilações também foi aceito. A suíte ficou **62/65**, com sete cenários demonstrados dentro dos três grupos novos; o rollback após o primeiro arquivo instalado já funcionava no baseline.

O R4 fixa fontes e recursos à identidade do payload, includes padrão à identidade capturada na preparação e EX5/logs aos bytes reconhecidos na evidência. Confere o conjunto antes/depois de cada compilação e mantém handles de leitura com compartilhamento somente para leitura durante compilação/transação no Windows. O hash do log é calculado sobre os mesmos bytes que o parser analisou. A transação usa a identidade aprovada e verifica os bytes da cópia temporária antes da troca atômica, com nova conferência do destino imediatamente antes de publicar.

Os mesmos cenários passaram a recusar antes de escrever no destino, sem recibo de sucesso. Novos casos cobrem reparo sem alterar a instalação/recibo anterior e cópia temporária com hash incompatível. As garantias se limitam às mutações ordinárias e fronteiras ensaiadas; não se reivindica isolamento contra kernel ou ator hostil com os mesmos privilégios. Falhas conservam diagnóstico; alterações da própria transação são recuperadas e arquivos posteriores desconhecidos continuam protegidos.

## Provas e limites

| Prova | Estado R4 |
|---|---|
| Core, transação e compilador sintético | **67/67 PASS** |
| Lógica da UI ligada ao Core | **18/18 PASS** |
| Payload e metadados adversariais | **12/12 PASS** |
| Build C# cruzado e Core exato dentro do EXE | **PASS** |
| 160 fontes MQL, ZIPs históricos e kit R5 protegidos | **Byte-idênticos** |
| Host completo do candidato R4 | Pendente do executor principal |
| Full web e revisão independente final R4 | Pendente do executor principal |
| WinForms, Windows x64 e ARM/Parallels nativos | **NOT_RUN** |
| Quatro compilações MQL pelo instalador R4 | **NOT_RUN** |
| Instalação, reparo e remoção nativos | **NOT_RUN** |
| Download real, acessibilidade e iniciante | **NOT_RUN** |
| Publicação/release | **NOT_RUN** |

A correção separada do compilador host foi autorizada pelo humano e aplicada pelo executor principal em `CHG-HARNESS-VISUAL-COMPILER-20261018`: inclui `-O2` na construção da bancada C++, preservando o prazo de 60 segundos e as contraprovas. O resultado histórico R3 de 47 PASS/1 PRODUCT_FAIL permanece íntegro; a proposta e o diagnóstico anterior não viram PASS retroativo nem prova do candidato combinado. Não há alteração de fontes MQL ou cálculos nesta correção.

As evidências completas RED/GREEN, fontes congelados e binários privados estão no arquivo de consolidação de 18/10/2026, em `installer/R4/` e `installer/candidate-R4-final/`. A bancada nativa externa foi pausada antes de qualquer execução no guest para não ensaiar a DLL R3 rejeitada. Sua eventual preparação deverá fixar a DLL R4 e gerar identidade própria. A abertura dos gráficos, observação do MT5, aceite humano e uso financeiro continuam separados do build.
