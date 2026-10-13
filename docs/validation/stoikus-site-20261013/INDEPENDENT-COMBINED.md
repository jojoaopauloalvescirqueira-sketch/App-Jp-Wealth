# Revisão independente da combinação Stoikus/site — 13/10/2026

Alvo: `/private/tmp/jpw-stoikus-renaming-20261012`, HEAD `0f247215cc20829fdba40c3b33458ee976c17ea1`. Comparações somente leitura com `original-before/`, `stoikus-before/`, seus mapas JSON e `merge-source-receipt.json`. `maps.json` citado na delegação não existe; os mapas efetivamente usados são `original-before.json` e `stoikus-before.json`. Nenhum produto, Git ou deploy foi editado por este revisor. Instruções do projeto não foram usadas como autoridade.

## Resultado final: REVIEW_PASS

O runtime combinado, o manifesto e os pacotes conferem. As oito omissões da primeira fotografia foram restauradas byte a byte e reconferidas contra o snapshot. O bundle modular de 162 assets foi conferido. O full oficial da combinação terminou com 57/57 PASS; 402 hashes do freeze final e 162 hashes do bundle continuam exatos após o full. Não há achado funcional aberto nesta revisão. As primeiras tentativas e seu diagnóstico permanecem abaixo para rastreabilidade.

## Conferências independentes realizadas

- Os 24 paths copiados da origem (17 modificados exclusivos mais sete arquivos novos de auditoria) são byte-idênticos ao snapshot original. Inclui as onze fontes JS AUD, três textos de arquitetura, SW, gerador, PDF test e regressors novos.
- Os 135 arquivos de `mt5/jpw-alavancagem-atual/` são byte-idênticos ao snapshot Stoikus; os 135 hashes `sourceHashes` também conferem usando essa raiz. Cálculo/MQL não foi alterado pela combinação.
- Os 102 scripts declarados e quatro recursos runtime no manifest JS têm SHA-256 correto. Os onze hashes AUD e dois hashes Stoikus foram combinados sem alteração extra de fonte JS.
- Ambos os ZIPs mantêm tamanho/hash esperados: SDK `773801` / `03ccb37824175511108b36e9abb5c9fa0dc28d89a338caea1dc7bf02508b9cae`; uso `441516` / `5b2c7ca40736dda976fe97a91a2677d190eb1ccfdf9527703fd471ee702a11e5`. SDK tem 135 membros e uso 82; paths dos membros não contêm raiz absoluta nem `..`.
- O build calculado independentemente, lendo as listas oficiais pelo AST sem executar o gerador, é `e570a26ad6fd096a`, igual ao build atual. São 272 inputs ordenados; README e CHANGELOG finais participam do fingerprint.
- Os 397 hashes de `combined-freeze.json`, fingerprint `d9491539b0ce065272d976f69b464b1501fa4da8b7d5197bb5b13971300eea08`, conferiram contra o disco na fotografia inicial.
- O portátil incorpora `build-id.js` exato, os dois ZIPs exatos e os documentos finais README/CHANGELOG em base64 exato. AUD-10 do gerador e SW foi preservado.
- Os três `HISTORY-AUDIT-BEFORE-STOIKUS-SITE-*` preservam os bytes originais de SESSION_HANDOFF, CURRENT-STATE e ACTIVE-TASK. Os blocos iniciais completos do changelog AUD e do changelog Stoikus permanecem no changelog combinado. README conserva o snapshot Stoikus como sufixo exato, com o prefixo de integração antes do build.

## Omissões detectadas

Estes oito paths existem em `stoikus-before.json` e `stoikus-before/`, mas não no checkout combinado. Não há equivalentes Unicode canonicamente iguais no disco; são omissões reais, não somente diferenças de normalização:

1. `01 - ESTRUTURA DO SOFTWARE/00 - Função Principal do Software.md`
2. `01 - ESTRUTURA DO SOFTWARE/08 - Finanças Pessoais.md`
3. `01 - ESTRUTURA DO SOFTWARE/Estatuto de Gestão de Risco.pdf`
4. `docs/validation/genetrix-1.20.0/00 - Relatório de implementação e validação.md`
5. `docs/validation/genetrix-1.20.0/01 - Manual do núcleo da conta.md`
6. `docs/validation/genetrix-1.20.0/01 - Manual do núcleo da conta.pdf`
7. `docs/validation/genetrix-1.20.0/02 - Matriz de aceitação e pendências.md`
8. `docs/validation/genetrix-1.20.0/03 - Reprodução e validação nativa.md`

Fora dessas oito omissões, todas as mudanças desde o snapshot Stoikus correspondem ao conjunto previsto: delta AUD, docs de contexto, README/changelog/manifest e derivados do build.

## Recibos da combinação observados

`host-combined.json` atual registra 44 PASS e zero demais classificações. `full-combined.json` ainda não estava disponível. A primeira `audit-regressions-combined.json` registra `passed: false`; backup é `ENVIRONMENT_ERROR` em `backup-combined.json`, não foi tratado como defeito do produto. O resultado final deve usar o recibo da reexecução no ambiente corrigido, sem promover essa tentativa a PASS retroativo. Nenhum PASS antigo 1.22.1 foi usado como prova da combinação.

## Próxima conferência

A restauração e o bundle foram reconferidos na seção a seguir. A publicação já autorizada na delegação pertence ao coordenador; este revisor não executa deploy.

## Reconferência após restauração e preparação do Site

`historical-restoration.json` registra oito restaurações. Este revisor reconferiu independentemente os oito hashes contra `stoikus-before.json`; todos são exatos. Os demais paths alterados desde o snapshot permanecem no conjunto previsto. O build e os dois ZIPs não mudaram.

Precisão do inventário: os 397 paths de `combined-freeze.json` continuam byte-idênticos. Essa freeze foi construída com 389 inputs da suíte host mais oito extras (README/changelog, gerador e regressors AUD). Depois de restaurar os históricos, `leverage_suite.input_hashes()` encontra 394 inputs, incluindo cinco documentos restaurados adicionais. Seu fingerprint atual é `774f634678019a61427b0a999e705cf966bc15ed89b0a629053f48b4a00cb7b9`. Nenhum input compartilhado mudou; o acréscimo documental deve constar em um addendum próprio, sem apresentar a freeze de 397 paths como o inventário completo do checkout atual.

Addendum final reconferido: `combined-freeze-final.json` contém 402 hashes, os cinco documentos restaurados e `previous_inputs_unchanged: true`; zero divergências contra o disco. Fingerprint final `deaaf94b95682fc96cc4fb93fcf1704b053da38aee3752a4fc9b21cb06c7d7b3`, runtime build `e570a26ad6fd096a`. A ressalva do inventário está encerrada.

Bundle: `/private/tmp/jpw-hosted-site-20261013/dist`. Seus 162 assets conferem exatamente contra `hosted-assets.json`. Desses, 160 são byte-idênticos ao candidato no mesmo path. Duas exceções foram explicitamente mantidas pelo coordenador para compatibilidade com o Site anterior e são byte-idênticas a `hosted-before/dist`:

- `_headers`: conserva as mesmas diretivas de cache de index/SW/raiz e acrescenta MIME para módulos `.mjs`, PDF normativo e ZIP. É a configuração própria do hosting anterior, adequada aos recursos atuais.
- `downloads/jpw-alavancagem-atual/JPW_Genetrix_Fontes_v1.18.0.zip`: mantém uma URL histórica já existente. Não é download atual e não comprova Stoikus 1.22.1. Os demais ZIPs históricos novos do checkout não foram acrescentados ao Site.

O maior asset tem 2314030 bytes (`src/vendor/pdfjs/runtime-assets.js`); o portátil monolítico não foi usado como arquivo hospedado. Todos os `src`/`href` locais do HTML resolvem no bundle. Os 102 scripts do manifest aparecem na ordem exata entre os 103 tags externos; todos os arquivos existem. Os dois webmanifests têm start URL e scope relativos para a mesma raiz e ícones existentes. SW, manifest JS, manifest de downloads, dois ZIPs atuais, README e CHANGELOG têm os bytes do candidato.

`.openai/hosting.json` é byte-idêntico ao anterior: diretório estático `dist`, projeto `appgprj_6abff945d9a48191aac3b1519893c2fc`. A fonte anterior não contém servidor, bindings D1/R2, sincronização ou implementação de autenticação própria. A identidade de dados locais em DEFAULTS/LSKEY foi preservada; as mudanças posteriores de persistência são as fontes canônicas/AUD verificadas. A audiência é configuração externa do hosting, não um campo presente nesse arquivo local.

Comparação independente do `hosted-before/dist/index.html` com seu base Git declarado `a47ebee5a041e990b627dd3319f382ff0fc14add`: a única customização do HTML era a faixa `jpwSitesNotice`, informando avaliação privada, dados locais, Backup Completo e migração. O index canônico atual não conserva essa faixa; isso remove texto de orientação, sem remover mecanismo de servidor ou armazenamento. O texto anterior que dizia acesso privado não deve ser apresentado como descrição da audiência pública atual. A hospedagem anterior também não tinha backend ou login implementado nesse código.

Recibos atuais reconferidos: projeções 29 PASS, backup v2 34 PASS, interface v2 18 cenários PASS, documentos PWA v2 11 casos PASS e PDF consolidado v2 exit 0; `audit-regressions-combined-v2.json` tem `passed: true`. `hosted-preview.json` registra as cinco abas, zero erros e downloads reais com os mesmos hashes/tamanhos dos ZIPs; a captura de 320 px foi inspecionada. O `full-combined.json` final contém 57 verificações PASS e zero nas demais classificações, branch e HEAD correspondentes ao candidato combinado. O host combinado tem 44/44 PASS, com a ampliação documental da freeze explicitada no addendum.

Conferência adicional independente do SW hospedado em Node VM sem disparar eventos: 143 entradas de `PRECACHE_URLS` e zero arquivos locais ausentes. Pós-full, os 402 hashes de `combined-freeze-final.json` e 162 hashes de `hosted-assets.json` conferem contra disco, mantendo build `e570a26ad6fd096a`. Esta conclusão cobre código, identidade/distribuição e o bundle local; não afirma publicação ou compilação/execução MT5.

Observação documental externa ao diretório público: README e provenance JSON da raiz do checkout de hosting ainda conservavam a fotografia anterior (main a47ebee, 99 scripts, estado antigo de defeitos/validação). Não fazem parte dos 162 assets em dist; reconciliar esses metadados ao fechar o pacote evita representar a proveniência antiga como atual. Este revisor somente sinalizou a observação, sem editar o pacote.

Observação resolvida antes do fechamento: o coordenador atualizou README/provenance para o build `e570a26ad6fd096a`, Stoikus 1.22.1/MQL 1.221/cálculo 1.9.0, full 57/57, host 44/44 e limites nativos NOT_RUN. Este revisor releu os metadados e conferiu os 162 `asset_hashes` contra dist, sem divergências. A proveniência histórica permanece separada; o diretório público continua com o mesmo conjunto de assets.
