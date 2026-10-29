# Correção delimitada — metadados econômicos compostos

Somente scratch. O repositório continua nos inputs da rodada interrompida, sem aplicação desta proposta pelo revisor.

Achado: METADATA-CONTRACT-FINDING.md, PRODUCT_FAIL P2. A política e as limitações da antiga coleção oficial eram expostas globalmente sobre o conjunto misto. UI19 já mostrava corretamente fontes e idade. A correção não muda a UI nem autoriza publicação.

## Arquivos

- infra/monthly-economic-feed/build_package.py: conserva a descrição oficial antiga emofficialBaseMetadata antes da composição; currencies deriva das fontes oficiais pré-merge, sem copiar as nove moedas já declaradas. Globais identificam origens mistas, o produtor assíncrono separado,2hFF e validade individual oficial. Todos os instantes anteriores permanecem intactos.
- src/js/40-app/16-monthly-economic-data.js: expõe o namespace, política de atualização e proveniência pública; generatedAtScope esclarece a data antiga da base. Há fallback condicional equivalente para base oficial antiga sempublicFeed que posteriormente recebev1/v2 emRAM. Base oficial sem fonteFF mantém seus metadados originais, sem inventar produtor. Nenhuma alteração emqueryRange,composição de eventos oucoverage.
- tools/monthly_economic_feed_test.py: somente extensões do helper puro e novoModel22. Exerce o pacote real, namespace antigo, origens,2h, mutabilidade, controle oficial puro, compatibilidade oficial+runtimev1/v2 e compilador sintético. Node24 e os checks existentes não mudam.

Aplicação sugerida: conferir hashesbefore emPROPOSAL-HASHES.json; aplicarSOURCE-ONLY.patch; executar o gerador mensal e os geradores oficiais de distribuição. O patch omite propositalmente o bloco JSON derivado; o candidato scratch contém a geração esperada e oJSON canônico esperado para comparação. Outros arquivos copiados no diretório candidate são insumos imutáveis da experiência, não fazem parte do patch.

## Provas executadas pelo autor deste patch

- NovoModel22 contra produto atual: RED real, exit1, kindeditorial em vez demixed.
- Mesma versão final do juiz no scratch:14ModelContract aprovados, incluindo o22. Sem navegador, rede ou perfil.
- Gerador offlinecheck:153eventos, sem escrita no modo check.
- Oito mutantes rejeitados pelo mesmo juiz finalSHA9a0b8b35967aee84e269f2043855ee963ae317f0e1219de3141b14c6e1de0d89. Nos mutantes de payload, JSON e bloco embutido são alterados juntos para que a rejeição seja semântica, não apenas desigualdade entre cópias: globais antigos; namespace removido; origemFF removida;48hFF; compilador esquece política antiga; API compartilha referências; runtime ignoraFF novo; runtime inventaFF na base oficial pura.
- Arrays events,sources,coverage,currencies,months,provenance,publicFeed epublicFeedProvenance, além degeneratedAt/updatedAt, permanecem exatamente iguais aos do candidato anterior. O manifesto contém os hashes normalizados. Contagens54base+97FF+9oficiais−7associações=153 preservadas.
- Node24 permanece2162c48cdd0b7d945a9e2dfb2c57a1fabf34191f4ff8d98f81f12acd9233b07f. Gate/visual/limites não foram editados.

A primeira versão de provas, anterior ao controle dinâmicov1/v2, está preservada emv1-before-runtime-control. O parecer independente deste patch será emitido por outro agente; o autor não se atribui essa aprovação. A rodadaFULL interrompida de52checks e413casos visuais não aprova estes bytes posteriores. Novo fingerprint, testes focais eFULL final próprios continuam necessários.
