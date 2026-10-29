# Preparação da entrega visual — 29/10/2026

Somente leitura das imagens/fontes existentes e escrita de roteiro/parecer em scratch. Não iniciei browser, teste concorrente, gerador ou edição do repositório durante o FULL iniciado às11:23BRT. O script abaixo foi apenas preparado e analisado por AST; não foi executado.

## Capturas atuais inspecionadas

Fonte declarada pelo inventário: build `aabc8d09faff4aee`, pacote econômico público local v2 servido em contexto descartável, oito eventos. O launcher fixa28/10/2026 às23:00UTC (20:00BRT); a captura não representa consulta ao mercado em29/10. Pacote SHA256 `6275de67ed8f13512941ac2f016bf9c7662d36c619551e4efb6c860a23492fcc`. Nenhum perfil/armazenamento do operador é carregado.

Os hashes das três imagens foram recalculados e correspondem ao inventory.json:

- `execEcal-1440-light.png`: `1cb894e101e147d6ed3882c985afff0654c1310b99cc6dbc6c01344b8a720459`.
- `calendarDialog-390-dark.png`: `db977acd553c4b4ee6e53fbaa0af3a78d9fd793055c4037703ddeb9027cf31dd`.
- `execEcal-320-light.png`: `3b2f4b3b6919b4f1013a45b7e5b9664bc0fac3e74ebf966fac15070c17f80c06`.

Em1440claro, mês e tabela estão lado a lado; os sete títulos acompanham as colunas, os números aparecem à direita e a hierarquia de data/resumo/Economia/eventos é legível. O título BOC Monetary Policy Report quebra em duas linhas sem atravessar a célula de valores. A captura mostra cinco linhas das oito existentes, dentro da área rolável; isso não significa ausência das demais.

No modal390escuro, o título principal quebra sem esconder os quatro controles. Mês/agenda ficam empilhados. Cada evento visível mantém identificação e Atual/Projeção/Anterior rotulados. A linha Overnight Rate apresenta2.50%/2.25% separados; Atual permanece travessão. No limite inferior há continuação cortada pela viewport do diálogo, coerente com rolagem; imagem estática não comprova a jornada de acesso restante.

No workspace320claro, os sete dias e os três valores econômicos aparecem sem corte horizontal aparente. Títulos longos e avisos quebram com altura automática. O conjunto econômico é mais extenso verticalmente e a imagem é uma captura longa do elemento, não uma única viewport do usuário.

Ressalva exata: na captura longa320, o botão flutuante azul de Notas se sobrepõe parcialmente ao aviso da linha BOC Press Conference. A combinação de screenshot longo de elemento com um controle position:fixed pode colocar o controle no meio do PNG, embora ele permaneça no canto da viewport real. A imagem, isoladamente, não prova conteúdo permanentemente inacessível nem autoriza concluir que toda a apresentação320 está sem sobreposições.

Para atribuição causal, comparei com o baseline preservado: `src/js/40-app/14-mvp-notes.js` é byte a byte igual; o prefixo do CSS que contém as regras do launcher de Notas também é idêntico. Portanto o controle fixo é preexistente a este delta. Ainda não foi demonstrado se a sobreposição daquela linha específica é nova, preservada ou somente característica da captura. O roteiro pós-FULL compara a mesma fixture e mede acesso por rolagem nos dois renderers sem mudar fonte, estilo ou conteúdo.

Os quatro impactos, detalhe aberto, toque real, leitor de tela, todos os estados de falha, acesso completo por rolagem e aceitação humana não podem ser aprovados a partir dessas três imagens. Os resultados funcionais/visuais executáveis pertencem aos recibos próprios, inclusive ao FULL ainda em andamento.

## Por que as imagens antigas não servem como antes/depois rigoroso

O RED original contém seis eventos SYN TABLE, com0,0.0%,−0.5% e1.2M, enquanto as capturas-current usam oito eventos do pacote público. Outras capturas do product-proposal mostram produto intermediário1e2e/8486 e detalhes abertos, não o produto final8cfa/31e. Não apresentá-las como comparação controlada do candidate atual.

O PREVIEW.json antigo registra buildbc08298ef8320bb0/JS1e2e, portanto também não identifica a captura-current/aabc. A entrega final deverá identificar o novo candidato e eventual URL de prévia verificada pelo responsável após os gates; esta revisão não acessou ou confirmou servidor/URL.

## Script preparado; execução proibida durante o FULL

Caminho: `/private/tmp/jpw-economic-calendar-table-20261028/product-proposal/capture-before-after-six.py`.
SHA256 preparado: `60175a21138dffc625ed30879fdd41aeb24bf0de7778fdf92aa46cf58b91c1ab`.
Estado: AST válido, execução/browser NOT_RUN.

O script exige `--after-full-confirmed` e recusa iniciar se ainda observar processo quality_gate.py --tier full. O responsável deve confirmar término e liberar a captura; o flag não é uma autorização automática. Exige diretório de saída novo sob product-proposal, não sobrescreve capturas anteriores e força request trace ao scratch. Usa contextos descartáveis, bloqueio de SW e bootstrap sintético que aborta rede desconhecida.

A comparação usa precisamente probe.fixture do RED original, hash `39fb08f84973c61771da8923bc8e5bc9e7a6b93637bebf355e78f6f71c2b5283`: seis eventos, relógio28/10/2026 às20:05UTC, mesma zonaAmerica/Sao_Paulo, mesmas strings de entrada e nenhuma fixture financeira pessoal. O domínio é comparado byte a byte entre todos os cenários e versões.

Antes: lê baseline-pending.tar.gz em RAM, verifica SHA256 `5c50501d04c0207027e1f9a9d43bc6980b25dad88fd827433d9058af7c3d9d3d`, lê somente membros19/CSS e serve esses bytes por overlay. Não extrai checkout ou arquivos-baseline no repositório. Exige JS75c783bd… e CSS3bc75488…

Depois: congela em RAM os arquivos atuais e exige JS `8cfaec067a59ba393ff2aa53ad097196460e64e6de111945d92d3da21c47a518` e CSS `31e7659038d380c2348919a7ffa4229be125c5893d03540a89f728e3ad3aed5e`, shellbuildaabc. Verifica novamente os inputs ao terminar.

Escopo da legenda obrigatório: **Antes = renderer/CSS baseline no shell atual; não é uma release antiga. Depois = renderer/CSS atuais no mesmo shell.** O adaptador16 recebe a mesma substituição sintética já usada pelo RED em ambos. O restante do shell permanece atual e comum, com hashes registrados. Não é comparação de dados públicos reais nem reprodução integral da distribuição histórica.

Cenários:1440claro/workspace,390escuro/modal e320claro/workspace, todos com altura1100. São seis screenshots de viewport real full_page=False, sem forçar largura do host, sem screenshot longo de elemento e com detalhes naturalmente recolhidos no produto atual. Baseline mantém sua proveniência naturalmente visível. As dimensões da viewport e o método são idênticos em cada par.

Com `--inspect-scroll-access`, após a captura principal320 o script examina avisos de horário e controles de fonte/detalhe dos seis eventos nas duas versões. Registra a posição inicial e a interseção com headerNotesBtn; depois usa scrollIntoView(center) nativo e cinco amostras de elementFromPoint para comprovar se o alvo chega integralmente a uma posição desobstruída. Salva screenshot da viewport real para sobreposição inicial/amostra ou eventual alvo ainda obstruído. Não altera fonte, CSS, DOM ou estado de dados. O resultado de captura não deve ser convertido em aprovação do produto; os achados de acesso ficam separados no inventário.

Comando preparado, para o responsável usar somente após término do FULL e liberação da captura:

```sh
PYTHONDONTWRITEBYTECODE=1 \
JP_WEALTH_CHROMIUM='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
'.superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3' \
'/private/tmp/jpw-economic-calendar-table-20261028/product-proposal/capture-before-after-six.py' \
--after-full-confirmed --inspect-scroll-access \
--out '/private/tmp/jpw-economic-calendar-table-20261028/product-proposal/comparison-six-after-full-1'
```

Executar na raiz CloudDocs real, sem usar a cwd Obsidian obsoleta. Não executar automaticamente nem em paralelo ao FULL. Nenhuma captura comparativa nova foi produzida nesta preparação.
