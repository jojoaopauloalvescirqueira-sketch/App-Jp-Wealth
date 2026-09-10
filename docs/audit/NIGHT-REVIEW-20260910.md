# Revisão noturna JP Wealth — entrega local de 10/09/2026

## CONFIRMADO — resultado e identidade

Quatro defeitos receberam correção delimitada: gravação recusada/retentativa em Finanças Pessoais, retorno de foco dos lançamentos/estornos Alladin, foco dos quatro atalhos principais do Dashboard e indicação do local correto de atualização da agenda. As regressões focais passaram. **O FULL final não passou: 48 PASS e 7 PRODUCT_FAIL na classificação bruta do gate; retorno 1.** Este é um candidate local com pendências, sem prontidão geral, aceite humano ou autorização de integração.

A revisão inventariou **27 famílias funcionais existentes** nos cinco módulos e recursos transversais. Todas têm algum check existente executado ou tentado; isso não significa 27 funcionalidades integralmente aprovadas. Os cenários interrompidos e os não executados estão discriminados na cobertura. Quatro destinos Research ainda vazios foram excluídos do denominador. Não se adicionaram funcionalidades ausentes.

| Identidade | Valor |
|---|---|
| Raiz da entrega | `/Users/joaopauloalves/.codex/night-reviews/20260910/product` |
| Branch local | `codex/night-review-20260910` |
| HEAD/base Git, sem novo commit | `4cb2e2a24c58a714b9909df6dd6f0415097480e2` |
| Candidate testado V2, fingerprint SHA-256 | `b2f11151e5838eb60a33a1409295af10d2b6b9d88eec78b1ce51e52738781f8e` |
| Build oficial | `60463a994a0068f8` |
| Candidate V1 preservado | `b1115ff97ca4996fdba88f0c9563cf9d571875547c83ad6c8f5ff2129e692945` |
| Base, build anterior | `88c0cb1ce5520311` |

O fingerprint identifica o JSON canônico ordenado dos 13 caminhos alterados e seus SHA-256; **não é um commit Git**. O manifesto inclui ainda 267 arquivos/links congelados como entradas. Este relatório foi acrescentado depois da validação, conforme previsto no freeze, apenas para registrar resultados. Sua identidade de entrega fica separada da identidade testada; nenhum runtime, teste, CHG ou artefato foi editado após o freeze V2.

Evidências duráveis: [manifesto V2](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/candidate-v2.json), [diff V2](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/candidate-v2.diff), [FULL final](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/full-final-v2/full.json), [recibo do processo](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/full-final-v2/process-final.json), [contrato CHG](/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/CHG-NIGHT-REVIEW-20260910.md).

## CONFIRMADO — correções e evidência antes/depois

| Item | Baseline exercitada | Candidate | Limite |
|---|---|---|---|
| NIGHT-01, PF, N2 | Criação recusada deixou cenários 1→2 em memória; retry levou a 3. Disco inicialmente intacto e log alterado. | Recusa mantém 1; retry explícito produz 2. `pfMutate` restaura somente PF e sequência/referência anterior do log em recusa comprovada. Rascunho permanece na sessão. | Não corrige Forex, NoCoda, Pivots ou Notas. UNKNOWN mantém a barreira conservadora e não permite retry cego. |
| NIGHT-02, Alladin, N1 | Foco perdido após cancelar/concluir lançamento e estorno, com os botões substituídos pelo render. | Resolve controle vivo; após estorno remover sua ação, retorna ao novo lançamento; em vista bloqueada usa título do contexto. | Payloads, domínio, guardas SUBMITTING/COMMITTED_WARNING e cálculos preservados. |
| NIGHT-03, Dashboard, N1 | Primeiro CTA abriu Forex sem foco na tela; execução vermelha parou ali. | Quatro CTAs por Enter entregam foco visível ao destino. Links profundos e ausência de gravação preservados. | Não se alegam quatro falhas observadas na baseline; os quatro destinos passaram no candidate. |
| NIGHT-04, Calendário, N0-V | Empty state Research mandava atualizar no Dashboard; primeiro assert interrompeu o teste antes do overlay. | Texto comum aponta Forex → Visão Geral. Ambas as superfícies passaram; atualização real acionou uma resposta sintética, sem consulta extra ao navegar repetidamente. | Nenhuma mudança em cache, API ou regra econômica. |

Fontes alteradas: `src/js/10-domain/12-personal-finance.js`, `src/js/20-ui/24-alladin-views.js`, `src/js/20-ui/25-dash-macro.js`, `src/js/40-app/17-economic-calendar.js`. O manifesto recebeu somente os quatro hashes correspondentes. Build e portable foram gerados exclusivamente por `tools/rebuild_monolith.py`, retorno 0; reprodutibilidade passou no FULL.

Testes alterados, sem remover oráculos: `tools/finpes_scenarios_test.py`, `tools/alladin_ui_tx_write_test.py`, `tools/alladin_ui_tx_reverse_test.py`, `tools/dashboard_macro_test.py`, `tools/research_navigation_test.py`. A solução PF e o núcleo da regressão anterior foram reaproveitados expressamente após reproduzir a falha na base atual. A worktree anterior não foi transportada nem modificada; seu CHG/artefatos não entraram nesta entrega.

PF cobriu os 32 atos públicos mapeados em 38 variantes: criação, edição, exclusão, validação, recusa, retry, cancelamento, gravação posterior por outro fluxo, recarga, conflito, recuperação, log no teto, campos desconhecidos e falha de clone. O retorno da persistência não pode ser sobrescrito pelo callback. Exceções/retornos indeterminados antes ou depois da escrita são tratados como UNKNOWN; o teste compara interface, memória, disco e histórico, sem deduzir que uma exceção significa ausência de gravação. Sucesso mantém referências e efeitos válidos. Os nove checks `finpes-*` passaram no FULL final.

Limite da comparação vermelha PF: 30 variantes completaram seus registros; oito exclusões interromperam a coleta ao procurar o registro já removido. As primeiras asserções vermelhas também impediram alcançar alguns subcasos posteriores. Não se apresentam essas interrupções como 38 comparações completas antes/depois.

Registros: [baseline focal](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/baseline-focal/pf.stdout), [complemento defensivo PF](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/pf-defensive-v2/stdout), [fonte PF reaproveitada](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/pf-source-reuse.json), [comandos e retornos](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/commands-and-results.json).

## CONFIRMADO — validação, reutilização e falhas preservadas

| Evidência | Resultado | Natureza |
|---|---|---|
| FULL histórico da base | 55 checks PASS | Reaproveitado por equivalência exata de conteúdo, não executado novamente nem sob rede pareada. |
| Cinco focais na baseline atual | Cinco processos com retorno 1 | Regressões vermelhas novas, com limites de interrupção descritos acima. |
| Focais Alladin, Dashboard e Research após patches | PASS | Novas execuções; preservados os recibos V1. |
| Primeiro complemento defensivo PF | TEST_HARNESS_FAIL | Injeção de structuredClone interferiu na serialização Playwright; preservado, não atribuído ao produto. |
| Complemento defensivo PF corrigido | PASS | Injeção restrita à chamada PF e restaurada antes da serialização; mesmo oráculo. Depois confirmado dentro do FULL congelado. |
| Matriz UI | 8/8 condições PASS, 16 screenshots | 1440/390 × claro/escuro × sidebar/topbar; teclado, foco, navegação, contagem de chamadas, recarga, armazenamento e overflow. |
| Realocação, sidebar e escolha de layout | Três processos PASS | Regressões próximas novas sobre V1; runtime e caminhos pertinentes idênticos em V2. |
| FULL V1 | 48 PASS / 7 PRODUCT_FAIL brutos | Execução nova preservada, 06:13:25–06:21:56 UTC. Identificou incompatibilidade do helper compartilhado com o teste documental. |
| Dashboard focal V2 | PASS | Nova execução do consumidor diretamente afetado. |
| Documental focal V2 | Falha, retorno 1 | Erros de carregamento no primeiro consentimento, sem repetir o antigo timeout de controller. |
| Observação SW V2 | PASS do oráculo limitado | Controller ativado e presente após recarga; recursos externos recusados. Não equivale à suíte documental. |
| FULL final V2 | **48 PASS / 7 PRODUCT_FAIL brutos** | Execução nova, 06:29:17–06:36:56 UTC; retorno 1; nenhum dos 267 inputs congelados mudou. |

A ligação histórica foi conferida: o FULL antigo rodou na árvore suja da instalação X2, sobre HEAD `5797462…`; seus nove hashes correspondem ao commit `57fbd25474b1570d4bd47253d73ed827eaed5cf9`. A árvore desse commit e a main base `4cb2e2a…` são ambas `2b748f947174fea62bb908f9b397c4795179c0f8`. O hash do resultado coincide com o recibo original. Isso sustenta reaproveitamento da baseline, sem transformar a execução antiga em FULL novo ou contraprova causal de rede. [Vínculo verificável](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/baseline-full-reuse.json).

V1→V2 alterou somente o CHG e o helper `dashboard_macro_test.boot`: padrão `service_workers="allow"` restaurado para consumidores externos e `block` explícito nos três chamadores internos do Dashboard. `statute_documentary_test` importa esse helper e exige controller; o bloqueio imposto na V1 causou sua interrupção após sete consentimentos aprovados. Nenhuma expectativa documental, gate ou SW do produto foi alterado. A descoberta justifica o FULL V2; não se repetiu a suíte apenas para buscar resultado favorável.

A matriz 8/8 é reaproveitada para V2 porque usa inicialização Alladin e a mesma asserção Dashboard; não chama `dash.boot`. Os três patches UI, PF, outros testes e artefatos têm os mesmos bytes. Isso não é uma nova execução da matriz. A realocação foi exercitada sem fornecer a raiz histórica anterior à mudança; não se alega nova prova financeira antes/depois da realocação.

Outros registros não apagados: primeiro canário com erro de fechamento de sockets/descrição IPv6 incorreta, corrigido por recibo V2; primeira versão do controlador da matriz **NOT_RUN**, corrigida antes da execução por usar atributo de navegação errado; falha do clone PF; FULL V1 e focais documentais. Não foi enfraquecido oráculo para ocultá-los.

### Sete falhas do FULL final

O gate classifica genericamente muitos retornos não zero como PRODUCT_FAIL. O rótulo bruto permanece; a análise causal é adicional e não o converte em PASS.

| Check | Evidência registrada e limite |
|---|---|
| smoke | Erros de resolução/carregamento no console; registros sem todas as URLs necessárias para atribuir cada falha. |
| settings | Falha na verificação de console; feed externo identificado. Não demonstra defeito novo nos cálculos/configurações. |
| statute-documentary | Interrupção durante consentimento por recursos recusados; consultas, download e operação documental offline não concluídos em V2. |
| galton-board | Primeiro fluxo UI interrompido pela asserção de console; não comprova falha física nova nem encerra intermitência histórica. |
| session-finalization | Interrupção na verificação de console do cenário focal; etapas posteriores não concluídas. |
| storage-governance | Erros de resolução/carregamento; atribuição específica de cada recurso permanece limitada. |
| mvp-notes | Erros de resolução/carregamento interrompem a suíte; isso não é a prova causal do defeito de gravação constatado em probe independente. |

Detalhes de job/check, trecho, classificação e limites: [triagem V2](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/full-final-v2/triage.md), [stdout integral do runner](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/full-final-v2/stdout), [outputs por check](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/full-final-v2/full.json). Não houve terceira tentativa do FULL nem liberação de APIs para passar.

## CONFIRMADO — cobertura funcional e defeitos mantidos abertos

O inventário registra finalidade, dados/estados, consumidores, fontes e testes por família. A [matriz completa de 27 famílias](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/coverage-table.md) associa checks reais e lacunas; [JSON final](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/coverage-final.json) e [inventário inspecionado](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/coverage-inventory.json) preservam a distinção entre leitura e execução.

| Grupo | Famílias inventariadas | Delimitação |
|---|---:|---|
| Dashboard | 2 | Síntese dos quatro módulos; status e atalhos. |
| Forex | 6 | Preparação/conta, ordens/risco, motor de lote, apuração diária, finalização de operação/histórico, planejamento/câmbio. |
| Finanças Pessoais | 5 | Orçamento, dívida/crédito, comparação, cenários, visão consolidada. |
| Research | 2 | NoCoda e Pivots; calendário deduplicado no transversal. |
| Alladin | 4 | Lançamentos/estornos, cadastros, caixa, posições por quantidade. |
| Transversal | 8 | Calendário, navegação, configurações/editor, backup/recuperação/finalização, notas, consulta educativa/normativa, Galton, PWA. |
| **Total** | **27** | Denominador funcional; não contagem de testes nem aprovação integral. |

Seis achados de produto continuam abertos e bloqueados para correção pelo escopo. Não foram incluídos silenciosamente no delta:

| ID | Achado | Evidência / limite | Próxima decisão |
|---|---|---|---|
| OPEN-01, N2 | Forex confirma realizado mensal/fechamento diário mesmo com gravação recusada. | VM com domínio e save reais, DOM/compute auxiliares sintéticos; memória avança, disco não. Não é interação completa de navegador. | Fatia própria de fronteira de persistência Forex. |
| OPEN-02, N2 | NoCoda sinaliza salvo e limpa dirty embora save retorne false. | Navegador: âncora em memória diverge do disco; retry explícito grava chave única. Recarga ocorreu após retry bem-sucedido. | Preservar rascunho e distinguir confirmação/rejeição. |
| OPEN-03, N2 | Pivots fecha formulário recusado; reinserir explicitamente duplica o pivot. | Navegador: 1 em memória/0 disco; reentrada gera 2 IDs gravados e recarregados. Não é duplicação automática sem ação do usuário. | Fatia específica da criação; outras mutações sob quota ainda não verificadas. |
| OPEN-04, N2 | Notas criação/edição recusadas perdem dirty. | Navegador, save false: recarga antes de outra gravação perde a nota nova/restaura o corpo antigo. Não se observou duplicação. | Correção delimitada de confirmação; pastas sob quota NOT_RUN. |
| OPEN-05, N3 | Reservas: painel insuficiente e clearance/snapshot regulares divergem. | VM: capital 10.000→20.000, FCR requerido 1.500→3.000, corrente 1.500, cobertura 50%; stubs de risco/compute limitam conclusão. | Decisão financeira/normativa e validação específica; não inferir regra V11. |
| OPEN-06, N3 | Alladin aceita datas impossíveis. | Domínio/save em VM persistiram depósito 2026-99-99 e estorno 2026-02-30; formato textual incorreto foi recusado. | Delimitar regra/calendário e autorização antes de corrigir. |

Os probes NoCoda/Pivots/Notas chamaram o save real e recusaram somente setItem da chave sintética alvo; seus resultados incluem retorno false, interface, memória, bytes armazenados e recarga. O processo terminou com retorno 1/propriedades violadas, não com sucesso fabricado. Os probes VM são coletores com retorno zero, **não testes aprovados**. O trecho PF vermelho no probe financeiro lê a baseline por `git show`, não o PF corrigido.

Evidências: [probes de persistência em navegador](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/adjacent-persistence/results.json), [recibo](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/adjacent-probe-receipt.json), [Forex VM](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/diagnostic-probes/forex.stdout), [Alladin VM](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/diagnostic-probes/finance.raw.json), [auditoria de proveniência](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/audit-diagnostic-evidence.md).

## CONFIRMADO — ambiente, comandos e preservação

Ferramentas existentes: Python `/private/tmp/jpw-dashboard-official-venv/bin/python`, Node do runtime local e Chromium Playwright instalado. Perfis novos, armazenamento e dados sintéticos. Os testes de navegador/domínio foram executados com o perfil processual `/usr/bin/sandbox-exec -f …/evidence/loopback-only.sb`: rede de saída negada com exceção localhost. Canário V2 comprovou respostas IPv4/IPv6 esperadas e EPERM para destino TEST-NET externo. Nenhuma permissão global foi alterada; não se afirma sandbox de filesystem.

Comando FULL final, executado na raiz da entrega:

```sh
/usr/bin/sandbox-exec -f /Users/joaopauloalves/.codex/night-reviews/20260910/evidence/loopback-only.sb /private/tmp/jpw-dashboard-official-venv/bin/python tools/quality_gate.py --tier full --artifact /Users/joaopauloalves/.codex/night-reviews/20260910/evidence/full-final-v2/full.json
```

Os comandos exatos dos 55 checks constam no JSON bruto. Os recibos focais registram argumentos, retorno e, quando capturados, horários/hashes. [Ledger consolidado](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/commands-and-results.json). O recibo defensivo PF isolado não traz sozinho cwd/fingerprint completo; sua execução no FULL V2 fornece a ligação congelada mais forte.

O FULL usou TMPDIR durável do experimento, Git global/sistema ignorados apenas no processo, hooks/templates locais vazios e signing desligado no processo. Trace V2 correlaciona por SID **7 init, 11 add, 11 commits sintéticos e 2 checkout**, todos em sete repositórios descartáveis sob `evidence/tmp`; inclusive init possui def_repo registrado nesta execução. Fonte do teste e política de efeitos mostram repositórios próprios, sem remotos. Não houve commit no repositório do produto. [Conferência Git sintético V2](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/full-final-v2/git-synthetic-verification.json).

Conferência local: a main original permanece em `4cb2e2a24c58a714b9909df6dd6f0415097480e2`, limpa, com 266 arquivos/links protegidos iguais ao manifesto inicial. Stash `bfdb323f05f0df27c79fd11cb18d64352a5c5194` preservado. Outra tarefa `codex/pf-save-retry`, HEAD `57974625381b864d5fd85678b6f23b85f90c3c6d`, mantém seus seis arquivos/fingerprint `c6c4b687…` e estado Git anteriores. O candidate atual mantém HEAD-base, sem staged ou conflitos. [Preservação antes do relatório](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/preservation-before-report.json); [conferência final e fingerprint da entrega](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/delivery-final.json).

Nesta revisão não foram executados commit do produto, push, PR, merge, deploy, reset ou stash. A instalação X2 já consta no histórico da base como commit `57fbd25…` integrado por `4cb2e2a…`; não se repetiram essas ações nem se agregou a revisão a elas. Não se afirma consulta remota nova ou estado atual de integração externa.

## CONFIRMADO — auditoria e imagens

Auditorias independentes focais, somente leitura de produto, confrontaram fontes, testes, hashes e recibos. O executor fez os testes; leitura dos revisores não é relatada como execução deles.

- [PF V1](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/audit-pf-final.md) e [adendo PF V2](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/audit-pf-v2.md): avaliação focal do pfMutate, consumidores e evidências; não concedem aprovação ao FULL falho.
- [UI V1](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/audit-ui-final.md) e [adendo UI V2](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/audit-ui-v2.md): UI_FOCAL_REVIEW_APPROVED limitado aos três patches. V2 reconhece a lacuna do helper compartilhado e justifica reaproveitamento da matriz.
- [Diagnóstico e proveniência](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/audit-diagnostic-evidence.md) e triagem do FULL preservam falhas, incertezas e distinção VM/navegador/baseline/candidate.

Screenshots no build `60463a994a0068f8`: [Dashboard desktop escuro](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/ui-matrix-final/sidebar-1440-dark-dashboard.png), [Forex celular claro](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/ui-matrix-final/sidebar-390-light-forex.png), [Forex navegação superior](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/ui-matrix-final/topbar-1440-light-forex.png), [Dashboard celular escuro](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/ui-matrix-final/topbar-390-dark-dashboard.png), [PF recusa no FULL V2](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/full-final-v2/pf-refused-light.png).

O executor inspecionou essas cinco imagens. Os avisos globais de backup/gravação sobrepõem conteúdo nas capturas e foram preservados; não se declara interface sem sobreposição. Screenshots não provam interação: [resultados e contratos da matriz](/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/ui-matrix-final/results.json) e recibos focais sustentam teclado, foco, atualização e persistência.

## INFERÊNCIA

A política de rede é compatível com as falhas de recursos externos. Em alguns checks o feed está identificado; nos registros sem URL não é possível atribuir cada erro ao mesmo destino. A observação SW foi separada e começou a capturar após boot: suas URLs não podem ser retroatribuídas aos logs do FULL. O padrão recorrente não justifica classificar indiscriminadamente todas as falhas como ambiente nem converter o FULL em PASS.

A preservação dos hashes do runtime/testes pertinentes sustenta reaproveitamento dos focais V1 na revisão V2. Isso não garante comportamento em todo navegador ou sessão. O escopo financeiro limitado e a menor alteração em pfMutate reduzem a superfície do delta; não demonstram ausência de todos os defeitos de persistência.

## NÃO VERIFICADO

Conclusão integral dos sete checks interrompidos, física/benchmark posteriores do Galton, APIs econômicas ao vivo, hardware celular físico, leitor de tela, picker nativo com dados reais, todas as mutações adjacentes sob quota e homologação normativa V11. A revisão não é auditoria geral de segurança nem prova de software sem bugs.

Não foram testados carregamento nativo de skills em novas sessões Codex/Claude, completude do Atlas, fidelidade AUD-05/P2 ou atualização do grafo. Essas pendências não são encerradas pelo FULL do produto. Contexto/README/descrições antigas de finalização e caminho antigo do Harness permanecem como dívida informada, sem edição nesta tarefa. Nenhuma alegação de compatibilidade universal dos agentes foi feita.

## RECOMENDAÇÃO

Manter este candidate local para revisão humana. Antes de integrar, resolver o gate falho mediante pacote delimitado de avaliação: onde a URL já foi identificada, preparar isolamento/fixture sintética apropriada; onde não foi, capturar apenas a observação discriminante necessária. Preservar os oráculos, a barreira de rede e todas as falhas anteriores. Isso exige delimitação própria se ultrapassar os arquivos/efeitos desta entrega; não foi executado aqui.

Priorizar em seguida fatias separadas de persistência Forex/NoCoda/Pivots/Notas. Reservas e datas exigem decisão material antes de patch. Recomendar atualização posterior do contexto para refletir o estado realmente aceito; não aplicá-la automaticamente.

Rollback permanece limitado ao delta desta branch comparado com BASE_SHA e manifesto. Artefatos derivados devem voltar pelo processo oficial a partir das fontes correspondentes. Nenhuma limpeza geral, exclusão de worktree, restauração do original ou manipulação de dados do usuário foi executada. A entrega encerra a rodada autorizada com limitações explícitas, não o desenvolvimento do produto.
