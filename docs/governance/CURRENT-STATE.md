# Estado atual do projeto

Data da fotografia: 2026-08-10
Source revision representada: `83f688f`
Branch: `main` (integrada e publicada em `origin/main`)
Validade: revisar apos mudanca material ou integracao material em `main`. Commit exclusivamente de reconciliacao documental nao altera, por si so, a source revision representada.
Nota: a source revision e a revisao MATERIAL cujo estado esta descrito aqui; o HEAD corrente pode estar a frente dela por commits documentais sem que esta fotografia fique desatualizada.

## Estado confirmado

- Repositorio Git local existente; ha um remote `origin` preexistente para GitHub. Nenhum remote foi criado ou alterado; `main` foi publicada em `origin/main` sob autorizacao especifica.
- Aplicacao estruturada a partir do HTML portatil, com 44 scripts no manifest.
- Persistencia principal continua em `jpwealth_v9_state`.
- Governanca M0-M5, autoridade A0-A4, risco N0-D a N3, oito skills `jpw-*` e duas skills genericas instaladas project-scoped (`repository-architecture`, `agentic-evolution-governance`) estao implementados localmente.
- Preflight, quality gate em tres tiers e workflow de CI estao preparados; nenhum workflow de CI ou deploy online foi acionado.
- Tier `standard` esta verde: 5 de 5 verificacoes em Chromium real.
- Tier `full` executa treze suites `*_test.py`: 16 de 16 verificacoes passam; nenhum `PRODUCT_FAIL` remanescente. Composicao cumulativa: fast 4, standard 6, full 16.
- O fechamento de toda mudanca material exige um veredito explicito de impacto agentico — `NO AGENTIC IMPACT` ou `AGENTIC IMPACT DETECTED`, sempre com BASIS — e, quando DETECTED, exige `skills/agentic-evolution-governance/SKILL.md` em modo IMPACT antes de encerrar a dimensao agentica. A regra canonica vive em `skills/jpw-post-change-audit/SKILL.md`, nao nesta fotografia.
- O preflight verifica dois sinais independentes de frescor do contexto: temporal (idade da fotografia) e material (existencia de alteracoes posteriores a source revision fora dos caminhos de reconciliacao contextual). O resultado material e tri-state — `true`, `false` ou `unknown` —, com `unknown` jamais codificado como `false`, e o aviso e nao bloqueante. O comportamento e protegido pelo teste permanente `preflight-context` no tier fast; a composicao dos gates esta em `docs/governance/QUALITY-GATES.md` e o mecanismo em `tools/agent_preflight.py`.
- Regras financeiras e contratos normativos nao foram alterados entre `f722eb3` e `cba50c6`: nenhuma formula, perfil, MDD, DD, fase, LIFO, stop ou MEI mudou.
- A representacao de `reserveMasterCapital` foi canonizada (N2 aprovada, `7d18bca`): o campo deriva de `params.saldoIni` tambem no boot fresco, com a mesma formula ja usada pela `migrate()`.
- Nenhuma chave de persistencia foi criada, removida ou renomeada; `jpwealth_v9_state` permanece a chave principal.
- O contrato de `investorPassword` esta alinhado entre codigo, `skills/jpw-data-safety/SKILL.md` e `docs/governance/SECURITY-MODEL.md` desde `b4e0fe7`; a regra canonica vive nesses dois documentos, nao nesta fotografia.

## Evidencia pos-implementacao

| Verificacao | Resultado | Observacao |
|---|---|---|
| `agent_preflight.py --mode audit` | PASS | Branch, contexto, manifest, hashes e caminhos sensiveis verificados. |
| `validate_project.py` | PASS | 44 JS, 366 IDs estaticos e portatil reconstruido; fallback Chromium funciona sem Node. |
| `quality_gate.py --tier standard` | PASS 5/5 | Preflight, estrutura, diff-check, smoke e Configuracoes. |
| `smoke_test.py` | PASS | Quatro telas, tres acoes do cabecalho e onboarding atual. |
| `settings_modal_test.py` | PASS | Sete categorias e folha de parametros atual. |
| `storage_governance_test.py` | PASS | Contratos de armazenamento exercitados. |
| `persistence_failure_test.py` | PASS | Falha de exportacao orienta contingencia manual. |
| `service_worker_upgrade_test.py` | PASS | Precache e ciclo de upgrade cobrem os recursos atuais. |
| `mvp_notes_test.py` | PASS | CRUD, filtros, mobile, menus, backup, Markdown, Trace ID e portatil. |
| `finalize_session_test.py` | PASS | Canonizacao de `reserveMasterCapital` em `7d18bca` eliminou o falso dirty. |
| `persistence_recovery_test.py` | PASS | Importacao e recuperacao transacionais em `8296f1a`. |
| `investor_password_test.py` | PASS | Segredo removido da persistencia em `e0b59d3`; permanece apenas em memoria de sessao. |
| `import_xss_security_test.py` | PASS | Backup adulterado nao executa, nao injeta DOM e nao persiste marcacao (`c7d9661`). |
| `async_generation_test.py` | PASS | Corrida entre wipe e geracao assincrona coberta. |
| `build_reproducibility_test.py` | PASS | Build ID e portatil reproduziveis a partir dos inputs oficiais. |
| `preflight_context_test.py` | PASS | Sete cenarios sinteticos do frescor material; prova TRUE/FALSE/UNKNOWN distintos, com UNKNOWN != FALSE. |
| `quality_gate.py --tier full` | PASS 16/16 | Nenhum `PRODUCT_FAIL` remanescente (execucao de 2026-08-10, revisao `c89f578`). |

Relatorios locais: `tools/.artifacts/quality-*-full.json` (ignorados pelo Git; usar o mais recente).

## Correcoes N0/N1 verificadas e integradas em `main`

- `hidden` volta a prevalecer no botao de Notas e no botao Salvar.
- Inspetor de Notas respeita a altura real da barra do editor e nao cobre Salvar.
- Alvos de toque do cabecalho fora do Dashboard atendem ao contrato de 40 px.
- Menu contextual de pasta abre lateralmente e nao bloqueia o acionador da pasta seguinte.
- Service worker precacheia logo e scripts finais; teste isola a fonte externa de calendario.
- Portatil nao tenta registrar um `dist/sw.js` inexistente.
- Falha de exportacao orienta o operador a registrar manualmente ordens, fechamentos e notas recentes.
- Harness antigo foi reconciliado com a UI, schema de Notas e semantica de backlog atuais, sem afrouxar falhas de produto.

## Pendencias N2

Nenhuma pendencia N2 aberta. Os tres itens da fotografia anterior foram resolvidos e verificados:

1. Representacao canonica de `reserveMasterCapital` entre estado vazio, migracao, checkpoint e reload — resolvida em `7d18bca`; `finalize_session_test.py` PASS.
2. Recuperacao bloqueada ate o arquivo importado ser lido, validado, normalizado e confirmado atomicamente — resolvida em `8296f1a`; `persistence_recovery_test.py` PASS.
3. Politica para a senha de investidor persistida em texto claro — resolvida em `e0b59d3` (persistencia removida; segredo apenas em memoria de sessao, nunca em localStorage, checkpoint ou backup); `investor_password_test.py` PASS.

## Pendencias normativas bloqueantes

Nao corrigir silenciosamente. Cada item exige decisao/confirmacao N3 e branch propria:

1. Perfis conservadores no codigo usam fatores revogados (66/50/33) em conflito com a tabela V10 (53/40/27).
2. `compute()` deriva drawdown do risco programado e perdas realizadas, nao da equity oficial ao vivo.
3. Ordem Genese nao aplica de forma combinada o teto de risco e o de alavancagem.
4. Stop abaixo de 2 ATR e classificado, mas nao bloqueado.
5. Downgrade nao aplica integralmente histerese de 0,50 ponto percentual e confirmacao H4.
6. Gatilho compulsorio de poda LIFO em +1,00 ponto percentual nao esta implementado.
7. Fase 4 permite inclusao operacional sem todo o rito de salvaguarda previsto.
8. Quarentena/guilhotina depende de formalizacao manual e nao de uma fonte autoritativa de equity.
9. Fator padrao do Stop Raiz-N aparece como 1,8, enquanto a norma atual indica 1,25.
10. Projecoes MEI por perfil precisam de decisao sobre memoria de calculo e aderencia normativa.

## Divida tecnica estrutural

- `openOnboardingModal()` concentra aproximadamente duas mil linhas e muitos contratos globais.
- Estado, dominio e interface ainda compartilham escopo global legado.
- Cabecalhos de seguranca sao minimos e nao ha CSP documentada.
- Estrutura semantica tem tres elementos `main` e nenhum `h1` estatico.
- A cobertura automatizada e mais forte em fluxos recentes do que no nucleo financeiro.

## Regra de atualizacao

Quem resolver ou invalidar um item deve atualizar esta fotografia com evidencia, commit e data. Nao remover falha apenas porque deixou de aparecer em um teste; registrar a causa e a verificacao final.
