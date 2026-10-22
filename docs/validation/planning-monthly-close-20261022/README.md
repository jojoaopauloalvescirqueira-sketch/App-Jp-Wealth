# Planejamento — fechamento mensal e revisão de uso

Candidato local **7430aeaf0109dcbe**, branch `codex/planejamento-patrimonial-20261020`, base `ea15afc`. Implementação concluída; **96/96 checks e 278/278 casos visuais PASS**, com **aceite estrito do congelamento pendente por alteração externa do contexto**. A saída do executor da suíte foi 0; o wrapper de congelamento saiu com 1. A primeira execução completa foi interrompida para corrigir um estímulo de teste, preservado abaixo. Aceite visual humano permanece separado. Sem commit, merge, push ou publicação.

[Prévia local](http://127.0.0.1:8000/index.html?v=7430aeaf0109dcbe) → Planejamento → Preenchimento mensal. Se houver rascunhos, salve-os ou exporte o Backup Completo antes de recarregar. Depois feche abas antigas e reabra o link para evitar código mantido pelo service worker; não apague armazenamento ou dados do navegador.

## O fluxo corrigido

A janela identifica conta e mês. Quando falta resultado, permite informar percentual ou US$, revisar e escolher **Salvar resultado e revisar fechamento**. Nenhum zero ou aporte previsto é assumido. Após confirmação do resultado, exibe o fechamento efetivo, pede nova conferência dos fluxos e permite **Confirmar fechamento**.

São duas gravações distintas. Cancelar depois de salvar o resultado conserva esse registro e informa que o mês continua aberto. Resultado, aportes, saques e patrimônio usam os modelos/comandos existentes, sem fórmula financeira nova.

Revisões antigas ficam bloqueadas, preservando os campos. **Atualizar revisão** relê a mesma conta/plano válido e exige nova conferência. Trocar plano, arquivar conta ou invalidar a base não reautoriza o rascunho anterior. Recusa conserva a entrada; resultado indeterminado impede repetição cega e aponta para recuperação.

Quando há meses anteriores pendentes, a janela identifica o primeiro e oferece acesso a ele, explicando os filtros. Não fecha em lote. O estado Sim/Não continua derivado da confirmação real.

[Antes: bloqueio sem recuperação](captures/before-missing-result.png) · [Depois no computador](captures/after-closure-review-1440.png) · [Resultado no celular](captures/after-missing-result-390.png) · [Revisão do resultado](captures/after-result-review-390.png) · [Capturas e contadores](CAPTURES.json).

## Achados e correções

| Achado confirmado | Resultado |
|---|---|
| Falta de resultado desabilitava o fechamento sem caminho de recuperação | Entrada/revisão/salvamento na própria janela |
| Conferir→Cancelar→registrar resultado→reabrir restaurava autorização de revisão antiga | Atualização explícita; campos preservados e consentimentos desmarcados |
| Mecanismo compartilhado afetava também diálogos legados | Resultado/formulário/reinício reconferem versão e preservam entradas |
| Nova entrada de fechamento precisava continuar legível no backup | Exportação usa somente unit/value já existentes no texto opaco; sem token ou schema novo |
| Zoom200% revelava margem/centro incorretos pela barra de rolagem externa | CSS restrito ao fechamento usa largura percentual do espaço disponível |
| Foco após confirmar o novo fechamento podia voltar ao corpo | Retorno ao acionador conectado/remapeado, com fallback contextual |

As regras de resultado obrigatório, conferência de fluxos e fechamento em sequência foram preservadas. A consulta de prévia acrescenta motivos estruturados; não converte texto de erro em regra. O motor e todos os bytes financeiros fora dessa consulta permanecem idênticos à base desta tarefa.

## Provas atuais

- **38/38** casos pós-build de fechamento: 11 comportamentos, três contraprovas, 16 combinações de layout/tema/largura e oito de zoom nativo de 200%. Confirmação/foco/aviso têm focal adicional após reforçar a asserção.
- **74/74** estado/consultas: 68 casos anteriores e seis novos; consulta não grava.
- **10/10** jornadas das três abas, após correção do estímulo de submissão para atingir o formulário real.
- Exploração separada: paridade de 9 jornadas/132 asserções, utilização ampla com 136 asserções, proporções 5/5 e 12 sondas práticas/recuperação. São evidências sobrepostas, não uma soma de testes independentes.
- HTTP, PWA offline, modular file://, portátil, validação estrutural e reprodutibilidade:PASS nas execuções focais próprias.
- Matriz visual do pacote final, executada no FULL3: **278/278 PASS**, incluindo os 240 anteriores, com 151 vínculos de fonte conferidos independentemente contra o congelamento; a suíte completa terminou com 96 PASS. O congelamento final permanece bloqueado pelo ajuste externo de instruções, descrito abaixo.

[Casos 38](evidence/CLOSE-38.json) · [Estado 74](evidence/state-postbuild.log) · [Três abas](evidence/THREE-TABS.json) · [Exploração](review/USAGE-REVIEW.md) · [Distribuição](evidence/distribution.log) · [Reprodutibilidade](evidence/reproducibility.log) · [Congelamento](FROZEN-INPUTS.json) · [Visual 278](VISUAL-RAW.json) · [Auditoria técnica](TECHNICAL-AUDIT.md) · [Backup da base conferido](BASELINE-ARCHIVE-VERIFIED.json).

A exploração utiliza contas e valores fictícios, perfis descartáveis e integração de cotação controlada. Não lê os dados financeiros pessoais do navegador. As capturas por toque mostram um writer após salvar o resultado e dois somente depois da confirmação do fechamento.

## Preservação, revisão e limites

Baseline recuperável: 2118 arquivos/links, 128 pendências anteriores. O congelamento abrange 2114 arquivos regulares, oito links e cinco controles privados, incluindo o arquivo comparador. O executor e seus 96 checks mantêm bytes/ordem. Os 68 casos de estado e as 240 identidades visuais anteriores permanecem; somente a interação obsoleta de um caso stale-choice foi substituída deliberadamente, conservando o objetivo de não sobrescrever a versão nova. As 61 entradas históricas de regressões permanecem intactas, com seis registros novos.

A revisão independente executou sete sondas adversas de identidade/rascunhos. Depois, encontrou um erro no novo teste: a submissão sintética era disparada no diálogo e não atingia o formulário. A FULL1 foi interrompida com saída real −15/sem relatório completo; não é PASS. O estímulo foi corrigido e agora exige `accepted=false/defaultPrevented=true` pelo handler real, preservação do estado e nova revisão. A confirmação independente e os artefatos anteriores foram mantidos. [Correção do estímulo](review/corrected-stimulus-review.md) · [Contraprova](review/event-target-counterproof.json) · [Tentativa1](attempts/full1/full-attempt1-interruption.json).

Também foram preservadas falhas intermediárias de geometria e sondas de teste. Opção nativa desabilitada é conferida pela propriedade DOM e pelo teclado; viewport fracionário no zoom usa `visualViewport`, mantendo margem de 12 px e tolerância de 2 px. Correções do verificador não substituem a demonstração real dos critérios.

O PDF atual foi aberto e renderizado: conteúdo legível; a segunda página conserva somente duas linhas de rodapé, dívida herdada não corrigida aqui. [Inspeção PDF](pdf/PDF-INSPECTION.json). O incidente histórico Alladin case F não é encerrado por esta entrega.

Safari, leitor de tela, toque físico, compreensão e aceite visual humano permanecem não estabelecidos. Nenhum teste finito comprova ausência universal de bugs. Fontes dos três minigames e Bolsas Globais, dados e formato de backup, normas, plugins e configuração de memória foram preservados.

## Nova execução final

A FULL2 terminou com 95 checks aprovados e uma falha: o teste estático de credenciais encontrou a palavra `authorization` num comentário explicativo novo, sem demonstrar segredo no pacote. O comentário foi reescrito; código executável e teste de segurança permaneceram idênticos, conforme revisão independente. O pacote foi reconstruído e o focal USD/BRL passou. A FULL3 executou os 96 checks no novo build e todos passaram; sua conferência posterior do congelamento detectou o ajuste externo abaixo. A falha anterior permanece preservada e não é apresentada como aprovação. [Diagnóstico independente](review/full2-comment-review.md) · [Tentativa 2](attempts/full2/ATTEMPT.json).

## Como finalizar um mês

1. Em **Planejamento → Preenchimento mensal**, abra o fechamento do mês desejado.
2. Se faltar resultado realizado, escolha **%** ou **US$**, informe o valor e pressione **Revisar resultado**. Lucro é positivo; prejuízo é negativo. Zero precisa ser informado explicitamente.
3. Confira a conversão e escolha **Salvar resultado e revisar fechamento**. Essa ação registra somente o resultado.
4. Confira resultado, aportes, saques e fechamento efetivo. Marque a conferência dos fluxos e escolha **Confirmar fechamento**.

Se houver um mês anterior pendente, use **Ir ao mês pendente** e resolva-o primeiro. Se os dados tiverem mudado desde a revisão, use **Atualizar revisão** e confira novamente. Cancelar antes de salvar preserva os fatos existentes; cancelar depois do registro do resultado mantém esse resultado e deixa o mês aberto.

## Resultado final e limite do congelamento

A FULL3 terminou com **96 PASS, zero falhas e saída real 0**. A matriz visual executou **278 casos únicos**, incluindo os 240 anteriores, todos PASS. [Resumo vinculado](FULL-RESULT.json) · [Saída bruta](FULL-RAW.json) · [Comando e conferência posterior](FULL-COMMAND.json) · [Log integral](FULL.log).

A conferência estrita posterior **falhou**: outra sessão corrigiu o caminho do Harness em `AGENTS.md` e criou dez aliases em `.claude/skills` durante os testes. O usuário confirmou diretamente essa origem. Todos os arquivos do aplicativo e dos testes permaneceram idênticos; o único arquivo regular diferente é `AGENTS.md`. Os oito links originais foram preservados. [Inventário da diferença](EXTERNAL-CONTEXT-DRIFT.json) · [Diferença em AGENTS](EXTERNAL-AGENTS-DIFF.patch).

Os ajustes externos foram preservados. Não foram incorporados silenciosamente ao contrato desta tarefa, revertidos nem usados para reclassificar `frozen_after=false` como sucesso. O recibo mantém **saída 1 do wrapper** e **aceite de FULL congelado bloqueado**. Validar o conjunto atual de instruções requer reconciliação autorizada e evidência estável própria; esta entrega não declara prontidão integral do workspace. A implementação e os resultados dos testes do produto estão disponíveis para revisão.

## Revisão independente final

A revisão concluiu: **evidências do produto aprovadas no escopo; aceite de FULL congelado bloqueado**. Conferiu os 96 resultados reais, os 278 casos visuais, preservação dos testes e comandos financeiros, sete sondas adversas e a origem externa confirmada da diferença. [Parecer](review/final-review.md) · [Recibo estruturado](FINAL-INDEPENDENT-AUDIT.json).

Os 151 hashes de entrada da matriz visual correspondem ao congelamento utilizado naquele teste. Após a alteração externa de AGENTS, 150 correspondem ao workspace atual; fontes do aplicativo e dos verificadores continuam iguais. Essa distinção foi mantida nos recibos.
