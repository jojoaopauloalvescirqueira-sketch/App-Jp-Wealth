# Revisão A0 — startup do avatar Dante

24/10/2026. Proposta em scratch; produto real ainda `2c4a3d9f65b3c664`. **Sem achado bloqueante P0–P3 no delta examinado.** Favorável à integração delimitada já autorizada, após reconciliação do escopo documental. Esta revisão não aplica código nem aprova o pacote/FULL.

## Evidência e segurança

- O patch muda somente renderSettingsProfileAvatar. Default ausente/nulo usa a entrada local imutável dante-mascote; valor pessoal não nulo continua sujeito ao mesmo settingsProfileAvatarValid. Isso inclui Dante salvo explicitamente. Read, header parser, normalizador, upload, writer e schema permanecem iguais.
- Conferi em VM que array e todos os objetos do catálogo são congelados, com uma única entrada dante-mascote. A confiança é na literal local curada e nas proteções de galeria; não é uma exceção para dados de armazenamento. O navegador continua decodificando a imagem para exibição; a proposta evita somente o parse JS redundante, sem medição de ganho geral de performance.
- Unidade independente com o render real extraído: seis casos na fonte original e seis na candidata. Ausente/nulo: uma chamada ao validador no original, zero na proposta. Foto pessoal e Dante explícito: uma chamada em ambos. Valor inválido continua recusado; string vazia continua em iniciais antes do decode. Nenhum objeto de perfil mudou. O error handler do default continuou retornando às iniciais.
- O total global de cinco atob em perfis salvos, isoladamente, não provaria o caminho de validação, pois inclui chamadas de workspace. A inspeção de fonte e a unidade por chamada acima confirmam especificamente que o render de dado pessoal conserva o validador.

## Recibos e oráculos

Li replay.py/log/receipt e README do construtor, sem rerun de browser próprio. O recibo contém um RED esperado (default original: dois atob com stacks no validador) e seis casos PASS: default candidato com zero, retrato pessoal, Dante salvo, foto inválida, foto vazia e run_profile_contract original completo. Só o módulo settings é trocado por route nos casos candidatos; perfil e bytes persistidos continuam ausentes/preservados conforme cada fixture. Os hashes reais do recibo foram reconferidos e coincidem; source_unchanged=true.

`download_assets_browser_test.py` permanece byte-exato. O critério global zero-atob antes de ação e os critérios de transporte/download não foram ajustados. O contrato de perfil original também não foi alterado. A tentativa1 com assertions erradas sobre um editor que ainda não existia no boot permanece histórica como erro do driver, sem promover seu exit1 a GREEN.

Provas próprias: comparação exata de que somente a função de render difere; 12 controles VM; congelamento do catálogo; hashes; `git apply --check proposal.patch` exit0, sem aplicar.

## Limites

O replay de startup cobre a fonte modular servida por route e o contrato de perfil, não todos os modos de distribuição do teste de downloads. Após aplicação/rebuild: repetir download-assets-browser inteiro (HTTP/file/portátil/PWA e contraprovas), focais de perfil/galeria/finalização e FULL com inputs finais. Sem transferência de aprovação do FULL anterior. Nenhum browser próprio/headed, dado real, aceite humano ou operação Git de mutação nesta revisão. Calendário adjacente continua separado e não aplicado por este parecer.

## Hashes

- Real `src/js/40-app/09-settings-modal.js`: `571f05b72c08266588656c633490309c3dced5418226499b59c57b5b5bc6ab22`
- Real `src/js/40-app/09-profile-avatar-catalog.js`: `1f1c854b32fc9f1ec11e0562e4ab156e2dcab8d796c2e427f31988f5ad059510`
- Real `tools/download_assets_browser_test.py`: `ba6c180b51527408f5b0a70bf09cda11a0439b0ca8df6289212c64ef26f404f0`
- Real `tools/settings_modal_test.py`: `b3d7d25b8846d93ecbde84e6b0f253c064271cbfa5c96f819c889267ff587eb8`
- Real `build-id.js`: `b7ddb6a2a3ad74a508663b7b6181b51e88abfc1d4426bd951c9d4be7136c1e18`
- Scratch `09-settings-modal.proposed.js`: `b1de3cdb9ec28c6983301f784f3ce0b3654a94c117998cf674cd85fcf98be0f0`
- Scratch `proposal.patch`: `396049187a31ee370aeabb41ddcf113165025ec189ee26a742559bf5fff2cffa`
- Scratch `replay-receipt.json`: `8299d0641c5ffd0a9476ae6d60450cfd7724c5576029e5a5977ee5d18f0c59fc`

Única escrita: este relatório externo.
