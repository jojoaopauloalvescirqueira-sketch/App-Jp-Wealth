# Estado atual do projeto

- Data da fotografia: 2026-08-11
Source revision representada: `8bb5f371` + diff Planejamento FX (candidato local)
- Nota da revisão: candidato material da feature **Planejamento FX** na branch
  `feature/fx-planning`, criada a partir de `main@8bb5f371` (que contém a
  reconciliação documental do Galton Board sobre `fb33ceb`). O diff está
  validado e não commitado; commit, push e merge aguardam autorização.
- Branch do candidato: `feature/fx-planning`
- HEAD atual: `8bb5f3714673` com diff material não commitado
- Estado de integração: candidato local; não commitado, não enviado, não
  integrado e não publicado
- Validade: esta fotografia descreve o disco no build local `aa658d200db90b27`.
  Qualquer mudança posterior em fonte, manifest, fixture, gerados ou testes
  invalida as evidências afetadas.

## Estado confirmado no disco

- A aplicação permanece estática, local-first, sem framework e sem backend
  obrigatório. Os scripts continuam clássicos e globais.
- `src/js/manifest.json` registra **59 scripts**: os 53 publicados em `fb33ceb`
  mais seis anexados ao fim, sem reordenar o legado —
  `10-domain/07-reserve-requirements.js` (FCR/FEO puro compartilhado) e os
  cinco módulos de `30-accounting/05-fx-planning/` (modelo, motor, estado,
  gráficos, interface).
- A chave financeira principal continua `jpwealth_v9_state`. O schema ganhou o
  agregado **aditivo** `fxPlanning` (schemaVersion 1, `plan:null`,
  `auditLog:[]`): guarda estrutural `fxPlanningNormalizeState()` em
  `migrate()`, normalização profunda em cópia na camada de acesso, campos
  desconhecidos preservados, trilha podada em 400 e integração com
  `dgLogChange`. Bases legadas carregam sem perda; builds antigos preservam o
  agregado dormente. Contrato em `docs/architecture/FX-PLANNING.md`.
- `reserveCalc()` do onboarding agora **delega** para
  `reserveRequirementsCalc()` — extração autorizada pelo gestor (decisão 1 de
  2026-08-11), matemática idêntica campo a campo (caracterizada em teste).
  Nenhuma constante normativa foi alterada ou duplicada.
- O Planejamento FX é **tela principal própria**: quinta entrada da rail
  (`#fxplan`, botão `.tab[data-screen="fxplan"]`, mesma mecânica das quatro
  telas atuais — pílula, menu móvel e teclado genéricos). A Contabilidade
  voltou ao estado estrutural anterior, sem restos da feature. O contrato do
  smoke test passou a **cinco telas** operacionais. Na faixa 901–1160px o
  topbar exibe pílulas numeradas 01–05 (precedente da rail colapsada) para os
  cinco rótulos não estourarem o cabeçalho. Quatro modos internos: Visão
  Geral, Planejamento, Realizado e Tabela. Card fora da personalização de
  layout nesta fase.
- Séries do domínio: baseline congelado na aprovação; forecast vigente
  recalculado do último fechamento real com premissas de `plan.current`
  (revisões preservadas em `revisions[]`); realizado imutável a mudanças de
  premissa. Convenções: retorno sobre abertura com aportes após o resultado;
  realizado com a álgebra do MEI (`R_aj=(V_t−V_{t−1}−F_t)/V_{t−1}`); custo
  cambial `Σ BRL ÷ Σ USD` com `affectsFxCostBasis` excluindo USD-nativo.
- `sw.js` precacheia os 59 scripts; `validate_project.py` mantém a equivalência
  como invariante. O tier `standard` passou a 8 verificações (inclui
  `fx_planning_test.py`) e o `full` a 18.
- `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` foram
  regenerados exclusivamente por `tools/rebuild_monolith.py`. Build ID
  `aa658d200db90b27`.

## Escopo e autoridade

- N1/A2: interface, gráficos, navegação interna do card, acessibilidade,
  responsividade, testes e documentação.
- N2/A3 delimitado: agregado `S.fxPlanning`, guarda estrutural em `migrate()` e
  entrada em `DEFAULTS`; extração de `reserveCalc()` expressamente autorizada.
- N3/A4: fora do escopo. Nenhuma fórmula financeira, perfil, fase, limite, MDD,
  DD, LIFO, stop, quarentena, contabilidade, MEI ou artigo do Estatuto foi
  alterado. As dez pendências N3 permanecem intocadas.
- Git/publicação: criação da branch autorizada e executada; commit, push,
  merge e deploy continuam sem autorização.

## Evidência deste candidato

| Verificação | Resultado | Escopo/observação |
|---|---|---|
| `python3 tools/agent_preflight.py --mode edit` | PASS | Branch `feature/fx-planning`, base `8bb5f3714673`, árvore limpa antes das edições. |
| `python3 tools/validate_project.py` | PASS | 59 scripts, hashes, ordem no HTML, precache equivalente, 377 IDs, portátil reconstruído. |
| `python3 -u tools/fx_planning_test.py` | PASS | Casos 1–20, reservas campo a campo, baseline×forecast×realizado, persistência (round-trip, legada, corrompida, campos desconhecidos, contiguidade), fluxo de UI, navegação entre as cinco telas com estados ativos exclusivos, ativação por teclado, refresh (rota não persistida → Dashboard), ausência de resíduos em `#contab` e viewport móvel. |
| `python3 tools/quality_gate.py --tier full` | PASS 18/18 | Zero `PRODUCT_FAIL`, `TEST_HARNESS_FAIL`, `ENVIRONMENT_ERROR`, `BASELINE_FAIL` ou `NOT_RUN`; artefato `tools/.artifacts/quality-20260811T183717-full.json` (reexecutado após a promoção a tela principal; a execução intermediária `183x` detectou e a correção da faixa 901–1160px resolveu o overflow do cabeçalho com cinco rótulos). |
| `git diff --check` | PASS | Sem whitespace errors. |
| Navegador real | PASS | Screenshots da tela independente (desktop, mobile e faixa 1024px com pílulas numeradas) e da Contabilidade restaurada, gerados em Chromium com dados sintéticos e entregues ao gestor; varredura de larguras 400–1280px sem scroll horizontal. |

Relatórios locais ficam em `tools/.artifacts/` e são ignorados pelo Git. Usar
apenas o artefato cuja árvore corresponda ao estado examinado.

## Impacto agêntico e reconciliação

`AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED`

`BASIS:` a feature altera manifest (53→59), schema persistido (agregado
aditivo), composição dos gates (standard 8/full 18), arquitetura (novo domínio
FX + função normativa compartilhada), inventário e superfície PWA —
representações consumidas por preflight, skills e agentes.

Blast radius do changeset `8bb5f371 + diff Planejamento FX`:

| Categoria | Impacto | Ação local | Estado no checkpoint |
|---|---|---|---|
| `AGENTS.md` e autoridade | AFFECTED | NOT_REQUIRED | CURRENT: classificação N1/N2/N3 existente cobre a mudança. |
| Skills e routing | AFFECTED | NOT_REQUIRED | CURRENT: preflight, change-control, data-safety, normative-audit, browser, test-triage e post-audit roteiam o trabalho. |
| Bootstrap/preflight e manifest | AFFECTED | REQUIRED | Manifest com 59 entradas e hashes finais; preflight/validate PASS. |
| Contexto operacional | AFFECTED | REQUIRED | `ACTIVE-TASK`, este `CURRENT-STATE` e `SESSION_HANDOFF` representam o candidato. |
| Arquitetura/contratos | AFFECTED | REQUIRED | `FX-PLANNING.md` criado; `CODE-MAP`, `STATE-SCHEMA` e `QUALITY-GATES` reconciliados. |
| Changelog/inventário | AFFECTED | REQUIRED | `CHANGELOG.md`, `README.md`, `tests/README.md` e `PROJECT-FILES.txt` (166) reconciliados. |
| Norma e ADRs N3 | NOT_AFFECTED | NOT_REQUIRED | FCR/FEO extraídos sem alteração de valor; nenhuma pendência N3 tocada. |
| Índice/vetor/memória de projeto | NOT_AFFECTED | NOT_REQUIRED | `INDEX NOT REQUIRED`. |

Natureza: a feature é `MATERIAL`; a atualização destes documentos é
`RECONCILIAÇÃO`. Não há nova source revision commitada. Runtime, contratos,
manifest, build, contexto e evidências estão reconciliados: `SYSTEM RECONCILED`.

## Contratos N2 vigentes

- `reserveMasterCapital` deriva de `params.saldoIni` também no boot fresco (`7d18bca`).
- Recuperação só substitui estado após leitura, validação, normalização e
  confirmação atômica (`8296f1a`).
- `investorPassword` permanece apenas em memória da sessão (`e0b59d3`).
- Preferência Galton isolada em `jpwealth_galton_preferences_v1`; wipe seletivo
  sem `localStorage.clear()`.
- **Novo (candidato):** agregado `fxPlanning` aditivo em `jpwealth_v9_state`;
  derivados nunca persistem; campos desconhecidos preservados; mutações
  auditadas e refletidas no changeLog de backup; `initialBalanceUsd` do plano é
  parâmetro do planejamento, nunca fonte canônica da Conta Mestre.

## Pendências normativas bloqueantes

Não corrigir silenciosamente. Cada item exige decisão/confirmação N3 e branch própria:

1. Perfis conservadores no código usam fatores revogados (66/50/33) em conflito com a tabela V10 (53/40/27).
2. `compute()` deriva drawdown do risco programado e perdas realizadas, não da equity oficial ao vivo.
3. Ordem Gênese não aplica de forma combinada o teto de risco e o de alavancagem.
4. Stop abaixo de 2 ATR é classificado, mas não bloqueado.
5. Downgrade não aplica integralmente histerese de 0,50 ponto percentual e confirmação H4.
6. Gatilho compulsório de poda LIFO em +1,00 ponto percentual não está implementado.
7. Fase 4 permite inclusão operacional sem todo o rito de salvaguarda previsto.
8. Quarentena/guilhotina depende de formalização manual e não de uma fonte autoritativa de equity.
9. Fator padrão do Stop Raiz-N aparece como 1,8, enquanto a norma atual indica 1,25.
10. Projeções MEI por perfil precisam de decisão sobre memória de cálculo e aderência normativa.

## Dívida e riscos residuais

- `openOnboardingModal()` concentra ~2 mil linhas; escopo global legado
  compartilhado; CSP não documentada (inalterados por esta feature).
- Planejamento FX: o card não participa da personalização de layout (registro
  em `13-dashboard-layout.js` é evolução futura); gráfico mensal dedicado de
  aportes, cenários múltiplos, importação/exportação do Excel e conciliação com
  `mei.history` ficaram deliberadamente fora do MVP; reconstrução de forecasts
  anteriores é aproximada quando um mês fechado é editado depois da revisão
  (sinalizado); painel FCR/FEO reflete o comportamento herdado do onboarding —
  sem despesas declaradas, FEO exigido 0 aparece como "Regular" (fidelidade à
  caracterização; mudança disso seria decisão normativa).
- Cobertura automatizada segue mais forte nos fluxos recentes que no núcleo
  financeiro legado.

## Regra de atualização

Quem alterar fonte, teste, manifest, fixture ou gerado depois deste checkpoint
deve repetir as verificações afetadas. Não remover falha porque deixou de
aparecer em um teste; registrar causa, comando, candidato e evidência.
