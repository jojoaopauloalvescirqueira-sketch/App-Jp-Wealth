# Ciclo de atualização da PWA

## Diagnóstico

A caracterização anterior observou uma sessão híbrida: recursos da página antiga e controller novo. A causa não foi a busca de atualização de `sw.js` pelo worker antigo; essa busca é feita pelo mecanismo próprio do navegador. O problema era o takeover imediato: `skipWaiting()` permitia ativação durante a existência de abas antigas e `clients.claim()` então passava a controlar essas abas.

## Política aprovada

O worker novo é instalado, mas permanece em `waiting` enquanto existir qualquer cliente controlado pelo worker anterior. Não há recarga automática, mensagem de ativação, nova URL de worker ou takeover forçado. As abas já carregadas e a navegação que descobre a publicação continuam integralmente no build anterior: o controller ativo entrega seu `index.html` cacheado e os recursos saem do mesmo cache versionado. O bootstrap do HTML antigo chama `registration.update()`, portanto o worker novo é descoberto e instalado sem executar HTML novo sobre scripts antigos. Depois que todos os clientes antigos fecham, a ativação normal ocorre e a próxima abertura recebe integralmente o build novo.

`clients.claim()` permanece no evento `activate`. Sem `skipWaiting()`, ela só é executada depois da ativação normal e não antecipa a troca de controller das abas antigas.

## Registro e build

O registro usa `updateViaCache: 'none'`, para que as buscas do script e de seus imports não reutilizem HTTP cache obsoleto. O URL e o scope permanecem `./sw.js` e `./`.

`index.html` contém um bootstrap inline mínimo que, no evento `load`, obtém o registro pronto e chama `registration.update()`. Ele fica no documento para que a própria navegação coerente entregue pelo cache antigo descubra a publicação, mesmo quando o script externo de registro também vem desse cache. `src/js/40-app/06-app-icons.js` chama `registration.update()` depois de registrar o worker, cobrindo a instalação corrente e carregamentos futuros. Essas chamadas somente descobrem o worker publicado: nenhuma delas força ativação, recarga ou troca de controller.

`tools/rebuild_monolith.py` gera `build-id.js` a partir de hash reproduzível do HTML (sem a linha gerada), CSS, manifest JavaScript, worker, scripts e manifesto PWA declarados. Os ícones usam a versão explícita `ICON_CACHE_VERSION` de `sw.js`, que deve ser incrementada quando seus bytes mudarem. A página carrega o Build ID antes dos scripts do terminal e o worker usa `importScripts`. O identificador não pertence a `S` nem a qualquer backup.

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
- Alterar um ícone sem também incrementar `ICON_CACHE_VERSION` não muda o Build ID; esse pareamento manual deve ser preservado até que os ícones integrem o fingerprint oficial.
