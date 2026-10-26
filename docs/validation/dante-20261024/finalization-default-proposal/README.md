# Proposta revisável — default Dante após finalizar sessão

**Somente teste em scratch; nenhum arquivo do projeto aplicado.** A falha bruta do FULL continua preservada. Esta proposta trata a substituição deliberada do default visual prevista no plano Dante, separadamente do defeito adjacente de ciclo de vida do calendário.

## Causa e contrato

`tools/finalize_session_test.py`, linhas822/845 do original, exige zero imagens depois da anonimização da sessão. O Dante aprovado é um fallback visual mesmo sem nome/foto no estado confirmado. O focal original `--only profile` confirmou a falha na primeira dessas linhas: a imagem é exatamente a entrada `dante-mascote`; memória confirmada/rascunho estão vazios, reader/busy/saving inativos, nome de exibição `Seu perfil`, e o perfil personalizado permanece preservado no armazenamento conforme o contrato anterior. Evidências: `../reports/finalization-triage.log` e `../reports/finalization-triage-facts.json`.

Finalizar sessão **preserva o perfil salvo**; o próprio teste original exige raw igual, fotografia salva e nome recuperado no reload. Portanto não se propõe apagar a chave. A ausência de dados pessoais exigida nesta sessão se aplica à memória e à interface bloqueada. Misturar essas duas fronteiras mudaria o comportamento de persistência sem autorização.

## Delta proposto

`proposal.patch` troca somente as duas expectativas `img.count()==0` por chamada ao novo helper observacional `assert_profile_session_default`. Todos os outros estímulos/asserts do teste permanecem byte a byte: upload real, reader atrasado, encerramento real, segunda aba, preservação do raw, controles desabilitados, chave não relacionada, reload e protocolo operacional.

O helper:

- chama a API real leitora `settingsProfileRead()` e confirma que o perfil personalizado sem erro ainda existe, com nome e fotografia diferentes de Dante — um controle positivo contra apagar/perder o perfil;
- exige estado `session`, confirmed e draft exatamente `{displayName:'',avatarDataUrl:null}`;
- exige uma única imagem em cada avatar da sidebar, cabeçalho e editor, todas com `src` exatamente igual ao catálogo `dante-mascote`, diferentes da fotografia pessoal salva, sem texto residual;
- exige input vazio, títulos `Seu perfil` e nome/título acessível do acionador do cabeçalho sem identidade pessoal.

Não há alteração de produto, schema, cálculo, writer, limpeza ou backup. O arquivo permanente proposto continua sendo somente o teste existente. Não são propostos novos arquivos do projeto nem um segundo runner.

## Replay e contraprovas

Comando executado na raiz real CloudDocs:

```sh
.superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3 /private/tmp/jpw-dante-20261024/finalization-default-proposal/replay.py
```

O driver importa a cópia candidata e usa produto, leitor, armazenamento, upload e fluxo de finalização reais em contextos descartáveis. Não substitui handlers/writers nem toca no arquivo do teste do projeto. O wrapper de contraprovas modifica somente alvos sintéticos em memória/DOM, verifica que o helper os rejeita, restaura pelo renderer original e exige o caso válido de novo.

Resultado do replay corrigido: exit0, `source_unchanged=true`:

| Caso | Resultado |
|---|---|
| Original sem adaptação, servido | PRODUCT_FAIL esperado na expectativa antiga de zero imagens |
| Candidato, servido | PASS nos três subcontratos de finalização de perfil |
| Candidato, portátil HTTP | PASS nos mesmos três subcontratos |
| Contraprovas | 24/24 rejeitadas |

Seis violações por ponto de verificação, quatro pontos no total (local/segunda aba × servido/portátil): fotografia pessoal residual na sidebar, no cabeçalho ou no editor; identidade pessoal em confirmed; nome pessoal no input; nome pessoal no `aria-label` do acionador do cabeçalho. Todas produziram rejeição do mesmo helper que aceita o caso válido. Não se usou clique forçado, mudança de timeout ou tolerância mais frouxa.

Saída bruta: `replay.log`. Recibo: `replay-receipt.json`, com casos,24contraprovas, hashes antes/depois do teste e dos módulos reais envolvidos e hash da cópia candidata. O replay de proposta ter exit0 significa que o original foi rejeitado e as expectativas revisadas/contraprovas funcionaram; **não transforma o FULL anterior em PASS**.

### Tentativa anterior do driver temporário

Preservada em `replay-bootstrap-harness-failure.log` e `replay-bootstrap-harness-failure.py.txt`: TEST_HARNESS_FAIL antes da asserção em análise. Importar a cópia de finalize executou o `os.chdir(ROOT)` já existente, apontando o servidor para scratch e causando timeout de bootstrap. O reparo foi exclusivamente `os.chdir(root)` no driver temporário após a importação. O processo anterior foi encerrado explicitamente (SIGINT não concluiu o teardown; SIGTERM encerrou exit143); Python/Node filhos foram conferidos ausentes depois. Nenhuma fonte/oráculo foi editado para contornar essa falha. O replay corrigido exit0 e o recibo final são distintos dessa tentativa.

## Autoridade e integração futura

O plano/CHG Dante já autorizou a substituição deliberada das expectativas do default por Dante preservando privacidade. O principal registrará que a omissão de `tools/finalize_session_test.py` na lista de arquivos de controles deve ser reconciliada especificamente para estas duas expectativas e seu helper mais forte. A revisão independente ocorrerá antes de aplicar, conforme a orientação atual. Isso não autoriza o defeito de calendário, que continua fora do contrato Dante.

Aplicação futura proposta: um arquivo existente de teste, sem produto ou build novo por este delta isolado; executar `finalize_session_test.py --only profile`, o teste inteiro servido/portátil, revisão do diff e o FULL vigente no candidato reconciliado. Proteções de control plane e aceite humano continuam próprios. Sem commit, push, merge, publicação ou limpeza autorizados. Nenhuma afirmação de avaliação visual humana.
