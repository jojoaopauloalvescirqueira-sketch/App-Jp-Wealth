# Nocuda Tool — implementação local

Contrato: [CHG-NOCUDA-TOOLS-20260917](../work/CHG-NOCUDA-TOOLS-20260917.md). Base `f1d383f9a3501b44c7d924c1335b22eb2f0e3d1b`; fontes de download em `downloads/nocuda/`.

## Produto e navegação

Ferramentas e Serviços é o sexto grupo do menu, depois dos módulos existentes. Calendário Econômico é o primeiro filho e Nocuda Tool o segundo. Layout lateral e barra superior utilizam o mesmo resolver e os mesmos nós. A ordem antiga de cinco módulos é acrescida de tools apenas em memória, sem regravar a preferência no carregamento.

O calendário reutiliza `#execEcal`, seu cache, filtros e renderer. `ecal` e a chamada legada `navigateLocal('research','calendar')` abrem tools-calendar. Research/Forex abre Estudos NoCoda e mantém Pivots. O estado financeiro `S.nocoda` desses estudos não é a Nocuda Tool e não foi modificado.

## Desenho

Três pontos: A/B na linha17 (nível1), C na linha9 (nível0). Distância assinada D é a diferença entre a reta A/B na barra de C e o preço C. Cada nível l vale `baseAB(x)+(l-1)*D`. O passo permanece0.125; largura e inclinação variam. Marcos1/3/5/9/17 são fixos e MAX corresponde ao nível4 (linha41). O padrão contém49linhas; máximo337. Escala linear e coordenadas de barras são requisitos.

Fonte [NOCUDA-TRANSFER](NOCUDA-TRANSFER.md) define wire, validação e limites. A página não deriva âncoras da imagem nem gera operações. A prévia é somente geometria, sem cotações.

## Transferência e segurança

Parser puro em `16-nocuda-transfer.js`: todos os campos obrigatórios, sem chaves adicionais/repetidas, limite16KiB, números finitos e consistência entre três pontos, D e intervalos de barras. Preços e D preservam lexemas decimais. Datas são UTC em milissegundos; offsets históricos de cada âncora são explícitos.

A UI usa textContent/SVG com atributos validados; não executa conteúdo importado. Ao alterar o rascunho, bloqueia cópia/exportação até nova validação e conserva o último desenho válido, restaurável por botão. Leitura de arquivo usa revisão para descartar respostas atrasadas. Limpar apaga explicitamente a sessão da ferramenta. Clipboard indisponível oferece seleção manual do código. Arquivo .txt contém exatamente o código, sem newline adicional.

Nenhum acesso ao estado financeiro, escritor, localStorage ou rede é acrescentado pela página. Campos têm `data-session`, exclusão já prevista no capturador genérico de rascunhos; não entram no backup financeiro. Recarregar encerra a sessão Nocuda.

A importação no destino exige símbolo, período, datas exatas e distâncias em barras compatíveis. Feeds diferentes ou desconhecidos exigem confirmação explícita de identidade/preços. Essa confirmação não relaxa as verificações geométricas. Sessões diferentes podem impedir reprodução; não há remapeamento silencioso para candle próximo.

## Arquivos e builds

TradingView: `Nocuda_Tool.pine` v1.1, script pessoal Pinev6. Modos Manual/Importado, aparência configurável e exportação nos Pine Logs. Código importado não reposiciona inputs interativos. O gerador editável substitui somente defaults marcados e `PRECONFIGURED`, preserva a validação inicial do contexto e mantém o alias de símbolo vazio para não aceitar um gráfico errado automaticamente. Conteúdo-base vem dos bytes fixados no build, inclusive em file://.

MT5: `Nocuda_Tool.mq5` e `.ex5` v1.0. Indicador com objetos de tendência, referências nativas arrastáveis e exportação local .txt. Não depende de DLL/clipboard, rede, EA ou ordens. Transparência é aproximada por mistura com o fundo. O guia explica offsets e persistência do desenho. Namespaces de instâncias têm delimitadores não permitidos no ID, e limpeza recusa prefixo vazio.

O gerador oficial declara os cinco downloads como inputs de fingerprint e incorpora seus bytes no build e no portátil. Service worker precacheia os mesmos arquivos; suas URLs nunca caem no fallback HTML de navegação. Links file:// usam os bytes incorporados porque download de caminhos vizinhos não é portátil entre navegadores. Não existe fetch externo da ferramenta.

## Verificação e limites

- Parser/protocolo:77 verificações unitárias e fixtures sintéticas.
- Interface:109 verificações HTTP, arquivo local, portátil, PWA offline, downloads byte a byte, geração editável, rejeições, recuperação, exclusão dos rascunhos, invariância de S/storage, celular, temas e teclado.
- MT5: MetaEditor64 em prefixo Wine isolado,0 erros/0 avisos. Binário compilado real; log e hashes externos identificam a compilação.
- Auditoria independente corrigiu newline, descarte de prévia, resumo de âncoras e captura genérica de rascunhos.
- Pine: geração/estrutura verificadas, compilação e execução no TradingView pendentes. A inspeção do editor não salvou nem adicionou indicador ao gráfico.
- MT5: execução em gráfico, arraste/reabertura e troca real com TradingView pendentes. Compilação não equivale a homologação visual.

A entrega é candidate local. Aceite humano, commit, push, integração e publicação não decorrem desses testes. Consulte ACTIVE-TASK e o relatório externo para resultado da regressão geral, sem confundi-lo com os testes focais acima.
