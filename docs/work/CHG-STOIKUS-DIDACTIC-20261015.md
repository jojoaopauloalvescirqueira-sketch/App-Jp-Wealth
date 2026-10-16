# Stoikus — didática publicada (2026-10-15 UTC)

# Stoikus — apresentação e instalação explicadas

Pedido: melhorar a didática de funcionamento, instalação e primeiro uso no site JP Wealth. A mudança mantém Stoikus 1.22.2/interface R3, cálculo 1.9.0 e todos os pacotes e fontes MQL.

## O que mudou

- Introdução em linguagem corrente: os programas executam no MT5; o site entrega arquivos e orienta o processo.
- Quatro componentes, dois gráficos: Monitor no gráfico de apoio; Conta e NoCuda no gráfico de trabalho; Abrir Painéis acrescenta os indicadores e encerra normalmente.
- Um roteiro de seis etapas: baixar kit/pin, conferir, compilar em estágio temporário, conferir recibos e copiar apenas quatro EX5, abrir os gráficos e fazer o primeiro uso.
- Requisitos visíveis antes do download; preparo de um terminal demo separado e identificação de executável, MetaEditor e pasta MQL5.
- Comandos fiéis ao kit selado, resultado esperado e ponto de parada em cada fase. Tabelas técnicas, SDK e parâmetros ficam em detalhes consultáveis.
- Ajuda por sintoma e estados do Monitor com motivo e próxima ação. Explicações da versão antiga sobre F7/cópia indiscriminada, fonte 8 e NoCuda 90% foram reconciliadas com o candidatoR3.

## Gauntlet e revisão

Referência de clareza: instalação oficial Position Sizer da EarnForex. A comparação A/B foi textual e heurística; os materiais têm escopo e extensão diferentes e continham pistas de identidade. Não constitui teste cego pleno, comparação visual, superioridade de mercado ou medida de compreensão com pessoas. Um crítico independente encontrou um P2 de pré-requisitos tardios e identificação do terminal; a R2 resolveu o problema e foi reavaliada.

A primeira verificação de 200% encontrou transbordamento no roteiro de seis colunas. A correção usa grade intrínseca, mantendo fontes e alvos; o antes/depois e a tentativa PRODUCT_FAIL foram preservados. O verificador estrutural também confundiu links de documentação com dependências externas; a correção separada conserva o bloqueio de recursos remotos e recebe regressão própria.

## Limites

O kit atual é ZIP de preparação para compilação, sem instalador EXE. Não foram instalados nem compilados programas no MT5 nesta mudança. Compilação, execução nativa, aceite humano e Windows x64 permanecem NOT_RUN. A prévia usa dados fictícios. A comparação textual e os testes do navegador não substituem esses ensaios. PWA/offline na hospedagem não foi revalidado; a evidência anterior permanece INCONCLUSIVE.

Os dados financeiros e preferências do navegador não foram modificados. Nenhuma ação no GitHub do projeto, MetaTrader, conta ou Parallels faz parte desta entrega. O repositório interno Sites é usado somente para publicar o site existente, mantendo a audiência pública.

## Evidências

As tentativas de adaptação dos testes de apresentação e os diagnósticos auxiliares permanecem separados dos resultados de produto. Oráculos financeiros, inventários e recusas de integridade foram preservados e revistos. A validação e a publicação abaixo conservam separadamente as tentativas anteriores e seus resultados.

## Publicação e provas finais

Publicado no mesmo site JP Wealth, versão de hospedagem 6, mantendo audiência pública. Stoikus continua1.22.2/interface R3; não houve nova versão dos programas.

- URL: https://jp-wealth-software.jojoaopauloalvescirq.chatgpt.site/#genetrixOverviewPanel
- Fonte interna Sites: 050cf7a81c30d715df73a1861f2e3a5bcbe1f408; build web 1e112dad5cf7ded7.
- Arquivo oficial: 168arquivos, contendo 167 estáticos exatos e manifesto de hospedagem; nenhum arquivo reempacotado manualmente.
- Comparação com site v5: apenas index.html, src/styles/app.css e build-id.js alterados; 164 estáticos e todos os caminhos preservados. HTML externo ao Stoikus byte a byte igual.
- 154 fontes/artefatos protegidos, mais manifesto atual, preservados por hash. Pacotes históricos públicos conferidos no destino real.

| Verificação | Resultado |
|---|---|
| Guia de uso e downloads/recusas de integridade | PASS, usage-R8 |
| Página HTTP, arquivo, portátil, navegação, teclado e 200% | PASS, leverage-page-R6 |
| Jornada/temas/telas e âncoras reais | PASS, 30 vistas R4; capturas móveis estacionárias R5 |
| Suíte geral original |56 PASS/1 PRODUCT_FAIL: falso bloqueio dos três hyperlinks oficiais pelo verificador |
| Correção estrutural integrada | PASS, structure-corrective-R2 |
| Regressão do guard de recursos |84/84 PASS em Python 3.9.6 e3.12.14, mesmo harness e expectativas |
| Freeze depois da correção |1.057 fontes/saídas/testes;167 estáticos idênticos aos usados nos 56 checks de runtime |
| Bytes na hospedagem |12 caminhos conferidos, incluindo atuais e ZIPs históricos |
| Navegador na hospedagem |5 abas,5 downloads exatos; sem erro de página nem mudança de estado/dados |

O resultado56/1 foi preservado e a resolução corretiva é separada. Não foi sintetizado full 57/57. Apenas o validador e sua regressão adicional mudaram depois do primeiro full; os outros1.055 arquivos de entrada e todo o mapa de hashes dos 167 arquivos estáticos permaneceram iguais. As 56 verificações de runtime não precisaram ser repetidas por esse delta de control plane. A primeira integração do guard registrou82/84 em Python 3.12 por diferença de RCDATA; foi corrigida sem mudar o harness e o reensaio84/84 nos dois runtimes foi revisto independentemente.

O guard é uma política conservadora de tokens da fonte canônica. Permite tokens de navegação a[href], inclusive literais inertes; recusa tokens de recursos remotos e ambiguidades. Não é um parserHTML5 geral nem scanner de CSS/JavaScript dinâmico. Pareceres, tentativas e mudanças explícitas desse contrato estão em evidence/validator-fix/. Nenhum P1/P2 concreto permaneceu identificado no recorte final.

A inspeção online usou a credencial de serviço/owner fornecida pelo próprio Sites, restrita ao domínio. Não prova acesso anônimo; o403CLI anterior continua descrito como limite de acesso da inspeção. O serviço confirmou audiência public. A diferença do hash do HTML servido decorre da injeção da hospedagem; o bloco Stoikus exato foi verificado e os demais recursos comparados por SHA-256. A prévia HTML foi conferida pelo download real de bytes incorporados; seu redirecionamento isolado não foi confundido com o transporte do download.

As 12 capturas R4 foram inspecionadas; uma captura 390/claro ainda mostrava o drawer durante fechamento. A recaptura R5 aguarda estado fechado observável, confirma visibility:hidden e registra 8 capturas móveis sem esse artefato. A captura inicial móvel não alcança todas as seções do documento; navegação/âncoras, alvos e reflow têm testes próprios.

## Continuidade

Os seis arquivos de fonte/teste diretamente editados foram integrados à worktree de continuidade, com backup e guardas; os derivados do candidato foram gerados pelos scripts oficiais no projeto congelado. A worktree contém também um Guia do site ainda não publicado: suas alterações foram preservadas e excluídas da composição pública. Gerar novamente o build dessa worktree deve considerar esse delta antes de qualquer publicação.

Esta pasta conserva candidate-sources.zip com 1.057 arquivos conferidos, site-didactic-v6.tar.gz oficial e evidence/ completo. O ZIP de candidato é para desenvolvimento/auditoria; não é pacote de instalação do EA. Os caminhos /private/tmp são de execução; estes arquivos duráveis permitem recuperar o trabalho. Nenhum commit/push/PR no GitHub do projeto foi feito; o commit050cf7a pertence somente ao repositório interno Sites.
