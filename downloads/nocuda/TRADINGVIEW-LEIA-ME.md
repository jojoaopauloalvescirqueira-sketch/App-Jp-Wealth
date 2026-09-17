# Nocuda Tool — TradingView 1.1

Arquivo: `Nocuda_Tool.pine` · Pine Script v6 · candidato local.

**Estado de validação:** a compilação no editor do TradingView, o arraste dos pontos e a cópia efetiva dos Pine Logs ainda precisam ser conferidos na plataforma. A revisão do código e os testes de geometria/formato no JP Wealth não substituem essas etapas. Não há instalação nem publicação automática.

## Instalação manual

1. Abra o ativo e o período desejados no TradingView, com candles convencionais e escala **linear**.
2. Abra o Pine Editor, crie um indicador pessoal e substitua o conteúdo pelo arquivo `.pine` completo.
3. Salve como **Nocuda Tool** e adicione ao gráfico. O editor fará a compilação.
4. No modo **Manual**, selecione A e B sobre a linha 17, em candles diferentes; selecione C sobre a linha 9. Para reposicionar, selecione o indicador e seus pontos. O menu **Redefinir pontos / Reset points** permite repetir a seleção.

A e B fixam a direção. C fixa a largura assinada entre as referências. Cada passo continua sendo **0,125**. A linha 1 é o nível −1; a 3, −0,75; a 5, −0,5; a 9, 0; a 17, 1. Existem oito espaçamentos entre 9 e 17. A configuração inicial projeta oito espaçamentos antes da linha 1 e 24 depois da 17, alcançando o nível 4, identificado como MAX. Ajuste a largura para adequar a malha ao movimento.

## Personalizar

As configurações do indicador oferecem cor, transparência de 0 a 100, espessura de 1 a 5, traço contínuo/tracejado/pontilhado, extensão nos dois sentidos e visibilidade. Há aparência geral e personalização independente dos cinco marcos, intermediárias e projeções. Os rótulos têm modo, tamanho, cor, transparência, posição, afastamento, nível e preço opcionais.

Os controles pertencem às **Entradas** do indicador. As linhas desenhadas pelo Pine não possuem a barra flutuante das ferramentas nativas. No modo **Importado**, geometria e aparência vêm integralmente do código recebido; os controles manuais permanecem guardados, mas não substituem os valores importados. Para editar uma importação por arraste e pelos controles visuais, use a versão editável descrita adiante.

## Exportar para MT5 ou JP Wealth

1. Confira o desenho e dê um identificador em **Transferir desenho**.
2. Ative **Gerar código nos Pine Logs**.
3. Abra **Pine Logs** pelo menu do editor ou pelo menu do indicador e copie somente a mensagem completa que começa em `NOCUDA|v=1|...`. Exclua a data/prefixo visual do log.
4. Desative a opção após copiar. Cole o texto na página **Ferramentas e Serviços → Nocuda Tool** do JP Wealth para validar e conferir os parâmetros, ou no importador da Nocuda Tool MT5.

A emissão é solicitada por essa opção e ocorre uma vez por execução completa do indicador, sem emissão a cada tick. Alterar entradas, símbolo ou período pode executar o script novamente; desative a opção após a cópia. Para pedir nova emissão, desative e ative novamente.

**Pine Logs só existem em scripts pessoais.** Este fluxo não é garantido para um script publicado. Não há botão Pine que grave diretamente no clipboard. O conteúdo exportado contém somente os parâmetros do desenho e a identificação do gráfico. No modo Importado, reexportar mantém o código original, inclusive os offsets históricos; isso não converte a origem dos dados para TradingView.

## Importar do MT5

1. Exporte o código pela **Nocuda Tool MT5**, já com offsets históricos de servidor conferidos para cada âncora. Não cole parâmetros de uma ferramenta nativa diferente.
2. No JP Wealth, valide o código e confira símbolo, período, datas UTC, preços, largura e contexto. Guarde uma cópia válida antes de alterar entradas.
3. Abra no TradingView o instrumento correspondente e o período informado no código.
4. Cole somente o código em **Importar desenho · código NOCUDA** e escolha **Importado**. Se a plataforma solicitar A/B/C ao adicionar um indicador novo, faça a seleção inicial e abra as configurações; esses pontos manuais não são usados no modo Importado.
5. Se o nome difere por sufixo ou contrato, preencha **Símbolo canônico** somente depois de confirmar que o instrumento e a escala de preço correspondem. Não há retirada automática de sufixos.
6. Se os provedores diferem, a ferramenta exige a confirmação explícita de instrumento e preço. Essa confirmação não desativa as verificações dos candles.

O parser exige o formato NOCUDA v1/bars1, todos os campos, passo 0,125 e escala linear. Rejeita campos desconhecidos/duplicados, números malformados, largura nula, datas incoerentes e limites excedidos. O desenho só aparece quando as três datas coincidem exatamente com aberturas de candles carregados, os intervalos em candles A→B/A→C coincidem com a origem e a largura assinada confere. Um candle ausente **não** é substituído pelo seguinte.

**Recuperação de erro:** uma alteração das entradas faz o Pine reiniciar o cálculo. Uma importação recusada não desenha uma nova malha e não altera os pontos manuais A/B/C, mas o Pine não mantém a malha importada anterior em memória após esse reinício. Volte ao modo Manual ou recoloque o último código válido guardado. O painel do JP Wealth preserva sua última conferência válida; isso não é backup automático das configurações do TradingView.

## Gerar uma versão editável

No JP Wealth, depois de validar o código, use **Gerar versão editável**. O arquivo resultante traz os seis valores de A/B/C e a aparência como valores iniciais das entradas. Copie esse arquivo para **um novo indicador pessoal**. Trocar o código de uma instância existente pode preservar entradas antigas salvas pelo TradingView; a instância nova evita essa confusão.

A importação textual comum não consegue alterar os pontos nativos: `input.price` e `input.time` exigem valores iniciais constantes. A versão gerada incorpora esses valores ao código-fonte e inicia em Manual. A referência importada é mantida no campo **Referência da versão editável** para checar símbolo, período, provedor e os intervalos iniciais. Não apague esse campo para ocultar incompatibilidades. Ao mover qualquer âncora, você cria uma geometria manual nova e pode exportá-la novamente.

## Limites de fidelidade

- Um conjunto por instância do indicador; use instâncias separadas para canais independentes.
- Geometria em distância de **candles**, sem converter silenciosamente para horas corridas.
- Até 4.999 candles entre o candle atual e a âncora mais antiga. Carregue histórico suficiente. No modo importado, mudar o período para contornar o limite torna o contexto incompatível.
- Períodos fixos entre um segundo e 30 dias; períodos mensais, ticks e gráficos sintéticos são recusados.
- Até 160 espaçamentos para cada lado além do intervalo 1–17, total máximo de 337 linhas.
- Use escala **linear**. O Pine não detecta de forma confiável o estado visual de escala logarítmica do painel. O código declara escala linear e não implementa transformação logarítmica.
- Conferir as três âncoras e suas contagens é necessário, mas não comprova igualdade de todos os candles intermediários nem de projeções futuras em provedores com sessões diferentes. Compare as projeções e não trate “importado” como equivalência de históricos.
- A posição horizontal dos rótulos é limitada ao intervalo suportado de desenho do Pine; pequenos detalhes tipográficos entre MT5 e TradingView podem diferir. Coordenadas e estilos do código não representam sinais nem ordens.

## Validação manual pendente

No editor real, compilar o arquivo original e uma versão gerada; verificar canais ascendentes, descendentes e largura negativa; alterar A/B/C e aparência; importar/exportar nos dois sentidos com um conjunto sintético; testar código duplicado/incompleto, símbolo/período errado, candle ausente e contagens divergentes. Conferir 1/3/5/9/17 e MAX pelos preços calculados, não apenas por screenshot. Confirmar que copiar dos Pine Logs entrega a linha integral sem prefixos e que os ticks não repetem a emissão.

Fontes oficiais: [Entradas](https://www.tradingview.com/pine-script-docs/concepts/inputs/), [Linhas e objetos](https://www.tradingview.com/pine-script-docs/visuals/lines-and-boxes/), [Pine Logs](https://www.tradingview.com/pine-script-docs/writing/debugging/#pine-logs), [Informações do gráfico](https://www.tradingview.com/pine-script-docs/concepts/chart-information/).
