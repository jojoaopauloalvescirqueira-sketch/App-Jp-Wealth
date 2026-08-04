# Ciclo de atualização da PWA

## Diagnóstico

A caracterização anterior observou uma sessão híbrida: recursos da página antiga e controller novo. A causa não foi a busca de atualização de `sw.js` pelo worker antigo; essa busca é feita pelo mecanismo próprio do navegador. O problema era o takeover imediato: `skipWaiting()` permitia ativação durante a existência de abas antigas e `clients.claim()` então passava a controlar essas abas.

## Política aprovada

O worker novo é instalado, mas permanece em `waiting` enquanto existir qualquer cliente controlado pelo worker anterior. Não há recarga automática, mensagem de ativação, nova URL de worker ou takeover forçado. Depois que todas as abas antigas fecham, a ativação normal ocorre e a próxima abertura recebe integralmente o build novo.

`clients.claim()` permanece no evento `activate`. Sem `skipWaiting()`, ela só é executada depois da ativação normal e não antecipa a troca de controller das abas antigas.

## Registro e build

O registro usa `updateViaCache: 'none'`, para que as buscas do script e de seus imports não reutilizem HTTP cache obsoleto. O URL e o scope permanecem `./sw.js` e `./`.

`tools/rebuild_monolith.py` gera `build-id.js` a partir de hash reproduzível do HTML (sem a linha gerada), CSS, manifest JavaScript, worker, scripts, manifestos e ícones. A página o carrega antes dos scripts do terminal e o worker usa `importScripts`. O identificador não pertence a `S` nem a qualquer backup.

## Cache e offline

O precache é atômico: falha de qualquer recurso crítico remove o cache parcial e impede a instalação. `sw.js` não é precacheado. Caches antigos só são removidos na ativação válida e somente se o nome começar por `jp-wealth-`; caches externos são preservados.

Navegações usam network-first com fallback para `index.html` do cache ativo. Recursos internos usam cache-first com correspondência exata, sem `ignoreSearch`; recursos externos seguem à rede e não são adicionados automaticamente ao cache estático.

## Hosting e publicação

Para Netlify, `_headers` aplica a `sw.js`, `index.html` e `/`:

```text
Cache-Control: no-cache, max-age=0, must-revalidate
```

Não usar `immutable` para esses caminhos. Após publicar uma alteração, manter as abas antigas abertas é seguro: elas ficam inteiramente na versão anterior; fechar todas permite a ativação do worker novo. Verificar o ciclo com:

```bash
python3 tools/rebuild_monolith.py
python3 tools/service_worker_upgrade_test.py
```

## Riscos residuais

- O navegador decide o momento exato da ativação após o último cliente antigo desaparecer; a próxima abertura é o ponto de verificação operacional.
- Uma publicação parcialmente distribuída pelo provedor ainda pode falhar o precache; nesse caso o worker anterior permanece ativo, que é o comportamento seguro.
- A política não oferece atualização imediata por decisão: uma aba antiga só muda quando o usuário a fecha.
