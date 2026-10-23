# Revisão factual de cobertura — Notificações

Candidate: **8b0b231a1b0c41b7**, branch `codex/notificacoes-acoes-20261022`. Esta revisão não altera fontes, testes, contratos ou gates e não conclui o FULL que está sendo executado pelo fluxo principal. Todos os ensaios próprios usaram contextos novos e dados sintéticos.

## Ligação efetiva aos gates

A enumeração foi obtida importando as definições do runner, sem executá-lo novamente. Os hashes atuais dos sete arquivos conferidos coincidem com `freeze-before.json`; detalhes em [wiring-and-freeze.json](wiring-and-freeze.json).

| Entrada | Ligação atual | Evidência de execução disponível nesta revisão |
|---|---|---|
| Central — 30 casos | `notification-center`, somente FULL, comando sem seleção parcial | Recibo focal `notification-final30-green.json`: 30 PASS, anterior à reconstrução final. O mesmo teste está congelado; isso não equivale ao resultado do FULL final. |
| Eficiência — 20 casos | `notification-efficiency`, somente FULL | Recibo focal `notification-final20-efficiency-green.json`: 20 PASS. Mesma distinção entre focal e FULL final. |
| Qualidade visual das notificações | Default `all` de `ui-visual-quality`, no STANDARD e FULL | O verificador atual exige **44 casos** de notificações, dentro de **322 casos** totais. O recibo focal `visual-second` contém **42 PASS**, antes da inclusão dos dois casos de nome longo; não comprova 44 PASS nem a execução integral atual. |
| Consulta/entrada contextual de Planejamento | `planning-state`, no STANDARD e FULL | Casos `PLNOTICE-Q01–Q09` e `PLNOTICE-CTX01–CTX04`, dentro da suíte de estado. A leitura identifica o vínculo; os resultados finais devem vir do recibo executado. |
| Disponibilidade adaptada | **Focal adicional fora do runner** | `notification_and_suspended_work`: três contextos PASS em `module-availability-notification-final-green.json`. Importar constantes desse módulo em outro teste não executa esses três contextos. |

O runner conserva **55 checks STANDARD** e **96 FULL**. A presença de casos no manifesto ou no runner demonstra o vínculo, não sua execução ou aprovação final.

## Correspondência com o plano aprovado

| Comportamento | Prova concreta | Limite da prova |
|---|---|---|
| Ações ativas, sem lidas/agenda/histórico genérico | `actionable-only-unresolved-count`, casos de calendário e mensagens nativas; contraprovas de badge oculto, duplicação e agenda promovida | Não constitui classificação universal de toda mensagem possível do aplicativo. |
| Dedupe e resolução | Filtros/dedupe; consulta mantém a pendência PF, mudança da condição remove-a; `PLNOTICE-Q04` usa comandos reais no harness de estado | A mudança de status PF no teste da central é uma fixture, não um fechamento completo pela UI de PF. |
| Planejamento factual por conta | Zero explícito, valores não nulos, anulados, arquivados, fechamentos invalidados, dependência anterior e ausência de 120 projeções nos casos Node; contexto multiconta, rascunho, toque e cancelamento no navegador | Não se repetem todas as combinações Node pela UI em cada distribuição. |
| Virada do mês | `planning-local-month-boundary`: relógio controlado em **America/Sao_Paulo**, timer rearmado por `pageshow`, passagem de 23h59 para 00h sem refresh manual posterior | Simulação controlada; não é observação de um mês de uso humano. Houve zero gravações financeiras, zero mudança de S/documento e zero gravações em caches econômicos nessa execução. |
| Forex somente com fatos | Períodos vazios não geram tarefas; identidades de conta/período e fontes manual/diária/legada contrastadas | Não prova todos os estados de risco, todos os instrumentos nem conformidade financeira da política. |
| Guards antes dos efeitos | Rascunho Planning preservado ao cancelar; substituição de S durante consentimento impede navegação; CTA cambial abre a conta/período corretos | Não é exploração exaustiva de toda combinação assíncrona entre abas. |
| Módulos congelados | Pendências operacionais suprimidas; incompatibilidade/integridade Alladin permanece em Sistema; clique antigo congelado não muda contexto | Integridade de todas as versões/esquemas dos módulos não foi injetada no navegador desta suíte. |
| Fonte indisponível e geração | Falha PF retém diagnóstico não atual sem dupla contagem; recuperação e troca de S removem diagnóstico da geração anterior | O teste injeta falha de leitor; não simula falha física de todos os serviços ou navegadores. |
| Proteção de dados/backup | UNKNOWN mantém bloqueio de save; confirmação atual/ausente/vencida/inválida/futura do backup; finalização preserva documento durável | Os novos testes do sino não injetam individualmente todas as recusas/conflitos/recuperações através de cada escritor real. Testes gerais de persistência têm escopo próprio. |
| Visual, teclado e foco | Seis casos de geometria/teclado da central; expansão e foco após refresh nos cenários visuais; matriz/zoom e contraprovas registrados no verificador | Conservação exata da posição de rolagem durante inserção/remoção/reordenação de condições não tem oráculo específico nesses testes. Não há aceite humano, leitor de tela, Safari ou toque físico comprovados. |

## Quatro distribuições: interação própria no build congelado

Os testes gerais de distribuição existentes exercitam Planejamento, geração e service worker. Eles **não abrem a central de notificações**; sua aprovação isolada não comprovaria o comportamento do sino. Para fechar essa lacuna de interação, esta revisão executou [distribution_probe.py](distribution_probe.py), com saída em [distribution-results.json](distribution-results.json) e [log final](distribution-isolated-final.log).

| Modo | Resultado observado |
|---|---|
| HTTP modular | PASS; build conferido em runtime. |
| Modular `file://` | PASS; build conferido em runtime. |
| Portátil `file://` | PASS; cópia do HTML em diretório temporário contendo **somente esse arquivo**, sem dependências locais ao lado; build conferido em runtime. |
| PWA offline | PASS; instalação/controlador/cache reais, remoção das rotas de fixture antes de recarregar offline, `navigator.onLine=false`, estado confirmado restaurado e build conferido em runtime. |

Em cada modo foram efetivamente exercitados: sino, duas pendências de contas distintas, expansão do diagnóstico, manutenção de expansão/contagem após refresh, fechamento/reabertura, filtro Planejamento e CTA para a conta explícita e seu primeiro mês anterior. Após a semeadura, S/localStorage/sessionStorage permaneceram idênticos e não houve requisições adicionais observadas na página durante essas ações. A identidade dos oito arquivos de aplicativo/distribuição registrados permaneceu igual antes/depois do ensaio.

Essa prova suplementar cobre a jornada descrita; **não repete os 30 casos da central, os 20 de eficiência ou os 44 visuais em cada distribuição**. Também não é inspeção completa de todo tráfego autônomo do service worker.

A primeira coleta de quatro modos passou na jornada, mas leu incorretamente o nome público do identificador e registrou build observado `null`. Seus arquivos `distribution-first-attempt.log` e `distribution-first-attempt-results.json` estão preservados: são prova da jornada coletada, **não prova daquela identidade de runtime**. A coleta seguinte confirmou o identificador e permanece em `distribution-before-portable-isolation.json`; a execução final acrescenta isolamento físico do portátil. Nenhum desses resultados foi reescrito como se comprovasse uma condição não observada.

## Resultados brutos e alegações permitidas

O mapa anterior `notification-test-contract-map.json`, no diretório privado da campanha, conserva REDs, falhas de harness, tentativas exploratórias e os recibos focais verdes. Os hashes dos três recibos finais focalizados constam em `wiring-and-freeze.json`; os arquivos originais foram apenas lidos nesta revisão.

Falhas brutas anteriores permanecem separadas: controles de lidas, diagnóstico perdido, períodos vazios, navegação antes da revalidação e cotação com fonte errada tiveram reproduções PRODUCT_FAIL próprias. Erros de sintaxe, fixtures incompletas e invocação involuntária do probe têm avaliação de harness explícita, sem apagar a classificação originalmente impressa. O primeiro FULL interrompido também possui registro próprio e não é promovido a PASS.

É sustentado: os vínculos descritos existem, os focais preservados têm os resultados citados e a jornada suplementar passou nos quatro modos no build conferido. **O resultado agregado do FULL final, estabilidade de todos os seus inputs, aceite visual/compreensão humana e publicação devem ser informados pelos seus próprios recibos; não são concluídos por esta revisão.**
