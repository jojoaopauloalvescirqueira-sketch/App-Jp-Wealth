# Calendário econômico — entrega local validada

Build **5b4ef1141c9583bf**, branch `codex/calendario-economico-ff-20261028`, HEAD preservado `3e24f60`. O calendário mensal recebeu Forex Factory, nove moedas e complementos oficiais Fed/BoC. O candidato anterior e suas alterações de Portfólio, Gerenciamento, Caixa Anual, Hedge Prop Firm e demais áreas foram preservados.

## Prévia e uso

[Abrir prévia local conferida](http://127.0.0.1:58911/index.html?v=5b4ef1141c9583bf). O endereço é uma origem isolada: não transfere os dados pessoais do endereço anterior. [Identidade HTTP](PREVIEW.json): sete arquivos HTTP200 idênticos aos bytes testados, incluindo build, adaptador e pacote.

Novas instalações oferecem USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD e CNY, inicialmente Alto impacto. Preferências antigas são preservadas; use **Filtros → Incluir moedas novas** para acrescentar EUR/CAD/AUD/CNY explicitamente. O dia 28/10 tem os sete tópicos CAD/FOMC documentados no recibo das capturas quando USD/CAD e Alto estão selecionados.

O pacote local foi coletado às **17:21:55 BRT de 28/10/2026**. A passagem de duas horas pode produzir aviso de conteúdo anterior na prévia; abrir ou baixar novamente um pacote antigo não renova seu frescor.

## Resultado automatizado

| Prova no candidato final | Resultado |
|---|---|
| `quality_gate.py --tier full` | **116/116 PASS**, exit 0; demais classificações zero |
| Duração FULL | 3.158,714 s, cerca de53 min; terminou19:44:50 BRT |
| Identidade dos inputs | **1643/1643** idênticos antes/depois; nenhum ausente |
| Matriz visual existente | **413/413 PASS**, tolerância de 2 px CSS, 877,799 s dentro do limite original de 900 s |
| Calendário/agenda | 17 casos PASS, incluindo nove moedas, filtros antigos/novos, foco, cursor, rascunhos e sessão |
| Consulta/runtime e coletor | 24 casos runtime e32 do coletor, chamados pelo check mensal; modelo com14 casos próprios |
| Pipeline real de navegador com transporte sintético | 186 verificações em18 contextos; feed→cache→consulta→lista/marcador e consumidor semanal |
| Recuperação/backup | 8 casos; nove moedas aceitas e preferência antiga preservada; cache público fora do backup |
| Distribuições | HTTP, PWA offline, arquivo local e portátil PASS |

[FULL original](full-final.json), [exit real](full-exit.json), [índice de116 checks](CHECK-INDEX.json), [auditoria de preservação](FINAL-AUDIT.json), [freeze](INPUT-FREEZE.json) e [recibos focais finais](proofs/FINAL-COPY-RECEIPT.json).

Os cenários incluem quatro layouts, dois temas, larguras320–1.440 px, teclado, foco e zoom nativo de 200%. Toque automatizado/emulado não comprova interação física, leitor de tela ou aceite humano.

## Inventário do que mudou

| Componente | Comportamento entregue |
|---|---|
| Alimentador local FF | Nove moedas/todos os impactos, snapshots e revisões; modelo de agendamento30 min e publicação preparado, sem ativação |
| Complementos oficiais | Fed/FOMC e Banco do Canadá, associados por catálogo documental explícito; referências antigas preservadas |
| Consulta mensal | Snapshot síncrono, intervalos reais, fontes por moeda, origens de impacto e horários originais; ausência não vira zero eventos |
| Identidade/revisão | Sem ID nativo inventado; retirada vira “Não consta na última coleta”; cancelamento exige informação explícita; divergência conserva referências e “A confirmar” |
| Atualização | Coleta, publicação e atualização declarada separadas; aviso FF após 2 h; falha conserva último conteúdo válido, com diagnóstico e recuperação explícita |
| Interface | Mesmos filtros na lista/bolinha; atualização manual, cobertura por dia, nove moedas e inclusão explícita sem reset das preferências |
| Sessão | Uma alimentação pública compartilhada; invalida respostas antigas, cancela timers e retoma após abertura aceita; sem coletores por digitação comum |
| Backup | Enum de preferências ampliado; sem migração de registros pessoais e sem incluir o cache público |
| Metadados | Política global coerente com fontes mistas; textos oficiais antigos conservados em `officialBaseMetadata`; cópias defensivas |
| Distribuição | Manifest/fingerprint/service worker/portátil reconstruídos pelos geradores oficiais |

Os fontes e controles alterados estão no [contrato do produto](../../work/CHG-JPW-ECONOMIC-CALENDAR-FF-PRODUCT-20261028.md), [contrato separado dos controles](../../work/CHG-JPW-ECONOMIC-CALENDAR-FF-CONTROLS-20261028.md), [arquitetura](../../architecture/CALENDAR-AGENDA.md) e [avaliação de impacto](AGENTIC-IMPACT.md).

## Fontes, cobertura e ativação externa

**153 registros locais =54 oficiais anteriores +97 FF +9 oficiais novos −7 associações documentadas**. São22 descritores de fonte e25 linhas de cobertura. A exportação FF recebida cobre parcialmente 25–31/10: **não constitui cobertura mensal completa**. CHF tem observações FF da semana, mantendo pendências das agendas oficiais suíças. [Inventário e limites](SOURCES-COVERAGE.md), [dados e hashes](SOURCE-INVENTORY.json).

**A ampliação externa v2 e seu agendamento não foram publicados nem ativados.** O endpoint remoto padrão v1 preexistente permanece limitado a quatro moedas/Alto; esta entrega não afirma tê-lo criado, desligado ou ampliado. Preparação local e coleta manual não comprovam execução agendada. Publicação, configuração externa e alcance da permissão serão etapas separadas. A permissão FF não comercial é declaração do proprietário, sem auditoria contratual pelo agente.

As referências oficiais permanecem vinculadas aos eventos. Não foram enviados dados pessoais ao alimentador, criadas dependências, alterados cálculos financeiros, migrados registros, executadas ordens, feitos commits/merge/push ou publicada a aplicação.

## RED/GREEN, contraprovas e revisão

CAD ausente, Fed ausente e cobertura fora do intervalo foram reproduzidos na base arquivada. O mesmo juiz do modelo rejeitou os fontes anteriores; a integração nova recebeu provas de transporte até a lista e o marcador. [Baseline](proofs/baseline-probe.json), [pipeline](proofs/full-shared-browser-pipeline.json), [runtime](proofs/runtime24.json), [contraprovas do runtime](proofs/runtime-counterproofs.json) e [coletor](proofs/collector-counterproofs.json).

Uma primeira rodada FULL foi deliberadamente interrompida ao detectar P2 nos metadados globais antigos. Os 52 checks aprovados e413 visuais dessa rodada são históricos, **não a aprovação final**. Após correção revisada, o novo caso permanente do modelo foi RED e GREEN; oito mutantes foram rejeitados. [Proposta](metadata/PROPOSAL.md), [RED](metadata/model22-red.log), [GREEN](metadata/model-contract-green.log), [contraprovas](metadata/counterproofs.json), [aplicação conferida](metadata/APPLIED-RECEIPT.json) e [rodada parcial preservada](attempt-1-metadata-audit/full-interruption-metadata.json).

Os controles existentes de FULL e qualidade visual não foram alterados neste delta. Somente expectativas superadas de moedas, fontes, rótulos e atualização foram substituídas dentro do contrato próprio; fixtures declaram seu isolamento. Erros dos helpers não foram apresentados como RED do produto. [Registro completo das rodadas](RUN-LEDGER.md).

A revisão foi cruzada: o revisor do adapter/UI/runtime/controles não aprova sua própria proposta posterior de metadados; outro revisor verificou essa correção, seus hashes e as capturas. [R3](review/REVIEW-R3.md), [metadados/freeze](review/applied-metadata-freeze-review.json), [capturas](review/CAPTURES-INVENTORY-REVIEW.md) e [recibos finais](review/FINAL-RECEIPT-REVIEW.md) e [confronto independente do delta e da entrega](review/INDEPENDENT-FINAL-5B4E-REVIEW.md). Revisão técnica e execução automatizada não substituem aceite humano.

## Comparação visual e preservação

[Antes1440/claro](captures/before-1440-light.png), [depois1440/claro](captures/after-1440-light.png), [depois390/escuro](captures/after-390-dark.png), [recibo DOM](captures/receipt.json).

“Antes” é uma comparação controlada com injeção dos dois fontes antigos arquivados no aplicativo candidato, USD apenas; não é uma execução integral do checkout antigo. “Depois” usa os fontes finais e USD+CAD. As imagens mostram o início da lista rolável; os sete títulos completos são comprovados pelo DOM, não por sete linhas simultaneamente visíveis.

Os 3.496 arquivos da base continuam presentes. Arquivos financeiros, AGENTS, gate, verificadores visuais e os fontes de notificações, ferramentas e guia protegidos permaneceram idênticos ao início desta tarefa. Sete payloads Stoikus/mercados mudaram somente seu buildId pela reconstrução oficial. O teste de Hedge reescreve um timestamp em recibo histórico: a execução nova foi preservada em `proofs`, o original restaurado byte a byte e a diferença única comprovada em [recibo próprio](proofs/historical-receipt-restored.json).

Achados históricos **Caixa Anual UX01/UX02**, falha suplementar de navegação e causas Epoch/Alladin continuam abertos em seus registros, mesmo com os checks desta rodada aprovados. Esta entrega não homologa V11 nem encerra esses incidentes.

## Aceite humano separado

Pendente: localizar as notícias CAD/FOMC de 28/10, personalizar moedas/impactos, reconhecer cobertura parcial e conteúdo anterior, conferir os horários no fuso desejado e verificar continuidade da agenda pessoal no endereço com seus próprios dados. Não há aceite visual humano presumido.
