# Revisão independente inicial — integração GENETRIX 1.21.2

Escopo: somente leitura do candidate congelado, base Git 7f0828488b2fc0ea62dc7c421174799cda47a34a e construção do pacote em diretórios sintéticos próprios. Nenhuma edição do produto, norma, instalação ou Git. Mesmo contexto de tarefa compartilhado; não é avaliação cega.

## Demonstrado

- ZIP canônico SHA256 `a9a77be170036747fec8322fdba7d80bd6256fbcae87e4c6dadb1348ff916261`, 760092 bytes, 132 membros. Todos os hashes internos conferem com o manifesto.
- 111 inputs runtime; fingerprint `9650de7a8573566f3532e3a3ecb2806d0a0e62e2afe7b8130f1331045c06a4b6`.
- Diferença de fontes contra a main: 26 membros, sendo quatro documentos novos e 22 modificados. A cópia ainda contém 4 EAs, 2 indicadores, 27 scripts e 69 bibliotecas; Monitor é recomendado, legados permanecem compatibilidade/rollback.
- Os 24 registros de mudanças do juiz correspondem integralmente aos hashes anteriores da main e aos bytes posteriores do snapshot entregue. Não há intervalo de juiz não documentado.
- Builder oficial da main recria o ZIP exato e de forma idempotente em três diretórios isolados. EX5 sem recibo nativo é rejeitado em todos. Os três diretórios foram executados no mesmo processo Python; isso não significa três sessões nativas.
- `nativeArtifact=null`, compiled indisponível, zero EX5 no ZIP. Compilação e execução 1.21.2 NOT_RUN, aceite operacional BLOCKED. Harness continua CANDIDATE e piloto histórico FAIL.

## Recomendação

Adotar os fontes e 24 mudanças de juiz por hashes, sem modificar o builder; atualizar apresentação/manifesto da página e validar downloads reais. Remover EX5 históricos da árvore corrente evita aparente executável atual, preservando Git/histórico anterior. Não apagar resultados anteriores para declarar aprovação.

Ainda não avaliado nesta revisão: candidate final do site, navegador/download, full gate, commit/CI/main publicada. O campo manifesto `siteIntegration=NOT_RUN` deve conservar seu significado histórico ou ser atualizado com uma conclusão explícita de escopo local após execução. Não substituir evidência nativa por aprovação da integração local.
