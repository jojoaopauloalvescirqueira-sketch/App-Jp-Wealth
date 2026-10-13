# Auditoria das correções AUD-01..AUD-10 — 12/10/2026

Data da fotografia: 2026-10-12

Source revision representada: `0f247215cc20829fdba40c3b33458ee976c17ea1`
Branch: `codex/audit-bugfixes-20261012` — delta local não commitado.
Build: `f1a235b550ce6db7`.

Estado deste registro: dez patches aplicados e full final PASS; teste manual e aceite humano pendentes. Resultado final de cada execução e candidate estão nos recibos externos; este texto não concede aceite ou autorização Git. Auditoria original: quatro achados altos e seis médios, preservada separadamente.

## Causas e comportamento corrigido

| ID | Causa | Correção e prova |
|---|---|---|
| AUD-01 | Limite de profundidade do workspace aplicado ao envelope inteiro | Inspeção iterativa de chaves/ciclos no backup; limite do workspace separado. Históricos reais sintéticos de 26/27/35 revisões sobrevivem export/import/recarga sem truncamento. Export passa pela própria validação antes de GENERATED. |
| AUD-02 | Só o container checklist era verificado | Grupos, itens, labels e valores conhecidos validados antes de defaults/consentimento/escrita. Conteúdo inválido já salvo entra na recuperação existente, com raw preservado. Ausência legada, zero e extensões compatíveis permanecem aceitos. |
| AUD-03 | Não-null era contado como valor financeiro conhecido | Cobertura e somas PF reutilizam pfAmountInDomain. String/decimal/inseguro/negativo permanecem fatos sem completar totais; zero continua válido. |
| AUD-04 | Adapter do painel recalculava reservas sem contexto suficiente | Consome os resultados canônicos de FCR/FEO, preservando status/findings/contexto e moeda; Satélite não fornece base Mestre. PENDING_GOVERNANCE/BLOCKED permanecem explícitos. |
| AUD-05 | Referência null virava drift zero | Calibração e simulação exigem referência finita; a UI explica a pendência mesmo com CID. Zero explícito é controle válido, sem ativar política sintética. |
| AUD-06 | Primeira observação ignorava a abertura do período | Compara a data UTC da observação à abertura selecionada, usando a convenção vigente. Recusa anterior ao ato factual; mesmo dia UTC e observação retrospectiva dentro do período permanecem válidos. |
| AUD-07 | Recuperação reconstruía campos, mas deixava formulário/view fechados | Reabre a view Research pertinente e formulário Pivots, restaurando edição e foco. Bases incompatíveis permanecem leitura/cópia. |
| AUD-08 | Aceitar descarte e trocar pasta mantinha editor sujo | Callback aceito fecha o rascunho antes de desenhar a pasta; cancelamento preserva a edição; nenhuma nota salva é regravada. |
| AUD-09 | Filtro/ordenação substituíam todo o DOM | Atualiza só estatísticas/resultados e listeners desses novos nós. Controles, editor, cursor e foco permanecem. |
| AUD-10 | Fallback de navegação interceptava arquivos Markdown | Documentos explícitos no cache/fingerprint e no portátil. Links online/offline entregam bytes do build; waiting/activate e fechamento de clientes permanecem conservadores. |

## Evidências

Diretório durável: /Users/joaoalvescirqueira/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/99 - OTHERS/JP Wealth - Auditoria 2026-10-12/Correcoes
Diretório de execução: /private/tmp/jpw-audit-bugfixes-20261012

- Backup/import: security-baseline-final-v2/results.json e security-final-v3/results.json. Tentativas anteriores e triagem preservadas em backup-import-fixture-triage.json; cobertura e transporte JSON das fixtures foram corrigidos, sem relaxar recusas do produto.
- Projeções: financial-baseline-root/receipt.json e financial-final/receipt.json, com 29 casos em Node VM; persistência ali é double sintético, não prova de browser.
- Interface: ui-baseline-corrected/receipt.json (6 PRODUCT_FAIL) e ui-final-v2/receipt.json (18 PASS, desktop/tablet/móvel e temas). O primeiro helper de data/menu falhou; sua tentativa continua registrada em ui-baseline-root.
- PWA: pwa-baseline.json (3 PASS/8 PRODUCT_FAIL) e pwa-final-v2.json (11 PASS após reconstrução). Validação oficial: 102 scripts e 670 IDs; tentativa inicial restrita sem runtimes/permissão de rebuild foi ENVIRONMENT_ERROR, depois reexecutada com sucesso.
- Focais existentes: focals-final/receipt.json, 10 PASS, com hashes antes/depois iguais: engine/read-model/ledger/state/recording Forex, startup de reservas, recuperação de drafts, backup, PDF consolidado e PDF local.
- Prova adicional de browser de domínio: domain-browser-final-v2/report.json. Tentativa anterior e sua triagem são mantidas, sem promover erro de fixture a defeito de produto.
- Full oficial, fingerprint e revisão final: full-final.json, candidate-before-full.json, candidate-final.json e independent-final/. O full anterior de main não é evidência destas correções.

Cada verificação recebe PASS, PRODUCT_FAIL, TEST_HARNESS_FAIL, ENVIRONMENT_ERROR, BASELINE_FAIL ou NOT_RUN segundo sua execução e causa. Só o recibo correspondente comprova comando, ambiente e alcance. Os recibos finais devem ser confrontados com hashes atuais; full ou cobertura não homologam V11.

## Limites, documentos e rollback

Todos os dados e perfis de browser são sintéticos. Dados reais, importação de backups pessoais, Safari/iPhone físico, instalação PWA real, produção e teste manual do proprietário são NOT_RUN. Fórmulas/parâmetros, política/engine canônicos, norma, schema, DEFAULTS, MT5, instruções e gates não foram alterados; hashes e diff final são conferidos no encerramento. Conflitos FCR/FEO e demais limites históricos continuam abertos.

As duas descrições de domínio (FX-PLANNING.md e PERSONAL-FINANCE.md) foram reconciliadas exatamente pelos diffs de domain-doc-proposal após a resposta humana específica “Autorizar essas duas atualizações descritivas”. O contrato registra somente esses dois paths adicionais.

Rollback recuperável: fonte original de cada arquivo no Git BASE_SHA e cópias externas baseline-source; reverter somente este delta mediante pedido, sem reset/stash/reescrita automática. Nenhum dado real foi migrado. Encerrar servidores e contexts descartáveis ao terminar; runtime temporário já autorizado pode ser reutilizado para o teste manual.

Teste manual e aceite do proprietário precedem qualquer autorização específica de commit, push, integração ou publicação. Nesta tarefa nenhuma dessas ações foi executada.

## Primeira execução full e novo candidate

full-attempt-01.json preserva o resultado bruto 55 PASS / 2 PRODUCT_FAIL do fingerprint9d1e728e. O teste state-integrity recusou corretamente checklist inválido, mas a mensagem nova deixou de identificar a chave exata checklist (C maiúsculo no rótulo); o helper recebeu só essa identificação na mensagem, sem mudar predicados ou alterar o teste. Revisão independente e checksum do delta: checklist-diagnostic-receipt.json e independent-final/checklist-diagnostic-review.json.

A finalização teve timeout de actionability em sessionCancel nessa execução. O mesmo teste/fontes passou no contracheque integral sem alteração de assertiva ou código de finalização, com identidade antes/depois igual (session-finalization-countercheck.json). A causa transitória não está plenamente identificada; o resultado bruto anterior é mantido e não virou PASS retroativo. A próxima execução full congela o novo candidate; não se usa a exceção histórica do Harness.

## Fechamento factual da validação

Full final: PASS, 57/57 verificações oficiais, no freeze7f39f8b84535e2fe41f7b6767c29f874deabbe5018555765625ea2d8a08cb548 (candidate-runtime-final.json). Regressores atuais: backup34, projeçõesVM29, interface18cenários/201assertivas, PWA11 e browser de domínio57, todos PASS com hashes estáveis. A primeira execução55/57 permanece histórica em full-attempt-01.json; a ocorrência transitória de cancelamento não foi apresentada como correção de código.

Revisão independente do produto registrada em independent-final/. O delta factual de encerramento tem recibo externo próprio; sua ausência significa NOT_RUN, não aprovação presumida. O fechamento altera somente sete documentos: quatro registros factuais, dois contratos descritivos explicitamente autorizados e o registro dessa autorização no CHG. Runtime, juízes e artefatos ficam byte-idênticos ao freeze do full. Preflight/contexto/estrutura do CHG e diff final são revalidados após essa reconciliação. Focais anteriores10PASS mantêm seus próprios hashes/alcance, não são promovidos ao novo freeze integral.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED
BASIS: CONTEXT-MAP roteia M1/M3/M4, PWA e contratos PF/FX para fontes afetadas. ACTIVE/CURRENT/SESSION e registros autorizados foram reconciliados por fato; instruções, router, skills, norma e juízes herdam referências sem mudanças. Os dois textos de domínio foram reconciliados por autorização adicional específica; seus consumidores herdam as fontes atualizadas. O parecer de impacto detalhado está em agentic-impact.md externo; clientes novos/Claude e índices externos continuam UNKNOWN/NOT_RUN. A reconciliação foi verificada nos arquivos e referências locais; não se presume carregamento em clientes novos ou sincronização externa.

Candidate local para teste manual do proprietário. Aceite manual, commit, push, merge e publicação continuam pendentes e separados. Dados sintéticos somente; dados reais, Safari/iPhone físico e produção NOT_RUN. Evidências serão copiadas para o diretório durável antes da entrega, com manifesto próprio; existência e hashes devem ser conferidos por receipt.
