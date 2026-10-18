# Instalador Stoikus — candidato R3 — 18/10/2026

O instalador 1.0.0-beta.1 foi atualizado para os mesmos fontes **Stoikus 1.23.0/R5**, cálculo **1.9.0**, presentes na main de base `bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4`. Este é um candidato local sem assinatura digital e com download público indisponível. Os recibos R1/R2 na pasta superior descrevem seus próprios bytes e permanecem históricos.

## Identidade

- EXE privado: `Stoikus_Setup_1.0.0-beta.1_win-x64.exe`.
- Tamanho: **117.146.165 bytes**.
- SHA-256: **`0d5919f1908f2dd87ce793221fd863ae46db6b4ca467971d6381ea3ee9d17e85`**.
- Payload diário: **469.034 bytes**, **86 membros**, exatamente quatro programas.
- SHA-256 do ZIP diário: `0bc6c856410b576ebf0412aa341056e8e02463c8f848fe34d2bd4e983ae5f7a3`.
- SDK oficial .NET **10.0.402**, publish autocontido `win-x64`, arquivo único, sem trimming/AOT. Não há EX5 incorporado.

## Alterações e contraprovas

A integração conserva o carregador compartilhado e os artefatos R5. O EXE fica fora do catálogo incorporado no HTML portátil. Sua eventual disponibilidade exige versão correta, URL de release limitada ao repositório, recibos do mesmo hash para cada plataforma/etapa e verificação de MIME, tamanho e SHA-256 antes do download.

O Core R2 exigia exit 0 do MetaEditor. A caracterização nativa anterior mostrou exit 1 com compilação válida. A regressão R3 demonstrou esse bloqueio e a aceitação indevida de log de outra fonte: **58/60** antes da correção. O candidato agora conserva o exit bruto, exige log completo da fonte exata, corpo reconhecido, zero erros/avisos e EX5 novo; recusa erro, output ausente, mensagem desconhecida e outro código de processo. Uma contraprova adicional de includes transitivos passou de **60/61** para **61/61** após corrigir a fronteira do stage. As falhas anteriores permanecem nos recibos privados.

O replay adicional de sete logs nativos capturados identificou linhas BMP não reconhecidas em Conta/NoCuda: **5/7** inicialmente. O novo teste permanente de recursos passou de **61/62** para **62/62**; valida nome do arquivo, identificador e caminho dentro do mesmo stage. O replay final passou **7/7**, incluindo a recusa dos dois logs de erro esperados. É execução do parser no host com registros antigos, não compilação nativa pelo instalador R3. O EXE anterior `30120f…1202b` permanece preservado como tentativa anterior.

## Validação e limites

| Prova | Estado observado |
|---|---|
| Core, filesystem e compilador sintético | **62/62 PASS** |
| Lógica da UI ligada ao Core | **18/18 PASS** |
| Payload e metadados adversariais | **12/12 PASS** |
| Downloader, regressões R4/R5 e instalador | **PASS** |
| Replay do parser em logs nativos anteriores | **7/7 PASS**, sem execução nativa nova |
| Validação estrutural e pacotes R4/R5/diário | **PASS** |
| Build C# e EXE cruzado | **PASS**, sem aprovação de execução Windows |
| 160 inputs MQL, históricos e entrega R5 | **Byte-idênticos** |
| Host da revisão | **47 PASS / 1 PRODUCT_FAIL**: timeout de 60s no HUD; sem drift |
| Full web do candidato combinado | Pendente do executor principal |
| Windows x64, Parallels ARM e WinForms nativo | **NOT_RUN para este EXE** |
| Compilação MQL e uso MT5 pelo instalador | **NOT_RUN** |
| Download real, acessibilidade e iniciante | **NOT_RUN** |
| Revisão independente final R3 | Pendente |
| Publicação/release | **NOT_RUN** |

A VM Windows 11 estava ligada, mas `prlctl exec` retornou a restrição da edição Pro/Business. A conclusão dos ensaios por outro canal permanece com o executor principal; isso não prova falha do instalador. Nenhum componente foi instalado/ativado, nenhum dado MT5 foi modificado e nenhuma negociação foi armada nesta etapa. O usuário possui apenas Windows ARM no Parallels; seu teste não substitui Windows x64 independente.

A cópia privada durável do candidato e os logs completos ficam no arquivo de consolidação de 18/10/2026, subpasta `installer/`. [Metadados do candidato e estados](candidate-R3.json). A integridade de código/build, o comportamento nativo e o aceite humano possuem provas próprias.

O host estável final preservou os 48 comandos e inputs: 47 passaram; `stoikus_hud_targets_test` atingiu o limite interno de 60 segundos, sem assert de produto observado. O resultado bruto permanece PRODUCT_FAIL, sem extensão do orçamento ou atribuição causal à carga. As fontes MQL e esse teste estão intactos. A tentativa inicial com 47 PASS / 1 PRODUCT_FAIL / 1 TEST_HARNESS_FAIL (inputs alterados durante a execução) permanece histórica e não certifica o candidato final. A triagem e o gate do candidato combinado pertencem ao executor principal.
