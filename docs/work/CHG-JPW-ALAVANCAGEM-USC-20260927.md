# CHG-JPW-ALAVANCAGEM-USC-20260927 — v1.1.0

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-USC-20260927
status: approved
objective: USC com unidades verificadas por instrumento, estimativas identificadas, painel cinza e instalação guiada da ferramenta MT5 1.1.0.
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
scope:
  allowed_files: [mt5/jpw-alavancagem-atual/, downloads/jpw-alavancagem-atual/, index.html, src/styles/app.css, src/js/20-ui/31-tools-services.js, sw.js, tools/build_leverage_package.py, tools/leverage_*, docs/work/CHG-JPW-ALAVANCAGEM-USC-20260927.md, docs/work/ACTIVE-TASK.md, build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  forbidden_files: [src/js/00-core/, src/js/10-domain/, data/, docs/normative/, docs/decisions/, skills/, AGENTS.md, tools/quality_gate.py, tools/validate_project.py, .github/]
  allowed_actions: [local implementation, synthetic tests, official generation, isolated native compilation and validation when available, independent audit]
  forbidden_actions: [commit, push, PR, merge, deploy, operational terminal installation, trading, real account data collection, changing network or operational settings]
  regressions_forbidden: [r1 evidence, financial state and rules of JP Wealth, navigation, PWA cache policy]
derived_artifacts:
  allowed: [source ZIP v1.1.0, manifest.json, build-id.js, sw.js generated version/assets only, portable HTML, compiled package only with native evidence]
  generation_commands: [python3 tools/build_leverage_package.py, python3 tools/rebuild_monolith.py, isolated MetaEditor X64 Regular]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [official documentation read only, loopback test server]
  temporary_artifacts: allowed
  cleanup_required: true
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [existing Python and browser tests, official generators, isolated MetaEditor and MT5 when usable]
acceptance_criteria:
  - Preserve gross notional divided by equity; USD 100 and USC 10000 are equivalent only with individually verified contract units.
  - Native USC script uniquely verifies scale 1 or 0.01, saves identity-bound technical profile without raw account data, preserves previous valid file on failed write.
  - Complete stale-data estimate is explicitly separated from current data and from unavailable data; oldest quote server time and last terminal equity are identified.
  - Gray 767676 panel defaults, measured text spacing and guided site installation without replacing MQL5 root.
  - Updated sources and tests have their own validation identity; no inherited native PASS from r1.
approved_tests: [original 117 assertions plus USC and quality cases, profile fault cases, site four layouts and 320/390/1440, HTTP/file/portable/offline downloads, structural validation, full gate, native compilation and isolated execution when available, independent audit]
rollback:
  source: [Preserved r1 candidate and manifest remain external; revert only this revision in a later authorized operation.]
  application_state: [No change to S or browser preferences.]
  data: [Profile writes are limited to the MT5 technical subdirectory, with verified temporary files and retained previous profile.]
  environment: [Stop only processes created for this task; preserve operator terminal and network.]
  verification: [Hash preserved r1 and freeze a new derived candidate.]
approved_by: Proprietario, PLEASE IMPLEMENT THIS PLAN nesta conversa
approved_at: 2026-09-27
expires_on: [material root/branch/base drift, expanded scope, new controlling conflict]
```

## Brief e fontes

O aplicativo organiza finanças e risco; esta página distribui uma ferramenta informativa calculada exclusivamente no MT5. A tarefa responde a indisponibilidade com USC e cotações antigas, sobreposição de texto e dificuldade de instalação. O r1 foi conferido em 25/25 arquivos, build `cf977fa0267e2206`, fingerprint `0938fb45aa9bd781dfe86e4f4b651d0c019af53402f0ab5febfc13b5bf565209`. A cópia preservada e os recibos ficam em `outputs/jpw-alavancagem-atual-validation-20260926` do projeto ChatGPT, fora desta worktree. As 21 entradas dirty são o delta r1 identificado; preflight edit com `--allow-dirty` passou, sem autorização para alterações alheias.

Responsabilidades: núcleo MQL5 puro para fórmulas e qualidade; adaptadores MT5 para leitura, verificação nativa e perfil; objetos de gráfico para apresentação; HTML/CSS/manifesto para instruções e downloads. O navegador não recebe dados da conta nem calcula alavancagem. Os consumidores compartilhados são geradores, downloads e navegação existente; ordem de scripts e política de cache permanecem iguais.

O Harness canônico externo foi conferido no caminho informado pelo AGENTS, hash `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`. Aplicam-se §§12–14,19,28–30,36–48. O contrato financeiro anterior documenta Estatuto V11 Art.4.5: a métrica aqui é informativa sobre equity corrente/último informado, distinta da alavancagem normativa sobre min(SI,equity), sem mudar tetos, fases ou autorizações.

Fontes específicas: MetaQuotes ACCOUNT_CURRENCY/ACCOUNT_EQUITY, OrderCalcProfit e runtime (uso proibido em indicadores); exemplos oficiais das corretoras PrimeXBT/Absel sobre unidades cent não universais. A decisão humana define somente USC e 100:1; o script confirma escala por instrumento, sem deduzir pelo nome. Perfil técnico usa hash de identidade, assinatura de especificações, escala e data; não é backup financeiro nem credencial. A ausência, corrupção, ambiguidade ou unidade alterada bloqueia o total sem conversão parcial.

## Matriz norma–código–teste da revisão

| Regra aprovada | Responsabilidade | Oráculo |
|---|---|---|
| USC /100 uma única vez no equity; escala 1/.01 por símbolo | Core + verificação + perfil | 100 USD = 10000 USC; contratos 1000 e 100000 centésimos ambos 0,60x |
| Nocional bruto completo, hedge sem netting | Core | Originais 117 + símbolos heterogêneos; uma unidade ausente invalida total |
| Atual <=30s com prova temporal; estimativa recalculada | Core + adapter | Início sem tick, offline, rotas antigas/recentes, recuperação |
| Sem zero artificial | Snapshot + estado | Falha de leitura/identidade não vira zero |
| Confirmação nativa sem ordens | Script separado | Quatro movimentos, tolerância 1%, empate/erro recusados |
| Perfil sem dados financeiros | Include local | Corrupção, conta/spec diferentes, escrita parcial recusada |

Native compilation/execution of 1.1.0 starts NOT_RUN. Screenshots of r1 compilation and 117 asserts remain historical, with no EX5 hash attribution to this revision. Full histórico 55 PASS / 2 PRODUCT_FAIL remains unchanged. No acceptance or integration is inferred from local implementation.

## Fechamento de implementação e evidências desta revisão

Derivado identificado como `jpw-alavancagem-atual-20260927-r2`, versão 1.1.0. O fingerprint, build e resultados finais serão registrados externamente em `/private/tmp/jpw-leverage-v110-evidence/CANDIDATE.json` e `DELIVERY.md`; este CHG não antecipa PASS do gate ou de execução nativa. O pacote permanece somente de fontes enquanto o manifesto declarar compilação pendente.

A revisão independente durante a implementação levou à recusa de zero sem testemunha temporal, à preferência por conversões sincronizadas, à reconferência dos metadados das rotas, à medição de altura do painel e à correção do quantum monetário do diagnóstico USC. A prova de unidade USC pode usar cotações antigas estruturalmente válidas, desde que os quatro resultados hipotéticos nativos e os valores de tick concordem; ela não torna a leitura Atual. A assinatura das especificações é capturada antes dos probes e conferida depois. A data técnica do perfil usa o relógio do computador, separada das datas das cotações.

O perfil usa dois slots com checksum, geração e releitura, mais exclusão de escritores por handle. Isso preserva uma geração válida em falha parcial, sem afirmar atomicidade não documentada de FileMove. A execução nativa deve confirmar o comportamento efetivo do filesystem e dos locks. Também continua necessária a observação nativa da sincronização de posições na inicialização/reconexão, dos contratos e do DPI; simulações de host não demonstram essas propriedades.

A tentativa de automação nativa encontrou a restrição de licença do `prlctl exec`; nenhuma compilação nova foi executada por esse comando. A captura integral da VM foi recusada pela revisão automática por possível exposição da sessão operacional. O terminal operacional, sua rede e seus perfis permanecem fora da intervenção. Recibo: `native-attempt.md` na pasta externa de evidências. As provas manuais 0 erros/0 avisos e 117 asserts do r1 continuam exclusivas daquela versão.

### Impacto sobre contexto agêntico

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED.
BASIS: o contrato de distribuição e o contexto da tarefa passam de fontes 1.0.0 com dados estritamente recentes a fontes 1.1.0 com USC/perfil e estimativa explicitamente identificada. README, página e manifesto são fontes operacionais da ferramenta e foram reconciliados; ACTIVE-TASK aponta para este CHG. O estado oficial integrado, agentes, skills, routing, Harness e critérios de aprovação não mudam. CURRENT-STATE e índices da main não devem representar um candidate não integrado como produto publicado. Não existe necessidade de reindexação para este delta local; o preflight de frescor não foi usado como prova semântica. Histórico e recibos r1 são artefatos históricos, não contexto a sobrescrever.

Gates posteriores permanecem separados: compilação/execução nativa, auditoria final, aceite humano e operações Git. Nenhum desses estados é inferido da implementação ou de testes suplementares.
