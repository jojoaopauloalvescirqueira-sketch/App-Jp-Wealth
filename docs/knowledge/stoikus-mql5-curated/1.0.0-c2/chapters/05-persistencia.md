# 5. Persistência, publicação e integridade dos dados

## 5.1 Quatro problemas que não cabem na palavra salvar

Persistência mantém informações entre execuções; publicação torna uma fotografia disponível a consumidores; coordenação decide quem pode alterá-la; recuperação reconstrói uma situação utilizável após interrupção. Um único arquivo pode participar dos quatro problemas, mas isso não os torna equivalentes. Conseguir escrever bytes não comprova identidade da conta, integridade do conjunto ou exclusividade do produtor. Da mesma forma, um leitor encontrar um número não demonstra que a publicação ainda é atual.

No Stoikus, a diferença é relevante porque convivem preferências visuais, estudos, histórico pessoal, contabilidade e publicações transitórias do núcleo. O README atual identifica preferências separadas e versionadas, rascunhos em memória e histórico preservado. O conteúdo desta pesquisa explica mecanismos e critérios de análise; não altera schemas, chaves, bancos ou política de gravação. Os exemplos usam identidades fictícias e não constituem migração ou correção autorizada do produto.

A primeira pergunta para qualquer estado é sua duração pretendida. Um rascunho pode durar a sessão; uma preferência precisa sobreviver à reabertura; a existência de um produtor precisa ser reavaliada após reinício; um registro histórico precisa manter proveniência e compatibilidade. Salvar todos esses objetos da mesma maneira costuma produzir erros opostos: perde-se o que deveria durar e restaura-se como atual o que deveria ter expirado.

## 5.2 A sandbox faz parte da identidade do arquivo

As operações de arquivos MQL5 trabalham dentro de uma sandbox. O nome informado a `FileOpen` é relativo à área apropriada, e não um caminho absoluto arbitrário. No terminal, a base normal é `MQL5/Files`; no teste, corresponde à área do agente. A opção `FILE_COMMON` seleciona a pasta comum dos terminais locais. Assim, o mesmo nome relativo pode representar arquivos distintos em dois contextos. [REF, FileOpen, p.PDF 2665–2667; TRD, sec. 4.5, p.PDF 404–405]

O escopo comum merece cuidado. Ele permite comunicação, mas também amplia o conjunto de processos capazes de alcançar o mesmo objeto. Uma fixture chamada simplesmente `state.csv` pode colidir com outra sessão. A proposta de ensaio deve reservar um diretório identificado por execução, componente e cenário, preservando os dados produtivos fora desse namespace. Usar `FILE_COMMON` não cria isolamento automático, transação ou garantia de que apenas um terminal será escritor.

`FileOpen` retorna um handle ou `INVALID_HANDLE`. Esse handle é uma referência do contexto que o abriu, não uma chave transportável para outro programa. O leitor abre sua própria referência ao arquivo compartilhado. A distinção entre nome durável e handle temporário ajuda também na limpeza: depois de fechar, a variável não deve continuar sendo tratada como recurso válido. A atribuição de uma sentinela inválida documenta o fim da aquisição. [TRD, sec. 4.5.3, p.PDF 414–415]

Há uma escolha de flags com efeito particularmente destrutivo: abrir apenas com `FILE_WRITE` pode truncar conteúdo existente. `FILE_READ|FILE_WRITE` preserva o arquivo, mas anexar exige ainda posicionar o cursor no final. Uma revisão deve verificar a combinação completa e o posicionamento, em vez de inferir append pelo nome da função chamadora. Para pesquisas e testes, isso exige caminhos sintéticos e controlados; não se experimenta o comportamento sobre um histórico real. [TRD, sec. 4.5.3, p.PDF 414]

## 5.3 Formato, unidades e compatibilidade

Arquivos de texto facilitam inspeção e intercâmbio; formatos binários podem ser compactos e preservar representações específicas. Nenhum deles se valida sozinho. Um bloco binário com comprimento divisível pelo tamanho de uma estrutura pode continuar semanticamente errado: outra estrutura pode ter o mesmo tamanho, ou registros antigos podem usar outra disposição. O livro demonstra que sucesso mecânico de leitura não estabelece que o conteúdo represente o tipo esperado. [TRD, sec. 4.5.1 e 4.5.3, p.PDF 406–407 e 412]

Um contrato de armazenamento precisa identificar versão, tipos, limites, unidades e significado de ausência. Se um campo representa moeda da conta, não deve virar percentual por interpretação da interface. Se um registro contém preço de um símbolo, casas decimais não substituem a identidade do instrumento. Um campo desconhecido ou uma versão futura não deve ser convertido silenciosamente para o formato atual. Recusar, preservar a origem e comunicar incompatibilidade pode ser a resposta correta.

Texto acrescenta questões de codificação, separadores e conversão. A referência exige `FILE_ANSI` quando a leitura deve usar uma codepage específica; sem ele, o arquivo é tratado como Unicode sem aquela conversão. `FILE_CSV` também não significa necessariamente vírgula: o delimitador padrão documentado é tabulação. O nome do formato não dispensa especificação de encoding e delimitador no contrato de exportação. [REF, FileOpen, p.PDF 2665–2666]

Um teste de ida e volta deve incluir acentos, campos vazios, valores iguais a zero, valores indisponíveis e identificadores extensos. A comparação verifica significado, não apenas se o segundo arquivo abre. Se o formato admite ordenação diferente, a comparação deve usar identidades e campos; se a ordem é significativa, deve preservá-la. A especificação do próprio formato decide essa escolha. Esta pesquisa não define um novo formato canônico do Stoikus.

## 5.4 Buffer não é confirmação do conjunto

O sistema mantém buffers de entrada e saída para reduzir operações físicas. `FileFlush(handle)` força a escrita dos dados pendentes daquele arquivo; `FileClose` também descarrega o buffer ao fechar. A chamada frequente de flush pode prejudicar desempenho. Essa função responde à pergunta sobre envio do buffer, não à pergunta sobre validade de todos os registros do documento. [REF, FileFlush, p.PDF 2676–2677; TRD, sec. 4.5.12, p.PDF 465–466]

Considere uma publicação composta por cabeçalho e cem registros. Se o leitor abre durante a gravação, encontrar um cabeçalho válido e os primeiros vinte registros não demonstra que a publicação foi concluída. Se o produtor falha no registro seguinte, a fotografia parcial continua sendo parcial mesmo que cada bloco anterior tenha passado por flush. A revisão precisa entender como o contrato distingue conjunto pronto, incompleto e anterior. Não é correto anunciar atomicidade só porque existe uma etapa chamada salvar.

Como proposta didática, um protocolo pode separar preparação, validação e anúncio de disponibilidade, identificando a geração publicada. O leitor só aceita uma geração que cumpra o contrato completo; o produtor conserva a anterior quando a nova falha. Os mecanismos concretos dependem das APIs e do formato existentes e exigem testes de falha. O diagrama abaixo expressa a obrigação lógica, sem afirmar que renomeação, cópia ou qualquer chamada isolada ofereça garantia atômica universal.

```mermaid
flowchart LR
    A[Preparar geração nova] --> B[Gravar dados]
    B --> C[Conferir conjunto e identidade]
    C --> D{Concluído?}
    D -->|sim| E[Anunciar geração utilizável]
    D -->|não| F[Preservar anterior e motivo]
```

Um ensaio de interrupção deve escolher pontos concretos: antes de abrir, após o cabeçalho, no meio dos registros e antes do anúncio final. O resultado esperado é derivado do contrato do leitor. A ausência de crash não basta; é preciso verificar se o consumidor recusou a geração incompleta e se o original permaneceu recuperável.

## 5.5 Variáveis globais do terminal e coordenação

Variáveis globais do terminal são objetos compartilhados diferentes das globais declaradas no programa. Armazenam `double`, possuem nomes e podem ser acessadas pelos programas do terminal. Não ficam automaticamente associadas à conta ou ao perfil. As persistentes podem sobreviver à sessão e expiram após quatro semanas sem uso conforme as condições documentadas; as temporárias existem apenas durante a execução do terminal. [TRD, sec. 4.6–4.6.1, p.PDF 482–484; REF, GlobalVariableTemp, p.PDF 2640]

O nome, portanto, participa do contrato. Se uma informação depende de conta, instalação, componente ou geração, a codificação precisa evitar que uma leitura encontre o estado de outro contexto. Reutilizar `LastValue` para todas as contas é um defeito de identidade, mesmo que o número seja válido como `double`. A validade numérica não resolve a validade semântica.

`GlobalVariableGet` possui uma forma que retorna diretamente o número e outra que retorna sucesso e preenche uma variável por referência. A primeira usa zero também no erro; a segunda facilita distinguir um zero legítimo de ausência ou falha. O chamador precisa impedir a publicação de um valor residual quando a leitura falha. [REF, GlobalVariableGet, p.PDF 2632–2633]

```mql5
bool TryReadSyntheticFlag(const string name,double &value)
  {
   double candidate=0.0;
   if(!GlobalVariableGet(name,candidate)) return(false);
   value=candidate;
   return(true);
  }
```

O trecho é original, ilustrativo e não foi compilado nativamente. Ele não cria variáveis nem implementa uma lease do produto. Seu contrato é preservar a separação entre resultado e sucesso. Se o chamador decidir usar zero como padrão, essa decisão precisa estar fundamentada no domínio específico, não escondida no adaptador genérico.

Coordenação exige operação indivisível. Verificar que uma variável não existe e criá-la depois permite que dois programas passem pela verificação antes de qualquer um criar o marcador. O livro demonstra esse intercalamento. `GlobalVariableSetOnCondition` fornece comparação e troca atômicas de uma variável existente; falha se o valor esperado não corresponde ou se a variável não existe. A atomicidade pertence à operação documentada, não a uma sequência manual de leitura e escrita. [TRD, sec. 4.6.6, p.PDF 489–491; REF, GlobalVariableSetOnCondition, p.PDF 2642]

Mesmo assim, um marcador não fornece proteção contra qualquer agente do terminal: o usuário e outros programas podem alterar variáveis globais. Uma lease deve ter identidade, propriedade, confirmação de renovação e comportamento na perda, dentro do modelo de confiança adotado. No código consultado, o Monitor suspende trabalho se não confirma sua titularidade; os runtimes conservam locks relacionados aos produtores legados. Referências: arquivo principal do Monitor e `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Accountant_Runtime.mqh`. Isso documenta o fluxo de fonte; o ensaio concorrente continua separado.

`GlobalVariablesFlush()` força a gravação das globais persistentes, mas não transforma temporárias em duráveis. O desenho não deve restaurar uma indicação de atividade como se provasse que o produtor continua vivo na sessão seguinte. [REF, GlobalVariablesFlush e GlobalVariableTemp, p.PDF 2639–2640]

## 5.6 SQLite e unidade de alteração

MQL5 oferece suporte nativo a SQLite, com conexões e consultas identificadas por handles. `DatabaseOpen` aceita um caminho relativo e flags de leitura, escrita, criação, memória ou área comum. Banco em memória e arquivo temporário possuem durações específicas; abrir com sucesso não prova que se abriu o banco pretendido nem que seu schema é compatível. [TRD, sec. 7.6, p.PDF 1839–1841; REF, DatabaseOpen, p.PDF 3241–3242]

Transações de banco agrupam alterações logicamente relacionadas. `DatabaseTransactionBegin` inicia, `DatabaseTransactionCommit` confirma e `DatabaseTransactionRollback` desfaz. Todas retornam sucesso ou falha; uma confirmação solicitada sem sucesso não autoriza mensagem de gravação concluída. O livro distingue essas transações das transações de negociação: a chegada de ordem, deal e posição não fornece a mesma unidade atômica do banco local. [TRD, sec. 7.6.13, p.PDF 1893–1894; REF, DatabaseTransactionBegin/Commit/Rollback, p.PDF 3302 e 3307–3308]

A definição do limite transacional deve seguir o invariante. Se dois registros precisam concordar para representar um episódio completo, gravar um e falhar no outro não pode deixar o episódio confirmado. Uma sequência de comandos individualmente bem-sucedidos não comprova esse requisito sem o agrupamento e a verificação adequados. Também é preciso conferir quem abre e encerra a transação: o suporte MQL5 descrito no livro não admite aninhamento direto de `DatabaseTransactionBegin`. Um contador em uma camada de abstração não equivale automaticamente a savepoints independentes. [TRD, sec. 7.6.13, p.PDF 1894–1896]

Consultas parametrizadas separam valores do texto SQL. Depois de preparar a consulta, `DatabaseBind` associa valores aos parâmetros; a numeração da API começa em zero e a notação SQL numerada `?1` corresponde ao índice zero. Esse detalhe deve aparecer nos testes porque um deslocamento pode produzir consulta válida com associação errada. O exemplo do livro também distingue `NULL` de zero, diferença essencial para preservar ausência. [TRD, sec. 7.6.9, p.PDF 1870–1871]

## 5.7 Fotografia auditada, recuperação e evidência

O README do Stoikus descreve a auditoria incremental do Histórico Pessoal mantendo conexão e transação entre etapas, leitura como preparando até percorrer o histórico e nova auditoria após mudança por outra conexão. Trata-se de uma propriedade documentada do candidato, sem novo ensaio nativo nesta pesquisa. Não se deve converter uma fatia concluída em confirmação total, nem conservar uma consulta visual enquanto sua fotografia perdeu validade. Fonte: `mt5/jpw-alavancagem-atual/README.md`, seção de continuidade 1.22.3.

A recuperação precisa ser verificada também do ponto de vista do usuário. Após reinício, os registros anteriores continuam disponíveis? A versão incompatível é preservada e explicada? Uma exportação parcial recebe motivo de falha? Um produtor que perdeu propriedade cessa gravação? A consulta mantém separadas conta observada e conta cuja história está aberta? Cada resposta exige um cenário e uma evidência, não uma inferência a partir da biblioteca utilizada.

O mesmo README registra limite do corpo canônico JSON em caracteres, e não como tamanho exato do arquivo final, e mantém CSV como caminho para históricos maiores. Uma auditoria técnica deve preservar essa unidade de medida e seus limites. Redefinir um limite de persistência para facilitar o teste seria uma alteração de contrato fora do escopo desta pesquisa. O conjunto correto de evidências inclui bytes e hashes antes/depois, fixture sintética, resultado de releitura e comparação semântica, além da versão exata do candidato. A biblioteca oferece mecanismos; o produto precisa demonstrar o contrato que construiu com eles.
