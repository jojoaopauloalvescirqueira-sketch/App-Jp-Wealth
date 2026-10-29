# Revisão delimitada do produto aplicado — 28/10/2026

Parecer estático do próprio autor, em leitura do repositório. Não substitui auditoria independente, browser, distribuição, FULL ou aceite humano. Única escrita desta revisão: este parecer em scratch.

## Resultado

Nenhum bloqueador material encontrado no delta aplicado examinado. PASS para fidelidade da aplicação, preservação dos arquivos-baseline fora do escopo e coerência estática de produto/contrato. Validação integral: NOT_RUN nesta revisão.

## Identidade e preservação verificadas diretamente

- Raiz: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`.
- Branch observada: `codex/calendario-tabela-ff-20261028`.
- HEAD de referência: `3e24f60f8cfe87f79335f40e95a0927379a9f834`.
- Baseline: `/private/tmp/jpw-economic-calendar-table-20261028/baseline-hashes.json`, 3.578 arquivos.
- JS aplicado: SHA256 `1e2e518bef9dccca48790f9752c48ba62619cd64c128ec87c55c6c58c779c831`.
- CSS aplicado: SHA256 `f1007dfe4122ac80aa2e8260b4db91079ad5291cec5f1b2dd6ab0aa3910beb38`.
- Os dois arquivos de produto são byte a byte iguais às cópias finais revisadas em product-proposal.
- Dos 3.578 arquivos, 3.574 mantêm o hash-baseline; somente `19-calendar-agenda.js`, `app.css`, `docs/architecture/CALENDAR-AGENDA.md` e `docs/work/ACTIVE-TASK.md` mudaram. Nenhum arquivo-baseline ausente.
- Os quatro verificadores Python candidatos existentes, quality_gate.py, ui_visual_quality_test.py, regression-memory.json, fontes15/16, manifest, index, dist, build-id e SW conservam os hashes-baseline. Portanto não houve aplicação N3 ou rebuild neste delta examinado.
- Novos arquivos regulares: plano, brief, CHG de produto e sete evidências sob `docs/validation/economic-calendar-table-20261028`. Os dezoito links de skills que aparecem na diferença de conjuntos não são novos: são links Git120000 preexistentes, omitidos pelo manifest de arquivos regulares; `git diff --name-only -- .agents .claude` está vazio.
- Comparação com baseline-pending.tar.gz: todo o conteúdo anterior de ACTIVE-TASK permanece como trecho contíguo; o contrato recebe somente a seção de tabela, sem exclusões das linhas anteriores. CSS fora do bloco local de calendário permanece byte a byte igual.

## Produto e contrato

A tabela usa table/caption/thead/th scope=col e sete td por evento. Roles explícitos reforçam a semântica durante reflow CSS; somente a linha do evento possui data-calendar-economic-id. Detalhe é tr separado com colspan7, alvo aria-controls prefixado pelo host e aria-expanded. O botão tem ação economic-detail exclusiva e nome relacionado ao evento, preservando a ação info das fontes globais.

Atual é sempre travessão com explicação acessível Não fornecido nesta alimentação. Projeção/Anterior usam a string recebida, sem Number/parseFloat, preservando zero, sinais e unidades. Conteúdo externo é passado por textContent. Links de detalhe exigem HTTPS e recusam credenciais. Impacto tem nome acessível e distinção por barras3/2/1 ou interrogação, além de cor; nenhum dado recebe semântica de favorabilidade de resultado.

Fonte, horário original e referências ficam no detalhe. Cancelamento/publicação explicitamente fornecidos, horário pendente, ausência na coleta e conflito continuam na linha recolhida. Data/fuso/quantidade ficam no cabeçalho; coleta/estado econômico aparecem somente quando Economia está habilitada. O início da atualização pública redesenha o resumo para expor Atualizando, mantendo o produtor existente.

Expansão fica em state por instância, sem persistência. O identificador visual considera provider/sourceId/currency/title/precision/instant/date/sourceUrl; exige correspondência única para manter expansão e foco, mesmo quando o ID for igual. Não há fallback por ID/título semelhante. Se a observação some ou fica ambígua, expansão é zerada; a observação voltando depois não reabre automaticamente. A recuperação de foco econômico só atua quando o foco anterior pertencia à linha/detalhe, e usa heading tabindex=-1 se não encontra alvo seguro. O formulário pessoal não é reconstruído nesse render. Scroll da agenda e do painel é capturado/restaurado.

Escape conserva o cancel nativo do diálogo; não existe interceptação econômica nova. Handlers de tarefas/compromissos, captura de draft e comando de fechamento permanecem. Não há nova consulta, writer financeiro ou persistência para a expansão. A inspeção dos corpos e do delta confirma os caminhos antigos de preferências/agenda; a contagem auxiliar de chamadas ficou inalterada: localStorage.setItem1, queryRange1, commands.save1, setCompleted1, remove1, fetch0 e refresh público1. Essa contagem é apoio de inventário, não teste de comportamento.

CSS mantém um DOM, mês308 e gap24, empilhamento por700 úteis (container740 com padding40 no desktop), e sete colunas somente com720 úteis na agenda. Cabeçalhos e linhas usam a mesma grade; números ficam à direita. No compacto os valores recebem rótulos e altura automática. Workspace<=360 expande apenas seu painel a100vw para acomodar308 úteis e sete dias44. Sem nova dependência ou mudança nos dados/fontes/cache/APIs.

Brief, CHG, plano e nova seção do contrato descrevem esse escopo e mantêm controles N3, FULL e aceite separados. O ponteiro ACTIVE registra a aprovação N3 ainda pendente. A referência ao futuro README de validação é uma pendência de fechamento documental, não prova de validação existente.

## Verificações desta revisão

PASS: branch/status lidos; comparação SHA256 de todos os3.578 caminhos; igualdade produto/proposta; comparação dos documentos com arquivo-baseline; preservação CSS fora do bloco; leitura do diff/produto/contratos; `git diff --check` dos quatro caminhos alterados; Node bundled `--check src/js/40-app/19-calendar-agenda.js`.

NOT_RUN: browser e interação (table_tests está executando os focais), contraprovas, geradores/rebuild, distribuição HTTP/PWA/file/portátil, FULL116/visual413, janelas nativas/zoom200, Safari/leitor de tela e aceite humano. Nenhuma mutação Git, API externa ou escrita no repositório foi executada por este revisor.
