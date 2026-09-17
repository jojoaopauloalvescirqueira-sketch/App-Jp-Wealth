# CHG-FOREX-IMPORT-OPERATION-20260916

```yaml
schema: jp-harness/chg/v1
change_id: CHG-FOREX-IMPORT-OPERATION-20260916
status: approved
objective: Corrigir leitura HTML/PDF local e tornar explicita a preparacao de conta e a edicao de ordens nas seis fases.
risk_level: N2
authority_required: A3
target:
  root: /Users/joaopauloalves/.codex/forex-import-operation/20260916/product
  branch: codex/forex-import-operation-20260916
  baseline_sha: 61120ec6018e66ebb8487126d083f2c0fc479a7d
scope:
  allowed_files: [src/js/10-domain/17-fx-consolidated-model.js, src/js/40-app/25-fx-consolidated-pdf.js, src/js/40-app/24-fx-consolidated-import.js, src/js/20-ui/28-fx-consolidated.js, src/js/20-ui/30-execution-board.js, src/styles/app.css, index.html, src/js/manifest.json, tools/rebuild_monolith.py, src/vendor/pdfjs/runtime-assets.js, sw.js, tools/fx_import_operation_test.py, tools/fx_import_numbers_test.py, tools/fx_pdf_local_test.py, tools/fx_account_setup_test.py, docs/architecture/FOREX-EXECUTION-BOARD.md, docs/work/CHG-FOREX-IMPORT-OPERATION-20260916.md, docs/work/ACTIVE-TASK.md, build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  allowed_actions: [implementacao local autorizada, testes sinteticos, geracao oficial, auditoria independente, candidate local]
  forbidden_actions: [commit, push, merge, deploy, alteracao de policy, alteracao normativa, dados pessoais, editar gates para obter aprovacao]
derived_artifacts:
  allowed: [src/vendor/pdfjs/runtime-assets.js, build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
data:
  test_policy: synthetic_only
  schema_change: forbidden
acceptance_criteria:
  - Interpretacao numerica independente do idioma; ambiguidades exigem revisao.
  - PDF textual suportado localmente em modular file/http e portatil, multipagina quando o layout for reconhecido.
  - Cadastro manual e por relatorio acessiveis, identidade e periodo revisados; saldo nao vira SI automaticamente.
  - Seis fases descobertas sem contexto e editaveis com conta/periodo explicitos, inclusive celular.
  - Escritores, concorrencia, backup e regras existentes preservados; falha/cancelamento sem falso sucesso.
approved_tests: [focais sinteticos, regressao Forex/importacao/backup, full, navegadores descartaveis, auditoria independente]
rollback:
  source: [baseline Git preservada, diff e fingerprint externos]
  data: [somente dados ficticios em contextos descartaveis]
approved_by: Proprietario, Autorizo ao plano de importacao e operacoes nesta conversa.
approved_at: 2026-09-16
```

## Compreensao e limites

1. JP Wealth registra fatos financeiros locais e apresenta a elegibilidade central. Esta tarefa recupera a entrada confiavel e visivel desses fatos.
2. O parser puro normaliza relatorios; o controlador coordena identidade/importacao; a UI apresenta revisao e o board registra ordens via escritores existentes.
3. HTML hoje usa idioma para separadores; PDF modular file falha em ESM e limita a uma pagina; ordens desaparecem sem periodo. O destino explicita leitura/revisao/preparacao e seis fases.
4. Consumidores: Consolidado, Contas, Operacao, backup, finalizacao, PWA e portatil. Escritas continuam sujeitas a epoch, identidade e leitura de confirmacao existentes.
5. Sem alteracao de politica/calculo, inferencia de fase, saldo como capital inicial, OCR, dependencia externa, vendor PDF.js ou schema publico. Nenhum dado pessoal usado. Correcoes pendentes do candidate settings-search-focus ficam preservadas na origem.
6. Fixtures com separadores distintos, datas, PDF textual multipagina, ausencia/ambiguidade, cancelamento, duplicacao e falhas; fluxo conta/periodo/seis fases, celular, recarga e backup; gates classificados separadamente.

Preflight audit/edit PASS na arvore nova limpa. A fonte main e a branch foram conferidas. O aviso de contexto historico desatualizado nao substitui os contratos e codigo relidos nesta base. Evidencias e recovery ficam em ../evidence.

## Fontes verificadas

- /Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - SoftwareDev/2 - DESENVOLVIMENTO DE SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md — SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`.
- /Users/joaopauloalves/.codex/forex-import-operation/20260916/product/docs/architecture/FOREX-V11-ENGINE.md — SHA-256 `9f651ee6c2be691bda08effad041871527908be0129d116ead38c287e3a8390b`.
- /Users/joaopauloalves/.codex/forex-import-operation/20260916/product/docs/architecture/STATE-SCHEMA.md — SHA-256 `ae2a7330f8d1b11417d59fc8758efb6a12a059d0f9b79a69fa36f890b7eadbe5`.
- /Users/joaopauloalves/.codex/forex-import-operation/20260916/product/docs/architecture/DB-STORAGE-GOVERNANCE.md — SHA-256 `3e44bc0dca3ed4ee4905f01007a351833affc4d3fdb64c10fa04a1dcc71e19e2`.

## Revisão de implementação

A revisão independente detectou prévia antiga confirmável após mudar opções de leitura; o controlador da interface passa a invalidar essa prévia e exigir nova análise. A escrita de preparação usa as transações canônicas existentes, com confirmações separadas e releitura. O gerador oficial acrescenta somente o payload PDF local derivado dos recursos já fixados; não muda política de cache, dependências ou formato de backup. O teste de interface usa bootstrap nominal e suprime somente a abertura inicial do onboarding no contexto fictício, para evitar o temporizador de boas-vindas interferindo no cenário de operações.

O FULL intermediário foi interrompido para incorporar a revisão antes do candidate final; seus resultados não são o gate final. Um teste Settings acusou corretamente drift de CSS durante aquela iteração; a execução separada estável passou. Falhas de suites antigas de cadastro/PDF são reproduzidas ou diagnosticadas separadamente, sem alterar seus oráculos.


## Resultado local verificado

Candidate build `ef588ca7418679a4`, baseado em `61120ec`, fontes preservadas durante a execução final. FULL: **57/57 PASS**. Focais: HTML54/54 e modelo52/52, preparação13/13, operações104/104, PDF local/HTTP/portátil/offline e fluxo completo modular/portátil, mais regressão do atalho após trocar a conta padrão. Os números são escopos diferentes, não uma métrica única de cobertura.

Consolidado anterior31/32 e cadastro30/32 mantêm falhas reproduzidas na base. O teste PDF anterior não monta seu ambiente completo. Um teste Node de contexto passou94/94, com intermitência separada na criação da terceira página da fixture (o escritor recusa estado desatualizado); essa falha não foi reproduzida na baseline. Nenhum teste antigo foi afrouxado. Três execuções FULL intermediárias foram interrompidas para incorporar correções; somente full-final.json representa este build. Duas tentativas com nomes .py inexistentes foram erros de invocação/NOT_RUN, corrigidas pela execução do teste .js existente.

A revisão encontrou e corrigiu prévia desatualizada, preservou o fechamento do painel após importar e vinculou o atalho à conta efetivamente importada. O atalho é removido se a conta padrão mudar. A revisão independente e as contraprovas não identificaram achado acionável restante dentro do recorte.

Comparação: `/Users/joaopauloalves/.codex/forex-import-operation/20260916/COMPARE.html`. Evidências, auditoria, relatório, capturas e recuperação em `../evidence/`; candidate-final.json identifica os18 caminhos com SHA-256. Suporte PDF restrito a texto/layout reconhecido, sem OCR. Arquivo real do proprietário e aceite manual: NOT_RUN. Sem commit, push, merge ou deploy.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: a ampliação da importação e a preparação de conta afetam o contrato operacional lido por agentes. A seção de arquitetura e a tarefa ativa foram reconciliadas dentro do escopo; instruções, autoridade e roteamento permanecem por referência. Avaliação IMPACT por categoria, limites e revisão física KEEP em ../evidence/audit-final.md. Sem indexação ou atualização de memória.
