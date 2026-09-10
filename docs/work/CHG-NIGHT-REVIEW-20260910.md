# CHG-NIGHT-REVIEW-20260910 — revisão noturna delimitada

Contrato anterior à escrita de runtime/testes, 2026-09-10. Registra a autorização expressa do objetivo noturno; não concede aceite, publicação ou autoridade adicional. Limite: 05:39:47–11:39:47 UTC; reservar validação/relato até 10:15 UTC. Um executor, revisores somente leitura do produto.

## Identidade, compreensão e autoridade

Raiz: `/Users/joaopauloalves/.codex/night-reviews/20260910/product`; branch autorizada `codex/night-review-20260910`; BASE_SHA `4cb2e2a24c58a714b9909df6dd6f0415097480e2`; build inicial `88c0cb1ce5520311`. Uma worktree dedicada foi criada da main local limpa. Original, stash e a tarefa PF anterior permanecem protegidos pelos manifestos em `../evidence/original-before.json` e `../evidence/pf-task-protected.json`.

JP Wealth é uma aplicação financeira local-first: preservar dados e dar confirmação rastreável é requisito, não refinamento opcional. PF mantém orçamento, dívidas/crédito e cenários em BRL_CENTS; sua fronteira compartilhada `pfMutate` atende os atos desses consumidores. A tarefa anterior demonstrou recusa de save seguida de ato fantasma/log em memória; a revisão atual precisa reproduzir isso na baseline vigente. Depois, recusa comprovada deve restaurar somente PF/log, sem apagar alterações legítimas em outros agregados. UNKNOWN não prova ausência de gravação: mantém tratamento conservador existente, bloqueia retry cego e orienta conferência. Nenhuma fórmula, unidade, schema ou regra financeira muda.

Dashboard resume os módulos e encaminha ao contexto operacional, sem gravar preferências ao navegar. Seu CTA deve entregar foco visível no destino. Alladin registra fatos append-only e estornos pelo domínio; a interface deve retornar o foco após cancelar/concluir o modal mesmo quando o render substitui o botão original. Calendário é compartilhado entre Research/modal e o widget de Forex: a orientação para atualizar deve apontar ao local realmente existente, sem duplicar consulta/cache.

Fontes lidas e confrontadas: AGENTS, README, CONTEXT-MAP, contratos PERSONAL-FINANCE/STATE-SCHEMA/DB-STORAGE-GOVERNANCE/DATA-RECOVERY/SECURITY-MODEL/QUALITY-GATES/CHANGE-PROCESS, Atlas e X2 da revisão base; consumidores atuais e testes focais. Harness real `A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`. O endereço antigo `00 -` em AGENTS não será corrigido aqui. Preflight audit/edit PASS na branch limpa, com aviso histórico de frescor preservado. Documento de recuperação/README descrevem finalização antiga: código/testes atuais preservam PF/Alladin/Tickets; a divergência será reportada, sem atualizar contexto canônico.

Risco máximo autorizado N2/A3 **somente PF X2-01**. Foco/navegação N1/A2; orientação textual N0-V/A2. Demais persistências e datas/reservas/cálculos são investigação, sem patch. A skill de change-control sugere ACTIVE-TASK; prevalece a proibição expressa de atualizar contexto: este CHG registra a tarefa sem editar ACTIVE-TASK.

## Delta permitido

- `src/js/10-domain/12-personal-finance.js`: somente fronteira pfMutate, após reprodução. Reaproveitar explicitamente a solução focal anterior como referência, sem copiar seu CHG ou seus artefatos e sem alterar a outra worktree.
- `src/js/20-ui/24-alladin-views.js`: resolução/retorno de foco de lançamento e estorno; preservar payload, guardas, domínio e confirmação.
- `src/js/20-ui/25-dash-macro.js`: foco dos CTAs principais, somente se reproduzido; preservar destino/links profundos.
- `src/js/40-app/17-economic-calendar.js`: orientação do empty state para Forex → Visão Geral; não mudar dados/cache/rede.
- Regressões existentes: `tools/finpes_scenarios_test.py`, `tools/alladin_ui_tx_write_test.py`, `tools/alladin_ui_tx_reverse_test.py`, `tools/dashboard_macro_test.py`, `tools/research_navigation_test.py`. Acrescentar oráculos antes dos patches. Reusar fixtures existentes, não criar framework. Bloquear SW nos testes de UI que não avaliam PWA para tornar as rotas sintéticas efetivas.
- `src/js/manifest.json`: somente SHA-256 das fontes alteradas, sem reordenar nem modificar configuração.
- `build-id.js`, `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`: exclusivamente geração por `tools/rebuild_monolith.py`.
- Este CHG e `docs/audit/NIGHT-REVIEW-20260910.md`; inventários, recibos, logs, screenshots, diff e fingerprints duráveis em `/Users/joaopauloalves/.codex/night-reviews/20260910/evidence`.

Todos os demais arquivos permanecem fora da edição. Nenhum commit do produto, push, PR, merge, deploy, reset, stash, atualização de skills/Harness/contexto/gates/CI ou alteração de dados reais. Nenhuma nova dependência. Correções adjacentes exigem estar no N0-V/N1 delimitado e novo registro prévio; fora disso, bloquear somente o item.

## Critérios e sequência de validação

1. Inventário deduplicado das famílias implementadas e seus consumidores; sucesso/falhas/evidência ou NOT_RUN justificado. Placeholder não conta como funcionalidade implementada.
2. Reutilizar FULL histórico 55/55 apenas após ligar seus hashes/árvore à base exata; registrar como reaproveitado, não nova execução. Seus limites de rede também serão explícitos.
3. Definir testes antes do runtime e manter os vermelhos: PF retorno/UI/memória/disco/log, quota/read/serialização/barreiras/conflito/UNKNOWN, retry/cancelamento/gravação posterior/recarga, demais atos compartilhados, campos desconhecidos e log no teto. Reuso delimitado do teste anterior é registrado; a execução vermelha é nesta base.
4. Alladin: novo lançamento/estorno, cancelar e concluir, foco conectado/visível após rerender, sem gravação por cancelar; manter guardas e regressões econômico/cadastral. Dashboard: quatro CTAs reais por teclado, destino/contexto/foco, links profundos e ausência de escrita.
5. Calendário: mensagem no modal e Research; atualização acessível em Forex, resposta sintética e contagem de chamadas; não usar API econômica real. Desktop/celular, temas e modos de navegação conforme aplicáveis, navegação repetida, preferências e rascunhos preservados.
6. Investigar débitos X2 e hipóteses adjacentes em fixtures, sem corrigir N2/N3 fora PF. Não transformar código inspecionado em comportamento testado.
7. Focais e regressões próximas; gerar oficialmente, congelar fingerprint de fontes/testes/artefatos, executar FULL final existente quando viável sob limite de rede. Não editar suíte/expectativas ou liberar APIs para obter PASS. Identificar efeitos dos testes Git: apenas repos descartáveis com .git próprio, sem remotos/hooks, nenhuma configuração global.
8. Auditoria independente focal do candidate; depois relatório com cobertura, resultados reais, falhas anteriores preservadas, riscos e limites. Duas tentativas sem aprendizado encerram o item. Auditar requisitos antes de concluir objetivo; não conceder aceite humano.

## Isolamento, preservação e rollback

Perfis de navegador novos, fixture PFv1 e demais fixtures existentes, armazenamento sintético e servidores 127.0.0.1. Conferir cada comando antes de executar; saídas ficam na worktree/evidence, não em originais. Execução de testes não autoriza rede econômica. Se necessária contenção processual local, só restritiva, sem permissões globais ou novo framework; documentar mecanismo e limites antes do FULL.

Rollback somente do próprio delta por comparação com BASE_SHA/evidências, sem reset/restauração ampla. Gerados voltam pelo processo oficial a partir das fontes anteriores. Não manipular dados do usuário. Encerrar apenas processos próprios; conservar worktree e evidências para revisão. Comparar no encerramento os hashes originais, stash e seis arquivos do candidate PF anterior. Candidate noturno permanece local e sem commit; atualização posterior de contexto é apenas recomendação.

## Registro anterior ao freeze

As cinco suítes focais vermelhas estão preservadas em `baseline-focal/`: PF deixou contagens1→2→3 após recusa/retry; Alladin perdeu foco nas quatro saídas econômicas; Dashboard falhou no primeiro CTA (não se alegam quatro vermelhos); o primeiro assert da agenda demonstrou a orientação antiga (o overlay ainda não foi alcançado nessa execução). Após patch, Alladin/Dashboard/Research passaram. O complemento defensivo PF inicialmente interferiu no structuredClone usado pelo próprio Playwright; a falha TEST_HARNESS_FAIL foi preservada e a injeção ficou restrita à chamada PF, sem modificar expectativa/runtime. `pf-defensive-v2` passou, incluindo UNKNOWN pela UI e clone recusado. A espera pelo fetch iniciado pelo modal da agenda elimina uma corrida do teste; não altera consultas do produto.

Contenção local do teste: `/usr/bin/sandbox-exec -f ../evidence/loopback-only.sb`, perfil de rede `cf35cca89f2e1b677995e788c0fe365bf627c641f260a3e4ea80cbde31a0c60e`, allow default com deny network-outbound e exceção apenas remote ip localhost:*. Fonte local Apple e revisão em `full-effects-review.md`. O canário v2 confirmou resposta esperada em127.0.0.1/::1 e EPERM ao destino reservado TEST-NET; não demonstra isolamento de filesystem. O recibo v1 preserva erro do controlador e sua descrição indevida de IPv6, corrigidos explicitamente no v2. Não foi ampliada permissão nem removida barreira.

FULL usará ambiente apenas processual: TMPDIR em evidence/tmp; Git sem GIT_DIR/WORK_TREE/COMMON_DIR/INDEX_FILE herdados, sem configuração global/sistema, hooks/templates vazios sob evidence e signing desligado no processo. O teste preflight_context cria repos novos em TemporaryDirectory, com git init e configuração de autor só local, sem remotos; comandos e trace confirmarão raízes sintéticas. Nenhuma configuração Git global é escrita. O gate existente escreve seus artefatos em tools/.artifacts; --artifact adicional fica em evidence. Não se modifica gate, suíte ou expectativas para contornar rede.

Matriz de interação externa reusa os helpers/fixtures das suítes, sem novo servidor/framework: oito contextos1440/390 × claro/escuro × sidebar/topbar; quatro CTAs por Enter, agenda nas duas superfícies, refresh único, criar/cancelar/concluir lançamento/estorno, fallback de foco sob schema futuro sintético, recarga e overflow. O schema do produto permanece idêntico; a fixture futura só aciona sua recusa existente. Screenshots serão ligados ao build congelado.

Probes externos confirmaram débitos NoCoda/Pivots/Notas por recusa real de setItem, save delegado false, disco preservado e memória/draft incoerentes; nenhuma correção foi aplicada nesses módulos. Forex/reservas/datas foram exercitados em VM sintética com os stubs documentados, sem atribuir a eles prova integral de UI. Preservar fatos, limitações e retornos não zero de propriedades violadas; nenhum desses resultados autoriza expansão.

## Revisão de avaliação V2, sem mudança de runtime

O FULL V1 executado sobre fingerprint `b1115ff97ca4996fdba88f0c9563cf9d571875547c83ad6c8f5ff2129e692945`, build `60463a994a0068f8`, terminou com48PASS/7PRODUCT_FAIL brutos e267inputs intactos. O revisor identificou uma regressão introduzida no helper `dashboard_macro_test.boot`: `statute_documentary_test` também o importa e depende de SW, mas o novo padrão block impedia obter controller. Seus sete consentimentos passaram; a consulta/offline não foi alcançada. Não atribuir esse timeout à rede ou ao produto.

Antes da correção, delimita-se o menor delta no arquivo de teste já permitido: parâmetro opcional service_workers com padrão allow (contrato anterior do helper), e block explícito nos chamadores internos dos testes de Dashboard. Nenhuma alteração no teste documental, em seu oráculo, no gate ou no SW do produto. A fronteira de rede do processo permanece a mesma. Preservar candidate.json/diff V1, primeiro FULL e auditorias; gerar candidate-v2.json/diff com a nova identidade. Executar os dois focais diretamente afetados e novo FULL pela mudança comprovada da fixture compartilhada, não para selecionar execução favorável. Os demais erros de recursos externos permanecem classificados pelos registros; nenhum acesso externo será liberado.

Focal V2: Dashboard PASS. Documental continua falhando, agora por console ERR_FAILED no consentimento, não pelo timeout anterior. Observação mínima separada com o mesmo helper confirmou SW activated/controller presente e preservado na recarga; registrou Frankfurter/feed recusados sob o perfil de rede. Esse resultado prova a disponibilidade do SW corrigida, não aprovação documental. Não alterar outros testes nem liberar APIs; preservar `v2-affected-focals/` e `v2-sw-observation/`. Novo FULL registra o estado final desta revisão, com limitações mantidas.
