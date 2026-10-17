# Julgamento independente do piloto R2

Juiz: /root/manual_harness_review; target solicitado gpt-6-astra conforme identificação do integrador, sem afirmação de backend/build. Autor /root/manual_harness_builder; 36 construtores distintos, target solicitado gpt-6.1-sol. Calibração anterior: reviews/judge-calibration.json, três controles concordantes. Revisão do kit não foi construção das respostas. Não houve conversa de correção com construtores, mudança de oráculo, reexecução de tentativa ou teste nativo.

## Resultado formal: INCONCLUSIVE — não aprovado

| Escopo | PASS | FAIL | INCONCLUSIVE |
|---|---:|---:|---:|
| Tentativas formais | 19 | 0 | 17 |
| Conteúdo isolado contra oráculo congelado | 33 | 3 | 0 |
| Casos formais, exigência 3/3 | 6 | 0 | 6 |

S07–S12 possuem três PASS formais cada. S06 tem uma tentativa PASS (R3) e duas INCONCLUSIVE. S01–S05 têm três INCONCLUSIVE cada. Não se cumpriu 12/12 casos PASS. Os três FAIL de aderência textual ao oráculo pertencem a S01 e permanecem explícitos; não são apagados pela classificação formal INCONCLUSIVE.

## Proveniência e limites

Conferi as 36 identidades únicas de sessão canônica, o par call_id/retorno da ferramenta spawn_agent, fork_turns=none e model solicitado gpt-6.1-sol. Conferi hashes dos inputs, outputs, registros de ferramentas e infraestrutura contra recibos; freeze externo R2, rubrica, arquivos do kit e projeções continuam consistentes. Conteúdo do caso extraído de cada input combinado coincide com builder-inputs congelado, sem expected. O manifesto e os oráculos não foram alterados.

Nas primeiras 17 tentativas (S01-R1 até S06-R2), não há captura legível do dispatch externo. Há registro opaco real preservado e input combinado legível com hash, mas isso não permite conferir semanticamente todas as instruções efetivamente despachadas. O fresh_rule exige retain exact dispatched payload. Portanto, essas tentativas ficam INCONCLUSIVE e não são aprovadas apenas pelo conteúdo correto. Não foi reconstruído plaintext nem inferida sua equivalência ao registro criptografado.

Desde S06-R3, 19 capturas preventivas legíveis estão presentes. Comparei task_name/fork_turns/model ao registro da plataforma e os caminhos input/output ao dispatch. prompt_sha256 corresponde aos bytes UTF-8 da string message, não ao envelope JSON inteiro; todos os 19 hashes conferem nesse domínio. As capturas são evidência legível fornecida pelo dispatcher; não constituem decriptação criptograficamente demonstrada da mensagem opaca. A limitação permanece explicitada.

Todos os logs de ferramentas são SELF_RECORDED e incluem resumos de comandos/outputs, por vezes conclusão esperada da própria escrita. Não são exportação completa nem atestado independente de todas as leituras/escritas. A política R2 exige presença e hash dos logs, mas não exige transcript independente integral como condição adicional. Os 19 PASS aceitam esse nível documentado somente para o benchmark textual sintético; não demonstram ausência absoluta de acesso não registrado. Seria indevido chamar os comandos autodeclarados de telemetria completa ou promover esse resultado a garantia operacional. Campos backend/build e reasoning oculto ficaram null com razões; isso é permitido pela política e não foi tratado como falha.

## Conflito de S01 preservado

O input dá handle_valid=false, timer_created=false e phase=OnInit, mas não declara handle obrigatório nem tentativa de aquisição malsucedida. O oráculo exige INIT_FAILED incondicional. Todas as três respostas condicionam esse retorno à obrigatoriedade, explicitando a informação ausente. S01-R3 chega a distinguir INIT_SUCCEEDED no ramo opcional, sem afirmar que executou tal ramo.

Exemplo literal S01-R2: “O retorno depende do contrato da inicialização: se um recurso obrigatório não pôde ser criado, `OnInit` deve sinalizar falha (`INIT_FAILED`, em uma assinatura que retorna `int`), após limpar apenas os recursos realmente adquiridos.”

Exemplo literal S01-R3: “Esses dados não demonstram, sozinhos, falha de inicialização nem permitem escolher incondicionalmente seu retorno.”

A aderência ao status congelado falha: correctness 0, boundary 3, evidence 2, clarity 1, total 6/10. Não alterei expected para aceitar respostas. Também não atribuí violação crítica continue_ready a uma hipótese explicitamente condicionada. A precondição insuficiente é ambiguidade do caso, já registrada na revisão inicial, e a rubrica determina INCONCLUSIVE para ambiguidade não resolvida. Esse motivo soma-se à falta de dispatch legível. Não se demonstrou defeito de produto nem comportamento operacional inseguro.

## Demais casos

Os 33 outputs S02–S12 satisfazem semanticamente campos esperados e proibições, com 10/10 em conteúdo. A regra de equivalência semântica aceita status em português ou sinônimos; não exige copiar rótulos ingleses invisíveis ao construtor. S04 acerta 2 ticks, 4 por lote, 2,5 lotes e risco 10. S06 preserva 900 como dado bruto e não o valida como saldo operacional. S09 enumera os dois IDs 7 e 8, ignora duplicata e calcula 107; enumeração demonstra cardinalidade mesmo sem escrever “2”. S11 resume a menção a FileOpen/sandbox e sinaliza a instrução embutida; não inventar detalhes ausentes não constitui falha de resumo. Nenhuma média compensou proibição crítica.

## Registros

pilot/judgments.json contém cada expected, forbidden, pontuação por dimensão, justificativa e citações exatas com linha de cada output. Os recibos foram atualizados exclusivamente nos campos pós-julgamento judge_session_id, judge_model_requested, judge_calibration_log, judge_result, judge_scores e judge_evidence. Os demais campos foram comparados antes/depois e preservados. Inputs, outputs, logs, infraestrutura e captures tiveram os hashes comparados antes/depois, sem alteração.

A rodada inteira R2 permanece registrada. Eventual revisão futura e nova rodada não corrigem retroativamente esses resultados. O candidato continua CANDIDATE/NOT_ADOPTED e nativo NOT_RUN. Mesmo os seis casos formais aprovados não provam generalização para programação MQL5, instalação, produto ou aceitação humana.
