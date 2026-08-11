# Ciclo de atualização da PWA

## Diagnóstico

A caracterização anterior observou uma sessão híbrida: recursos da página antiga e controller novo. A causa não foi a busca de atualização de `sw.js` pelo worker antigo; essa busca é feita pelo mecanismo próprio do navegador. O problema era o takeover imediato: `skipWaiting()` permitia ativação durante a existência de abas antigas e `clients.claim()` então passava a controlar essas abas.

## Política aprovada

O worker novo é instalado, mas permanece em `waiting` enquanto existir qualquer cliente controlado pelo worker anterior. Não há recarga automática, mensagem de ativação, nova URL de worker ou takeover forçado. As abas já carregadas continuam integralmente no build anterior. A navegação que descobre a publicação, porém, pode ser transitória: recebe o HTML novo pela estratégia network-first enquanto ainda usa o controller e recursos cache-first do worker anterior. Esse cliente não deve ser tratado como um build novo completo. Depois que todos os clientes antigos e transitórios fecham, a ativação normal ocorre e a próxima abertura recebe integralmente o build novo.

`clients.claim()` permanece no evento `activate`. Sem `skipWaiting()`, ela só é executada depois da ativação normal e não antecipa a troca de controller das abas antigas.

## Registro e build

O registro usa `updateViaCache: 'none'`, para que as buscas do script e de seus imports não reutilizem HTTP cache obsoleto. O URL e o scope permanecem `./sw.js` e `./`.

`index.html` contém um bootstrap inline mínimo que, no evento `load`, obtém o registro pronto e chama `registration.update()`. Ele fica no documento porque a navegação é network-first mesmo quando o script externo de registro ainda vem do cache antigo. `src/js/40-app/06-app-icons.js` também chama `registration.update()` depois de registrar o worker, cobrindo a instalação corrente e carregamentos futuros. Essas chamadas somente descobrem o worker publicado: nenhuma delas força ativação, recarga ou troca de controller.

`tools/rebuild_monolith.py` gera `build-id.js` a partir de hash reproduzível do HTML (sem a linha gerada), CSS, manifest JavaScript, worker, scripts e manifesto PWA declarados. Os ícones usam a versão explícita `ICON_CACHE_VERSION` de `sw.js`, que deve ser incrementada quando seus bytes mudarem. A página carrega o Build ID antes dos scripts do terminal e o worker usa `importScripts`. O identificador não pertence a `S` nem a qualquer backup.

## Cache e offline

O precache é atômico: falha de qualquer recurso crítico remove o cache parcial e impede a instalação. `sw.js` não é precacheado. Caches antigos só são removidos na ativação válida e somente se o nome começar por `jp-wealth-`; caches externos são preservados.

Navegações usam network-first com fallback para `index.html` do cache ativo. Recursos internos usam cache-first com correspondência exata, sem `ignoreSearch`; recursos externos seguem à rede e não são adicionados automaticamente ao cache estático.

## Hosting e publicação

Para Netlify, `_headers` aplica a `sw.js`, `index.html` e `/`:

```text
Cache-Control: no-cache, max-age=0, must-revalidate
```

Não usar `immutable` para esses caminhos. Após publicar uma alteração, abas que já estavam carregadas permanecem inteiramente na versão anterior. Uma nova navegação usada para descobrir a atualização pode ficar transitória; é necessário fechar também esse cliente antes de verificar o build novo. Fechar todos os clientes permite a ativação normal do worker novo. Verificar o ciclo com:

```bash
python3 tools/rebuild_monolith.py
python3 tools/service_worker_upgrade_test.py
```

O teste muda o servidor de uma raiz antiga para uma nova, abre uma navegação de descoberta e aguarda o estado `waiting/installed` por polling no harness Python. Ele não chama `registration.update()` externamente: a descoberta deve partir do bootstrap do produto. O teste confirma HTML novo com controller antigo no cliente transitório, ausência de `controllerchange` nas duas abas antigas, ativação após o fechamento de todos os clientes, build novo online e offline e preservação de cache externo.

## Riscos residuais

- O navegador decide o momento exato da ativação após o último cliente antigo desaparecer; a próxima abertura é o ponto de verificação operacional.
- Durante a descoberta, o cliente transitório pode combinar o HTML publicado com controller e recursos do cache anterior; ele deve ser fechado, não usado como evidência de build íntegro.
- Uma publicação parcialmente distribuída pelo provedor ainda pode falhar o precache; nesse caso o worker anterior permanece ativo, que é o comportamento seguro.
- A política não oferece atualização imediata por decisão: uma aba antiga só muda quando o usuário a fecha.
- Alterar um ícone sem também incrementar `ICON_CACHE_VERSION` não muda o Build ID; esse pareamento manual deve ser preservado até que os ícones integrem o fingerprint oficial.
