# Proposta revisável — evitar atob redundante no default Dante

**Cópia em scratch, ainda não aplicada ao projeto.** O oráculo de download zero decodificação antes da ação permanece intacto. O FULL bruto anterior continua preservado com sua falha; este replay não o reclassifica.

## Causa observada

O hook original de `download_assets_browser_test.py` conta todas as chamadas JS de `window.atob` desde antes do carregamento. Antes da primeira ação há duas chamadas de `settingsProfileAvatarValid`, disparadas pelo render da sidebar e do cabeçalho para o mesmo Dante padrão. Ambas fazem o parse binário de um JPEG estático já pertencente ao catálogo imutável. Isso viola o oráculo de startup sem que tenha ocorrido qualquer pedido de download.

O replay usa o mesmo hook global e mantém o critério `decodes===0`. RED do arquivo real original:2decodes e zero transportes de download. Os stacks apontam `renderSettingsProfileAvatar` → `settingsProfileAvatarValid` → `atob`; estão no recibo. O editor da conta só é criado depois de abrir Configurações; portanto o checkpoint de boot observa apenas os dois avatares que realmente existem nessa fase.

## Menor delta proposto

`proposal.patch` toca somente `renderSettingsProfileAvatar` em `src/js/40-app/09-settings-modal.js`:

- distinguir dado pessoal/persistido não nulo de ausência/nulo;
- na ausência/nulo, atribuir diretamente à imagem o JPEG estático da entrada imutável `dante-mascote`;
- qualquer `avatarDataUrl` não nulo continua passando por `settingsProfileAvatarValid` integralmente — inclusive uma escolha explícita de Dante salva no perfil e qualquer outro retrato da galeria.

`settingsProfileRead`, `settingsProfileAvatarValid`, `settingsProfileImageHeader`, rasterização Canvas, uploads, schema, writer, limite de bytes/pixels e catálogo não mudam. Conteúdo inválido salvo continua em fallback de iniciais, sem sobrescrever seus bytes. Evento de erro da imagem padrão continua voltando a iniciais pelo mesmo handler.

A confiança decorre de código/asset local do catálogo: objeto externo e entradas são congelados, a imagem foi normalizada pelo pipeline e os testes de galeria verificam formato/dimensões/limite. O navegador ainda decodifica a imagem para exibi-la; somente o parse JS redundante de `atob` deixa de acontecer. Dados vindos de armazenamento não recebem essa exceção, mesmo que sejam textualmente iguais ao JPEG do mascote.

Não se propõe mudar o teste de download, payload loader, transportes ou horários de carregamento. O avatar usado na apresentação do guia já atribui o JPEG estático sem chamar o validador; não exige outra alteração.

## RED/GREEN executado em fonte real servida

Comando na raiz CloudDocs:

```sh
.superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3 /private/tmp/jpw-dante-20261024/avatar-startup-proposal/replay.py
```

Exit0 do replay de proposta; `source_unchanged=true`. Somente a resposta HTTP de09-settings-modal é roteada para a cópia candidata nos casos GREEN; os arquivos do projeto permanecem intactos. Chromium headless/contextos sintéticos.

| Caso | Resultado | Chamadas atob no boot |
|---|---|---:|
| Default original | PRODUCT_FAIL esperado pelo oráculo zero | 2 |
| Default com candidato | PASS, perfil continua ausente e Dante aparece | 0 |
| Retrato pessoal salvo | PASS, validação preservada e foto prevalece | 5 |
| Dante salvo explicitamente como foto | PASS, validação de armazenamento preservada | 5 |
| JPEG salvo inválido | PASS, rejeitado e bytes preservados | 5 |
| String vazia inválida salva | PASS, rejeitada e iniciais preservadas | 0, rejeição anterior ao decode |
| Contrato completo de perfil existente | PASS sem alterar seu código/oráculos | não é checkpoint zero |

O último caso executa `settings_modal_test.run_profile_contract` original: upload PNG/JPEG/WebP, normalização/dimensões, positivo5MiB/16MP, negativos de formato/MIME/dimensões/animação/corrupção, falhas/leitura/gravação, rascunho/cancelamento e concorrência de abas, metadata preservada e ausência de mutação financeira continuam comprovados no recorte desse teste. Nenhuma foto pessoal foi isentada da validação.

Recibo: `replay-receipt.json`, incluindo stacks de decode, origens de imagem, ausência/preservação de raw, erros, hashes de módulos/testes/catálogo/build antes/depois e hash da cópia candidata. Saída bruta: `replay.log`. Patch/cópia: `proposal.patch`, `09-settings-modal.proposed.js`.

Tentativa1 preservada em `attempt-1-replay.*`: a causa do RED já era2atob, mas três asserts adicionais do driver scratch esperavam que o editor de conta existisse no boot. Isso era erro do harness temporário; a tentativa inteira exit1 não é GREEN. O driver foi corrigido para observar os dois avatares reais de startup e repetiu todos os sete casos. Produto, validador e oráculo zero permaneceram iguais.

## Revisão e integração pendentes

Escopo N2 Dante já autoriza ajustar o fallback, mas o principal exigiu review independente deste delta antes da aplicação. Nenhum arquivo de produto/teste foi aplicado. Depois do aceite da revisão, será necessário aplicar somente este arquivo, rebuild oficial e repetir download-assets-browser completo (HTTP, file, portátil isolado, portátilHTTP, PWAoffline e contraprovas de invalidação/integridade/transportes), focais de perfil/galeria/finalização pertinentes e FULL vigente. Os testes permanentes existentes já detectam a regressão; nenhum enfraquecimento ou novo runner é necessário.

Sem novos pacotes, headed, dados reais, escritor financeiro, catálogo19, commit, push, merge ou publicação. Nenhum aceite visual humano afirmado.
