# Stoikus 1.22.1 — integração e publicação em 13/10/2026

Publicado no projeto existente **JP Wealth Software**, versão Sites **3**: https://jp-wealth-software.jojoaopauloalvescirq.chatgpt.site. A audiência existente foi preservada. Build web: `e570a26ad6fd096a`; source do repositório interno Sites: `4cdff1d563b36229561b008b4fb99fd655001f48`.

A pasta principal iCloud foi atualizada com 128 escritas e 34 remoções de nomes renomeados. Seus 402 hashes conferem com o candidato validado. O checkout local permanece na branch `codex/audit-bugfixes-20261012`, HEAD `0f247215cc20829fdba40c3b33458ee976c17ea1`, com alterações não commitadas. Não houve commit, push ou merge no repositório GitHub do usuário. O helper oficial realizou commit e push somente no repositório interno Sites, necessários à publicação autorizada.

## Validação

Site: **57/57 PASS**. Suíte host Stoikus: **44/44 PASS**. Regressões: projeção 29 casos, backup 34, interface 18 cenários, documentos PWA 11 e PDF PASS. Bundle hospedado: 162 assets conferidos por hash, cinco abas, teclado, desktop/mobile e downloads. Verificação final na pasta principal: fast 4/4 PASS e 101 controles negativos rejeitados.

As correções de auditoria foram preservadas. Os pacotes conservam a identidade da versão 1.22.1 e cálculo 1.9.0. Durante a preparação, oito documentos históricos foram restaurados após uma diferença de normalização Unicode. O full valida o mesmo runtime; cinco entradas documentais foram incluídas no freeze final de 402 hashes, com nova execução host 44/44. A restauração não alterou runtime.

## Publicação e limites

Resultado nativo Sites: **succeeded**. A leitura HTTP autorizada confirmou build-id.js, manifesto e os dois ZIPs, todos byte-idênticos ao bundle enviado. A tentativa anônima retornou 403; não foi comprovado acesso anônimo irrestrito. A versão anterior 2 foi preservada no serviço. O archive contém 163 arquivos normais e sidecars AppleDouble de macOS; o serviço contabiliza os 163 arquivos normais. Não se presume que os sidecars sejam servidos.

Compilação e execução nativas MT5: **NOT_RUN**. Sem EX5 atual, instalação operacional, negociação ou acesso a dados financeiros reais. O servidor local de preview foi encerrado pelo coordenador após a verificação.

Rollback local deve usar o apply-plan e os snapshots, limitado aos caminhos aplicados, preservando alterações concorrentes e dados. Para o Site, a versão anterior 2 tem archive e ID próprios. Nenhuma reversão foi executada.

[Revisão final independente](FINAL-PUBLICATION-REVIEW.md) · [Revisão da integração](INDEPENDENT-COMBINED.md) · [Publicação](publication.json) · [Leitura online](live-publication-readback.json).

## Entrega GitHub posterior

Pedido explícito “realize esse passo 1, 2 3”; “execute”. A entrega é preparada na worktree `codex/stoikus-renaming-20261012` a partir de 0f24721, sem incluir o Guia de Aprendizagem concorrente da pasta principal. A fotografia acima descreve a publicação anterior. Resultados GitHub posteriores devem ser consultados no PR e nos recibos externos `/private/tmp/jpw-stoikus-github-20261013`.

A preparação GitHub corrigiu um espaço excedente no guia e encaminhou as evidências do teste de uso para o diretório do recibo, compatível com Linux. Gerador oficial regenerou os dois ZIPs, o manifesto e o build web `6455102de8b5f1fa`. Os recibos Sites versão 3 acima continuam referentes ao build anterior, não são declaração de publicação destes novos hashes.
