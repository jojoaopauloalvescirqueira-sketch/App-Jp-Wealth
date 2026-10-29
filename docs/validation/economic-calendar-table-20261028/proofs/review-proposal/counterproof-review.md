# Revisão independente das contraprovas — 28/10/2026

Escopo: leitura do launcher run_counterproofs.py, receipt.json integral por casos/tracebacks e final-scratch-five.json. Conferência de hashes sem importar/executar os testes. Nenhuma execução browser/FULL, escrita no repositório ou auditoria de distribuição nesta revisão.

## Veredicto

O recibo final-scratch-five.json comprova, por execução relatada pelo autor e identidade conferida, PASS5/5 com os candidatos finais de produto e testes. Substitui a limitação de versão anterior no recibo overlay-focal-3; não substitui FULL/distribuição/aceite humano.

Não endosso o agregado PASS12/12 das contraprovas como prova de12 propriedades pretendidas. Resultado da revisão desse agregado: TEST_HARNESS_FAIL / AUDIT_FAIL delimitado à classificação CP05. Onze rejeições têm causa pertinente confirmada pela mensagem/frame; CP05 rejeitou uma violação real, mas pelo oráculo de overflow, sem alcançar o oráculo de alinhamento declarado.

## Achado CP-REVIEW-01 — HIGH para integridade da evidência

Arquivo: tests-proposal/run_counterproofs.py, linha56 (classificador de rejeição). Hash3b18ce2eb9fa39ccb212e121bbffdcb99d4de9da7ac0e1b4e29c8dacf38d58f9.

O classificador faz expected_marker in (str(error)+'\n'+trace). CP05 desloca o último th+5px; isso aumenta scrollWidth da agenda de735 para740 e falha na linha83 do helper, 'No horizontal overflow'. O marcador esperado 'Real header and cell column bounds align' aparece somente no traceback da chamada record(..., expected_marker) que inclui o próprio texto esperado. Por isso a classificação PASS é falsa para a propriedade de alinhamento.

A contraprova prova que o juiz rejeita esse overflow. Não prova que uma coluna desalinhada sem overflow é rejeitada. O produto não é o defeito aqui, nem o helper congelado: é a atribuição de causa no launcher scratch.

Ajuste mínimo recomendado ao autor: comparar str(error) ou a identidade exata do frame final de asserção; nunca pesquisar no traceback inteiro incluindo callsite com o marcador. Para asserções sem mensagem, como CP08, verificar função/linha da asserção efetiva. CP05 deve deslocar um th interno ou deslocar o último para a esquerda5px, mantendo o overflow válido antes de esperar a falha de alinhamento. Preservar o recibo incorreto e executar nova contraprova; não reescrever a história. Nenhum ajuste foi realizado pelo revisor.

## Conferência das doze rejeições

| Caso | Resultado observado | Julgamento independente |
|---|---|---|
| CP01 zero→ausência | assert_values forecast esperado0, observado— | Rejeição pertinente |
| CP02 Actual inventado | assert_values actual esperado—, observado0 | Rejeição pertinente |
| CP03 Anterior oculto | assert_layout 'All fields visible',6 campos | Rejeição pertinente |
| CP04 explicação removida | assert_values 'Actual absence needs a clear accessible explanation' | Rejeição pertinente aos canais verificados (ARIA/notas); não teste de leitor de tela |
| CP05 th+5px | assert_layout 'No horizontal overflow',740>735 | Motivo diferente; falsoPASS de propriedade declarada |
| CP06 número à esquerda | assert_layout 'Numeric ink must align right',1153.359 versus1254.609 | Rejeição pertinente |
| CP07 cabeçalhos em719 | assert_layout 'Seven headers only when economic area>=720', área719 | Rejeição pertinente; row.area735 é precondição anterior ao prepare, observação de falha confirma719 |
| CP08 aviso oculto | frame table_case linha171, assert 'última coleta' in rows.nth(3).inner_text() | Rejeição pertinente; AssertionError vazio, causa verificada pelo frame final |
| CP09 dois detalhes | table_case espera detalhe0 invisível, recebe visível ao abrir detalhe1 | Rejeição pertinente |
| CP10 alvo em outro host | details: 'Detail target belongs to same host', calendarWorkspaceEconomicDetail0 no modal | Rejeição pertinente |
| CP11 reaproveitamento de observação alterada | table_case espera aria-expanded=false, recebe true | Rejeição pertinente à expansão; mutação também rouba foco, mas falha ocorre antes da asserção de foco |
| CP12 draft/cursor corrompidos | table_case espera SYN table draft, recebe BROKEN synthetic draft | Rejeição pertinente ao texto do draft; mutação também zera cursor, mas não demonstra isoladamente a sensibilidade do oráculo de cursor |

Os casos usam import do helper congelado35ea… e as mesmas funções assert_values/assert_layout/details/table_case; wrappers de setup injetam somente defeitos DOM/MutationObserver nos casos de estado e são restaurados em finally. O classificador não aceita TimeoutError/erro genérico: esses caminhos são TEST_HARNESS_FAIL. Nos onze casos pertinentes a leitura do frame/mensagem confirma falha da asserção de produto, não erro de bootstrap. A comparação com traceback inteiro permanece frágil para outras mutações futuras mesmo que onze atuais tenham motivo correto.

As propriedades de foco e cursor possuem casos positivos, mas CP11/CP12 não devem ser descritas como contraprovas independentes de todos os efeitos que suas mutações combinam. Não exige alterar os cinco testes congelados; exige precisão do relatório e, se for necessária essa alegação específica, estímulos isolados futuros autorizados.

## Identidade

- receipt12: c4708f1ad6ec6c3f25d2c9ad6bd7782e8d9a83cef8717b05a4973eea19f9958f
- launcher:3b18ce2eb9fa39ccb212e121bbffdcb99d4de9da7ac0e1b4e29c8dacf38d58f9, igual ao registrado no recibo.
- final-scratch-five:c48f1219844f81c2781adf249af24e7bd9371140c19b9b909a67be83f517ec7f
- patch testes:37a46edbd8e2c56e6327ce8dc8e42cc034c1063c2ef6a55520effa53bc8a39c3
- helper:35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a
- JS produto nos dois recibos:1e2e518bef9dccca48790f9752c48ba62619cd64c128ec87c55c6c58c779c831
- CSS produto nos dois recibos:f1007dfe4122ac80aa2e8260b4db91079ad5291cec5f1b2dd6ab0aa3910beb38

Os12 hashes de mutation foram recalculados e conferem. Hashes dos cinco candidatos nos novos recibos correspondem aos finais revisados. Arquivo complementar: counterproof-review-hashes.json.

A apresentação dos patches para autorização humana permanece possível com esta limitação explícita; o agregado12/12 não deve embasar conclusão de integridade das contraprovas antes do reparo descrito. Aplicação dos testes, FULL, distribuição, native200 e aceite humano continuam separados e pendentes. Estado de branch/produto aplicado recebido do coordenador, não auditado novamente nesta tarefa.

## Adendo — reavaliação do launcher e recibo v2

Recebidos e lidos run_counterproofs.py v2, counterproofs-final-v2/receipt.json e counterproofs-v1-triage.json. Nenhum navegador foi executado pelo revisor; este é parecer independente sobre fontes, estímulos e evidências de execução do autor.

A correção resolve CP-REVIEW-01 no launcher v2: o classificador exige a mensagem real da exceção e a função/linha do último frame pertencente ao helper congelado. Não pesquisa mais o traceback completo. CP08 usa a asserção-fonte exata de table_case:171 porque sua exceção não tem mensagem. Hash obrigatório do helper vincula os números de linha ao código revisado. O launcher v1 e o recibo bruto foram preservados; o registro de triagem o classifica efetivamente TEST_HARNESS_FAIL. O achado histórico acima continua válido para v1.

CP05 agora desloca o último cabeçalho−5px. A rejeição real é 'Real header and cell column bounds align within2 CSSpx' em assert_layout:101 para previous, depois de passar pelo teste de overflow. Os limites do cabeçalho e célula diferem5px, conforme estímulo; portanto esta execução alcançou o oráculo pretendido.

As12 rejeições v2 correspondem às mensagens e frames finais declarados: CP01/02 assert_values:58; CP03 assert_layout:93; CP04 assert_values:66; CP05 assert_layout:101; CP06 assert_layout:97; CP07 assert_layout:91; CP08 table_case:171; CP09 table_case:179; CP10 details:33; CP11 table_case:193; CP12 table_case:215. Conferi as mensagens registradas, fontes das asserções e função/linha. Não identifiquei falsoPASS de motivo de falha no v2.

Veredicto atualizado: AUDIT_PASS delimitado à correção do launcher e à sensibilidade demonstrada dessas12 contraprovas. PASS12/12 v2 pode ser reportado como rejeição correta das12 violações executadas. Mantêm-se os limites de CP11/CP12: demonstram expansão indevida e corrupção do texto do draft, respectivamente; não alegar contraprovas isoladas adicionais de foco/cursor que não chegaram a ser julgadas. Isso não aprova integralmente os controles, aplicação N3, FULL, distribuição, nativos ou aceite humano.

Identidade v2 conferida:

- launcher9e1b4cff1b6c4c6e4eed37f6569165dba9066a555cbfc8331a29fb97faf55260
- receiptb389a3218467e1e1fc2fbea4bcd60e3c122c89cf047ac95f0cb1cafba231552b
- helper35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a
- ProdutoJS1e2e518bef9dccca48790f9752c48ba62619cd64c128ec87c55c6c58c779c831/CSSf1007dfe4122ac80aa2e8260b4db91079ad5291cec5f1b2dd6ab0aa3910beb38.

Recalculei os12 hashes dos estímulos e os cinco hashes de candidatos: todos iguais aos registrados. O recibo informa igualdade dos candidatos antes/depois; os arquivos presentes conferem com os hashes congelados. Nenhuma alteração de produto ou dos cinco testes foi necessária para a correção do classificador scratch.
