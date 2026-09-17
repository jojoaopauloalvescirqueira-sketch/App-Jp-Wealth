# Nocuda Tool — MetaTrader 5

Versão 1.00. Indicador de desenho manual em escala linear. Não envia ordens, não
calcula lote, não acessa credenciais e não usa DLL, rede ou clipboard do sistema.

## Arquivos e instalação

- `Nocuda_Tool.mq5`: fonte editável.
- `Nocuda_Tool.ex5`: binário gerado pelo MetaEditor a partir da fonte desta entrega.

No MT5, use **Arquivo → Abrir pasta de dados**. Copie o `.ex5` para
`MQL5/Indicators/Nocuda Tool/`; opcionalmente copie o `.mq5` junto. Atualize a lista
no Navegador e adicione **Nocuda Tool** ao gráfico. Também é possível abrir o
`.mq5` no MetaEditor e compilar com F7. Esta entrega não instala arquivos na
plataforma do operador.

A compilação foi verificada com MetaEditor64 e Wine isolado: **0 erros e
0 avisos**. Isso confirma o código compilável e a existência do binário; a
interação visual no terminal, a persistência do template e a transferência real
MT5 ↔ TradingView ainda precisam de validação no ambiente das plataformas.

## Desenho e referências

A malha mantém o passo proporcional de **0,125**. A e B são dois pontos da
**linha 17**, nível `1`; C é um ponto da **linha 9**, nível `0`.

| Marco | Nível |
|---|---:|
| Linha 1 | −1 |
| Linha 3 | −0,75 |
| Linha 5 | −0,5 |
| Linha 9 | 0 |
| Linha 17 | 1 |
| MAX / linha 41 | 4 |

Arraste as extremidades do segmento **A/B17** para ajustar a inclinação e o ponto
**C9** para ajustar a largura. Dê dois cliques no objeto se o MT5 exigir seleção
antes do arraste. O movimento horizontal é ajustado à abertura de um candle; as
coordenadas de preço permanecem as escolhidas. A malha usa a distância horizontal
em **candles**, preservando sessões e intervalos sem negociação.

Com as seis entradas de pontos zeradas, o indicador propõe uma posição inicial
com base no gráfico. Essa posição é um ponto de partida visual: ajuste os pontos
conforme seu desenho. Para definir por números, preencha A/B/C com horários de
abertura de candles **no horário do servidor/gráfico**, e preços; ative
`ReiniciarPontos`. Após aplicar, desative essa opção para preservar os arrastes.

`ProjecoesAntes=8` acrescenta oito linhas antes da linha 1. `ProjecoesDepois=24`
acrescenta 24 após a linha 17, alcançando o nível 4/MAX. O limite de cada lado é
160. O intervalo 1–17 contém 17 linhas e 16 espaçamentos.

## Aparência

Nas propriedades do indicador existem grupos separados para 1, 3, 5, 9, 17,
intermediárias e projeções externas. Cada grupo controla visibilidade, cor,
transparência, espessura de 1 a 5 e traço `S` contínuo, `D` tracejado ou `P`
pontilhado. A extensão aceita `R` direita, `L` esquerda, `B` ambas ou `N` segmento.

Rótulos podem mostrar marcos, todas as linhas ou nenhum; possuem tamanho, cor,
posição, distância em porcentagem da largura D, deslocamento e opções de nível, preço e MAX. A posição `T`
acompanha o último candle; `L`, `C` e `R` usam início, centro e fim do segmento.
Deslocamentos futuros de rótulos usam a duração do período; não são novos pontos
da geometria. Rótulos anteriores ao histórico carregado não são desenhados.

O MT5 não oferece alfa real para estes objetos nativos: transparência é
aproximada misturando a cor com o fundo atual do gráfico. O RGB e a transparência
originais continuam no código exportado. O próprio MT5 pode renderizar linhas
tracejadas/pontilhadas com espessura maior que 1 como contínuas. Os controles
A/B17 e C9 permanecem visíveis quando `MostrarControles=true`, mesmo que a linha
correspondente esteja oculta; desative a opção para ocultar também os controles.

A ferramenta é uma malha administrada com objetos `OBJ_TREND`, mais um marcador
C9. Isso evita depender da interpretação implícita dos níveis do Canal de
Fibonacci. O nome no Navegador é **Nocuda Tool**; os controles são objetos nativos,
mas os estilos completos devem ser ajustados **nas propriedades do indicador**.
Alterações manuais de estilo nas linhas geradas são sobrescritas na atualização.

## Exportar MT5 → JP Wealth → TradingView

1. Ajuste A/B17 e C9. Abra as entradas do indicador.
2. Confira `SimboloCanonico` e `FeedIdentificador`. O símbolo canônico deve ser o
   mesmo na ferramenta de destino. Identifique o provedor publicamente;
   `UNKNOWN` significa que ele ainda não foi informado. Se o nome do MT5 tiver um sufixo diferente,
   por exemplo `NZDUSD.m`, informe o alias pretendido e marque
   `MapeamentoSimboloConfirmado`. O alias é uma decisão explícita do operador;
   o indicador não remove sufixos automaticamente.
3. Informe `OffsetA_min`, `OffsetB_min` e `OffsetC_min`: o fuso histórico do
   servidor em cada ponto, em minutos em relação a UTC. Exemplo: UTC+2 = 120;
   UTC−3 = −180. Os offsets podem diferir por horário de verão. Ative
   `OffsetsHistoricosConfirmados`.
4. Se as datas foram arrastadas, revise os três offsets e clique
   **Confirmar fusos A/B/C**. Enquanto essa confirmação estiver pendente,
   exportar permanece bloqueado. Alterar os offsets de um desenho arrastado
   preserva suas datas locais e recalcula UTC somente a partir dos valores
   explicitamente informados.
5. Clique **Nocuda: exportar .txt**. O indicador escreve e relê o arquivo para
   confirmar o conteúdo. A mensagem informa o nome em `MQL5/Files/`; use
   **Arquivo → Abrir pasta de dados** para encontrá-lo. Cada exportação recebe
   um nome novo e não substitui as anteriores.
6. Abra o `.txt` e copie o código, ou carregue o arquivo em
   **JP Wealth → Ferramentas e Serviços → Nocuda Tool**. Cole o código validado
   no campo de importação da ferramenta TradingView.

Os tokens decimais importados de preços e largura são preservados até que seus
valores sejam efetivamente editados. O arquivo não acrescenta quebra de linha.

O arquivo contém apenas o desenho, a identidade pública do ativo/feed, o
período, datas/preços e os estilos. Nenhum número de conta é incluído. O arquivo
é local; esta ferramenta não o envia a um servidor. O MT5 não copia diretamente
para o clipboard: esse caminho é deliberadamente feito por arquivo, sem DLL.

## Importar TradingView/JP Wealth → MT5

1. Abra o ativo e período de destino em um gráfico linear.
2. Informe o símbolo canônico e confirme um alias, se necessário. Se o feed
   de origem diferir de `FeedIdentificador`, ou algum deles for `UNKNOWN`, confira ativo, contrato e escala de
   preços e ative `ProvedorDiferenteConfirmado`. Isso não elimina a validação dos
   candles nem garante históricos idênticos.
3. Defina os offsets históricos do **servidor MT5 de destino** para A/B/C e
   confirme. Esses valores são independentes dos offsets de origem dentro do
   código. Os instantes UTC originais são preservados ao importar.
4. Cole o código completo em `ImportarDesenho` e ative `AplicarImportacao`.
5. O importador valida versão, campos, números, estilos, largura, ativo,
   período, existência de abertura exata dos três candles e contagens A–B/A–C.
   Incompatibilidades são recusadas, sem correção silenciosa de horários/preços.
6. Para usar posteriormente os estilos das entradas locais, desative
   `AplicarImportacao`. Para reaplicar deliberadamente o mesmo código após
   arrastar pontos, ative também `ReiniciarPontos`; desative-o após aplicar.

Importação ativa usa os estilos do código. Controles locais só passam a
substituí-los quando `AplicarImportacao` está desativado. Uma importação inválida
não aplica uma malha parcial; o estado anterior do desenho, quando existe,
permanece nos objetos do gráfico. Corrija o código nas entradas para reativar.

## Persistência, compatibilidade e limites

- Use um `InstanceId` diferente para cada Nocuda Tool no mesmo gráfico.
- A ferramenta mantém seu código e referências locais em objetos ocultos do
  próprio gráfico. Ao salvar templates/perfis, inclua esses objetos. A entrega
  não promete backup externo automático; exporte o `.txt` antes de alterações
  importantes, reinstalação ou mudança de plataforma.
- Remover o indicador apaga apenas os objetos com seu ID. Guarde o `.txt` para
  recuperar e importe-o em uma nova instância.
- Trocar para um período incompatível suspende a malha; os parâmetros originais
  permanecem para o retorno ao período certo. Não recalculamos o desenho para
  outra periodicidade silenciosamente.
- O histórico carregado precisa incluir as três datas. Candles ausentes,
  sessões diferentes ou contagem divergente impedem a importação. Compartilhar
  um nome de ativo não garante que os feeds de duas corretoras sejam iguais.
- Mesmo quando os três pontos e contagens coincidem, compare visualmente o
  desenho: diferenças de sessão fora das âncoras podem alterar projeções futuras.
- O período mensal do MT5 é recusado por não possuir duração fixa.
- O protocolo v1 usa escala linear; escala logarítmica não é suportada.
- Não é possível colar o código sobre qualquer gráfico sem instalar a Nocuda
  Tool. Ele é uma entrada da ferramenta, não um formato nativo universal.
- A ida e volta real nas duas plataformas permanece **não verificada** nesta
  entrega. Compilação, testes matemáticos e validação do protocolo não
  substituem a prova visual com os mesmos dados.

## Referências técnicas

- [Objetos de linha nativa e extensões](https://www.mql5.com/en/docs/constants/objectconstants/enum_object/obj_trend)
- [Busca de candle por horário e modo exato](https://www.mql5.com/en/docs/series/ibarshift)
- [Arquivos no sandbox MQL5](https://www.mql5.com/en/docs/files/fileopen)
