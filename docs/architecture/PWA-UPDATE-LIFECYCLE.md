## Bolsas Globais — redesign local — 16/10/2026

Somente fontes de apresentação/controlador e predicado compartilhado mudam neste incremento; não há recurso de runtime, dependência ou protocolo novo. O gerador oficial atualiza fingerprints, manifesto e portátil, preservando a ordem dos scripts e os originais de calendário/globo. No celular, recolher o mapa adia sua solicitação ao loader; recursos precacheados não são executados por essa instalação. O ciclo conservador do worker abaixo continua vigente. Não usar uma página de prévia aninhada sob o scope do PWA: a navegação controlada recebe o index canônico; a prévia direta usa origem local separada.

## Bolsas Globais — recursos locais 15/10/2026

O precache acrescenta quatro scripts clássicos de coordenação, `src/data/market-hours/calendar-v1.json` e `src/vendor/aisol-dot-globe/aisol-globe.iife.js`. O sidecar `src/vendor/market-hours/runtime-payload.js` é exclusivo de file e permanece fora da lista web. A transferência de instalação da PWA não executa o IIFE; sua carga/execução é acionada pela entrada aceita. Portátil contém JSON inerte com os mesmos bytes. Build ID inclui insumos explícitos e verifica a correspondência do vendor congelado; nenhuma instalação ou requisição externa ocorre no build normal. O ciclo waiting/ativação/cache coerente descrito abaixo é preservado. [Contrato](MARKET-HOURS.md).

# Ciclo de atualização da PWA

## Diagnóstico

A caracterização anterior observou uma sessão híbrida: recursos da página antiga e controller novo. A causa não foi a busca de atualização de `sw.js` pelo worker antigo; essa busca é feita pelo mecanismo próprio do navegador. O problema era o takeover imediato: `skipWaiting()` permitia ativação durante a existência de abas antigas e `clients.claim()` então passava a controlar essas abas.

## Política aprovada

O worker novo é instalado, mas permanece em `waiting` enquanto existir qualquer cliente controlado pelo worker anterior. Não há recarga automática, mensagem de ativação, nova URL de worker ou takeover forçado. As abas já carregadas e a navegação que descobre a publicação continuam integralmente no build anterior: o controller ativo entrega seu `index.html` cacheado e os recursos saem do mesmo cache versionado. O bootstrap do HTML antigo chama `registration.update()`, portanto o worker novo é descoberto e instalado sem executar HTML novo sobre scripts antigos. Depois que todos os clientes antigos fecham, a ativação normal ocorre e a próxima abertura recebe integralmente o build novo.

`clients.claim()` permanece no evento `activate`. Sem `skipWaiting()`, ela só é executada depois da ativação normal e não antecipa a troca de controller das abas antigas.

## Registro e build

O registro usa `updateViaCache: 'none'`, para que as buscas do script e de seus imports não reutilizem HTTP cache obsoleto. O URL e o scope permanecem `./sw.js` e `./`.

`index.html` contém um bootstrap inline mínimo que, no evento `load`, obtém o registro pronto e chama `registration.update()`. Ele fica no documento para que a própria navegação coerente entregue pelo cache antigo descubra a publicação, mesmo quando o script externo de registro também vem desse cache. `src/js/40-app/06-app-icons.js` chama `registration.update()` depois de registrar o worker, cobrindo a instalação corrente e carregamentos futuros. Essas chamadas somente descobrem o worker publicado: nenhuma delas força ativação, recarga ou troca de controller.

`tools/rebuild_monolith.py` gera `build-id.js` a partir de hash reproduzível do HTML (sem a linha gerada), CSS, manifest JavaScript, worker, scripts, os dois manifestos PWA, os wordmarks e as matrizes dos ícones e seus exports opacos de 192 e 512 px, com fundo até as bordas, documentos normativos e próprio gerador declarados. Os ícones e manifestos usam a versão explícita `ICON_CACHE_VERSION` de `sw.js`, incrementada quando os bytes ou o mapeamento da marca mudam. A página carrega o Build ID antes dos scripts do terminal e o worker usa `importScripts`. O identificador não pertence a `S` nem a qualquer backup.

Na atualização de eficiência de 2026-10-14, `build-id.js` conserva somente ID e metadados leves, seguros também no contexto do worker. NoCuda e ZIPs Stoikus são obtidos pelo loader na ação do usuário; seus originais continuam no precache web. Os sidecars gerados para `file://` ficam fora desse precache e da ordem de scripts inicial. No portátil, essas famílias usam JSON inerte incorporado, interpretado sob demanda. O tratamento dos demais documentos abaixo permanece específico de cada documento. Os novos derivados integram a verificação de reprodutibilidade. Ver [contratos de eficiência](APP-EFFICIENCY.md).

## Cache e offline

O precache é atômico: falha de qualquer recurso crítico remove o cache parcial e impede a instalação. `sw.js` não é precacheado. Caches antigos só são removidos na ativação válida e somente se o nome começar por `jp-wealth-`; caches externos são preservados.

Navegações controladas usam o `index.html` canônico do cache ativo, com rede apenas como fallback excepcional se essa entrada estiver ausente. A primeira navegação ainda não controlada vem normalmente da rede. Recursos internos usam cache-first com correspondência exata, sem `ignoreSearch`; recursos externos seguem à rede e não são adicionados automaticamente ao cache estático. Assim, um controller antigo nunca combina HTML publicado novo com scripts ou CSS do cache anterior.

## Hosting e publicação

Para Netlify, `_headers` aplica a `sw.js`, `index.html` e `/`:

```text
Cache-Control: no-cache, max-age=0, must-revalidate
```

Não usar `immutable` para esses caminhos. Após publicar uma alteração, abas que já estavam carregadas e a navegação usada para descobrir a atualização permanecem inteiramente na versão anterior. É necessário fechar todos esses clientes antes de verificar o build novo; isso permite a ativação normal do worker novo. Verificar o ciclo com:

```bash
python3 tools/rebuild_monolith.py
python3 tools/service_worker_upgrade_test.py
```

O teste muda o servidor de uma raiz antiga para uma nova, abre uma navegação de descoberta e aguarda o estado `waiting/installed` por polling no harness Python. Ele não chama `registration.update()` externamente: a descoberta deve partir do bootstrap do produto. O teste confirma que a navegação de descoberta permanece integralmente no build antigo, que o worker novo chegou a `waiting`, que não houve `pageerror`, erro de console nem requisição falha, que as abas antigas não receberam `controllerchange`, e que, após o fechamento de todos os clientes, o build novo abre coerente online e offline com o cache externo preservado.

## Riscos residuais

- O navegador decide o momento exato da ativação após o último cliente antigo desaparecer; a próxima abertura é o ponto de verificação operacional.
- A primeira atualização a partir de um worker publicado antes desta política ainda obedece ao código antigo já instalado; esse cliente deve ser fechado e reaberto para concluir a transição. A garantia de navegação coerente vale a partir do worker que contém esta política.
- Uma publicação parcialmente distribuída pelo provedor ainda pode falhar o precache; nesse caso o worker anterior permanece ativo, que é o comportamento seguro.
- A política não oferece atualização imediata por decisão: uma aba antiga só muda quando o usuário a fecha.
- O navegador decide se atualiza metadados de uma instalação PWA já existente. A escolha em Configurações troca imediatamente cabeçalho, favicon, Apple touch icon e o manifesto oferecido para a próxima instalação; reinstalação pode ser necessária para ver o novo ícone instalado.


## Consulta normativa — adoção V11 (2026-09-08)

O PDF canônico e o Anexo Paramétrico pertencem ao fingerprint e ao cache do build.
Esses dois recursos recebem tratamento próprio antes do fallback de navegação do
shell, preservando seus bytes e a consulta offline. A regra não altera o ciclo de
instalação/ativação/atualização nem as demais rotas. No HTML portátil, o gerador
incorpora os originais em links de download com data URLs; não depende de /dist/docs
ou de uma pasta externa. O texto derivado também continua no leitor do onboarding.

## Documentação do projeto — correção AUD-10 (2026-10-12)

README.md e CHANGELOG.md recebem correspondência exata antes do fallback de navegação, da mesma forma que a consulta normativa. Esses dois documentos entram no precache atômico e no fingerprint explícito de rebuild_monolith.py. Uma aba controlada consulta os bytes documentais de seu próprio build, inclusive offline; a navegação para eles não recebe index.html.

No portátil, os links são incorporados como data URLs de download com os bytes originais. O gerador usa a lista explícita desses dois documentos, sem varrer diretórios. Sua fixture de PDF inclui os mesmos inputs obrigatórios. Isso não muda scope/URL do worker, waiting, activate, controllerchange ou recarga. A transição de build continua dependendo do fechamento dos clientes antigos.

A regressão tools/pwa_document_navigation_test.py usa um perfil sintético, verifica os links de Configurações sob controller online/offline, os bytes cacheados, a incorporação portátil e a preservação do estado. O servidor dessa fixture oferece Markdown como texto para observar a navegação; em hosting que baixa Markdown, o destino continua sendo o arquivo original. O teste service_worker_upgrade_test.py permanece necessário para o ciclo de atualização.
