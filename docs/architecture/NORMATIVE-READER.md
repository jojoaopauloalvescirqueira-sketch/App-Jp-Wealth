# Consulta do Estatuto V11

Contrato do CHG-JPW-NORMATIVE-READER-20261001, N1/A2. O leitor fica em
Ferramentas e Serviços → Estrutura Normativa JP Wealth, rota `tools-normative`.
O catálogo inicial possui somente o Estatuto V11 original. A consulta não muda
normas, cálculo, estado financeiro, schema, aceite documental ou histórico.

## Identidade e fonte

- ID documental: `estatuto-v11`; apresentação: Estatuto JP Wealth V11.0.
- Fonte preservada: `docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf`.
- 125 páginas; 1.499.074 bytes.
- SHA-256: `2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769`.

Tamanho, assinatura PDF e SHA-256 são confirmados antes de criar o worker ou
transferir os bytes. Depois de carregar, a quantidade de páginas também precisa
corresponder à identidade. Divergência impede a leitura e o download como original
verificado. Indisponibilidade do motor após o hash confirmado mantém abertura e
download do original, com erro de leitura explícito. O título interno genérico do
PDF não é usado como identidade normativa.

O PDF possui texto em todas as páginas e nenhum outline. A busca usa somente
texto incorporado; não há OCR nem índice automático por artigos. O documento
completo permanece a fonte, sem re-exportação ou reconstrução da diagramação.

## UI, recursos e ciclo de vida

`src/js/20-ui/34-normative-reader.js` publica `window.JPWNormativeReader`:

- `enter()`: abre somente quando a região está visível; entrada repetida é idempotente.
- `leave()`: cancela carga, renderização e busca; destrói documento/worker,
  desconecta miniaturas, revoga URLs temporárias e remove as páginas do DOM.
- `refreshLayout()`: redesenha a página atual quando necessário.
- `snapshot()`: identidade e estado efêmero de leitura, sem dados financeiros.

`JPWTools.ui.selectView('normative')` aciona a entrada. Troca de ferramenta ou
saída aceita da navegação Tools aciona o descarte. Observação defensiva de
visibilidade protege caminhos que ocultem o módulo. Nenhuma ação grava storage.
Página, zoom, rotação e preferência de miniaturas vivem apenas na sessão.

Navegação anterior/próxima, página direta, zoom, ajuste à largura, rotação, busca
com anterior/próximo, TextLayer para seleção/cópia, miniaturas sob demanda,
abertura do original, download e tela cheia com expansão local estão disponíveis.
A busca ignora diferenças de maiúsculas e acentos, limita a expressão a 120
caracteres e informa o teto de 1.000 ocorrências quando atingido. O destaque
identifica os trechos de texto correspondentes; não modifica o PDF.

O leitor mantém um único canvas de página completa e prepara somente os proxies
das páginas adjacentes. Bitmaps são limitados a oito milhões de pixels no desktop
e quatro milhões em área estreita. Miniaturas são desenhadas por interseção, com
até duas tarefas simultâneas. Erros de página e miniatura são explícitos; não são
convertidos em página branca com anúncio de sucesso.

Enter confirma página e busca; Shift+Enter volta um resultado. Page Up/Page Down,
Home e End navegam quando o foco está no conteúdo. ⌘F/Ctrl+F foca a busca somente
dentro da região. Escape cancela busca ou fecha a expansão. A expansão contém
o ciclo de Tab e retorna o foco ao controle de origem. Controles têm rótulos em
português e status anunciado. Páginas mantêm fundo e cores originais nos dois temas.

## Recursos locais e portabilidade

PDF.js/worker 6.3.289 são os bytes existentes em `src/vendor/pdfjs/`, sob Apache-2.0.
Nenhum arquivo vendorizado foi alterado. A licença/proveniência continua descrevendo
a incorporação original para extração; este contrato documenta o novo consumidor
de visualização. O importador FX tem adapter, worker e ciclo de vida independentes.
O leitor não modifica `GlobalWorkerOptions` compartilhado nem chama o importador.

`getDocument` recebe dados binários e worker próprio, com eval, XFA, WASM e busca
remota de recursos desabilitados. Fontes incorporadas são usadas para renderização.
Não existem dependências React/Framer, CDNs, URL de PDF arbitrária, telemetria,
conteúdo PDF executado como HTML, ou OCR externo.

O componente Framer fornecido serviu de referência de recursos, sem cópia do
código. A inspeção não demonstrou licença para reutilizá-lo, e seus imports
dependem de React/Framer, PDF.js remoto 3.11.174 e OCR externo. A implementação
local tem origem própria. A versão antiga de PDF.js aparece no intervalo afetado
pelo [aviso oficial GHSA-wgrm-67xf-hhpq](https://github.com/mozilla/pdf.js/security/advisories/GHSA-wgrm-67xf-hhpq);
o leitor utiliza os bytes locais 6.3.289 existentes e desabilita eval. A API de
renderização e TextLayer segue a
[documentação oficial de PDF.js](https://mozilla.github.io/pdf.js/api/draft/module-pdfjsLib.html).

- HTTP/HTTPS: busca do PDF canônico na mesma origem, atendida também pelo cache
  versionado da PWA. O hash é aplicado aos bytes efetivamente recebidos.
- `file://` estruturado: carga clássica sob demanda de
  `src/vendor/normative/statute-payload.js` e do payload PDF.js já existente.
- HTML portátil: os dois payloads são incorporados pelo gerador oficial; pode
  abrir em uma pasta sem recursos vizinhos.
- PWA offline: PDF, leitor, worker e payload pertencem ao mesmo precache; o ciclo
  conservador de atualização permanece intacto, sem ativação ou recarga forçada.

`tools/rebuild_monolith.py` gera o payload normativo com identidade/metadados e
base64 dos bytes originais. Ele é separado da allowlist exclusiva de
`runtimeAssets`; não é uma segunda fonte normativa. O fingerprint já inclui o
original, o gerador e os scripts. Não editar payloads nem `dist/` manualmente.

## Validação e limites

`tools/normative_reader_test.py` usa o aplicativo integrado em Chromium isolado,
bootstrap nominal de rede e estado/aceite sintéticos. Cobre bytes gerados e
portáteis, pixels/texto, páginas inicial/intermediária/final, navegação, busca,
seleção/cópia, download por hash, abertura do original, saída/cancelamento,
recuperação após hash divergente, quatro formas de carga e geometria mobile.
Recibos finais são externos ao repositório e identificam os hashes testados.
O aceite inicialmente pendente também é comparado antes e depois de abertura,
busca e download. Falhas explícitas de arquivo ausente, worker indisponível e
canvas indisponível precisam apresentar erro, preservar o estado e recuperar
pela ação Tentar novamente. Console nominal recebe zero erros; o cenário de
404 injeta e atribui somente a resposta esperada ao PDF canônico.
Somente os cenários de respostas HTTP injetadas bloqueiam service workers no
contexto isolado, para impedir que a fixture contamine o precache durante a
instalação. O cenário offline mantém o SW real, testa também adulteração do PDF
no cache isolado e restaura seus bytes antes de confirmar o retry. Nenhuma
política ou etapa de atualização do SW é substituída pelo teste.

As capacidades só recebem PASS quando executadas no candidate correspondente.
Safari/iOS nativos, leitores de tela e fidelidade visual integral das 125 páginas
exigem avaliação própria; TextLayer não comprova acessibilidade plena. Impressão
e interação com anotações/links do PDF são delegadas à abertura do original. A
consulta não comprova homologação financeira nem registra aceite do Estatuto.
O evento real de abertura do original e seus bytes verificados são comprovados
separadamente do visualizador PDF nativo. Sua renderização permanece NOT_RUN no
Chromium sem janela, que
[não suporta navegação para PDF](https://playwright.dev/python/docs/api/class-page#page-goto).
