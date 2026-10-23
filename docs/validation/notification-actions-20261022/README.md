# Notificações — central de ações relevantes

Candidate local **8b0b231a1b0c41b7**, branch `codex/notificacoes-acoes-20261022`, HEAD `d517be0748f886085b3029c809bd68046e5c0f77`, mais as alterações pendentes delimitadas. Preservadas as 14 modificações anteriores de Planejamento. [Contrato](../../architecture/NOTIFICATION-CENTER.md), [brief](../../work/BRIEF-NOTIFICATION-ACTIONS-20261022.md), [plano aprovado](../../superpowers/plans/2026-10-22-notification-actions.md) e [inventário completo](notification-inventory.json).

**FULL final: 96/96 PASS, exit 0; mesmos 2.255 arquivos e links antes/depois, sem divergências.** Execução 2026-10-22T17:32:19.747517-03:00 → 2026-10-22T18:07:50.727861-03:00. Revisão independente e focais têm escopos próprios; aceite visual humano continua pendente. Sem commit, merge, push ou publicação. [Recibo final](final-run/FINAL-RECEIPT.json), [runner bruto](final-run/full-raw.json), [log](final-run/full.log), [identidade](final-run/full-recording-receipt.json). A [conferência independente posterior](independent-review/FULL-ADDENDUM-20261022.md) confirmou o bruto, a matriz e os mesmos inputs atuais, sem repetir testes.

Prévia HTTP conferida byte a byte contra os arquivos locais: http://127.0.0.1:8000/index.html?v=8b0b231a1b0c41b7. O link não limpa dados nem confirma ações.

## Resultado de produto

O sino conta causas ativas agrupadas, independentemente de leitura. Cada item tem contexto, síntese, ação específica e diagnóstico expansível. Foram retirados controles de leitura, agenda, sucessos, rascunhos ordinários e textos permanentes de onboarding/norma. As proteções normativas do Forex continuam no módulo.

Planejamento tem uma ação por conta/plano com meses passados de fatos vigentes: resultado explícito, inclusive zero, fluxos não anulados ou fechamento invalidado. O primeiro mês anterior bloqueante é explicado como dependência. A consulta não calcula a trajetória de 120 meses nem certifica saldos. O acesso contextual respeita rascunhos, geração, conta/plano, disponibilidade e filtros; sua adaptação de filtros é transitória, sem alterar preferências salvas.

Fontes falhas geram uma única ação de verificação, mantendo o diagnóstico anterior identificado como **informação não atual**. Módulos congelados não geram cobranças operacionais; integridade/preservação continuam em Sistema. Falha, ausência e zero são distintos.

## Catálogo de pertinência

| Área | Gatilho | Encaminhamento |
|---|---|---|
| Sistema | Gravação indeterminada, falha, conflito, recuperação ou bloqueio existentes | Ver recuperação |
| Backup | Mecanismo atual indica cópia pendente/não confirmada | Revisar backup |
| Forex | Fatos sinalizados, stop aberto não validado, exposição excedida, encerramento compulsório ou conciliação | Revisar conta/período na Operação |
| Referências | Preço/data efetivamente usados por instrumento de ordem ativa precisam de revisão | Revisar referências na conta/período |
| Planejamento | Meses passados com fatos vigentes ainda não confirmados, com dependência anterior quando necessária | Revisar meses |
| PF | Pendências derivadas do orçamento ou crédito excedido, quando ativo | Revisar pendências/crédito |
| Integridade | Incompatibilidade ou leitura recusada em módulo, inclusive congelado | Ver recuperação em Sistema |
| Consulta indisponível | Exceção de uma fonte | Verificar novamente, sem falso diagnóstico saudável |

O inventário JSON identifica 17 famílias/identidades e suas condições de resolução. Ele documenta a implementação, sem criar prazo de backup, regra financeira ou autorização operacional.

## Comparação real de interface

Mesmos dados sintéticos: duas contas com resultado zero explícito em agosto/2026 e backup de 01/08/2026; relógio de 14/09/2026. A referência anterior foi carregada dos bytes preservados pelo browser, sem restaurar/sobrescrever fontes do projeto.

| Medida observada | Antes | Depois |
|---|---:|---:|
| Caracteres visíveis da lista, detalhes recolhidos | 2.047 | 483 |
| Badge nesse cenário | 3 | 3 |
| Gravações após semear, ao abrir/consultar | 0 | 0 |

Os três itens representam causas diferentes entre versões; igualdade numérica não implica igualdade semântica. O novo corpo mostra contas/ação em vez do diagnóstico normativo permanente. Não foi medido ganho de compreensão humana.

- [Desktop antes](captures/before-1440.png) · [Desktop depois](captures/after-1440.png)
- [Celular antes](captures/before-390.png) · [Celular depois](captures/after-390.png)
- [Dados e hashes da comparação](captures/comparison.json)

## Defeitos encontrados durante a implementação

| Achado confirmado | Correção | Prova permanente |
|---|---|---|
| Leitura zerava contagem apesar da causa ativa | Contagem de causas, sem comandos de leitura | `actionable-only-unresolved-count` |
| Falha de fonte perdia detalhe do diagnóstico anterior | Retenção completa, marcada não atual | `replacement-diagnosis-generation` |
| Período Forex vazio gerava conciliação | Exigir fatos/observações pertinentes | `forex-empty-context-no-action` |
| Contexto mudava durante consentimento, mas a tela era alterada antes de revalidar | Guards e revalidação antes de navegar/selecionar | `forex-guard-generation-before-navigation` |
| Aviso usava data do cadastro em vez do preço efetivo manual/diário | Projeção readonly da mesma precedência da Board | `forex-price-reference-provenance` |
| Nome longo vazava dentro do scroll apesar de diálogo caber | Quebra de metadados e contraprova do overflow interno | `notification-long-context-wrap` |
| Resultado zero e dependência anterior não eram tarefas específicas | Projeção factual e entrada contextual | `PLNOTICE-Q02` e demais casos de estado/contexto |

A revisão independente encontrou os quatro problemas centrais de vazio, cotação, guard e contexto longo, confirmou as correções com seus próprios contrastes e encerrou sem P1/P2 pendentes no recorte. [Parecer](independent-review/FINAL-REVIEW.md), [recibo](independent-review/FINAL-REVIEW.json).

## Verificação focal e distribuição

| Execução | Resultado e limite |
|---|---|
| Builder oficial `rebuild_monolith.py --refresh-manifest` | Exit0, build `8b0b231a1b0c41b7` |
| Validador estrutural | PASS: 120 scripts, 704 IDs; não equivale à interação |
| Integração JP Engenharia | PASS: 86 registros; integridade estrutural, sem certificar comportamento |
| Notificações | 30/30 PASS em HTTP modular, dados sintéticos |
| Eficiência | 20/20 PASS; coleção financeira não acionada por digitação comum |
| Estado de Planejamento | 87/87 PASS; RED anterior e mutantes preservados |
| Disponibilidade | Focal adicional PASS; fora do runner FULL |
| Visual focal anterior | 42/42 PASS; antecede os dois casos de contexto longo. Não representa 44/44 |
| Distribuições suplementares | 4/4 PASS:HTTP, modular file://, portátil isolado e PWA com reload offline real |
| Revisão independente | PASS no recorte; sem substituição do FULL/aceite humano |
| FULL final congelada | **96/96 PASS; exit 0; mesmos 2.255 arquivos e links** |
| Matriz visual final padrão | **322/322 PASS; 44 casos de notificações incluídos; source_unchanged=true** |

Os quatro modos suplementares abriram o sino, filtraram, expandiram, preservaram expansão/contagem após refresh e navegaram para conta/mês explícitos sem writes ou rede adicional. O portátil foi isolado em diretório contendo somente seu HTML. Isso não repete os 30 + 20 casos em cada modo. [Cobertura e limites](coverage-review/COVERAGE.md), [recebimento de distribuição](coverage-review/distribution-results.json).

O runner mantém seus 96 checks. Os 278 IDs visuais antigos permanecem; 44 adições elevam a matriz padrão para 322, todos executados e aprovados no candidato final. Notificações (30) e eficiência (20) estão no FULL; a matriz visual padrão integra STANDARD/FULL. Recibos focais em [focal-receipts](focal-receipts/manifest.json); alguns arquivos brutos de saída contêm uma sequência de JSONs mais o resumo, conforme seu produtor original.

## Preservação e identidade

[Auditoria de preservação](preservation-review/README.md) compara baseline, tar recuperável, deltas anteriores e freeze: 2.255 entradas, 2.237 arquivos e 18 links; 2.205/2.232 arquivos regulares do baseline idênticos, 27 deltas identificados e nenhum ausente. Os 78 objetos anteriores de memória factual foram conservados na mesma ordem, com oito adições. Engines, política, persistência, backup, AGENTS e runner conservam os hashes do baseline. As adições de consulta/contexto/hooks são explicitadas, não descritas como ausência de mudança em todos os arquivos financeiros.

Retirar apenas as adições autorizadas reconstrói byte a byte Planning state/UI, execution-board model e finalize-session. O teste de Planning UI anterior conserva bytes exatos. Manifesto mantém os 120 scripts na mesma ordem e dez recursos originais de download com metadados preservados. Artefatos gerados mudaram legitimamente pelo builder.

## Tentativas anteriores e recuperação

- Preflight edit inicial bloqueou corretamente as 14 mudanças conhecidas; só prosseguiu com preservação autorizada e allow-dirty explícito.
- RED de pertinência, diagnóstico perdido, contexto vazio, origem de cotação e overflow permanecem como falhas brutas históricas; não foram reclassificados retroativamente.
- Estímulos de fixture inválidos, configuração PF congelada, ausência legítima de DOM lazy e rota real para o sino no layout Glass foram corrigidos nos testes, com tentativas preservadas. Contraprovas usam os mesmos oráculos positivos.
- Uma saída JSON de RED independente foi sobrescrita por engano; o log RED original e o resultado adversarial permanecem. A correção do artefato foi registrada, sem afirmar preservação daquele JSON original.
- Primeira FULL interrompida aos 3 minutos para corrigir um comando de metadado novo que apontava para helper não executável. O runner/produto/oráculos não mudaram. Tentativa incompleta preservada em `full-first-incomplete`; nova execução começou com freeze próprio e concluiu 96/96. A primeira tentativa continua incompleta, sem FULL PASS atribuído.
- Primeira captura comparativa semeou S antes de chamar writers e foi recusada por conflito. A semeadura foi corrigida; o guard não foi removido. Primeira prova suplementar não mediu o identificador runtime; a limitação e a repetição com identidade explícita estão preservadas.

Campanha integral e backup recuperável: `.superpowers/sdd/2026-10-22-notification-actions/`. Rollback, se solicitado: remover somente o delta desta tarefa sobre o baseline preservado e reconstruir pelo gerador oficial, sem resetar trabalho de outras tarefas.

## Limites

Testes automatizados em Chromium, contextos sintéticos e zoom nativo; não há validação de perfil real, dados reais, Safari, leitor de tela, aparelho físico, compreensão humana ou aceite visual do proprietário. Nenhuma ausência de aviso certifica segurança financeira. Não foram configuradas notificações externas, preferências novas, histórico persistente ou conexão adicional. Não houve configuração/escrita de memória global nem operações Git de integração/publicação.
