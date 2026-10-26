# Revisão independente A0 — default Dante após finalizar sessão

24/10/2026. Proposta somente de teste em scratch; **nenhuma edição aplicada ao projeto**. Produto real congelado: build `2c4a3d9f65b3c664`, branch `codex/dante-guia-20261024`, HEAD `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67` mais o conjunto pendente congelado.

## Parecer

**Não identifiquei achado bloqueante P0–P3 nesta proposta delimitada.** As duas expectativas de zero imagens estão obsoletas diante do default visual Dante aprovado. Substituí-las por exigência do mascote exato e ausência da identidade pessoal nos estados/hosts relevantes conserva a proteção de anonimização e amplia sua observação. Não se propõe remover o perfil persistido ou mudar produto para satisfazer o teste antigo.

A conclusão trata apenas a causa das duas asserções e o delta revisável. Não aprova o FULL bruto, a finalização inteira, o bug adjacente do calendário, a aplicação de patch ou operação Git. O produto/testes reais permanecem congelados e sem esta adaptação.

## Causa e contrato confrontados

O original `tools/finalize_session_test.py:817–825` exige que o raw do perfil não mude depois de finalizar e depois da conclusão atrasada do FileReader, além de input vazio, edição desabilitada e chave não relacionada preservada. Na segunda aba (:839–850), exige o nome/foto salvos preservados, UI de sessão vazia e recuperação do nome confirmado no reload. Portanto o contrato antigo já distingue **anonimização nesta sessão** de **remoção da identidade salva**. Apagar a chave para produzir zero imagens violaria esses controles positivos de preservação.

A exceção observada nas linhas822/845 é a contagem de imagens: antes, ausência de foto deixava iniciais; agora `renderSettingsProfileAvatar` (settings:192–205) resolve visualmente `dante-mascote` quando avatarDataUrl é nulo. O source é escolhido em variável local e não é atribuído ao estado/perfil salvo.

`handleSettingsProfileSessionWipe` (:405–410) cancela a operação assíncrona e limpa confirmed/draft, raw/envelope em memória, bloqueia a sessão e renderiza. `settingsProfileReload` (:170–176) conserva esse bloqueio durante a sessão; a recuperação do perfil salvo depende de novo boot. O leitor `settingsProfileRead` (:151–163) somente lê/valida a chave e retorna uma representação; o novo helper não cria escrita de perfil ao chamá-lo.

Li `reports/finalization-triage.log` e `finalization-triage-facts.json`, produzidos pelo construtor. Na primeira asserção antiga: confirmed/draft vazios, blocked=session, busy/saving/reader inativos, input vazio, título Seu perfil, uma imagem exatamente Dante, botão Salvar desabilitado, identidade personalizada ainda salva e chave alheia preservada. Esses dados são consistentes com o código e sustentam **oráculo desatualizado**, sem evidência de ressurgimento pessoal nesse ponto. Não executei esse browser triage por conta própria.

A falha de AssertionError permanece no bruto como registrada. O diagnóstico identifica a expectativa incompatível; não muda o arquivo bruto nem converte a execução anterior em PASS.

## Menor delta e preservação

A comparação AST própria mostrou:

- 23 funções anteriores, nenhuma removida;
- um helper novo, assert_profile_session_default;
- somente run_profile_finalize_contract difere entre as funções antigas;
- ao substituir em AST exatamente as duas asserções `.locator('#settingsProfileAvatar img').count()==0` pelas chamadas do helper com page/b, a função inteira coincide com a candidata.

Logo, upload real, FileReader atrasado/liberado, gesto real de finalização, segunda aba, raw exato preservado, controles desabilitados, chave não relacionada, reload e protocolo operacional mantêm seus estímulos e expectativas anteriores. Não há mudança de tolerância, timeout, skip, escritor, fixture salva ou caminho de execução do runner.

O novo helper é observacional. Seu controle positivo exige perfil salvo legível, nome e foto pessoal ainda existentes, foto diferente do mascote. Isso impede que apagar o perfil ou retornar um leitor vazio satisfaça o teste. As igualdades anteriores de raw e nome conhecido continuam sendo a referência exata de preservação, além dessa verificação positiva.

## Força e limites do oráculo novo

O helper exige:

1. blocked=session e confirmed/draft exatamente `{displayName:'',avatarDataUrl:null}` — campos pessoais ou keys extras nesses objetos falham;
2. catálogo Dante real e perfil pessoal salvo sem bloqueio, com nome/foto e foto diferente de Dante;
3. uma única imagem em cada host sidebar/cabeçalho/editor, source exatamente igual a Dante e diferente da foto pessoal salva, sem texto residual nesses hosts;
4. input vazio, os dois títulos Seu perfil e rótulo/título acessíveis do acionador do cabeçalho sem a identidade pessoal.

Essa condição é mais específica que trocar zero por um: uma foto pessoal residual, uma imagem arbitrária ou um perfil perdido não passa. O catálogo também não pode ser trocado silenciosamente pela foto salva, pois o controle de diferença salvo-versus-Dante rejeitaria isso.

A abrangência não é universal. O helper verifica explicitamente confirmed/draft e os hosts indicados; não afirma varrer toda a heap, todo atributo do documento ou todos os recursos do browser. Raw/envelope e leitor assíncrono foram inspecionados na fonte/triage, enquanto os estímulos antigos de callback continuam executados pelo caso. O estado salvo continuar legível é o contrato preservado, não prova de apagamento físico ou de proteção contra acesso ao armazenamento.

O fato de uma imagem ser exatamente Dante não prova seu carregamento/pixels ou qualidade visual; essa proposta trata privacidade e semântica do default. A validação visual tem evidência própria e aceite humano separado.

## Replay e contraprovas conferidos

Li o driver, recibo e log bruto. O driver corrigido importa a cópia de teste e usa produto, leitor, upload, storage, handlers e fluxo de finalização reais. Só o helper é envolvido por um wrapper temporário para as contraprovas; o caso válido executa o helper original antes e depois das mutações. Não há substituição de writer/handler para fabricar a finalização.

Resultados lidos do construtor:

| Execução | Resultado bruto |
|---|---|
| Teste original, servido | PRODUCT_FAIL esperado na linha822, zero imagens |
| Candidato, servido | PASS nos três subcontratos de perfil |
| Candidato, portátil HTTP | PASS nos mesmos três subcontratos |
| Contraprovas | 24 rejeições esperadas pelo helper |

São **seis tipos de violação repetidos em quatro pontos**, não 24 classes distintas: local/segunda aba × servido/portátil. As seis são foto pessoal na sidebar, cabeçalho ou editor; identidade pessoal em confirmed; nome pessoal no input; e nome pessoal no aria-label do cabeçalho. O wrapper restaura confirmed/draft e usa o renderer original para reconstruir a UI; exige novamente o caso válido. Isso evita contar uma falha deixada pela mutação anterior como a próxima rejeição.

O driver não injeta uma foto falsa no catálogo nem remove a identidade salva para obter verde. A correspondência do resultado com expected inclui a falha original; o exit0 do replay é uma validação da proposta/contraprovas, não um FULL verde.

A tentativa anterior do driver é preservada e descrita como TEST_HARNESS_FAIL: importação da cópia executava o chdir já existente e o servidor apontava para scratch, com timeout de bootstrap. O reparo mostrado no driver atual é `os.chdir(root)` após importar. Esse incidente não demonstra falha do produto nem deve ser apagado pelo replay posterior.

## Verificações executadas pelo revisor

- SHA-256 dos quatro arquivos reais monitorados coincide com source_before/source_after do recibo: **PASS**.
- SHA-256 da cópia de teste coincide com proposal_sha256: **PASS**.
- Comparação AST com normalização apenas das duas asserções: **PASS** para o recorte de preservação descrito.
- Compilação sintática da cópia via compile, sem importar/executar o módulo: **PASS**.
- `git apply --check /private/tmp/jpw-dante-20261024/finalization-default-proposal/proposal.patch`: **PASS**, somente checagem, sem aplicação.
- Browser próprio, headed, toque físico, finalização com dados reais, novo FULL e aceite humano: **NOT_RUN** por este revisor.

Nenhum arquivo de produto ou teste foi modificado durante esta revisão.

## Autoridade e conclusão de integração

O packet vigente do principal identifica esta adaptação como substituição do default já coberta pelo plano humano Dante, preservando o contrato de privacidade, e determina reconciliar a omissão de `tools/finalize_session_test.py` na allowlist do CHG antes da aplicação. Esta análise confirma o vínculo funcional: o delta depende diretamente do novo fallback Dante e não muda o comportamento de finalização ou armazenamento.

A omissão de filename precisa ser reconciliada explicitamente no registro antes de editar, conforme o escopo informado. Esta revisão não amplia a autorização nem demanda uma nova por formalidade quando a substituição do default já foi autorizada. Testes pertencem ao control plane N3/A4 e devem conservar sua trilha de comparação/revisão.

Depois da aplicação autorizada e reconciliação, executar o focal `--only profile`, o teste inteiro servido/portátil e o FULL vigente com hashes finais de testes/fontes/configuração. O produto pode conservar o mesmo build por ser delta apenas de teste, mas a identidade do conjunto validado muda e deve incluir o hash novo do juiz. A falha bruta anterior permanece histórica.

O calendário continua sendo defeito runtime adjacente com proposta/autorização própria. Esta adaptação de expectativa não o corrige, não altera sua classificação e não libera o pacote enquanto houver gate obrigatório falhando. Commit, push, merge, publicação e limpeza permanecem fora desta revisão.

## Identidades examinadas

- Real `tools/finalize_session_test.py`: `0b912d2677d119bc3e921900a9606cf0d41359c81bb403fc9bd6dd3c20b525e4`
- Real `src/js/40-app/09-settings-modal.js`: `571f05b72c08266588656c633490309c3dced5418226499b59c57b5b5bc6ab22`
- Real `src/js/40-app/07-finalize-session.js`: `2ec8087cfd53de281830a609e29398248c3599a6ed33370114a941b95bcf8d1b`
- Real `build-id.js`: `b7ddb6a2a3ad74a508663b7b6181b51e88abfc1d4426bd951c9d4be7136c1e18`
- Cópia `finalize_session_test.proposed.py`: `9419592bf4754f56cfaf47e5f2568d9b5e97a71c7bd5fd98951ceb98c67c0452`
- `proposal.patch`: `51f1b20fe70a7b8a9a0c3f3a282598b6aa50ff9871a3022b845ca49b9a6c95ce`
- `replay-receipt.json`: `6656bb5e52b8a61686237b955e275858a3eb8568d1abb6b09a565c8f0c04045a`

Única escrita desta revisão: `/private/tmp/jpw-dante-20261024/reports/finalization-default-proposal-review.md`. Sem aplicação de patch, edição de projeto, execução de browser ou operação Git de mutação.
