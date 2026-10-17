# Leitura semântica REF4977–5270 — lote 14b

Leitura integral de todo o texto extraído das 294 páginas PDF físicas, em nove lotes de até 28.000 caracteres, expostos sem truncamento. Numeração impressa do texto coincide com os números apresentados; citações abaixo usam página PDF. Figuras não foram inspecionadas visualmente: páginas com imagens e pouco texto não autorizam inferência de aparência. MQL_NOT_RUN: nenhum exemplo foi compilado ou executado.

Escopo exclusivo: CCanvas, CChartCanvas, CHistogramChart, CLineChart, CPieChart, CCanvas3D e CChart. O registro anterior reference-batch-14 permanece preservado; REF4976 não é contado aqui, tampouco REF5271–5703. Ancestrais listados recebem cobertura parcial delimitada, sem duplicar páginas nem afirmar leitura fora do intervalo. Aplicações são propostas técnicas para Stoikus, não constatação de uso atual, implementação ou regra normativa JP Wealth.

## Síntese aplicada

Canvas separa recurso, objeto e publicação. Create não associa objeto; CreateBitmap ancora em tempo/preço e CreateBitmapLabel em pixels. Resize perde a imagem anterior; Destroy pode remover objeto vinculado. Essa combinação recomenda propriedade explícita do recurso e redesenho completo após redimensionamento, com cálculo de domínio independente do desenho [REF, CCanvas, PDF4977–5057]. TransparentLevelSet afeta somente conteúdo já composto; fonte e medição também são estado do canvas. Suavização Bézier deve ser identificada como visualização para não insinuar dados inexistentes [REF, PolygonSmooth/PolylineSmooth, PDF5039/5041].

Gráficos canvas tratam séries e índices, descritores, escalas e apresentação. Accumulative deve ser escolhido conscientemente para evitar dupla acumulação; CalcArea descreve área da figura, sem contrato de lucro ou integral financeira. Exemplos com rand/Sleep são scripts demonstrativos e não arquitetura de monitor EA por eventos [REF, CChartCanvas/CHistogramChart/CLineChart, PDF5058–5145].

3D é pesquisa futura condicionada a DX11/Shader Model 5.0; não há evidência aqui de suporte na máquina do usuário. Render compõe buffer, enquanto Update publica. Projeção/recorte podem ocultar objetos sem que dados deixem de existir [REF, CCanvas3D, PDF5160–5185].

CChart exige distinguir referência do gráfico, janela real e indicadores. Getters que retornam false/0 sem vínculo são ambíguos; ChartID=-1 identifica falta de associação e variantes bool de GetInteger/GetDouble/GetString ajudam a distinguir falhas. Detach não é Close. Remover indicador por short name pode remover dependentes e não libera o handle de cálculo: IndicatorRelease é responsabilidade separada [REF, CChart, PDF5191/5237–5249/5254–5259].

## Limites documentais concretos

Não corrigidos silenciosamente: FillEllipse mostra FillPolygon no protótipo (4991); TextWidth fala em height no retorno (5051); ShowFlags mostra getter bool para flags uint (5068); VScaleParams inverte descrições min/max (5097); CCanvas3D repete declaração/include de CCanvas (5160); ScaleFix_11 mostra setter string (5199); FixedMin mostra FixedMax (5201); IndicatorsTotal inclui chart_id no protótipo (5248); ViewTargetSet cita ViewRotationSet na nota (5184). Arc/Pie apresentam int para ângulos descritos em radianos (4983/4987). São aparentes inconsistências da fonte textual, não bugs comprovados do terminal. Conferir includes instalados e compilação nativa antes de exemplos executáveis.

## Evidência dos lotes

- Lote 0: PDF4977–4997, 27725 caracteres, SHA-256 `fa4df198feb06b693af1d0705a1dfa192569bce039ba970d83586178e5376ad3`; texto integral exposto.
- Lote 1: PDF4998–5033, 27751 caracteres, SHA-256 `45ec754be694f76f77db33c3e68bca971a5747234c519c69f9bce259451cce1e`; texto integral exposto.
- Lote 2: PDF5034–5059, 25704 caracteres, SHA-256 `0b905aedf6a71c9801eeb5b50c9a6df3f8cddcf0b37ee27a64e8c3f63e1a6057`; texto integral exposto.
- Lote 3: PDF5060–5114, 27150 caracteres, SHA-256 `c6d3c5927077e79133b689063cae1083700d4650c1ab71330ea241941fbb6106`; texto integral exposto.
- Lote 4: PDF5115–5144, 27653 caracteres, SHA-256 `1ac2e097b50bb98247477fa0d95ceb4ab5bdaa12b87e2185336b8d5f49e92efc`; texto integral exposto.
- Lote 5: PDF5145–5175, 27664 caracteres, SHA-256 `7a80fedf4a26043674e18e600fa7d331fe7a06c13a7c1a904b8856e5adb1e647`; texto integral exposto.
- Lote 6: PDF5176–5203, 27626 caracteres, SHA-256 `7b4ccf1d5fa418990882a30671038210c7c08ff3f8a2948d886a4bf08058c203`; texto integral exposto.
- Lote 7: PDF5204–5246, 26334 caracteres, SHA-256 `7f615a349335a243837ab80d9a17b62387954308e3061acf6304b453d73ac585`; texto integral exposto.
- Lote 8: PDF5247–5270, 19045 caracteres, SHA-256 `ea6afee86c840e5fe701c42417a4c30783fa5e4380b703f5f198208f5a27b6c7`; texto integral exposto.

## Notas por seção intersectante

### REF-0001 — MQL5 Reference

[REF, MQL5 Reference, p.PDF 4977–5270]. Ancestral da referência: somente interseção PDF4977–5270 lida aqui. Conteúdo aplicado cobre gráficos 2D/3D e wrapper de gráficos de preço; nenhuma declaração de leitura integral do livro por este leitor.

### REF-1136 — Standard Library

[REF, Standard Library, p.PDF 4977–5270]. Ancestral Standard Library: somente interseção PDF4977–5270 lida aqui. Proposta: usar contratos de recursos e retornos para desenho robusto; não implica uso atual destas classes pelo Stoikus.

### REF-2371 — Custom Graphics

[REF, Custom Graphics, p.PDF 4977–5158]. Ramo Custom Graphics: leitura PDF4977–5158; página 4976 pertence ao leitor anterior. Canvas, gráficos de séries, legenda, escalas e pizza fornecem interface gráfica, sem definir fórmula financeira.

### REF-2372 — CCanvas

[REF, CCanvas, p.PDF 4977–5057]. CCanvas cria recursos gráficos independentes ou vinculados a objetos e oferece primitivas, texto e transparência. Proposta Stoikus: encapsular um painel visual sem misturar seu ciclo de vida ao cálculo financeiro.

### REF-2373 — Attach

[REF, Attach, p.PDF 4981–4981]. Attach possui formas para obter o recurso existente de OBJ_BITMAP_LABEL ou criar um recurso com dimensões. Verificar o bool antes de desenhar; a forma padrão ignora alfa.

### REF-2374 — Arc

[REF, Arc, p.PDF 4982–4985]. Arc usa retângulo e raios de corte ou centro, raios e ângulos, com variante que devolve extremidades. A descrição declara radianos apesar de int na assinatura: verificar o include antes de exemplo compilável; aplicação eventual em mostrador de estado.

### REF-2375 — Pie

[REF, Pie, p.PDF 4986–4989]. Pie preenche setor elíptico com cores ARGB separadas para borda e área; variantes usam raios/ângulos e podem devolver extremidades. Mesma dúvida int/radianos de Arc; não converter isso em regra de risco.

### REF-2376 — FillPolygon

[REF, FillPolygon, p.PDF 4990–4990]. FillPolygon recebe coordenadas X/Y dos vértices e cor ARGB; a extração da assinatura omite colchetes, enquanto a descrição fala em arrays. Usar somente após conferir o include; proposta: regiões visuais do painel.

### REF-2377 — FillEllipse

[REF, FillEllipse, p.PDF 4991–4991]. FillEllipse preenche elipse delimitada pelo retângulo; a assinatura impressa diz FillPolygon, aparente inconsistência documental. Não copiar o nome errado para um exemplo Stoikus.

### REF-2378 — GetDefaultColor

[REF, GetDefaultColor, p.PDF 4992–4992]. GetDefaultColor é estático e retorna cor por índice. Proposta: paleta consistente para séries, sem usar cor como única identificação do estado.

### REF-2379 — ChartObjectName

[REF, ChartObjectName, p.PDF 4993–4993]. ChartObjectName retorna o nome do objeto vinculado; permite rastrear a propriedade visual de um painel e limitar a limpeza aos seus próprios objetos.

### REF-2380 — Circle

[REF, Circle, p.PDF 4994–4994]. Circle desenha círculo por centro e raio; contorno/traçado, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2381 — CircleAA

[REF, CircleAA, p.PDF 4995–4995]. CircleAA desenha círculo por centro e raio; contorno/traçado com antialiasing, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2382 — CircleWu

[REF, CircleWu, p.PDF 4996–4996]. CircleWu desenha círculo por centro e raio; contorno/traçado com antialiasing de Wu, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2383 — Create

[REF, Create, p.PDF 4997–4997]. Create cria recurso sem objeto; nome é base acrescida de sequência pseudoaleatória, dimensões são pixels e retorna bool. Proposta: guardar ResourceName real, sem pressupor que coincide com o nome solicitado.

### REF-2384 — CreateBitmap

[REF, CreateBitmap, p.PDF 4998–4999]. CreateBitmap ancora o objeto em tempo/preço; variante curta usa janela principal atual e outra aceita chart_id/subwin. Para Stoikus, esta ancoragem se move com o mercado e difere de um painel fixo em pixels.

### REF-2385 — CreateBitmapLabel

[REF, CreateBitmapLabel, p.PDF 5000–5001]. CreateBitmapLabel ancora em X/Y pixels e aceita chart/subjanela na variante longa. Proposta mais adequada para painel fixo; verificar criação e dimensões antes de desenhar.

### REF-2386 — Destroy

[REF, Destroy, p.PDF 5002–5002]. Destroy elimina recurso e também o objeto ao qual estiver vinculado. Proposta: chamar apenas para recursos pertencentes ao componente, sem remover objetos do operador.

### REF-2387 — Ellipse

[REF, Ellipse, p.PDF 5003–5003]. Ellipse desenha elipse por dois pontos; contorno/traçado, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2388 — EllipseAA

[REF, EllipseAA, p.PDF 5004–5004]. EllipseAA desenha elipse por dois pontos; contorno/traçado com antialiasing, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2389 — EllipseWu

[REF, EllipseWu, p.PDF 5005–5005]. EllipseWu desenha elipse por dois pontos; contorno/traçado com antialiasing de Wu, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2390 — Erase

[REF, Erase, p.PDF 5006–5006]. Erase limpa todo o canvas ou o preenche com ARGB (padrão 0). Proposta: preparar fundo antes do redesenho e testar transparência no formato escolhido.

### REF-2391 — Fill

[REF, Fill, p.PDF 5007–5007]. Fill usa ponto inicial X/Y e cor para preencher uma área. É operação raster distinta de preencher toda a superfície; proposta restrita a decoração, sem inferir fronteiras de risco.

### REF-2392 — FillCircle

[REF, FillCircle, p.PDF 5008–5008]. FillCircle desenha círculo por centro e raio; preenchido, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2393 — FillRectangle

[REF, FillRectangle, p.PDF 5009–5009]. FillRectangle desenha retângulo por dois pontos; preenchido, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2394 — FillTriangle

[REF, FillTriangle, p.PDF 5010–5010]. FillTriangle desenha triângulo por três vértices; preenchido, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2395 — FontAngleGet

[REF, FontAngleGet, p.PDF 5011–5011]. FontAngleGet retorna inclinação da fonte. Proposta: consultar configuração ao medir/exibir rótulos para evitar inconsistência do painel.

### REF-2396 — FontAngleSet

[REF, FontAngleSet, p.PDF 5012–5012]. FontAngleSet recebe inclinação em décimos de grau e retorna bool. Proposta: não confundir com radianos de Arc/Pie.

### REF-2397 — FontFlagsGet

[REF, FontFlagsGet, p.PDF 5013–5013]. FontFlagsGet retorna flags atuais da fonte; proposta: conservar configuração ao desenhar mensagens temporárias.

### REF-2398 — FontFlagsSet

[REF, FontFlagsSet, p.PDF 5014–5014]. FontFlagsSet configura flags de criação da fonte e retorna bool; detalhes são remetidos a TextSetFont, logo não inventar bits nesta seção.

### REF-2399 — FontGet

[REF, FontGet, p.PDF 5015–5015]. FontGet devolve nome, tamanho, flags e ângulo por referência; proposta: snapshot tipográfico antes de sobreposição de alerta.

### REF-2400 — FontNameGet

[REF, FontNameGet, p.PDF 5016–5016]. FontNameGet retorna nome da fonte; proposta: logar configuração efetiva do painel para diagnóstico de diferenças de layout.

### REF-2401 — FontNameSet

[REF, FontNameSet, p.PDF 5017–5017]. FontNameSet recebe nome (exemplo Arial) e retorna sucesso. Proposta: verificar resultado em vez de presumir disponibilidade da fonte.

### REF-2402 — FontSet

[REF, FontSet, p.PDF 5018–5018]. FontSet agrupa nome/tamanho/flags/ângulo e retorna bool; ângulo usa décimos de grau, tamanho remete a TextSetFont. Medir rótulos após configurar a fonte.

### REF-2403 — FontSizeGet

[REF, FontSizeGet, p.PDF 5019–5019]. FontSizeGet retorna tamanho vigente; não prova altura real do texto em pixels. Proposta: usar TextHeight/TextSize para layout.

### REF-2404 — FontSizeSet

[REF, FontSizeSet, p.PDF 5020–5020]. FontSizeSet retorna bool e remete a TextSetFont para convenção de tamanho. Proposta: recalcular layout após mudança.

### REF-2405 — Height

[REF, Height, p.PDF 5021–5021]. Height retorna altura do recurso gráfico. Proposta: validar limites Y no painel, sem confundir com altura da subjanela de CChart.

### REF-2406 — Line

[REF, Line, p.PDF 5022–5022]. Line desenha segmento entre dois pontos; contorno/traçado, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2407 — LineAA

[REF, LineAA, p.PDF 5023–5023]. LineAA desenha segmento entre dois pontos; contorno/traçado com antialiasing, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2408 — LineWu

[REF, LineWu, p.PDF 5024–5024]. LineWu desenha segmento entre dois pontos; contorno/traçado com antialiasing de Wu, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2409 — LineHorizontal

[REF, LineHorizontal, p.PDF 5025–5025]. LineHorizontal desenha segmento horizontal com X inicial/final e Y; contorno/traçado, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2410 — LineVertical

[REF, LineVertical, p.PDF 5026–5026]. LineVertical desenha segmento vertical com X e Y inicial/final; contorno/traçado, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2411 — LineStyleSet

[REF, LineStyleSet, p.PDF 5027–5027]. LineStyleSet aceita ENUM_LINE_STYLE ou padrão personalizado. Proposta: separar visualmente séries/limiares também por traço.

### REF-2412 — LineThick

[REF, LineThick, p.PDF 5028–5028]. LineThick desenha segmento entre dois pontos; contorno/traçado com antialiasing, espessura, estilo e terminação ROUND/BUTT/SQUARE, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2413 — LineThickVertical

[REF, LineThickVertical, p.PDF 5029–5029]. LineThickVertical desenha segmento entre dois pontos; contorno/traçado com antialiasing, espessura, estilo e terminação ROUND/BUTT/SQUARE, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2414 — LineThickHorizontal

[REF, LineThickHorizontal, p.PDF 5030–5030]. LineThickHorizontal desenha segmento entre dois pontos; contorno/traçado com antialiasing, espessura, estilo e terminação ROUND/BUTT/SQUARE, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2415 — LoadFromFile

[REF, LoadFromFile, p.PDF 5031–5031]. LoadFromFile lê BMP e retorna bool; nome inclui extensão. Proposta: recurso visual opcional com caminho de falha explícito, sem bloquear monitoramento.

### REF-2416 — PixelGet

[REF, PixelGet, p.PDF 5032–5032]. PixelGet devolve ARGB no ponto X/Y. Proposta: inspeção de buffer como diagnóstico, sem afirmar aparência do PDF ou terminal.

### REF-2417 — PixelSet

[REF, PixelSet, p.PDF 5033–5033]. PixelSet escreve ARGB em coordenadas inteiras. Proposta: uso pontual em indicadores de estado, respeitando dimensões do recurso.

### REF-2418 — PixelSetAA

[REF, PixelSetAA, p.PDF 5034–5034]. PixelSetAA desenha ponto com coordenadas double e antialiasing. Proposta: suavização visual, sem aumentar precisão dos dados financeiros.

### REF-2419 — Polygon

[REF, Polygon, p.PDF 5035–5035]. Polygon desenha polígono por arrays paralelos X/Y; contorno/traçado, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2420 — PolygonAA

[REF, PolygonAA, p.PDF 5036–5036]. PolygonAA desenha polígono por arrays paralelos X/Y; contorno/traçado com antialiasing, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2421 — PolygonWu

[REF, PolygonWu, p.PDF 5037–5037]. PolygonWu desenha polígono por arrays paralelos X/Y; contorno/traçado com antialiasing de Wu, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2422 — PolygonThick

[REF, PolygonThick, p.PDF 5038–5038]. PolygonThick desenha polígono por arrays paralelos X/Y; contorno/traçado com antialiasing, espessura, estilo e terminação ROUND/BUTT/SQUARE, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2423 — PolygonSmooth

[REF, PolygonSmooth, p.PDF 5039–5039]. PolygonSmooth suaviza segmentos por Bézier e depois rasteriza com antialiasing; tension=0.5 e step=10 são parâmetros de desenho. Proposta: evitar suavização em séries de risco quando ela sugerir valores não observados.

### REF-2424 — Polyline

[REF, Polyline, p.PDF 5040–5040]. Polyline desenha polilinha por arrays paralelos X/Y; contorno/traçado, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2425 — PolylineSmooth

[REF, PolylineSmooth, p.PDF 5041–5041]. PolylineSmooth combina Bézier e antialiasing com espessura, terminação, tension e step. Proposta: rotular qualquer curva suavizada e preservar os pontos originais em diagnósticos.

### REF-2426 — PolylineThick

[REF, PolylineThick, p.PDF 5042–5042]. PolylineThick desenha polilinha por arrays paralelos X/Y; contorno/traçado com antialiasing, espessura, estilo e terminação ROUND/BUTT/SQUARE, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2427 — PolylineWu

[REF, PolylineWu, p.PDF 5043–5043]. PolylineWu desenha polilinha por arrays paralelos X/Y; contorno/traçado com antialiasing de Wu, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2428 — PolylineAA

[REF, PolylineAA, p.PDF 5044–5044]. PolylineAA desenha polilinha por arrays paralelos X/Y; contorno/traçado com antialiasing, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2429 — Rectangle

[REF, Rectangle, p.PDF 5045–5045]. Rectangle desenha retângulo por dois pontos; contorno/traçado, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2430 — Resize

[REF, Resize, p.PDF 5046–5046]. Resize retorna bool e não preserva a imagem anterior. Proposta: redesenhar todo o painel após alteração de dimensões; não confiar no buffer antigo.

### REF-2431 — ResourceName

[REF, ResourceName, p.PDF 5047–5047]. ResourceName retorna identificador do recurso efetivamente criado; proposta: usá-lo na rastreabilidade e liberação, em vez de reconstruir o nome.

### REF-2432 — TextHeight

[REF, TextHeight, p.PDF 5048–5048]. TextHeight mede com a fonte atual e retorna pixels. Proposta: dimensionar linhas do painel por medição efetiva.

### REF-2433 — TextOut

[REF, TextOut, p.PDF 5049–5049]. TextOut desenha texto com âncora X/Y, ARGB e alinhamento; usa fonte atual. Proposta: separar conteúdo do estado da sua posição e validar legibilidade manualmente.

### REF-2434 — TextSize

[REF, TextSize, p.PDF 5050–5050]. TextSize devolve largura/altura por referência com fonte atual. Proposta: calcular colisões entre rótulos antes de desenhar.

### REF-2435 — TextWidth

[REF, TextWidth, p.PDF 5051–5051]. TextWidth mede largura com fonte atual, mas Return Value diz height, aparente errata. Proposta: validar o contrato pelo include antes de dimensionar componentes.

### REF-2436 — TransparentLevelSet

[REF, TransparentLevelSet, p.PDF 5052–5052]. TransparentLevelSet: 0 totalmente transparente, 255 opaco; afeta o já desenhado e não os desenhos posteriores. Proposta: aplicar depois de compor o grupo desejado, sem presumir estado persistente para novos elementos.

### REF-2437 — Triangle

[REF, Triangle, p.PDF 5053–5053]. Triangle desenha triângulo por três vértices; contorno/traçado, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2438 — TriangleAA

[REF, TriangleAA, p.PDF 5054–5054]. TriangleAA desenha triângulo por três vértices; contorno/traçado com antialiasing, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2439 — TriangleWu

[REF, TriangleWu, p.PDF 5055–5055]. TriangleWu desenha triângulo por três vértices; contorno/traçado com antialiasing de Wu, usando cor ARGB. Proposta Stoikus: decoração ou representação visual de dados já calculados; validar limites em pixels e não derivar quantias do raster.

### REF-2440 — Update

[REF, Update, p.PDF 5056–5056]. Update publica mudanças e redraw=true solicita redesenho. Proposta: compor múltiplas primitivas e publicar em um ponto controlado para reduzir trabalho visual.

### REF-2441 — Width

[REF, Width, p.PDF 5057–5057]. Width retorna largura do recurso em pixels; proposta: usar com Height na validação de coordenadas de desenho.

### REF-2442 — CChartCanvas

[REF, CChartCanvas, p.PDF 5058–5113]. CChartCanvas deriva de CCanvas e coordena eixos, legendas, grade, descritores e séries; CHistogramChart/CLineChart/CPieChart são descendentes. Proposta: preferir esta abstração para gráficos diagnósticos de dados, não para estado de negociação.

### REF-2443 — ColorBackground

[REF, ColorBackground, p.PDF 5062–5062]. ColorBackground consulta/configura a cor uint do elemento Background do gráfico canvas. Proposta: contraste consistente entre fundo, texto, borda e grade; mudança de aparência não altera série.

### REF-2444 — ColorBorder

[REF, ColorBorder, p.PDF 5063–5063]. ColorBorder consulta/configura a cor uint do elemento Border do gráfico canvas. Proposta: contraste consistente entre fundo, texto, borda e grade; mudança de aparência não altera série.

### REF-2445 — ColorText

[REF, ColorText, p.PDF 5064–5064]. ColorText consulta/configura a cor uint do elemento Text do gráfico canvas. Proposta: contraste consistente entre fundo, texto, borda e grade; mudança de aparência não altera série.

### REF-2446 — ColorGrid

[REF, ColorGrid, p.PDF 5065–5065]. ColorGrid consulta/configura a cor uint do elemento Grid do gráfico canvas. Proposta: contraste consistente entre fundo, texto, borda e grade; mudança de aparência não altera série.

### REF-2447 — MaxData

[REF, MaxData, p.PDF 5066–5066]. MaxData consulta/configura número máximo de séries permitidas. Proposta: impor orçamento de séries visuais para não crescer sem limite.

### REF-2448 — MaxDescrLen

[REF, MaxDescrLen, p.PDF 5067–5067]. MaxDescrLen consulta/configura tamanho máximo dos descritores. Proposta: planejar abreviação e rótulo completo acessível por outro meio.

### REF-2449 — ShowFlags

[REF, ShowFlags, p.PDF 5068–5068]. ShowFlags possui getter descrito como bool e setter uint de flags. Aparente incompatibilidade para combinação de bits; verificar include antes de persistir um bitmask.

### REF-2450 — IsShowLegend

[REF, IsShowLegend, p.PDF 5069–5069]. IsShowLegend consulta bool de visibilidade de Legend. Proposta: refletir estado real do componente no controle de UI; o getter não desenha nem valida dados.

### REF-2451 — IsShowScaleLeft

[REF, IsShowScaleLeft, p.PDF 5070–5070]. IsShowScaleLeft consulta bool de visibilidade de ScaleLeft. Proposta: refletir estado real do componente no controle de UI; o getter não desenha nem valida dados.

### REF-2452 — IsShowScaleRight

[REF, IsShowScaleRight, p.PDF 5071–5071]. IsShowScaleRight consulta bool de visibilidade de ScaleRight. Proposta: refletir estado real do componente no controle de UI; o getter não desenha nem valida dados.

### REF-2453 — IsShowScaleTop

[REF, IsShowScaleTop, p.PDF 5072–5072]. IsShowScaleTop consulta bool de visibilidade de ScaleTop. Proposta: refletir estado real do componente no controle de UI; o getter não desenha nem valida dados.

### REF-2454 — IsShowScaleBottom

[REF, IsShowScaleBottom, p.PDF 5073–5073]. IsShowScaleBottom consulta bool de visibilidade de ScaleBottom. Proposta: refletir estado real do componente no controle de UI; o getter não desenha nem valida dados.

### REF-2455 — IsShowGrid

[REF, IsShowGrid, p.PDF 5074–5074]. IsShowGrid consulta bool de visibilidade de Grid. Proposta: refletir estado real do componente no controle de UI; o getter não desenha nem valida dados.

### REF-2456 — IsShowDescriptors

[REF, IsShowDescriptors, p.PDF 5075–5075]. IsShowDescriptors consulta bool de visibilidade de Descriptors. Proposta: refletir estado real do componente no controle de UI; o getter não desenha nem valida dados.

### REF-2457 — IsShowPercent

[REF, IsShowPercent, p.PDF 5076–5076]. IsShowPercent consulta bool de visibilidade de Percent. Proposta: refletir estado real do componente no controle de UI; o getter não desenha nem valida dados.

### REF-2458 — VScaleMin

[REF, VScaleMin, p.PDF 5077–5077]. VScaleMin consulta/configura mínimo vertical double. Proposta: explicitar escala para comparações entre sessões, preservando unidade.

### REF-2459 — VScaleMax

[REF, VScaleMax, p.PDF 5078–5078]. VScaleMax consulta/configura máximo vertical double. Proposta: validar max maior que min no gráfico diagnóstico.

### REF-2460 — NumGrid

[REF, NumGrid, p.PDF 5079–5079]. NumGrid consulta/configura número de divisões verticais uint. Proposta: controlar densidade visual sem arredondar os dados de origem.

### REF-2461 — DataOffset

[REF, DataOffset, p.PDF 5080–5080]. DataOffset consulta/configura deslocamento int dos dados. Exemplo CPieChart usa incremento para rotação; não interpretar como deslocamento temporal universal.

### REF-2462 — DataTotal

[REF, DataTotal, p.PDF 5081–5081]. DataTotal retorna quantidade de séries. Proposta: verificar limites de índice antes de atualização/remoção.

### REF-2463 — DrawDescriptors

[REF, DrawDescriptors, p.PDF 5082–5082]. DrawDescriptors é método virtual para desenhar descritores. Proposta: especialização visual de componente, sem transferir validação de risco para uma rotina de renderização.

### REF-2464 — DrawData

[REF, DrawData, p.PDF 5083–5083]. DrawData virtual desenha série por índice uint, padrão 0. Proposta: validar identidade/índice de série antes de personalizar desenho.

### REF-2465 — Create

[REF, Create, p.PDF 5084–5084]. Create virtual cria recurso gráfico com nome-base acrescido de sequência pseudoaleatória, dimensões e formato; retorna bool. Proposta: interromper desenho no caso de falha e manter cálculo independente.

### REF-2466 — AllowedShowFlags

[REF, AllowedShowFlags, p.PDF 5085–5085]. AllowedShowFlags limita o conjunto de flags de exibição permitido. Proposta: tornar explícitos os elementos suportados pelo componente antes de expor controles.

### REF-2467 — ShowLegend

[REF, ShowLegend, p.PDF 5086–5086]. ShowLegend configura flag bool de visibilidade de Legend; true exibe e false oculta. Proposta: preservar interpretação dos dados mesmo quando legenda/escala/valores forem ocultados.

### REF-2468 — ShowScaleLeft

[REF, ShowScaleLeft, p.PDF 5087–5087]. ShowScaleLeft configura flag bool de visibilidade de ScaleLeft; true exibe e false oculta. Proposta: preservar interpretação dos dados mesmo quando legenda/escala/valores forem ocultados.

### REF-2469 — ShowScaleRight

[REF, ShowScaleRight, p.PDF 5088–5088]. ShowScaleRight configura flag bool de visibilidade de ScaleRight; true exibe e false oculta. Proposta: preservar interpretação dos dados mesmo quando legenda/escala/valores forem ocultados.

### REF-2470 — ShowScaleTop

[REF, ShowScaleTop, p.PDF 5089–5089]. ShowScaleTop configura flag bool de visibilidade de ScaleTop; true exibe e false oculta. Proposta: preservar interpretação dos dados mesmo quando legenda/escala/valores forem ocultados.

### REF-2471 — ShowScaleBottom

[REF, ShowScaleBottom, p.PDF 5090–5090]. ShowScaleBottom configura flag bool de visibilidade de ScaleBottom; true exibe e false oculta. Proposta: preservar interpretação dos dados mesmo quando legenda/escala/valores forem ocultados.

### REF-2472 — ShowGrid

[REF, ShowGrid, p.PDF 5091–5091]. ShowGrid configura flag bool de visibilidade de Grid; true exibe e false oculta. Proposta: preservar interpretação dos dados mesmo quando legenda/escala/valores forem ocultados.

### REF-2473 — ShowDescriptors

[REF, ShowDescriptors, p.PDF 5092–5092]. ShowDescriptors configura flag bool de visibilidade de Descriptors; true exibe e false oculta. Proposta: preservar interpretação dos dados mesmo quando legenda/escala/valores forem ocultados.

### REF-2474 — ShowValue

[REF, ShowValue, p.PDF 5093–5093]. ShowValue configura flag bool de visibilidade de Value; true exibe e false oculta. Proposta: preservar interpretação dos dados mesmo quando legenda/escala/valores forem ocultados.

### REF-2475 — ShowPercent

[REF, ShowPercent, p.PDF 5094–5094]. ShowPercent configura flag bool de visibilidade de Percent; true exibe e false oculta. Proposta: preservar interpretação dos dados mesmo quando legenda/escala/valores forem ocultados.

### REF-2476 — LegendAlignment

[REF, LegendAlignment, p.PDF 5095–5095]. LegendAlignment usa ENUM_ALIGNMENT com LEFT/TOP/RIGHT/BOTTOM. Proposta: reservar área da legenda antes de calcular a região dos dados.

### REF-2477 — Accumulative

[REF, Accumulative, p.PDF 5096–5096]. Accumulative(true) substitui valor corrente da série pela soma dos anteriores no desenho; false mantém modo padrão. Proposta: declarar se o gráfico mostra níveis ou acumulados, sem acumular novamente uma série já acumulada.

### REF-2478 — VScaleParams

[REF, VScaleParams, p.PDF 5097–5097]. VScaleParams recebe max,min,grid, mas descrições de max/min aparecem invertidas. Exemplo passa máximo positivo primeiro; conferir include e teste nativo antes de ensinar assinatura como validada.

### REF-2479 — DescriptorUpdate

[REF, DescriptorUpdate, p.PDF 5098–5098]. DescriptorUpdate altera descritor na posição da série, índice zero-based, e retorna bool. Proposta: manter identidade da série ao atualizar o texto.

### REF-2480 — ColorUpdate

[REF, ColorUpdate, p.PDF 5099–5099]. ColorUpdate altera cor na posição zero-based e retorna bool. Proposta: associar cor à identidade estável, não à posição após inserções.

### REF-2481 — ValuesCheck

[REF, ValuesCheck, p.PDF 5100–5100]. ValuesCheck é método virtual auxiliar de cálculos internos do gráfico. Não representa validação normativa de dados Stoikus; proposta: manter validação de domínio fora do desenho.

### REF-2482 — Redraw

[REF, Redraw, p.PDF 5101–5101]. Redraw é método virtual para redesenhar gráfico. Proposta: especialização visual de componente, sem transferir validação de risco para uma rotina de renderização.

### REF-2483 — DrawBackground

[REF, DrawBackground, p.PDF 5102–5102]. DrawBackground é método virtual para redesenhar fundo. Proposta: especialização visual de componente, sem transferir validação de risco para uma rotina de renderização.

### REF-2484 — DrawLegend

[REF, DrawLegend, p.PDF 5103–5103]. DrawLegend é método virtual para redesenhar legenda. Proposta: especialização visual de componente, sem transferir validação de risco para uma rotina de renderização.

### REF-2485 — DrawLegendVertical

[REF, DrawLegendVertical, p.PDF 5104–5104]. DrawLegendVertical recebe dimensões máximas de texto e retorna largura da legenda em pixels. Proposta: reservar margem lateral medida.

### REF-2486 — DrawLegendHorizontal

[REF, DrawLegendHorizontal, p.PDF 5105–5105]. DrawLegendHorizontal recebe dimensões máximas de texto e retorna altura da legenda em pixels. Proposta: reservar margem superior/inferior medida.

### REF-2487 — CalcScales

[REF, CalcScales, p.PDF 5106–5106]. CalcScales é método virtual para calcular coordenadas das marcas da escala. Proposta: especialização visual de componente, sem transferir validação de risco para uma rotina de renderização.

### REF-2488 — DrawScales

[REF, DrawScales, p.PDF 5107–5107]. DrawScales é ponto de desenho da escala; variantes direcionais recebem draw e retornam largura para Left/Right ou altura para Top/Bottom. Proposta: reservar essa dimensão no layout, separando medição de exibição.

### REF-2489 — DrawScaleLeft

[REF, DrawScaleLeft, p.PDF 5108–5108]. DrawScaleLeft é ponto de desenho da escala; variantes direcionais recebem draw e retornam largura para Left/Right ou altura para Top/Bottom. Proposta: reservar essa dimensão no layout, separando medição de exibição.

### REF-2490 — DrawScaleRight

[REF, DrawScaleRight, p.PDF 5109–5109]. DrawScaleRight é ponto de desenho da escala; variantes direcionais recebem draw e retornam largura para Left/Right ou altura para Top/Bottom. Proposta: reservar essa dimensão no layout, separando medição de exibição.

### REF-2491 — DrawScaleTop

[REF, DrawScaleTop, p.PDF 5110–5110]. DrawScaleTop é ponto de desenho da escala; variantes direcionais recebem draw e retornam largura para Left/Right ou altura para Top/Bottom. Proposta: reservar essa dimensão no layout, separando medição de exibição.

### REF-2492 — DrawScaleBottom

[REF, DrawScaleBottom, p.PDF 5111–5111]. DrawScaleBottom é ponto de desenho da escala; variantes direcionais recebem draw e retornam largura para Left/Right ou altura para Top/Bottom. Proposta: reservar essa dimensão no layout, separando medição de exibição.

### REF-2493 — DrawGrid

[REF, DrawGrid, p.PDF 5112–5112]. DrawGrid é método virtual para desenhar grade. Proposta: especialização visual de componente, sem transferir validação de risco para uma rotina de renderização.

### REF-2494 — DrawChart

[REF, DrawChart, p.PDF 5113–5113]. DrawChart é método virtual para desenhar gráfico. Proposta: especialização visual de componente, sem transferir validação de risco para uma rotina de renderização.

### REF-2495 — CHistogramChart

[REF, CHistogramChart, p.PDF 5114–5131]. CHistogramChart oferece séries, colunas, gradiente e atualizações; exemplo é script com laço Sleep e destruição final. Proposta: gráfico diagnóstico de distribuições, sem transplantar laço bloqueante para EA por eventos.

### REF-2496 — Gradient

[REF, Gradient, p.PDF 5119–5119]. Gradient liga/desliga preenchimento em gradiente (padrão true). Proposta: opção estética, sem significado quantitativo adicional.

### REF-2497 — BarGap

[REF, BarGap, p.PDF 5120–5120]. BarGap configura afastamento do histograma em relação à origem segundo o texto. Sem unidade explícita nesta página: verificar implementação antes de prometer espaçamento.

### REF-2498 — BarMinSize

[REF, BarMinSize, p.PDF 5121–5121]. BarMinSize configura largura mínima das colunas. Proposta: testar com muitas amostras e janela estreita, pois a legibilidade limita a densidade.

### REF-2499 — BarBorder

[REF, BarBorder, p.PDF 5122–5122]. BarBorder usa uint no protótipo mas descreve true/false para bordas. Proposta: confirmar assinatura instalada antes de exemplo compilável.

### REF-2500 — Create

[REF, Create, p.PDF 5123–5123]. Create virtual cria recurso por nome-base, dimensões em pixels e formato, devolvendo bool. Proposta: validar sucesso antes de carregar séries; nome real pode diferir da base.

### REF-2501 — SeriesAdd

[REF, SeriesAdd, p.PDF 5124–5124]. SeriesAdd acrescenta série de doubles com descritor/cor e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2502 — SeriesInsert

[REF, SeriesInsert, p.PDF 5125–5125]. SeriesInsert insere série de doubles na posição indicada com descritor/cor e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2503 — SeriesUpdate

[REF, SeriesUpdate, p.PDF 5126–5126]. SeriesUpdate substitui série na posição zero-based, valores/descritor/cor e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2504 — SeriesDelete

[REF, SeriesDelete, p.PDF 5127–5127]. SeriesDelete remove série por posição zero-based e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2505 — ValueUpdate

[REF, ValueUpdate, p.PDF 5128–5128]. ValueUpdate altera elemento por índices de série e posição, ambos zero-based. Retorna bool. Proposta: atualizar apenas dados validados e tratar falha sem publicar uma composição incompleta.

### REF-2506 — DrawData

[REF, DrawData, p.PDF 5129–5129]. DrawData virtual desenha a série no índice informado (ordem de adição, zero-based). Proposta: manter renderização distinta da gestão dos valores e unidades.

### REF-2507 — DrawBar

[REF, DrawBar, p.PDF 5130–5130]. DrawBar desenha retângulo preenchido a partir de canto superior esquerdo, largura/altura e cor. Proposta: representar grandezas com escala explícita, não usar dimensões como cálculo de saldo.

### REF-2508 — GradientBrush

[REF, GradientBrush, p.PDF 5131–5131]. GradientBrush cria pincel por espessura e cor de preenchimento. Proposta: detalhe de renderização fora da lógica financeira.

### REF-2509 — CLineChart

[REF, CLineChart, p.PDF 5132–5145]. CLineChart desenha curvas e permite preencher área; exemplo gera valores aleatórios e atualiza com Sleep. Proposta: visualização de séries temporais reais em rotina por eventos, preservando unidades e lacunas.

### REF-2510 — Filled

[REF, Filled, p.PDF 5136–5136]. Filled controla preenchimento sob curva. Proposta: estética opcional que não cria probabilidade ou intervalo de confiança.

### REF-2511 — Create

[REF, Create, p.PDF 5137–5137]. Create virtual cria recurso por nome-base, dimensões em pixels e formato, devolvendo bool. Proposta: validar sucesso antes de carregar séries; nome real pode diferir da base.

### REF-2512 — SeriesAdd

[REF, SeriesAdd, p.PDF 5138–5138]. SeriesAdd acrescenta série de doubles com descritor/cor e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2513 — SeriesInsert

[REF, SeriesInsert, p.PDF 5139–5139]. SeriesInsert insere série de doubles na posição indicada com descritor/cor e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2514 — SeriesUpdate

[REF, SeriesUpdate, p.PDF 5140–5140]. SeriesUpdate substitui série na posição zero-based, valores/descritor/cor e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2515 — SeriesDelete

[REF, SeriesDelete, p.PDF 5141–5141]. SeriesDelete remove série por posição zero-based e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2516 — ValueUpdate

[REF, ValueUpdate, p.PDF 5142–5142]. ValueUpdate altera elemento por índices de série e posição, ambos zero-based. Retorna bool. Proposta: atualizar apenas dados validados e tratar falha sem publicar uma composição incompleta.

### REF-2517 — DrawChart

[REF, DrawChart, p.PDF 5143–5143]. DrawChart virtual compõe o gráfico e seus elementos. Proposta: coordenar redesenho completo após alterar séries/legendas sem recalcular domínio dentro da UI.

### REF-2518 — DrawData

[REF, DrawData, p.PDF 5144–5144]. DrawData virtual desenha a série no índice informado (ordem de adição, zero-based). Proposta: manter renderização distinta da gestão dos valores e unidades.

### REF-2519 — CalcArea

[REF, CalcArea, p.PDF 5145–5145]. CalcArea retorna área da figura limitada pela curva de uma série. Proposta: não tratar área de desenho como resultado financeiro ou integral temporal sem conhecer escala/amostragem.

### REF-2520 — CPieChart

[REF, CPieChart, p.PDF 5146–5158]. CPieChart compõe pizza com valores, cores e rótulos; exemplo explora flags, legenda e rotação via DataOffset. Proposta: composição de categorias mutuamente definidas, não resultado ou previsão.

### REF-2521 — Create

[REF, Create, p.PDF 5150–5150]. Create virtual cria recurso por nome-base, dimensões em pixels e formato, devolvendo bool. Proposta: validar sucesso antes de carregar séries; nome real pode diferir da base.

### REF-2522 — SeriesSet

[REF, SeriesSet, p.PDF 5151–5151]. SeriesSet recebe arrays paralelos de valores, rótulos e cores e retorna bool. Proposta: validar correspondência dos arrays e domínio dos valores antes de exibir composição.

### REF-2523 — ValueAdd

[REF, ValueAdd, p.PDF 5152–5152]. ValueAdd acrescenta valor com descritor/cor ao final da pizza e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2524 — ValueInsert

[REF, ValueInsert, p.PDF 5153–5153]. ValueInsert insere valor com descritor/cor na posição da pizza e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2525 — ValueUpdate

[REF, ValueUpdate, p.PDF 5154–5154]. ValueUpdate altera valor/descritor/cor da fatia por posição zero-based. Retorna bool. Proposta: atualizar apenas dados validados e tratar falha sem publicar uma composição incompleta.

### REF-2526 — ValueDelete

[REF, ValueDelete, p.PDF 5155–5155]. ValueDelete remove valor da pizza por posição zero-based e retorna bool. Proposta Stoikus: manter identidade estável e revalidar índices após inserções/remoções; falha de desenho não muda o estado financeiro.

### REF-2527 — DrawChart

[REF, DrawChart, p.PDF 5156–5156]. DrawChart virtual compõe o gráfico e seus elementos. Proposta: coordenar redesenho completo após alterar séries/legendas sem recalcular domínio dentro da UI.

### REF-2528 — DrawPie

[REF, DrawPie, p.PDF 5157–5157]. DrawPie recebe limites angulares em radianos, índice, pontos de referência e cor. Proposta: implementação visual; não usar ângulo para reconstruir quantias originais.

### REF-2529 — LabelMake

[REF, LabelMake, p.PDF 5158–5158]. LabelMake forma rótulo a partir de texto/valor; to_left=true usa rótulo antes do valor, false inverte. Proposta: manter unidade no texto para evitar ambiguidade.

### REF-2530 — 3D Graphics

[REF, 3D Graphics, p.PDF 5159–5185]. Seção 3D usa DirectX, gerenciamento de recursos e objetos de cena. Limite Stoikus: pesquisa visual futura; nenhuma necessidade operacional ou integração atual demonstrada.

### REF-2531 — CCanvas3D

[REF, CCanvas3D, p.PDF 5160–5185]. CCanvas3D controla câmera, luz e recursos; exige DX11/Shader Model 5.0. A declaração/include impressos repetem CCanvas/Canvas.mqh, aparentes erros documentais. Proposta futura condicionada à plataforma real; sem inferir suporte no macOS.

### REF-2532 — AmbientColorGet

[REF, AmbientColorGet, p.PDF 5162–5162]. AmbientColorGet devolve DXColor com intensidade no canal alfa. Limite: alfa de luz tem semântica de intensidade, não assumir transparência do canvas.

### REF-2533 — AmbientColorSet

[REF, AmbientColorSet, p.PDF 5163–5163]. AmbientColorSet configura DXColor com intensidade no alfa. Pesquisa futura: manter parâmetros de iluminação separados dos valores representados.

### REF-2534 — Attach

[REF, Attach, p.PDF 5164–5164]. Attach associa recurso de OBJ_BITMAP_LABEL, podendo fornecer dimensões e formato. Limite futuro: verificar bool e contexto gráfico antes de uso 3D.

### REF-2535 — Create

[REF, Create, p.PDF 5165–5165]. Create cria recurso 3D independente com dimensões/formato e retorno bool. Pesquisa futura exige verificar falha de criação em hardware alvo.

### REF-2536 — Destroy

[REF, Destroy, p.PDF 5166–5166]. Destroy libera recurso e contexto 3D e elimina objeto vinculado. Pesquisa futura: tratamento explícito de propriedade e encerramento do recurso.

### REF-2537 — DXContext

[REF, DXContext, p.PDF 5167–5167]. DXContext retorna handle int do contexto gráfico. Limite futuro: identificador de recurso não comprova capacidade ou sucesso de renderização.

### REF-2538 — DXDispatcher

[REF, DXDispatcher, p.PDF 5168–5168]. DXDispatcher retorna ponteiro CDXDispatcher do gerenciador de recursos. Pesquisa futura: não assumir ownership transferido pelo getter.

### REF-2539 — InputScene

[REF, InputScene, p.PDF 5169–5169]. InputScene retorna ponteiro CDXInput para buffer de parâmetros da cena. Pesquisa futura: separar dados de cena do estado financeiro.

### REF-2540 — LightColorGet

[REF, LightColorGet, p.PDF 5170–5170]. LightColorGet devolve cor/intensidade direcional em DXColor com intensidade no alfa. Limite futuro: não confundir com alfa de composição raster.

### REF-2541 — LightColorSet

[REF, LightColorSet, p.PDF 5171–5171]. LightColorSet recebe DXColor com intensidade no alfa. Pesquisa futura: iluminação altera aparência, não os valores subjacentes.

### REF-2542 — LightDirectionGet

[REF, LightDirectionGet, p.PDF 5172–5172]. LightDirectionGet devolve vetor DXVector3 da direção da luz. Limite futuro: vetor visual sem papel no cálculo Stoikus.

### REF-2543 — LightDirectionSet

[REF, LightDirectionSet, p.PDF 5173–5173]. LightDirectionSet recebe DXVector3 da direção da luz. Pesquisa futura de renderização, sem introduzir dependência no monitor.

### REF-2544 — ObjectAdd

[REF, ObjectAdd, p.PDF 5174–5174]. ObjectAdd aceita ponteiro a descendente de CDXObject e retorna bool. Pesquisa futura: verificar adição antes de renderizar, sem pressupor gestão de memória além do documentado.

### REF-2545 — ProjectionMatrixGet

[REF, ProjectionMatrixGet, p.PDF 5175–5175]. ProjectionMatrixGet devolve matriz DXMatrix da projeção 3D para quadro 2D. Pesquisa futura: guardar projeção na evidência visual para comparação.

### REF-2546 — ProjectionMatrixSet

[REF, ProjectionMatrixSet, p.PDF 5176–5176]. ProjectionMatrixSet usa campo de visão em radianos, aspecto e planos near/far; só objetos dentro desse volume aparecem. Limite: ausência visual não comprova ausência de dados.

### REF-2547 — Render

[REF, Render, p.PDF 5177–5177]. Render atualiza buffer interno, inclui RenderBegin/RenderEnd e não publica sozinho; requer Update. Flags limpam cor/profundidade. Pesquisa futura: separar sucesso de renderização da publicação.

### REF-2548 — RenderBegin

[REF, RenderBegin, p.PDF 5178–5178]. RenderBegin prepara contexto e aceita flags de limpeza de cor/profundidade; retorno false inclui falha na atualização de entradas do shader. Pesquisa futura: abortar quadro com falha.

### REF-2549 — RenderEnd

[REF, RenderEnd, p.PDF 5179–5179]. RenderEnd copia quadro para buffer e pode redesenhar; redraw padrão false. Pesquisa futura: não afirmar imagem publicada apenas pelo retorno de Render.

### REF-2550 — ViewMatrixGet

[REF, ViewMatrixGet, p.PDF 5180–5180]. ViewMatrixGet devolve matriz com posição e direção da câmera. Pesquisa futura: registrar câmera para comparar cenas.

### REF-2551 — ViewMatrixSet

[REF, ViewMatrixSet, p.PDF 5181–5181]. ViewMatrixSet configura matriz de visualização. Limite: transformação de câmera afeta percepção, não significado dos dados.

### REF-2552 — ViewPositionSet

[REF, ViewPositionSet, p.PDF 5182–5182]. ViewPositionSet configura posição e altera matriz de visualização. Pesquisa futura: manter pose explícita para reprodução.

### REF-2553 — ViewRotationSet

[REF, ViewRotationSet, p.PDF 5183–5183]. ViewRotationSet usa vetor de ângulos Euler e altera matriz. Unidade não explicitada nesta página; não inferir.

### REF-2554 — ViewTargetSet

[REF, ViewTargetSet, p.PDF 5184–5184]. ViewTargetSet fixa alvo e combina com ViewUpDirectionSet; nota menciona ViewRotationSet ao descrever alvo, aparente lapso. Pesquisa futura: conferir implementação.

### REF-2555 — ViewUpDirectionSet

[REF, ViewUpDirectionSet, p.PDF 5185–5185]. ViewUpDirectionSet define direção superior do quadro e altera matriz; trabalha com ViewTargetSet para direção do olhar. Proposta futura somente.

### REF-2556 — Price Charts

[REF, Price Charts, p.PDF 5186–5270]. CChart deriva de CObject e encapsula propriedades, vínculos, indicadores, navegação e persistência de gráficos de preço. Proposta: acesso visual controlado; não confundir com CChartCanvas de séries raster.

### REF-2557 — ChartID

[REF, ChartID, p.PDF 5191–5191]. ChartID retorna -1 quando não há gráfico associado. Proposta: testar vínculo explicitamente, pois getters de propriedades frequentemente retornam valores também válidos como false/0.

### REF-2558 — Mode

[REF, Mode, p.PDF 5192–5192]. Mode consulta/configura modo barras/velas/linha via ENUM_CHART_MODE; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2559 — Foreground

[REF, Foreground, p.PDF 5193–5193]. Foreground consulta/configura posição do gráfico no primeiro plano; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2560 — Shift

[REF, Shift, p.PDF 5194–5194]. Shift consulta/configura deslocamento da borda direita; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2561 — ShiftSize

[REF, ShiftSize, p.PDF 5195–5195]. ShiftSize consulta/configura percentual de deslocamento; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2562 — AutoScroll

[REF, AutoScroll, p.PDF 5196–5196]. AutoScroll consulta/configura rolagem automática; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2563 — Scale

[REF, Scale, p.PDF 5197–5197]. Scale consulta/configura nível de escala inteiro; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2564 — ScaleFix

[REF, ScaleFix, p.PDF 5198–5198]. ScaleFix consulta/configura fixação da escala; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2565 — ScaleFix_11

[REF, ScaleFix_11, p.PDF 5199–5199]. ScaleFix_11 consulta bool para escala 1:1 mas setter está impresso com string. Aparente inconsistência: confirmar include antes de exemplo compilável.

### REF-2566 — FixedMax

[REF, FixedMax, p.PDF 5200–5200]. FixedMax consulta/configura preço máximo fixo double; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2567 — FixedMin

[REF, FixedMin, p.PDF 5201–5201]. FixedMin consulta mínimo fixo, mas protótipo do setter diz FixedMax e parâmetro descritivo max. Aparente errata: não copiar literalmente para código.

### REF-2568 — PointsPerBar

[REF, PointsPerBar, p.PDF 5202–5202]. PointsPerBar consulta/configura pontos por barra double; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2569 — ScalePPB

[REF, ScalePPB, p.PDF 5203–5203]. ScalePPB consulta/configura habilitação da escala por pontos por barra; setter retorna bool. Getters sem vínculo usam sentinelas (false, 0, EMPTY_VALUE ou WRONG_VALUE conforme tipo). Proposta: validar ChartID antes da leitura e preservar preferências de visualização do operador.

### REF-2570 — ShowOHLC

[REF, ShowOHLC, p.PDF 5204–5204]. ShowOHLC controla exibição de OHLC no CChart, com setter bool de sucesso; getter false também ocorre sem vínculo. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2571 — ShowLineBid

[REF, ShowLineBid, p.PDF 5205–5205]. ShowLineBid controla exibição de LineBid no CChart, com setter bool de sucesso; getter false também ocorre sem vínculo. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2572 — ShowLineAsk

[REF, ShowLineAsk, p.PDF 5206–5206]. ShowLineAsk controla exibição de LineAsk no CChart, com setter bool de sucesso; getter false também ocorre sem vínculo. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2573 — ShowLastLine

[REF, ShowLastLine, p.PDF 5207–5207]. ShowLastLine controla exibição de LastLine no CChart, com setter bool de sucesso; getter false também ocorre sem vínculo. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2574 — ShowPeriodSep

[REF, ShowPeriodSep, p.PDF 5208–5208]. ShowPeriodSep controla exibição de PeriodSep no CChart, com setter bool de sucesso; getter false também ocorre sem vínculo. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2575 — ShowGrid

[REF, ShowGrid, p.PDF 5209–5209]. ShowGrid controla exibição de Grid no CChart, com setter bool de sucesso; getter false também ocorre sem vínculo. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2576 — ShowVolumes

[REF, ShowVolumes, p.PDF 5210–5210]. ShowVolumes controla exibição de Volumes no CChart, com setter bool de sucesso; getter false também ocorre sem vínculo. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2577 — ShowObjectDescr

[REF, ShowObjectDescr, p.PDF 5211–5211]. ShowObjectDescr controla exibição de ObjectDescr no CChart, com setter bool de sucesso; getter false também ocorre sem vínculo. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2578 — ShowDateScale

[REF, ShowDateScale, p.PDF 5212–5212]. ShowDateScale controla exibição de DateScale no CChart, com setter bool de sucesso; esta página apresenta somente setter. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2579 — ShowPriceScale

[REF, ShowPriceScale, p.PDF 5213–5213]. ShowPriceScale controla exibição de PriceScale no CChart, com setter bool de sucesso; esta página apresenta somente setter. Proposta: configuração visual explícita; ocultar uma linha de preço/escala não altera cotação, posição ou cálculo.

### REF-2580 — ColorBackground

[REF, ColorBackground, p.PDF 5214–5214]. ColorBackground consulta/configura cor de fundo; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2581 — ColorForeground

[REF, ColorForeground, p.PDF 5215–5215]. ColorForeground consulta/configura cor de eixos/escala/OHLC; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2582 — ColorGrid

[REF, ColorGrid, p.PDF 5216–5216]. ColorGrid consulta/configura cor de grade; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2583 — ColorBarUp

[REF, ColorBarUp, p.PDF 5217–5217]. ColorBarUp consulta/configura cor de barras de alta/sombras/contornos; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2584 — ColorBarDown

[REF, ColorBarDown, p.PDF 5218–5218]. ColorBarDown consulta/configura cor de barras de baixa/sombras/contornos; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2585 — ColorCandleBull

[REF, ColorCandleBull, p.PDF 5219–5219]. ColorCandleBull consulta/configura cor de corpo de vela de alta; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2586 — ColorCandleBear

[REF, ColorCandleBear, p.PDF 5220–5220]. ColorCandleBear consulta/configura cor de corpo de vela de baixa; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2587 — ColorChartLine

[REF, ColorChartLine, p.PDF 5221–5221]. ColorChartLine consulta/configura cor de linha/Doji; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2588 — ColorVolumes

[REF, ColorVolumes, p.PDF 5222–5222]. ColorVolumes consulta/configura cor de volumes/níveis de posições; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2589 — ColorLineBid

[REF, ColorLineBid, p.PDF 5223–5223]. ColorLineBid consulta/configura cor de linha Bid; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2590 — ColorLineAsk

[REF, ColorLineAsk, p.PDF 5224–5224]. ColorLineAsk consulta/configura cor de linha Ask; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2591 — ColorLineLast

[REF, ColorLineLast, p.PDF 5225–5225]. ColorLineLast consulta/configura cor de linha Last; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2592 — ColorStopLevels

[REF, ColorStopLevels, p.PDF 5226–5226]. ColorStopLevels consulta/configura cor de níveis SL/TP; getter retorna CLR_NONE sem vínculo e setter bool informa sucesso. Proposta: identidade visual legível; configurar a cor de SL/TP não envia nem altera stops.

### REF-2593 — VisibleBars

[REF, VisibleBars, p.PDF 5227–5227]. VisibleBars lê quantidade de barras visíveis (0 sem vínculo). Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2594 — WindowsTotal

[REF, WindowsTotal, p.PDF 5228–5228]. WindowsTotal lê janelas incluindo subjanelas de indicadores (0 sem vínculo). Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2595 — WindowIsVisible

[REF, WindowIsVisible, p.PDF 5229–5229]. WindowIsVisible lê visibilidade da subjanela, 0 principal (false sem vínculo). Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2596 — WindowHandle

[REF, WindowHandle, p.PDF 5230–5230]. WindowHandle lê HWND, INVALID_HANDLE sem vínculo. Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2597 — FirstVisibleBar

[REF, FirstVisibleBar, p.PDF 5231–5231]. FirstVisibleBar lê índice da primeira barra visível (-1 sem vínculo). Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2598 — WidthInBars

[REF, WidthInBars, p.PDF 5232–5232]. WidthInBars lê largura em barras (0 sem vínculo). Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2599 — WidthInPixels

[REF, WidthInPixels, p.PDF 5233–5233]. WidthInPixels lê largura em pixels (0 sem vínculo). Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2600 — HeightInPixels

[REF, HeightInPixels, p.PDF 5234–5234]. HeightInPixels lê altura em pixels por subjanela (0 sem vínculo). Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2601 — PriceMin

[REF, PriceMin, p.PDF 5235–5235]. PriceMin lê preço mínimo visual por subjanela (EMPTY_VALUE sem vínculo). Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2602 — PriceMax

[REF, PriceMax, p.PDF 5236–5236]. PriceMax lê preço máximo visual por subjanela (EMPTY_VALUE sem vínculo). Proposta: dimensionar/descrever viewport e validar sentinelas; intervalo visível não equivale ao conjunto completo de mercado ou histórico.

### REF-2603 — Attach

[REF, Attach, p.PDF 5237–5237]. Attach vincula gráfico atual ou identificador informado. Proposta: fixar explicitamente o chart pretendido para evitar afetar janela do operador.

### REF-2604 — FirstChart

[REF, FirstChart, p.PDF 5238–5238]. FirstChart vincula primeiro gráfico do terminal. Proposta: inventário visual com identidade explícita e sem modificar automaticamente cada gráfico.

### REF-2605 — NextChart

[REF, NextChart, p.PDF 5239–5239]. NextChart passa ao gráfico seguinte ao vinculado. Proposta: controlar término da enumeração e identidade antes de agir.

### REF-2606 — Open

[REF, Open, p.PDF 5240–5240]. Open abre e vincula gráfico por símbolo/timeframe; NULL/0 usam contexto atual e retorna identificador. Proposta: recurso opt-in em diagnóstico, sem abrir gráficos no monitor por pressuposto.

### REF-2607 — Detach

[REF, Detach, p.PDF 5241–5241]. Detach desfaz associação da instância. Distinto de Close; proposta: usar para soltar referência sem encerrar janela do operador.

### REF-2608 — Close

[REF, Close, p.PDF 5242–5242]. Close fecha gráfico vinculado. Proposta: restringir a gráficos criados pelo componente e com autorização de fluxo; não usar como limpeza genérica.

### REF-2609 — BringToTop

[REF, BringToTop, p.PDF 5243–5243]. BringToTop traz gráfico à frente e retorna bool. Proposta: ação de interface solicitada, não reação automática a cada evento.

### REF-2610 — EventObjectCreate

[REF, EventObjectCreate, p.PDF 5244–5244]. EventObjectCreate configura envio de eventos de criação de objetos. Proposta: habilitar apenas quando o componente consome esses eventos; filtrar nomes próprios.

### REF-2611 — EventObjectDelete

[REF, EventObjectDelete, p.PDF 5245–5245]. EventObjectDelete configura envio de eventos de exclusão de objetos. Proposta: tratar remoção de componente e evitar ciclos de recriação não controlados.

### REF-2612 — IndicatorAdd

[REF, IndicatorAdd, p.PDF 5246–5246]. IndicatorAdd recebe subjanela e handle; subjanela inexistente pode ser criada e falha requer GetLastError. Proposta: manter controle de handle e identidade da janela.

### REF-2613 — IndicatorDelete

[REF, IndicatorDelete, p.PDF 5247–5247]. IndicatorDelete identifica short name, remove primeira duplicata e dependentes; não libera cálculo/handle, exigindo IndicatorRelease separadamente. Proposta: short names com parâmetros e ownership explícito para não remover outro indicador.

### REF-2614 — IndicatorsTotal

[REF, IndicatorsTotal, p.PDF 5248–5248]. IndicatorsTotal permite inventário por gráfico/subjanela; assinatura impressa inclui chart_id, divergindo do resumo de método. Conferir include; usar total com índices zero-based.

### REF-2615 — IndicatorName

[REF, IndicatorName, p.PDF 5249–5249]. IndicatorName devolve short name por índice zero-based; é distinto do arquivo iCustom e recomendado conter parâmetros. Proposta: inventário antes de remoção segura.

### REF-2616 — Navigate

[REF, Navigate, p.PDF 5250–5250]. Navigate desloca gráfico relativo a ENUM_CHART_POSITION por número de barras. Proposta: navegação de diagnóstico sem confundir barras visíveis com intervalo completo de dados.

### REF-2617 — Symbol

[REF, Symbol, p.PDF 5251–5251]. Symbol retorna nome do símbolo ou string vazia sem vínculo. Proposta: rejeitar contexto vazio antes de ligar dados ao painel.

### REF-2618 — Period

[REF, Period, p.PDF 5252–5252]. Period retorna ENUM_TIMEFRAMES ou 0 sem vínculo. Proposta: distinguir ausência de vínculo de convenção de período atual nas chamadas que aceitam 0.

### REF-2619 — Redraw

[REF, Redraw, p.PDF 5253–5253]. Redraw solicita redesenho do gráfico vinculado. Proposta: agrupar alterações visuais antes da chamada.

### REF-2620 — GetInteger

[REF, GetInteger, p.PDF 5254–5254]. GetInteger tem retorno direto e variante bool com saída por referência para propriedade long/ENUM_CHART_PROPERTY_INTEGER; falha pode ser investigada com GetLastError. Proposta: preferir variante bool para distinguir ausência de valor legítimo; propriedades numéricas permitem subjanela.

### REF-2621 — SetInteger

[REF, SetInteger, p.PDF 5255–5255]. SetInteger configura propriedade long/ENUM_CHART_PROPERTY_INTEGER e retorna bool. Proposta: validar identificador/tipo e resultado de cada mudança visual antes de declarar configuração aplicada.

### REF-2622 — GetDouble

[REF, GetDouble, p.PDF 5256–5256]. GetDouble tem retorno direto e variante bool com saída por referência para propriedade double/ENUM_CHART_PROPERTY_DOUBLE; falha pode ser investigada com GetLastError. Proposta: preferir variante bool para distinguir ausência de valor legítimo; propriedades numéricas permitem subjanela.

### REF-2623 — SetDouble

[REF, SetDouble, p.PDF 5257–5257]. SetDouble configura propriedade double/ENUM_CHART_PROPERTY_DOUBLE e retorna bool. Proposta: validar identificador/tipo e resultado de cada mudança visual antes de declarar configuração aplicada.

### REF-2624 — GetString

[REF, GetString, p.PDF 5258–5258]. GetString tem retorno direto e variante bool com saída por referência para propriedade string/ENUM_CHART_PROPERTY_STRING; falha pode ser investigada com GetLastError. Proposta: preferir variante bool para distinguir ausência de valor legítimo; propriedades numéricas permitem subjanela.

### REF-2625 — SetString

[REF, SetString, p.PDF 5259–5259]. SetString configura propriedade string/ENUM_CHART_PROPERTY_STRING e retorna bool. Proposta: validar identificador/tipo e resultado de cada mudança visual antes de declarar configuração aplicada.

### REF-2626 — SetSymbolPeriod

[REF, SetSymbolPeriod, p.PDF 5260–5260]. SetSymbolPeriod troca símbolo/timeframe; NULL/0 usam contexto atual, retorna bool. Proposta: tratar mudança de contexto como ação explícita e revalidar fontes do painel.

### REF-2627 — ApplyTemplate

[REF, ApplyTemplate, p.PDF 5261–5261]. ApplyTemplate aplica arquivo de template e retorna bool. Proposta: transformação visual explícita com evidência anterior/posterior; página não prova preservação do programa ou sucesso operacional.

### REF-2628 — ScreenShot

[REF, ScreenShot, p.PDF 5262–5262]. ScreenShot salva estado atual em GIF com dimensões/alinhamento. Proposta: evidência candidata de UI deve verificar arquivo e conteúdo visual; esta leitura não gerou screenshot.

### REF-2629 — WindowOnDropped

[REF, WindowOnDropped, p.PDF 5263–5263]. WindowOnDropped retorna subjanela de soltura do expert/script (0 principal). Proposta: inicialização interativa, não fonte de estado financeiro.

### REF-2630 — PriceOnDropped

[REF, PriceOnDropped, p.PDF 5264–5264]. PriceOnDropped retorna preço do ponto de soltura. Limite: coordenada de interação não é cotação confirmada nem preço de execução.

### REF-2631 — TimeOnDropped

[REF, TimeOnDropped, p.PDF 5265–5265]. TimeOnDropped retorna datetime do ponto de soltura. Limite: não substituir relógio/evento de mercado por posição visual.

### REF-2632 — XOnDropped

[REF, XOnDropped, p.PDF 5266–5266]. XOnDropped retorna coordenada X do ponto de soltura. Proposta: posicionamento inicial de componente visual apenas.

### REF-2633 — YOnDropped

[REF, YOnDropped, p.PDF 5267–5267]. YOnDropped retorna coordenada Y do ponto de soltura. Proposta: combinar com dimensões atuais antes de posicionar painel.

### REF-2634 — Save

[REF, Save, p.PDF 5268–5268]. Save virtual grava parâmetros em handle binário previamente aberto com FileOpen e retorna bool. Proposta: persistência visual separada dos dados normativos, validar I/O.

### REF-2635 — Load

[REF, Load, p.PDF 5269–5269]. Load virtual restaura parâmetros de handle binário já aberto e retorna bool. Proposta: validar arquivo e retorno sem tratá-lo como validação de estado Stoikus.

### REF-2636 — Type

[REF, Type, p.PDF 5270–5270]. Type retorna identificador 0x1111 para CChart. Proposta: discriminação de classe em coleção, não versão de produto nem código de erro.

## Ledger

`reference-batch-14b-coverage.json` conserva lista exata de páginas `consolidation_full_text_pages`, hashes originais de cada texto de página, hashes dos lotes, IDs com notas e delimitação dos ancestrais. Extração não foi usada como substituto da leitura: o texto integral foi exposto antes da redação. Nenhuma alteração em produto, manual, harness ou Git.
