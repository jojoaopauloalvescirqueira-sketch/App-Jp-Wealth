# Estado atual do projeto

Data da fotografia: 2026-08-09
Baseline auditado: `f722eb3`
Branch de trabalho: `audit/governanca-multiagente`
Validade: revisar apos qualquer mudanca material ou integracao em `main`.

## Estado confirmado

- Repositorio Git local existente; ha um remote `origin` preexistente para GitHub. Nenhum remote foi criado/alterado e nenhuma operacao de rede foi executada nesta sessao.
- Aplicacao estruturada a partir do HTML portatil, com 44 scripts no manifest.
- Persistencia principal continua em `jpwealth_v9_state`.
- Governanca M0-M5, autoridade A0-A4, risco N0-D a N3 e oito skills `jpw-*` estao implementados localmente.
- Preflight, quality gate em tres tiers e workflow de CI estao preparados; nenhum workflow, push ou deploy online foi acionado nesta sessao.
- Tier `standard` esta verde: 5 de 5 verificacoes em Chromium real.
- Tier `full` executa todos os oito testes `*_test.py`: 9 verificacoes passam e 2 falham por defeitos N2 conhecidos.
- Nenhuma formula financeira, perfil, MDD, DD, fase, LIFO, stop, MEI, schema ou chave de persistencia foi alterada nesta branch.

## Evidencia pos-implementacao

| Verificacao | Resultado | Observacao |
|---|---|---|
| `agent_preflight.py --mode audit --allow-dirty` | PASS | Branch, contexto, manifest, hashes e caminhos sensiveis verificados; dirty conhecido. |
| `validate_project.py` | PASS | 44 JS, 366 IDs estaticos e portatil reconstruido; fallback Chromium funciona sem Node. |
| `quality_gate.py --tier standard` | PASS 5/5 | Preflight, estrutura, diff-check, smoke e Configuracoes. |
| `smoke_test.py` | PASS | Quatro telas, tres acoes do cabecalho e onboarding atual. |
| `settings_modal_test.py` | PASS | Sete categorias e folha de parametros atual. |
| `storage_governance_test.py` | PASS | Contratos de armazenamento exercitados. |
| `persistence_failure_test.py` | PASS | Falha de exportacao orienta contingencia manual. |
| `service_worker_upgrade_test.py` | PASS | Precache e ciclo de upgrade cobrem os recursos atuais. |
| `mvp_notes_test.py` | PASS | CRUD, filtros, mobile, menus, backup, Markdown, Trace ID e portatil. |
| `finalize_session_test.py` | PRODUCT_FAIL | `reserveMasterCapital` muda de `''` para `'0'` apos reload e gera falso dirty. |
| `persistence_recovery_test.py` | PRODUCT_FAIL | Importacao invalida pode liberar o gate de recuperacao antes da validacao. |
| `quality_gate.py --tier full` | PRODUCT_FAIL 9/11 | Somente os dois defeitos N2 acima permanecem. |

Relatorios locais: `tools/.artifacts/quality-*-full.json` (ignorados pelo Git; usar o mais recente).

## Correcoes N0/N1 verificadas nesta branch

- `hidden` volta a prevalecer no botao de Notas e no botao Salvar.
- Inspetor de Notas respeita a altura real da barra do editor e nao cobre Salvar.
- Alvos de toque do cabecalho fora do Dashboard atendem ao contrato de 40 px.
- Menu contextual de pasta abre lateralmente e nao bloqueia o acionador da pasta seguinte.
- Service worker precacheia logo e scripts finais; teste isola a fonte externa de calendario.
- Portatil nao tenta registrar um `dist/sw.js` inexistente.
- Falha de exportacao orienta o operador a registrar manualmente ordens, fechamentos e notas recentes.
- Harness antigo foi reconciliado com a UI, schema de Notas e semantica de backlog atuais, sem afrouxar falhas de produto.

## Pendencias N2

1. Tornar canonica a representacao de `reserveMasterCapital` entre estado vazio, migracao, checkpoint e reload.
2. Manter recuperacao bloqueada ate o arquivo importado ser lido, validado, normalizado e confirmado atomicamente.
3. Decidir politica para a senha de investidor hoje persistida em texto claro.

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
