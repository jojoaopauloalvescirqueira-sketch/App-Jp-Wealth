# Revisão de preservação — Notificações

**PASS na inspeção de identidade e preservação**, em 2026-10-22T17:35:30.393298-03:00. Não foram executados testes, build ou operações Git nesta revisão. Apenas este diretório de evidências foi escrito.

## Identidade e novo congelamento

Branch `codex/notificacoes-acoes-20261022`; HEAD `d517be0748f886085b3029c809bd68046e5c0f77`; build `8b0b231a1b0c41b7`. Novo freeze de **2026-10-22T17:32:19.747517-03:00**, SHA-256 `f837a24ed3e66759ccfa7b37dbfc078b8946cb5c2958d5fe99169fd8e200b41c`: **2255 entradas conferidas, 0 diferenças** no instante da inspeção. O Harness externo também coincide.

O runner exclui somente `docs/validation/notification-actions-20261022/`; este relatório está nessa exclusão. A FULL estava em andamento. O freeze-after final ainda é necessário. A primeira execução interrompida permanece histórica em `full-first-incomplete` e não é promovida a aprovação.

## Preservação comprovada

O baseline contém 2.232 arquivos regulares: **2.205 idênticos, 27 alterados e nenhum ausente**. Os 25 membros regulares do arquivo recuperável conferem com seus hashes no baseline. Das 14 modificações preexistentes:

- `tools/planning_ui_test.py` mantém os bytes exatos, SHA-256 `e3bc18beac78be38cdba8a3cb5551eda63916d0142deda59e5cef7dfa14c9ad5`.
- Planning UI conserva as alterações anteriores de prazos desde hoje e de explicação do início retroativo. Remover em memória apenas as adições de notificações reconstrói o arquivo inteiro do baseline, SHA-256 `a118f07d6b101299c0ad88bf1064c75aed6d88113b974eb9c47c8eab183c9bd2`. [Patch anterior contra HEAD](preexisting-planning-ui.patch).
- Os **78 objetos antigos** de regression-memory são idênticos e continuam na mesma ordem; há **8 novos**, total **86**. A correção do comando visual afeta somente objeto novo.
- Os outros **11 caminhos preexistentes** são artefatos derivados regenerados. Seus bytes antigos estão recuperáveis; não se alega igualdade desses novos artefatos com o baseline.

## Limites do delta e distribuição

No recorte de 57 fontes core/domínio/contabilidade/norma/decisões, **54 são idênticas**. As exceções são Planning state/UI e execution-board model. Remover exclusivamente suas adições autorizadas reconstruiu os bytes anteriores integrais; isso demonstra preservação do código anterior, sem afirmar que os três arquivos ficaram inalterados.

| Arquivo alterado | Adição delimitada conferida |
|---|---|
| Planning state | Query factual `pendingActions`, exportação e invalidação opcional após confirmação |
| Planning UI | Destino contextual, controle privado de ciclo de vida e exportação |
| Execution-board model | Query readonly `priceReferences` e exportação |
| Finalização da sessão | Uma linha opcional de descarte das notificações; removê-la reconstrói o arquivo anterior |

Os hashes em [preservation.json](preservation.json) confirmam igualdade dos motores Forex/Planning, política, persistência, filesystem, governança de backup, ledger, PF, Alladin, AGENTS e runner oficial. Os sete caminhos encontrados de backup/persistência/schema no recorte de origem/arquitetura também são idênticos. Nenhuma alteração do formato de backup ou de seus escritores foi encontrada. A consulta estreita `pendingActions` não substitui a validação financeira integral.

O manifesto conserva **120 scripts**, com caminhos e ordem iguais ao baseline. Os dez recursos originais de download conservam caminhos, tamanhos e SHA-256 do baseline. Os artefatos derivados têm bytes novos. Esta revisão não executou o builder: inspecionou o log de geração, os arquivos e a identificação declarada do candidato; distribuição e reprodutibilidade dependem dos respectivos checks da FULL corrente.

## Evidências e limites

[Preservação e hashes](preservation.json) · [Comparação completa](baseline-file-comparison.json) · [Arquivo recuperável](archive-comparison.json) · [Oito registros novos](regression-additions.json).

Preservação de bytes não prova correção funcional, homologação financeira, proteção universal, aceite humano ou publicação. Dados reais e perfis pessoais não foram acessados. Uma FULL em andamento não recebe PASS deste relatório.
