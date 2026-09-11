# TECHNICAL DEBT CLOSURE — campanha finita

## Brief e fronteiras
O JP Wealth é software financeiro local: integridade e rastreabilidade prevalecem. Notas gerencia rascunhos e recuperação; Alladin projeta fatos append-only; Galton é laboratório isolado do motor. O incremento elimina inacessibilidade de ações globais, acoplamento de leitura sem qualidade explícita e, somente se reproduzida, inicialização parcial de Galton. Não altera cálculo, parâmetros, schema ou norma. Consumidores e oráculos constam dos recibos closure-*; fronteiras financeiras e histórico são invariantes.

N2 conservador para recuperação/leitura. O contexto N3/A4 possui [contrato dedicado](CHG-TECHNICAL-DEBT-CONTEXT-20260911.md), autorizado nas partes C/D/G/K. O juiz permanece intacto: nenhum gate, validador, Harness, skill ou política será alterado. Este contrato descreve autorização recebida, não cria autoridade.

Base recuperável: fcbb25767073a4ab08a9f0ac2ac16069a3008bfe mais V2 e706077826091e353dee686f0cdc79554402080870941bafbf55aea23b2a1f56, 289 inputs, build a48cf004f5ea5dc0. Evidências em ../evidence/debt-resolution-20260911; closure-start.json confirma identidade e preservação antes da escrita. Nenhum aceite deste novo pacote.

Trabalho concorrente delimitado: Notas (14-mvp-notes/index/estudos-notas), Alladin (13/24/25/teste de envelope/ALLADIN), coordenador (Galton, geração e contexto). Revisão agêntica em leitura; auditor final não implementa. Mudanças de documentação descrevem seleção explícita corrente e mantêm cláusulas históricas; nenhuma restrição dos agentes é removida.

Ordem: contraprovas e expectativas → correções mínimas → focais → contexto → geração oficial → freeze → FULL e controles → auditoria → recuperação. Evidências válidas V2 serão reaproveitadas apenas com inputs pertinentes idênticos; resultados novos identificados separadamente.


Complemento técnico: o defeito de cache do Calendário já consta da ficha JPW-FEAT-0001 §G. Escrita recusada exige resultado explícito, sem novo cache em RAM/pipeline. Responsável cache: somente 15-ff-news, 17-economic-calendar e teste focal; consumidor Dashboard coordenado após delta Alladin.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-TECHNICAL-DEBT-CLOSURE-20260911",
  "status": "approved",
  "objective": "Encerrar dívidas técnicas conhecidas determináveis, consolidar V2 e contexto afetado, sem decidir OPEN-05 nem integrar.",
  "risk_level": "N2",
  "authority_required": "A3",
  "target": {
    "root": "/Users/joaopauloalves/.codex/reliability-campaigns/20260911/product",
    "branch": "codex/debt-resolution-20260911",
    "baseline_sha": "fcbb25767073a4ab08a9f0ac2ac16069a3008bfe"
  },
  "scope": {
    "allowed_files": [
      "src/js/40-app/14-mvp-notes.js",
      "src/js/10-domain/13-alladin.js",
      "src/js/20-ui/24-alladin-views.js",
      "src/js/20-ui/25-dash-macro.js",
      "src/js/40-app/18-galton-board/06-controller.js",
      "index.html",
      "src/styles/app.css",
      "src/js/manifest.json",
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "tools/studies_notes_persistence_contract_test.py",
      "tools/alladin_ledger_read_model_test.py",
      "tools/galton_board_test.py",
      "src/js/40-app/15-ff-news.js",
      "src/js/40-app/17-economic-calendar.js",
      "tools/ff_news_cache_test.py",
      "docs/work/CHG-TECHNICAL-DEBT-CLOSURE-20260911.md",
      "tools/settings_modal_test.py",
      "README.md"
    ],
    "forbidden_files": [
      ".github/**",
      "docs/normative/**",
      "AGENTS.md",
      "CLAUDE.md",
      "skills/**",
      "Harness mestre",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      "outras worktrees"
    ],
    "allowed_actions": [
      "implementar e testar apenas dívidas conhecidas, baseline V2 identificada",
      "registro externo closure-* no diretório de evidências existente",
      "uso explícito consultivo de skills, leitura dos traces, sem cliente/credenciais/infraestrutura nova",
      "atualizar somente contexto diretamente afetado; geração oficial",
      "Cache Calendário: explicitar recusa técnica da gravação já registrada no Atlas §G; sem cache paralelo nem mudar agendamento/rede/dados financeiros",
      "M-02 histórico: remover landmark main duplicado no conteúdo do diálogo Configurações, mantendo IDs/classe/layout/foco; h1 já presente no app não será redesenhado"
    ],
    "forbidden_actions": [
      "decisão financeira N3, alteração de schema/migração",
      "alterar juiz/gates/CI/expectativas para PASS",
      "commit/push/PR/merge/deploy, reset/stash/tag",
      "dados reais, APIs econômicas ao vivo, instalação global"
    ],
    "regressions_forbidden": [
      "perda de draft/estado/backup ou mudança nos valores financeiros",
      "história convertida em PASS corrente",
      "alteração do envelope bruto legado transactions()",
      "alteração de direitos de execução por texto do candidate"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "../evidence/debt-resolution-20260911/closure-*"
    ],
    "generation_commands": [
      "python -B tools/rebuild_monolith.py",
      "python -B tools/quality_gate.py --tier full --artifact CAMINHO_EXTERNO"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "servidor loopback em perfis sintéticos de teste",
      "Git/GitHub somente leitura se necessário; nenhum deploy/publicação"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python/Chromium/Node já existentes",
      "servidor local de fixtures; sandbox loopback existente",
      "Git em fixture própria sem remoto/hooks; Git do produto somente leitura"
    ]
  },
  "acceptance_criteria": [
    "Notas: Tab/Shift+Tab alcançam backup/recuperação sem fechar draft sujo; nested modal e semântica preservados",
    "Alladin: read-model explícito de qualidade, lista bruta compatível, valores/ordem/guardas equivalentes",
    "Galton: só corrigir falha de inicialização parcial após contraprova; retorno/cleanup/epoch preservados",
    "Classificar cada dívida existente sem apagar falhas históricas; OPEN-05 permanece NEEDS_HUMAN_RULE",
    "Contexto corrente identificado e histórico preservado; sem alegar descoberta ou homologação",
    "Candidate congelado, FULL final, auditoria independente e recuperação; sem integração",
    "HTTP válido com cache recusado não anuncia cache atualizado: estado anterior preservado e indisponibilidade da atualização explícita; retry normal recupera"
  ],
  "approved_tests": [
    "oráculos fixados antes de alterações: teclado Notes, envelope Alladin, inicialização parcial Galton",
    "focais baseline V2 e candidate com mesma configuração/asserções; regressões próximas",
    "FAST e standard cobertos cumulativamente pelo FULL existente, reprodutibilidade/PWA existentes",
    "validação explícita CHG/CTX sem alterar validador e provas consultivas delimitadas",
    "auditoria após freeze, restauração em cópia e preservação do original",
    "Cache: baseline V2 versus candidate, negar apenas chave técnica, cache anterior/ausente/JSON inválido e HTTP inválido; recuperação e consumers sem escrita financeira",
    "M-02: main único, conteúdo rotulado no diálogo Configurações; mesmos seletores/layout/pesquisa e regressão existing settings_modal_test"
  ],
  "rollback": {
    "source": [
      "candidate-v2.tar verificado; reverter somente incremento em cópia; preservar baseline fcbb e V1/V2"
    ],
    "application_state": [
      "nenhuma alteração de estado do aplicativo"
    ],
    "data": [
      "fixtures sintéticas, sem dados reais"
    ],
    "environment": [
      "preservar stash, outras worktrees e evidências"
    ],
    "verification": [
      "hashes/modos de todos os inputs, delta e snapshot final; recuperar final e V2 em cópias sem Git do produto"
    ]
  },
  "approved_by": "proprietário: /goal TECHNICAL DEBT CLOSURE & PROJECT STABILIZATION, arquivo 52f572f5-7e88-4514-9f12-9a99fcaf7835/pasted-text.txt; autorização específica desta campanha, não aceite nem publicação",
  "approved_at": "2026-09-11T22:17:58.221429+00:00",
  "expires_on": [
    "mudança material de autoridade, financeira, dados reais, recuperação insegura ou efeito externo não coberto"
  ]
}
```
