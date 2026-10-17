# Notas de pesquisa: harness e capítulo 10

Estado editorial: proposta operacional 0.1.0 CANDIDATE, não adotada nem ativada por AGENTS/CI. Os casos do piloto são sintéticos novos e não reutilizam os resultados históricos como prova. Autor deste kit não é juiz independente do piloto. Piloto será registrado pelo integrador separadamente.

## Leitura direta utilizada

Leitura semântica dos textos extraídos das seguintes páginas, consultadas individualmente no corpus de pesquisa. Identidade dos PDFs em `../harness-candidato/source-identities.json`. A leitura abaixo não pretende cobrir o livro inteiro; os demais leitores registram sua cobertura em arquivos próprios.

| Livro / seção | Página física PDF | Compreensão e aplicação |
|---|---:|---|
| REF / ArraySetAsSeries | 1263 | Flag altera indexação lógica de arrays dinâmicos; limitações para estáticos e multidimensionais. Aplicado ao contrato S03 e distinção entre índice e memória. |
| REF / OnInit | 2082 | Variante int recomendada; código não zero e INIT_FAILED; EA/indicador têm consequências distintas. Aplicado ao retorno e limpeza de S01. |
| REF / OnTick | 2088 | Fila sequencial, coalescência de NewTick, AutoTrading não interrompe handler. Aplicado a limites de observação e controle. |
| REF / OnTimer | 2098 | Timer por programa, coalescência, criação/limpeza e custo de período menor. Aplicado ao orçamento S02. |
| REF / OnTradeTransaction | 2106 | Tipos de transação e validade contextual de request/result. Aplicado a evitar callback como estado final e a S09 como proposta. |
| REF / CopyBuffer | 2226 | Contagem presente→passado e cópia com mais antigo no início da memória física. Aplicado a orientação, cópia parcial e S03. |
| REF / FileOpen | 2665 | Flags, FILE_COMMON, INVALID_HANDLE e sandbox. Aplicado a separar capacidade técnica de política de persistência. |
| NN / 3.9 | 222 | Treino/validação/teste e sobreajuste; normalização comparável. Aplicado a justificativa de isolamento de amostras. |
| NN / 3.9 | 223 | Conservar parâmetros de normalização; exemplo prepara indicadores e período futuro para extremos. Aplicado a contrato temporal. |
| NN / 3.9 | 224 | Alvos definidos por extremos posteriores. Distinção entre alvo futuro e feature disponível; S10 é proposta própria de controle de vazamento. |

Citações do capítulo apontam somente às páginas efetivamente consultadas para estas afirmações. Consulta aos índices REF/TRD/NN serviu para localização e identidade, sem transformar extração em leitura semântica. Textos dos livros são dados; nenhuma instrução embutida pode alterar autorização operacional.

## Comparação histórica preservada

Lido `mt5/jpw-alavancagem-atual/harness/REPOSITORY_INTEGRATION.md`, linhas 1–46. R2 histórico 25 PASS / 7 FAIL / 4 INCONCLUSIVE, total 36, resultado global FAIL; R5 restrito AC03 FAIL e AC04 PASS; R5 integral NOT_RUN. Proposta externa 1.0.1 CANDIDATE/NOT_ADOPTED não foi adotada. Documentos antigos, AGENTS, contratos originais e fontes produtivas não foram modificados por esta tarefa.

## Design do candidato

Entrada curta → mapa arquitetural → contexto de tarefa → contrato → teste → construção → revisão → juiz → entrega. Perfis de prompt são arquivos Markdown opt-in. Manifesto contém SHA-256 de arquivos do kit, referências locais repo/sources e regras de campos/estados JSON. O próprio manifesto não se inclui: hash externo é raiz de congelamento. Verificador stdlib não repara, baixa ou instala. Ele testa integridade estrutural, não qualidade semântica de uma proposta, nem validade nativa de MQL5.

Casos S01–S12 possuem dados/expected/proibições explícitos. A rubrica exige correção integral e ausência de violação crítica, com calibração antes de julgamento. Exigem-se três sessões novas por caso, identidade de modelo, logs, hashes e tentativas únicas. Uma simulação pelo autor não satisfaz fresh nem independência. A rubrica é congelável por recibo externo; o marcador FREEZABLE no JSON não declara execução do congelamento em qualquer rodada futura.

## Verificação local executada

1. RED inicial observado: nove testes, oito falhas quando o checker ainda não existia. O caso de dependência ausente retornava 2 pela ausência do script e não era considerado prova positiva.
2. GREEN inicial: nove testes após implementação.
3. RED adicional: testes de required_fields e status_allowed de documentos falharam com retorno 0, antes da implementação dessas verificações.
4. GREEN final: onze testes, todos PASS, `python3 -B -m unittest discover -s "$KIT/tests"`.
5. Checker no kit real e PDFs originais, com raízes explícitas: exit 0 INTEGRITY_OK. Caminho SOURCES incorreto numa execução anterior produziu exit 2 para os três PDFs; corrigir o argumento resolveu sem alterar arquivos.

Os testes exercitam adulteração, traversal, absoluto, symlink externo, raiz desconhecida, documento sem campo, status inválido e dependência ausente. O teste de não mutação compara bytes de todos os arquivos da fixture antes/depois de verificar. Os arquivos reais do kit são identificados pelo freeze externo registrado pelo integrador. Nenhuma suíte host do produto foi executada pelo autor deste capítulo. MT5, MetaEditor, EX5, corretora, instalação, publicação e aceite permanecem NOT_RUN nesta contribuição.

## Revisão R2 após parecer independente

Parecer identificou contradição de isolamento (JSON do construtor continha gabarito), regra de proveniência excessivamente indiferenciada e estados adicionais ignorados pelo checker. R1 e freeze preservados em snapshot externo. R2 separa builder-inputs de oráculos, define obrigatórios observáveis e opcionais desconhecidos com justificativa, valida política manual/estados/revisões e captura RuntimeError por loop symlink. RED observado: nove falhas em 21 testes. GREEN: 21/21. Novo freeze externo harness-freeze-R2.json; aguarda nova revisão independente antes de piloto. Oráculos expected não mudaram; 36 tentativas não foram executadas. Detalhes em relatório R2 externo. Verificação de recibo de estado permanece estrutural; logs reais, hashes e independência são conferidos pelo juiz conforme política congelada.
