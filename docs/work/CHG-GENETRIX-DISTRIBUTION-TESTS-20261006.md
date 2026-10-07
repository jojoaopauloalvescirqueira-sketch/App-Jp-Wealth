# CHG — Correção dos dois testes de distribuição GENETRIX

- Data: 2026-10-06.
- Estado: implementação autorizada pelo pedido «antes disso, conserte os 2 product fail»; integração Git não executada.
- Escopo: `tools/leverage_package_test.py` e `tools/leverage_page_test.py`.
- Base: `ac3a2faffeb398357ff105adbf1d47f70ca309bd`, em worktree isolado `codex/genetrix-ci-distribution-fix-20261006`.
- Risco: N3, alteração de instrumentos de validação; a auditoria independente não substitui aceite ou integração.

## Contrato e comportamento

1. Antes: o pacote e a página distribuídos declaram 1.18.0; os dois testes exigem 1.17.0, 100 membros e trechos antigos da documentação. Preservar o recibo bruto histórico com dois `PRODUCT_FAIL`.
2. Depois: os testes devem verificar a distribuição 1.18.0 existente contra expectativas explícitas, sem adaptar o produto ao erro do teste.
3. Responsabilidade: somente oráculos de distribuição, metadados e guia. ZIP e manifesto usam o gerador oficial, sem edição manual.
4. Consumidores: suíte MT5 host, contrato de download e instalação da página GENETRIX. Nenhuma fórmula, fonte MQL5, schema, arquivo normativo ou comportamento de negociação é alterado.
5. Delta mínimo: atualizar versões/nomes, inventário e trechos documentais; adicionar rejeição de entradas duplicadas e validar que mutações negativas realmente ocorreram.
6. Regressão/recuperação: preservar as verificações de hashes, conteúdo, determinismo, dependências, recibos nativos, navegação, teclado, layouts, download adulterado e uso offline. Rollback reaplica os dois testes da base; o candidato anterior e a instalação operacional permanecem preservados.

## Critérios congelados antes da edição

- Produto 1.18.0; MQL 1.180; cálculo 1.9.0; NoCuda mantém sua versão própria 1.30.
- 108 membros distribuídos exatos: os 100 anteriores mais o manual, os seis includes e o script de testes de Histórico Pessoal. Os 109 arquivos rastreados incluem uma provenance NoCuda fora da distribuição; não ampliar o manifesto incidentalmente.
- Guia com 107 linhas de destino: 103 fontes/recursos e quatro documentos informativos; manter destinos antigos. A provenance Genetrix permanece no disclosure específico, sem instalação no MQL5.
- Compilação e terminal `pending` / `NOT_RUN`; pacote compilado indisponível e `nativeArtifact` nulo. Nenhum ensaio host/browser comprova execução nativa.
- Fixtures de membro ausente, adicional, substituído mantendo a contagem, duplicado e conteúdo adulterado devem ser recusadas; versão divergente e EX5 sem evidência também.
- Dois testes corrigidos em três processos novos; suíte MT5 completa e gate web full. Registrar cada tentativa, ambiente, códigos de saída e hashes.
- Revisor diferente dos autores recebe candidato congelado, critérios e todas as tentativas; contexto compartilhado declarado.

## Fontes e autoridade

O pedido do usuário autoriza a correção local. Fontes documentais explicam o contrato, sem conceder permissões adicionais. Consultados `AGENTS.md`, mapa contextual, gates e rotinas JPW de preflight, controle de mudança, triagem, browser e auditoria posterior.

Core JP Wealth 2.0 relocalizado no vault `2 - TRABALHO/99 - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`; SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`. O preflight passou, com `SOURCE REVISION UNKNOWN` na fotografia contextual existente; essa limitação não foi apagada.

O briefing inicial confundiu 109 rastreados com 108 distribuídos. A contagem foi corrigida e documentada antes da implementação, por inventário independente. Uma hipótese preliminar do revisor sobre omissões no guia também foi corrigida após comparação completa; não é achado confirmado de produto.

## Limites

Não importar os candidatos 1.19/1.20 nem o novo harness. Não instalar no MT5, negociar, publicar, fazer commit, push ou merge. Uma falha adicional será investigada e registrada, sem reescrever o critério para obter aprovação.
