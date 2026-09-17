# Ícones PWA sólidos — 2026-09-17

Pedido atual: eliminar a borda branca observada no iPhone, preencher o ícone
com fundo totalmente sólido e ampliar as letras. Este pedido substitui o
acabamento transparente anteriormente aprovado; o registro anterior é histórico.

## Fronteira e compreensão

Raiz `/Users/joaopauloalves/.codex/nocuda-tools/20260917/product`, branch existente
`codex/nocuda-tools-20260917`, HEAD `6ef8d7689130b8476c64fd90881e00050b2725e9`.
Preexistentes: launcher e mudança de nome, preservados. Snapshot de recuperação
em `tools/.artifacts/pwa-solid/before`. Preflight audit/edit: PASS com alterações
conhecidas e aviso histórico de frescor já delimitado.

O JP Wealth é uma aplicação financeira local/PWA. Os PNGs representam sua marca
na instalação; 06-app-icons coordena os links conforme a preferência existente.
Hoje há cerca de 5% de margem transparente e arredondamento embutido. O novo
arquivo será quadrado, opaco até as bordas, com texto maior; o sistema aplica sua
própria máscara. Vermelho/Preto, JP WEALTH e BUILT ON METHOD são preservados.

Escopo: N0-V nos seis PNGs/preview; manutenção derivada N1 no versionamento de
assets e teste de produto que hoje exige transparência. O usuário autorizou a
correção visual; não é mudança de política do worker, gate ou Harness.
Arquivos permitidos: seis PNGs; 06-app-icons e constante correspondente do SW;
manifest JS/hash; CSS somente recorte da prévia; contrato de imagem em
brand_identity_contract_test; build-id/portátil via gerador oficial; este CHG,
ACTIVE-TASK e referências descritivas de assets em PWA-UPDATE-LIFECYCLE e
ARCHITECTURE (ambos em docs/architecture).
Sem dados, schema, backup, cálculo, preferência nova, identidade/start_url/scope
do PWA, servidor, dependência ou alteração de gatilhos de atualização.

Fontes: AGENTS, preflight/change-control, contexto e arquitetura PWA; contrato
anterior de transparência; código/assets e testes de marca. Harness §§12–14 e
36–48, SHA `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`.
Apple App Icons e Safari/WebKit: ícones quadrados e opacos, máscara do sistema;
apple-touch-icon é a fonte prioritária quando fornecida no iOS.

## Critérios e recuperação

Fundos opacos, contínuos até as quatro bordas, sem moldura clara; logotipo
centralizado maior, grafia correta, variantes consistentes e legíveis em tamanho
pequeno. Contrato focal deve testar opacidade e preenchimento em vez do contrato
visual substituído, mantendo identidade, preferências e ciclo conservador.
Validar PNGs/links, marca no navegador, build, atualização/offline e gate aplicável.
Não confundir prévia com instalação física no iPhone nem integração na main.

Rollback: restaurar somente o delta deste snapshot e reconstruir; preservar
nome novo, launcher e bases do usuário. Sem commit/push/merge neste pedido.


## Edição e distribuição dos assets

Edição pelo image_gen integrado, sem API externa/CLI. Matrizes geradas 1254×1254
copiadas para `assets/pwa-icon-primary.png` e `assets/pwa-icon-secondary.png`.
Exports 192/512 pelo `sips -z TAM TAM MATRIZ --out DESTINO`, sem outra alteração
criativa dos pixels. PNGs RGB sem alpha; marca branca com largura 90,3% e
altura 38,7%, comparada a 73,2%/31,1% no vermelho anterior. Aproximadamente23%
mais larga; limites inteiros arredondam conforme a resolução.

Prompt vermelho usado:

> Use case: precise-object-edit. Edit target: attached JP WEALTH red PWA icon. Produce a single square 1024x1024 production app icon, fully opaque, edge to edge flat saturated red #e60000 background. Remove all transparent margins, white edges, borders, rounding, gradients, shadows and texture: every edge and all four square corners must be the same solid red. Preserve the exact distinctive white JP monogram and angular WEALTH lettering from the reference, with exact white tagline BUILT ON METHOD. Enlarge the entire centered three-line brand lockup: WEALTH should span about 84% of the canvas width (8% margin each side), top JP proportionate, tagline centered beneath and legible. Preserve relative proportions and exact spelling, no new shapes. Vertical lockup centered. This is the actual square PNG icon file, not a mockup; no phone, no outer frame. Only output the finished icon.

Prompt preto usado (sobre a imagem vermelha já editada):

> Use case: precise-object-edit. Edit this exact app icon. Change ONLY the solid red background to solid pure black #000000 edge to edge, including all four square corners. Preserve precisely the same white JP monogram, white WEALTH lettering, white BUILT ON METHOD tagline, their positions, shape, scale and spacing. No new layout, no texture, no gradients, no transparency, no border, no rounding, no shadows. Output the opaque square black variant as a production PNG, not a mockup.

Resultado medido: 1254px e marca 90,3%; o prompt é intenção, as medidas acima são
as efetivamente obtidas. O raster vermelho conserva pequenas variações de cor;
a opacidade e a ausência de margens claras são integrais. Fontes Apple:
[ícones e máscara do sistema](https://developer.apple.com/design/human-interface-guidelines/app-icons/)
e [precedência do apple-touch-icon no iOS](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/).

## Evidências em andamento

Build `2f6b01f3daddaabe`. Contrato dos seis PNGs: PASS, com revisão independente
do decoder RGB/RGBA contra Pillow e fixtures em memória. Marca em navegador:
PASS em reexecução isolada; a primeira execução do gate falhou, registro original
preservado. Reprodutibilidade do build e upgrade/offline: PASS.

Na UI CUA, `127.0.0.1:8872` continuou com recursos antigos após reabertura; sem
limpeza de caches nem takeover. A origem isolada `localhost:8872` entregou o link
Apple `?v=20260917-solid-r1` e os ícones novos. Tema claro/escuro e largura
1280/390 conferidos visualmente. O aviso textual legado do seletor tem overflow
no mobile, fora do delta dos ícones; nenhuma correção adjacente foi aplicada.
O teste automatizado de upgrade confirmou o ciclo normal com duas abas/offline,
mas a tentativa na UI não é contada como upgrade confirmado dessa origem antiga.

Instalação física no iPhone: NOT_RUN. Main/atalho local não atualizados; este
candidate não é publicação ou aceite humano.


## Auditoria de escopo e impacto

`git diff --check`: PASS. Comparação contra o snapshot: index e nomes novos
intactos; os únicos deltas de JS/SW são as constantes de versão dos assets.
Manifest JS atualiza somente hash correspondente nesta etapa. CSS muda apenas
`border:1px` para `border:0` na imagem de prévia. O portátil é exatamente o
anterior com novo build/versionamento e essa regra CSS; comparação integral PASS.
Wordmarks do cabeçalho, preferência, id/start_url/scope, backup, dados e motor
financeiro não têm delta. Nenhum dado real foi usado nos testes.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED

BASIS: agentes/validadores consultam o contrato de imagem e as descrições de
assets em ARCHITECTURE/PWA-UPDATE-LIFECYCLE. Estes agora descrevem fundo opaco;
ACTIVE-TASK aponta para a mudança atual. Contrato de opacidade substitui a
exigência visual anterior por pedido expresso. Preflight, gate, instruções,
routing, skills, registries e normas não mudam. Arquivos históricos permanecem
históricos; nome/launcher têm registros próprios preservados. INDEX NOT REQUIRED;
nenhuma memória/índice externo foi escrito. Reconciliação limitada à descrição
dos ícones locais, não à aceitação ou integração geral do projeto.

## Diagnóstico limitado do gate geral

Dashboard isolado: main passou; candidate falhou por timeout de boot antes das
asserções visuais de um caso. Cópia temporária com os 17 arquivos pré-ícones
restaurados passou 24 casos e falhou por `net::ERR_SOCKET_NOT_CONNECTED` com
pageerror vazio. Os 94 hashes JS e o teste foram conferidos. Isso revela fragilidade
na execução, mas não reproduz a mesma falha nem estabelece sua causa. Logs
`dashboard-main.log`, `dashboard-candidate.log`, `dashboard-pre-icons.log` em
`tools/.artifacts/pwa-solid`. Não classificar silenciosamente como baseline.
Navegação PF passou na reexecução isolada, preservando o registro do gate.


## Resultado final desta execução

Gate standard no Python 3.12: **36 PASS / 10 PRODUCT_FAIL**, sem outras categorias.
Comando: `tools/quality_gate.py --tier standard --artifact tools/.artifacts/pwa-solid/standard.json`.
Relatório/log preservados, sem reclassificação nem alteração de gate.

| Suíte com falha original | Resultado observado |
|---|---|
| Dashboard Macro | Timeout aguardando boot/cards; comparação descrita acima. |
| Marca no navegador | Painel ainda sem conteúdo; reexecução isolada PASS. |
| Galton | Helper `$` indisponível na sonda. |
| Execução em três colunas | Timeout na sonda. |
| Navegação PF | Dependência de render indisponível; reexecução isolada PASS. |
| Cotação USD/BRL | Estado esperado pela sonda indisponível. |
| Finalização Alladin | Timeout e `bindFsSeg` indisponível. |
| Serialização da sessão | Timeout na sonda. |
| Cadastro Alladin | Timeout na sonda. |
| Ledger Alladin | Timeout na sonda. |

Causa definitiva dessas falhas gerais não estabelecida. Não se declara gate
standard aprovado, regressão financeira corrigida ou prontidão para integração.
A entrega é o delta visual local verificado: contrato dos PNGs, marca em teste
isolado, UI dos ícones, build reproduzível e atualização/offline aprovados.
As suítes financeiras não foram alteradas para contornar as falhas.

Arquivos finais: `assets/pwa-icon-primary.png`, `assets/pwa-icon-secondary.png`
e exports correspondentes 192/512. Prompts e método de geração acima.
Fingerprint dos arquivos em `tools/.artifacts/pwa-solid/fingerprint.json`.
Sem commit, push, merge, instalação iPhone ou migração de dados nesta etapa.
