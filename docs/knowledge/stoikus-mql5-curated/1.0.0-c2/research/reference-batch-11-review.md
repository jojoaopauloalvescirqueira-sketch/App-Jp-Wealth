# REF — lote11: revisão semântica parcial honesta

Leitura integral efetiva do texto extraído das páginas físicas PDF **3239–3430 (192 páginas)** em13 lotes menores que30000caracteres, retornos com max_output_tokens20000 e sem truncamento. **3431–3607 (177p) permanece NÃO LIDO neste registro** por limite de contexto. O fato de os arquivos/lotes restantes já estarem extraídos não constitui leitura.

Fonte: MQL5 Language REFERENCE, MetaQuotes,7284p, SHA256 `9ae05ce748d23ce0de9b230fc6c7093a2af0adc3ce3544244a74e1c7d628d499`. Ledger adjacente guarda hashes originais de texto/linhas JSONL e lista exata de páginas lidas. Originais preservados. Sem conferência visual, compilação MetaEditor, terminal MT5/EX5, conexão Python, benchmark, piloto ou produto/Git. Todo exemplo **MQL_NOT_RUN / PYTHON_MT5_NOT_RUN**.

O texto inclui contratos, parâmetros, retornos, erros, notas, código e resultados documentais. Extração corta lateralmente algumas linhas longas de exemplos; não se reconstruiu o complemento. Artefatos de espaçamento e possíveis erros editoriais são tratados como achados do extraído, ainda sem conferência visual. Paginação indicada é física PDF; nenhum mapeamento impresso adicional foi inferido.

As aplicações são propostas conceituais ao Monitor event-driven que não negocia, descrito no BRIEF; este lote não examinou o código do Stoikus para provar uso de qualquer API. Python/ML permanecem futuros; capacidades de plataforma não autorizam armar Supervisor, negociar ou alterar regras JPW.

## Achados materiais

- Requests SQLite são recursos próprios: Prepare não executa, Read executa; Reset preserva bindings; Finalize/Close invalidam handles. `?1` SQL equivale a índice0 em Bind.
- `Read=false` com5126 é término normal; ausência de tabela e erro operacional exigem distinção. Commit/Rollback também podem falhar.
- Exemplos DEALS→TRADES restringem método simples a hedging. Não generalizar joins por position_id a netting/saídas parciais. Exemplo horário chama `sum(profit)` de líquido sem somar custos: nomenclatura não é regra de PnL JPW.
- Python exige identidade terminal/conta, fusos UTC, limiteMax bars e distinção None versus resultado vazio. Timestamp millisecond repetido não comprova tick duplicado.
- Estimativa de margem ignora posições/pendentes existentes; order_check não garante execução. order_send é capacidade documental de negociação, fora do escopo do Monitor atual.
- DirectX é pipeline gráfico opcional e dependente de hardware; sem uso atual demonstrado.

## Registro por ID

### REF-0001 — MQL5 Reference · [REF, MQL5 Reference, p.PDF 3239–3430]

Contêiner geral; este registro cobre exclusivamente3239–3430, não o livro inteiro.

Aplicação: Contêiner; não duplicar contagem de filhos.

Cobertura: PARTIAL_EXTRACTED_TEXT_READ; seção catalogada 74–7284.

### REF-1033 — Working with databases · [REF, Working with databases, p.PDF 3239–3317]

Trecho3239–3317: SQLite inclui agregações estatísticas (mediana, percentis, variância amostral/populacional) e matemática SQL; conexões, requests, bindings e transações têm ciclos próprios. Introdução3238 não lida.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: PARTIAL_EXTRACTED_TEXT_READ; seção catalogada 3238–3317.

### REF-1034 — DatabaseOpen · [REF, DatabaseOpen, p.PDF 3241–3242]

Abre caminho relativo MQL5\Files; INVALID_HANDLE em falha. Nome vazio/NULL cria temporário em disco; :memory: cria RAM; ambos desaparecem ao fechar. Sem READONLY/READWRITE assume READWRITE; extensão padrão.sqlite; COMMON compartilha pasta de terminais.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3241–3242.

### REF-1035 — DatabaseClose · [REF, DatabaseClose, p.PDF 3243–3243]

Fechar conexão invalida automaticamente todos os handles de requests. Handle inválido sinaliza erro5121; retorno void não é prova de sucesso.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3243–3243.

### REF-1036 — DatabaseImport · [REF, DatabaseImport, p.PDF 3244–3246]

Importa CSV/ZIP; retorna linhas ou-1. Tabela ausente é inferida dos dados, incluindo nomes/tipos. skip_comments é conjunto de caracteres reconhecidos no início da linha, não prefixo literal. APPEND, cabeçalho, aspas, CRLF e pasta comum alteram interpretação.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3244–3246.

### REF-1037 — DatabaseExport · [REF, DatabaseExport, p.PDF 3247–3252]

Exporta tabela ou consulta somente leitura a UTF8; SELECT/select não pode alterar banco. Separador NULL usa tab; vazio transforma saída em strings não reimportáveis como tabela. Aspas duplicam aspas internas e protegem separadores/quebras; sobrescreve por padrão, BOM padrão.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3247–3252.

### REF-1038 — DatabasePrint · [REF, DatabasePrint, p.PDF 3253–3257]

Imprime tabela/consulta no Experts journal com flags para cabeçalho/índice/moldura/alinhamento. Retorna quantidade ou-1; exemplo executa PRAGMA TABLE_INFO e LEFT OUTER JOIN. Nomes CreataTable nas chamadas versus CreateTable nas definições aparecem divergentes no extraído; não copiar sem revisar.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3253–3257.

### REF-1039 — DatabaseTableExists · [REF, DatabaseTableExists, p.PDF 3258–3258]

false pode significar tabela inexistente com5126, conclusão normal; também handle/parâmetro/execução inválidos. Separar ausência esperada de falha operacional.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3258–3258.

### REF-1040 — DatabaseExecute · [REF, DatabaseExecute, p.PDF 3259–3270]

Executa SQL e retorna bool. Exemplo agrega DEALS por símbolo/magic e TRADES por hora; líquido inclui swap/comissão na primeira agregação. Conversão simples DEALS→TRADES é condicionada a hedging; join por position_id não demonstra reconciliação universal de saídas parciais/netting. Exemplo horário chama sum(profit) de net_profit apesar de armazenar custos separadamente: não promover nomenclatura a regra JPW.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3259–3270.

### REF-1041 — DatabasePrepare · [REF, DatabasePrepare, p.PDF 3271–3279]

Prepare valida/compila SQL e produz handle, sem executar; primeira DatabaseRead executa. Parâmetros ?1,?2 suportados. Exemplo lê primeiras dez estruturas e finaliza cada request; mantém ressalva hedging na montagem de trades.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3271–3279.

### REF-1042 — DatabaseReset · [REF, DatabaseReset, p.PDF 3280–3285]

Reset permite reexecução sem recompilar e preserva valores já vinculados; trocar só um parâmetro é possível. Deve anteceder Bind após Read; não aceitar handle finalizado.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3280–3285.

### REF-1043 — DatabaseBind · [REF, DatabaseBind, p.PDF 3286–3290]

Bind usa índice0 enquanto ?N começa em1. Aceita tipos simples; request em execução/concluído exige Reset (5128). Exemplo persiste ticks em transação, mantendo símbolo vinculado uma vez e alterando campos por tick.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3286–3290.

### REF-1044 — DatabaseBindArray · [REF, DatabaseBindArray, p.PDF 3291–3295]

Vincula array como valor de parâmetro, útil BLOB; limite de bytes INT_MAX. Mesma diferença índice0/?1. Assinatura impressa no extraído diz DatabaseBind apesar do título BindArray; exemplo usa DatabaseBindArray e lê arquivos binários.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3291–3295.

### REF-1045 — DatabaseRead · [REF, DatabaseRead, p.PDF 3296–3296]

Read avança registro e executa request; false exige last error:5126 é fim normal, inclusive inserts sem linhas de resultado. Não classificar todo false como erro.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3296–3296.

### REF-1046 — DatabaseReadBind · [REF, DatabaseReadBind, p.PDF 3297–3300]

ReadBind avança e preenche struct só numérica/strings, sem arrays/herança. Campos não podem exceder colunas; struct menor permite leitura parcial e restante via ColumnXXX. Exemplo soma125000 e média31250 de quatro salários; resultado é exemplo documental.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3297–3300.

### REF-1047 — DatabaseFinalize · [REF, DatabaseFinalize, p.PDF 3301–3301]

Finalize remove request criado por Prepare; void, handle inválido produz5121. Não reutilizar handle finalizado.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3301–3301.

### REF-1048 — DatabaseTransactionBegin · [REF, DatabaseTransactionBegin, p.PDF 3302–3306]

Begin inicia unidade de transação; fechar com Commit no sucesso ou Rollback em erro. Exemplo compara2737 inserts:48.5ms versus25818.9ms e532.8x; números pertencem ao exemplo, não benchmark Stoikus.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3302–3306.

### REF-1049 — DatabaseTransactionCommit · [REF, DatabaseTransactionCommit, p.PDF 3307–3307]

Commit conclui alterações desde Begin e retorna bool; checar falha própria. Nota usa nome DatabaseBeginTransaction, divergente da API titulada TransactionBegin.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3307–3307.

### REF-1050 — DatabaseTransactionRollback · [REF, DatabaseTransactionRollback, p.PDF 3308–3308]

Rollback cancela alterações desde Begin em falha; também retorna bool que pode falhar. Registrar falha da recuperação separadamente.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3308–3308.

### REF-1051 — DatabaseColumnsCount · [REF, DatabaseColumnsCount, p.PDF 3309–3309]

ColumnsCount retorna número ou-1 e pode ser chamado antes de Read, exceção aos demais ColumnXXX.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3309–3309.

### REF-1052 — DatabaseColumnName · [REF, DatabaseColumnName, p.PDF 3310–3310]

ColumnName usa índice0..count-1; documentação exige ao menos uma chamada Read. Saída string por referência e bool de sucesso.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3310–3310.

### REF-1053 — DatabaseColumnType · [REF, DatabaseColumnType, p.PDF 3311–3311]

ColumnType retorna INTEGER/FLOAT/TEXT/BLOB/NULL ou INVALID; exige Read prévio. NULL é tipo explícito, não zero econômico.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3311–3311.

### REF-1054 — DatabaseColumnSize · [REF, DatabaseColumnSize, p.PDF 3312–3312]

ColumnSize retorna bytes ou-1; exige Read e índice válido. Dimensionar BLOB sem confundir bytes com elementos.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3312–3312.

### REF-1055 — DatabaseColumnText · [REF, DatabaseColumnText, p.PDF 3313–3313]

ColumnText preenche string por referência no registro corrente; para próximo chamar Read. Verificar bool antes de usar saída.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3313–3313.

### REF-1056 — DatabaseColumnInteger · [REF, DatabaseColumnInteger, p.PDF 3314–3314]

ColumnInteger preenche int por referência; contrato de índice e Read prévio. Não estreitar tickets longos por conveniência.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3314–3314.

### REF-1057 — DatabaseColumnLong · [REF, DatabaseColumnLong, p.PDF 3315–3315]

ColumnLong preserva campo long por referência; mesmo contrato do registro corrente e checagem bool.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3315–3315.

### REF-1058 — DatabaseColumnDouble · [REF, DatabaseColumnDouble, p.PDF 3316–3316]

ColumnDouble preenche double por referência, após Read; bool distingue falha de valor zero válido.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3316–3316.

### REF-1059 — DatabaseColumnBlob · [REF, DatabaseColumnBlob, p.PDF 3317–3317]

ColumnBlob retorna campo como array por referência; consultar tamanho/tipo e Read primeiro. Não é serialização de objeto arbitrário.

Aplicação: Proposta de persistência/auditoria SQLite; nenhuma chamada presente do produto foi verificada. Testar contratos/erros e recuperação em candidato isolado antes de adoção.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3317–3317.

### REF-1060 — Working with DirectX · [REF, Working with DirectX, p.PDF 3318–3346]

DirectX11/Shader Model5 exigem GPU compatível; contexto, buffers, shaders e inputs formam pipeline3D. Recursos só valem no contexto criador e requerem liberação explícita.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3318–3346.

### REF-1061 — DXContextCreate · [REF, DXContextCreate, p.PDF 3320–3320]

Create retorna contexto dimensionado em pixels ou INVALID_HANDLE. Objetos criados pertencem exclusivamente ao contexto; liberar com DXRelease.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3320–3320.

### REF-1062 — DXContextSetSize · [REF, DXContextSetSize, p.PDF 3321–3321]

SetSize altera largura/altura somente entre renderizações de frames; bool requer checagem.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3321–3321.

### REF-1063 — DXContextGetSize · [REF, DXContextGetSize, p.PDF 3322–3322]

GetSize devolve dimensões por referência; distinguir getter do SetSize duplicado no quadro introdutório.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3322–3322.

### REF-1064 — DXContextClearColors · [REF, DXContextClearColors, p.PDF 3323–3323]

ClearColors preenche buffer de render com DXVector de cor; útil limpar antes do frame seguinte.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3323–3323.

### REF-1065 — DXContextClearDepth · [REF, DXContextClearDepth, p.PDF 3324–3324]

ClearDepth limpa buffer de profundidade antes do frame; checar bool.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3324–3324.

### REF-1066 — DXContextGetColors · [REF, DXContextGetColors, p.PDF 3325–3325]

GetColors recorta imagem com largura/altura/offset e devolve pixels uint ARGB; tamanho resultante é largura×altura.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3325–3325.

### REF-1067 — DXContextGetDepth · [REF, DXContextGetDepth, p.PDF 3326–3326]

GetDepth fornece array float com profundidade relativa0..1 por pixel, não distância financeira/física.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3326–3326.

### REF-1068 — DXBufferCreate · [REF, DXBufferCreate, p.PDF 3327–3327]

BufferCreate distingue vertex e index; index exige uint[], vertex array de estruturas. start/count selecionam elementos; liberar handle.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3327–3327.

### REF-1069 — DXTextureCreate · [REF, DXTextureCreate, p.PDF 3328–3333]

TextureCreate recorta retângulo de imagem conforme formato DX; tabela mapeia formatos DXGI, de floats/inteiros a UNORM/SRGB, compressão BC e vídeo. Formato determina interpretação dos bytes; não intercambiar layouts.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3328–3333.

### REF-1070 — DXInputCreate · [REF, DXInputCreate, p.PDF 3334–3334]

InputCreate aloca inputs de shader pelo tamanho em bytes da estrutura; retorna handle a liberar.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3334–3334.

### REF-1071 — DXInputSet · [REF, DXInputSet, p.PDF 3335–3335]

InputSet escreve dados em handle criado por InputCreate; não é handle do contexto, apesar do comentário resumido da assinatura.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3335–3335.

### REF-1072 — DXShaderCreate · [REF, DXShaderCreate, p.PDF 3336–3336]

ShaderCreate compila HLSL5 por source/entry_point, retorna handle ouINVALID e texto compile_error. Há vertex, geometry e pixel; não prova compilação realizada aqui.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3336–3336.

### REF-1073 — DXShaderSetLayout · [REF, DXShaderSetLayout, p.PDF 3337–3337]

Layout associa semantic_name/index e formato de cada campo; deve coincidir com estrutura do vertex buffer e entrada HLSL.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3337–3337.

### REF-1074 — DXShaderInputsSet · [REF, DXShaderInputsSet, p.PDF 3338–3338]

ShaderInputsSet recebe handles; quantidade deve coincidir com cbuffer declarados no shader.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3338–3338.

### REF-1075 — DXShaderTexturesSet · [REF, DXShaderTexturesSet, p.PDF 3339–3339]

ShaderTexturesSet recebe handles de textura; quantidade deve coincidir com objetos Texture2D declarados.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3339–3339.

### REF-1076 — DXDraw · [REF, DXDraw, p.PDF 3340–3340]

Draw renderiza faixa de vertices do buffer previamente ligado; shaders devem estar definidos antes.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3340–3340.

### REF-1077 — DXDrawIndexed · [REF, DXDrawIndexed, p.PDF 3341–3341]

DrawIndexed usa primitivas descritas por index buffer, vertex buffer/shaders previamente ligados e topologia definida.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3341–3341.

### REF-1078 — DXPrimiveTopologySet · [REF, DXPrimiveTopologySet, p.PDF 3342–3342]

PrimiveTopologySet (grafia da API) escolhe pontos, listas/tiras de linhas/triângulos e variantes adjacency; não mudar contagem sem considerar topologia.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3342–3342.

### REF-1079 — DXBufferSet · [REF, DXBufferSet, p.PDF 3343–3343]

BufferSet liga buffer vertex/index ao contexto e faixa start/count usada na renderização.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3343–3343.

### REF-1080 — DXShaderSet · [REF, DXShaderSet, p.PDF 3344–3344]

ShaderSet liga shader; vertex, geometry e pixel podem coexistir no pipeline.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3344–3344.

### REF-1081 — DXHandleType · [REF, DXHandleType, p.PDF 3345–3345]

HandleType distingue INVALID, CONTEXT, SHADER, BUFFER, INPUT e TEXTURE; ajuda diagnosticar ciclo de recursos.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3345–3345.

### REF-1082 — DXRelease · [REF, DXRelease, p.PDF 3346–3346]

Release libera handle não usado explicitamente; bool e GetLastError devem ser observados.

Aplicação: Sem uso atual demonstrado no Monitor; visualização3D opcional futura, sem requisito financeiro ou de execução.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3346–3346.

### REF-1083 — Python Integration · [REF, Python Integration, p.PDF 3347–3430]

Integração Python usa comunicação entre processos com terminal; pacote MetaTrader5 expõe dados e ações de negociação. Exemplo Windows/Python3.8 e versões2020 é histórico documental; não instalação atual validada. Capítulo continua3431–3437 ainda não lido.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: PARTIAL_EXTRACTED_TEXT_READ; seção catalogada 3347–3437.

### REF-1084 — initialize · [REF, initialize, p.PDF 3353–3354]

initialize pode localizar terminal, receber caminho EXE e login/password/server/timeout/portable. Sem login usa última conta; pode iniciar terminal. True só confirma conexão com terminal, não identidade pretendida nem execução de trade.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3353–3354.

### REF-1085 — login · [REF, login, p.PDF 3355–3357]

login conecta conta especificada; credenciais/servidor omitidos podem vir do banco do terminal. Timeout padrão60000ms pode gerar exceção. Verificar conta/servidor após conexão, não usar credenciais de exemplos.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3355–3357.

### REF-1086 — shutdown · [REF, shutdown, p.PDF 3358–3358]

shutdown encerra conexão previamente estabelecida, sem retorno. Proposta: cleanup em finally para pesquisa futura.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3358–3358.

### REF-1087 — version · [REF, version, p.PDF 3359–3360]

version retorna tupla versão/build/data do terminal ouNone; distinta da versão do pacote Python. Registrar ambas em evidência reproduzível.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3359–3360.

### REF-1088 — last_error · [REF, last_error, p.PDF 3361–3362]

last_error usa códigos próprios da biblioteca, não enumeração GetLastError MQL: sucesso1; erros negativos, incluindo IPC/timeout/autotrading. INIT e CONNECT aparecem com mesmo-10003 no extraído.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3361–3362.

### REF-1089 — account_info · [REF, account_info, p.PDF 3363–3365]

account_info retorna namedtuple consolidando propriedades conta ouNone. Campos balance/equity/profit/margin/currency/margin_mode ajudam contextualizar snapshot, sem inferir regra de risco JPW.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3363–3365.

### REF-1090 — terminal_info · [REF, terminal_info, p.PDF 3366–3368]

terminal_info retorna namedtuple/None com connected, trade_allowed, tradeapi_disabled, build, maxbars, paths e outros. Nota repete TerminalInfoDouble; exemplo de saída não é estado deste ambiente.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3366–3368.

### REF-1091 — symbols_total · [REF, symbols_total, p.PDF 3369–3369]

symbols_total inclui todos símbolos, customizados e desabilitados em MarketWatch; quantidade não é universo negociável selecionado.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3369–3369.

### REF-1092 — symbols_get · [REF, symbols_get, p.PDF 3370–3372]

symbols_get retorna tupla ouNone; filtro group com* e! aplica inclusão antes de exclusão, em sequência. Diferenciar resultado vazio válido de erro.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3370–3372.

### REF-1093 — symbol_info · [REF, symbol_info, p.PDF 3373–3376]

symbol_info consolida propriedades numéricas/textuais; exemplo mostra tick_value_profit/loss distintos, point/tick_size/volume_step e currencies. Não hardcode propriedades de EURJPY do exemplo.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3373–3376.

### REF-1094 — symbol_info_tick · [REF, symbol_info_tick, p.PDF 3377–3378]

symbol_info_tick devolve último tick ouNone, comtime/time_msc/flags/bid/ask/last/volume; presença não demonstra frescor nem Last negociado quando é0.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3377–3378.

### REF-1095 — symbol_select · [REF, symbol_select, p.PDF 3379–3382]

symbol_select altera MarketWatch; remoção bloqueada se há gráficos abertos/posições. Não tratar chamada como consulta inofensiva em pesquisa só leitura.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3379–3382.

### REF-1096 — market_book_add · [REF, market_book_add, p.PDF 3383–3383]

market_book_add assina mudanças DOM por símbolo e retorna bool; requer pareamento de release.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3383–3383.

### REF-1097 — market_book_get · [REF, market_book_get, p.PDF 3384–3386]

market_book_get exige assinatura prévia e retorna tupla BookInfo ouNone; tipo/preço/volume em lotes. Exemplo consulta10 vezes com pausa5s, não captura garantida de todo evento.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3384–3386.

### REF-1098 — market_book_release · [REF, market_book_release, p.PDF 3387–3387]

market_book_release cancela assinatura DOM do símbolo e retorna bool; assegurar limpeza mesmo após erro.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3387–3387.

### REF-1099 — copy_rates_from · [REF, copy_rates_from, p.PDF 3388–3391]

copy_rates_from retorna numpy estruturado ouNone; barras com abertura<=data pedida, limitado ao histórico/Max bars in chart. Datas devem ser UTC conscientes. Tabela extraída duplica M12 na linha15min: não perpetuar sem conferir original/API.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3388–3391.

### REF-1100 — copy_rates_from_pos · [REF, copy_rates_from_pos, p.PDF 3392–3394]

copy_rates_from_pos índice0 é barra corrente e cresce ao passado; retorno contém OHLC/tick_volume/spread/real_volume. Limite de histórico é do terminal; barra0 não deve ser tratada como fechada.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3392–3394.

### REF-1101 — copy_rates_range · [REF, copy_rates_range, p.PDF 3395–3397]

copy_rates_range inclui aberturas>=from e<=to; normalizar UTC e verificar cobertura real/limiteMax bars. Não assumir quantidade requerida equivale a dados disponíveis.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3395–3397.

### REF-1102 — copy_ticks_from · [REF, copy_ticks_from, p.PDF 3398–3400]

copy_ticks_from recebe símbolo/data/contagem/filtroINFO,TRADE,ALL e retorna numpy ouNone. Flags descrevem alterações; preservar time_msc e volume_real mostrados no resultado, não só resumo textual de colunas.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3398–3400.

### REF-1103 — copy_ticks_range · [REF, copy_ticks_range, p.PDF 3401–3403]

copy_ticks_range usa intervalo e filtros de ticks; contrato exige UTC e alerta para apresentação com offset local. Exemplo possui ticks distintos com mesmo time_msc, logo timestamp sozinho não prova duplicação.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3401–3403.

### REF-1104 — orders_total · [REF, orders_total, p.PDF 3404–3404]

orders_total conta ordens ativas; não confundir com posições. Exemplo<=0 imprime ausência, mas código de pesquisa precisa tratar falha conforme contrato observado.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3404–3404.

### REF-1105 — orders_get · [REF, orders_get, p.PDF 3405–3407]

orders_get filtra por symbol/group/ticket; symbol faz ignorar ticket. None é erro; tupla vazia deve ser tratada antes de acessar[0] como faz o exemplo de DataFrame.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3405–3407.

### REF-1106 — order_calc_margin · [REF, order_calc_margin, p.PDF 3408–3410]

order_calc_margin estima margem na moeda da conta sem considerar ordens pendentes/posições correntes. Não é margem incremental da carteira nem verificação de regra de limite JPW.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3408–3410.

### REF-1107 — order_calc_profit · [REF, order_calc_profit, p.PDF 3411–3413]

order_calc_profit estima BUY/SELL entre preços na moeda da conta no ambiente atual; resultado não é PnL líquido garantido. Exemplos mostram assimetria BUY/SELL USDJPY por conversão, não tabela universal de pontos.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3411–3413.

### REF-1108 — order_check · [REF, order_check, p.PDF 3414–3417]

order_check retorna estrutura de checagem, não garantia de execução. Documenta ações/filling/expiração; tabela RETURN afirma Market/Exchange neste trecho: resolver compatibilidade com capítulo de trade antes de usar, não assumir política universal.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3414–3417.

### REF-1109 — order_send · [REF, order_send, p.PDF 3418–3422]

order_send envia ação ao servidor e retorna MqlTradeResult, com request e retcode. Identificar position no fechamento; price omitido para Market Execution/DEAL conforme contrato. Aceitação/verificação em etapas não garante execução; exemplo abre e fecha e é exclusivamente NOT_RUN.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3418–3422.

### REF-1110 — positions_total · [REF, positions_total, p.PDF 3423–3423]

positions_total conta posições abertas, separado de ordens. Consulta seria proposta Python futura, não evidência de bridge presente.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3423–3423.

### REF-1111 — positions_get · [REF, positions_get, p.PDF 3424–3426]

positions_get retorna posições filtradas; symbol ignora ticket. None é erro e len0 é ausência válida; filtros group sequenciais. Preservar ticket e identifier sem tratá-los sempre iguais.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3424–3426.

### REF-1112 — history_orders_total · [REF, history_orders_total, p.PDF 3427–3428]

history_orders_total conta histórico por intervalo com datetime/epoch; resultado não é deals. Exemplo usa datetime local ingênuo apesar de alertas UTC dos capítulos de dados; projetar pesquisa futura com fuso explícito.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: FULL_EXTRACTED_TEXT_READ; seção catalogada 3427–3428.

### REF-1113 — history_orders_get · [REF, history_orders_get, p.PDF 3429–3430]

Leitura parcial3429–3430: history_orders_get admite intervalo+group, ticket ou position (ORDER_POSITION_ID), retorna namedtuple/None e aplica filtros sequenciais. Exemplo continua3431, ainda não lido. Não declarar cobertura integral deste ID.

Aplicação: Proposta Python futura; BRIEF declara ausência atual de ML/bridge. Sem instalação/conexão/negociação autorizada ou executada neste estudo.

Cobertura: PARTIAL_EXTRACTED_TEXT_READ; seção catalogada 3429–3431.
