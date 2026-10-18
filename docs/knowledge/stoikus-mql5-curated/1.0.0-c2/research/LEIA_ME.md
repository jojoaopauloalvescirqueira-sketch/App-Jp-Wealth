# Fontes, método e cobertura

Os originais são REF (*MQL5 Language REFERENCE*, 7.284 páginas), TRD (*MQL5 Programming for Traders*, 2.047) e NN (*Neural Networks for Algorithmic Trading with MQL5*, 690). O manifesto `source-manifest.json` contém tamanho, SHA-256, metadados e resultado da extração por página. As edições locais e as consultas oficiais posteriores são fontes distintas. Não há substituição dos PDFs pela documentação online.

## Como verificar a pesquisa

1. Confira o PDF e seu hash no manifesto. A pasta original não foi alterada.
2. Encontre o assunto em `section-catalog.jsonl`: cada entrada tem ID estável desta pesquisa, título, profundidade e páginas físicas inicial/final.
3. Consulte `coverage-matrix.jsonl` e `coverage-summary.json`. A matriz calcula cobertura textual por união de páginas explicitamente lidas. Não credita a abertura de uma família a todos os seus descendentes, não soma sobreposições duas vezes e não converte extração em leitura.
4. Abra os arquivos `*-review.md` e respectivos `*-coverage.json`. Eles registram conhecimento, aplicação conceitual, proposta ou ausência de uso atual, método, páginas realmente lidas, hashes e limites. IDs, títulos e faixas permitem retornar ao original.
5. Confira o recibo visual e as contraprovas quando a conclusão depender de fórmula, figura ou código. Leitura de texto não certifica um gráfico invisível na extração ou um exemplo executável.

`page-inventory.jsonl.gz` contém as 10.021 identidades textuais, contagens e estados por página, sem incluir o texto integral dos livros. `pagination-map.json` compara numeração física e números extraídos: REF pelo início da página, TRD/NN pelo rodapé. Uma numeração não detectada permanece desconhecida; o método não é auditoria visual de todas as páginas.

## Etapas e limites

O conteúdo foi extraído por Poppler em modo layout, página por página, incluindo código e tabelas como texto. Leituras semânticas foram feitas em lotes de texto integral, com análise específica e registros por pesquisador. Os limites dos lotes e reparos de respostas truncadas permanecem nos ledgers. Há exceções documentadas de lote ligeiramente maior que o alvo de 30 mil caracteres. Preparar um arquivo ou índice não conta como exibi-lo e analisá-lo.

Os registros iniciais são deliberadamente conservados. Alguns declaram PENDING ou NOT_READ para páginas posteriormente lidas por outro pesquisador; isso não os torna incorretos retrospectivamente. Para a cobertura agregada consulte a união mais recente, seguindo seus hashes para os registros originais. Para a profundidade de uma interpretação consulte as notas correspondentes. União de páginas é uma conferência de rastreabilidade, não uma segunda leitura independente integral.

Algumas linhas extensas de código foram cortadas lateralmente pela edição ou pela extração. Títulos e exemplos têm inconsistências documentadas: retorno narrado diferente do protótipo, nomes copiados de outra função ou exemplos didáticos permissivos. As notas não reconstroem caracteres ausentes por suposição e não transformam essas anomalias bibliográficas em bugs comprovados do Stoikus. A conferência visual dirigida está em `validation/source-visual-review.json`, fora desta pasta. Exemplos dos livros e novos trechos MQL conservam NOT_RUN/NOT_COMPILED quando aplicável.

A aplicação ao Stoikus significa pertinência conceitual à arquitetura examinada, salvo indicação de arquivo e comportamento efetivamente observados. A documentação de uma capacidade como WebRequest, Python, OpenCL, ONNX, sinal ou operação de mercado não prova que o produto a utiliza nem autoriza ativá-la. Os anexos preservam a distinção entre contrato da plataforma, código observado, regra JP Wealth e proposta do estudo.

## Organização dos anexos

- `engineering-notes.md` e `engineering-coverage.json`: análise focal inicial de MQL5, integração e fluxo do produto; cobertura inicial não extrapolada.
- `trd-*-review.md`: complementos que cobrem programação básica, tipos/classes, arquivos, aplicações, gráficos, trading/tester, integrações e conclusão.
- `neural-notes.md`, `nn-*-review.md`: fundamentos, camadas densas, gradientes, OpenCL, CNN, LSTM, atenção/GPT, normalização/dropout, dados e avaliação. Nem todo arquivo inicial de leitura é uma leitura de corpo integral.
- `reference-batch-*-review.md`: leitura sequencial da referência da linguagem e biblioteca padrão. Sufixos de continuação mantêm as entregas parciais anteriores intactas.
- `critical-synthesis.md`: decisões e propostas comparadas pelo benefício, custo, risco, dependências e prova.
- `official-sources.json`: páginas oficiais consultadas posteriormente, data e âmbito; divergências são registradas separadamente.

Consultas adicionais oficiais presentes nas notas de TRD final tratam `initialize`, `last_error` e `copy_rates_from` em Python. Os exemplos dessas APIs não foram conectados ao terminal. O manual concentra as fontes online necessárias à sua argumentação; a pesquisa registra as demais consultas nos ledgers próprios.

O corpus privado de extração e os lotes brutos ficam no diretório de trabalho registrado nos recibos. Os anexos entregues incluem notas autorais, hashes e localizadores. Não distribuem cópias completas ou extrações integrais dos três livros.
