# CHG — GENETRIX 1.21.2 no site — 2026-10-08

## Autoridade recebida e fronteira

Pedido atual do proprietário, conforme o packet de integração: **“integre esse a última versão do site”**. Autorização Git explícita já registrada na conversa: **“Execute commit, push e merge”**. Essas citações registram instruções humanas; este documento não é assinatura, novo aceite, autorização normativa ou permissão de publicação externa. O coordenador executará as ações Git separadamente, depois dos gates aplicáveis. Este autor documental não executa operações Git.

Raiz: `/private/tmp/jpw-genetrix-site-1-21-2-20261008`. Branch: `codex/genetrix-1-21-2-site-20261008`. BASE_SHA/HEAD conferido: `7f0828488b2fc0ea62dc7c421174799cda47a34a`. Base oficial anterior: GENETRIX 1.20.0. Fonte nova: candidato 1.21.2 recebido, byte-idêntico ao ZIP e ao manifesto indicados abaixo. O destino é a `main`/GitHub e o aplicativo local; não se presume hosting, instalação MT5, troca de conta ou armamento.

O lote mantém duas trilhas: produto/distribuição e transferência do juiz previamente revisado. O N3 da segunda não é norma financeira. Não aplicar a exceção §19.1, retirar bloqueios ou converter resultados históricos em PASS.

```yaml
schema: jp-harness/chg/v1
change_id: CHG-GENETRIX-1-21-2-SITE-20261008
status: approved
objective: integrar o candidato GENETRIX 1.21.2 ao site e reconciliar sua representação documental
risk_level: N1
authority_required: A2
target:
  root: /private/tmp/jpw-genetrix-site-1-21-2-20261008
  branch: codex/genetrix-1-21-2-site-20261008
  baseline_sha: 7f0828488b2fc0ea62dc7c421174799cda47a34a
scope:
  allowed_files:
    - mt5/jpw-alavancagem-atual/**
    - downloads/jpw-alavancagem-atual/**
    - index.html
    - .gitignore
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
    - docs/work/CHG-GENETRIX-1-21-2-SITE-20261008.md
    - docs/work/ACTIVE-TASK.md
    - docs/governance/CURRENT-STATE.md
    - docs/governance/CONTEXT-MAP.md
    - CHANGELOG.md
    - docs/validation/genetrix-1.21.2/**
  allowed_actions:
    - transferir os 132 membros canônicos previamente conferidos, sem alterar seu conteúdo
    - apresentar fontes 1.21.2 e separar provas compiladas históricas 1.20.0
    - reconciliar somente o contexto focal GENETRIX
    - gerar derivados pelos processos oficiais e executar verificações autorizadas
  forbidden_actions:
    - alterar fórmulas, parâmetros, schemas ou normas
    - instalar ou operar no terminal MT5
    - armar o Supervisor ou enviar solicitações de negociação
    - editar os 132 membros canônicos para corrigir seus cabeçalhos históricos
    - publicar externamente ou configurar hosting
  regressions_forbidden:
    - apresentar EX5 1.20.0 como executável 1.21.2
    - converter ausência de dado ou de teste em zero ou PASS
    - perder fontes, histórico, preferências ou estudos
acceptance_criteria:
  - ZIP 1.21.2 e manifesto coerentes, com os 132 membros canônicos idênticos à origem
  - download compilado atual indisponível até prova nativa correspondente
  - página e derivados oficiais representam as versões e limitações corretas
  - controles do juiz em contrato independente, com before/after e resultados preservados
  - gates locais e revisão independente vinculados ao candidate final, sem aprovação herdada
approved_tests:
  - preflight e conferência de links/diff/hashes
  - suíte web full e focais GENETRIX no host
  - suíte MT5 host e revisão independente do candidate congelado
rollback:
  source:
    - preservar a base Git 7f082848 e os pacotes/provas anteriores
    - reverter somente o delta de integração por operação Git posteriormente autorizada
  application_state:
    - nenhum dado real, gráfico ou instalação MT5 é modificado
approved_by: proprietário, conforme instruções conversacionais citadas acima
approved_at: null
expires_on:
  - raiz, branch, base, inventário canônico, objetivo ou autorização divergirem materialmente
```

A allowlist acima documenta o lote coordenado. A autoria deste subagente é estritamente limitada aos seis documentos nomeados pelo coordenador: este CHG, ACTIVE-TASK, seção focal de CURRENT-STATE/CONTEXT-MAP, topo do CHANGELOG e INTEGRATION. Não concede escrita nas demais superfícies.

## Contrato dedicado — transferência do control plane previamente revisado

A autorização para a atualização dos próprios juízes pertence aos contratos de origem aprovados e ao pedido atual de integrar o candidato concreto; esta trilha conserva sua revisão e não inventa uma nova aprovação de méritos. Registro recebido: 24 linhas, correspondendo ao ensaio ATR já incluído no pacote canônico e a 23 ferramentas Python. Há 21 arquivos presentes na base e três bridges novos; ausência na base é registrada como ausência, sem hash fictício. A proveniência por hash não substitui auditoria semântica nem execução.

```yaml
schema: jp-harness/chg/v1
change_id: CHG-GENETRIX-1-21-2-JUDGE-TRANSFER-20261008
status: approved
objective: transferir somente os bytes do juiz previamente aprovado para a integração 1.21.2
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-genetrix-site-1-21-2-20261008
  branch: codex/genetrix-1-21-2-site-20261008
  baseline_sha: 7f0828488b2fc0ea62dc7c421174799cda47a34a
scope:
  allowed_files:
    - mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_RaizN_Live_Tests.mq5
    - tools/jpw_genetrix_brand_test.py
    - tools/jpw_genetrix_ui_test.py
    - tools/jpw_mt5_design_test.py
    - tools/jpw_nocuda_fibo_controller_test.py
    - tools/jpw_nocuda_fibo_ui_test.py
    - tools/jpw_nocuda_integration_test.py
    - tools/jpw_personal_history_test.py
    - tools/jpw_positions_ui_test.py
    - tools/jpw_signal_copy_ui_test.py
    - tools/leverage_details_event_test.py
    - tools/leverage_geometry_test.py
    - tools/leverage_host_layout.py
    - tools/leverage_host_runtime.py
    - tools/leverage_host_shim.py
    - tools/leverage_live_adapter_test.py
    - tools/leverage_package_test.py
    - tools/leverage_panel_test.py
    - tools/leverage_reliability_test.py
    - tools/leverage_scheduler_test.py
    - tools/leverage_stop_ui_test.py
    - tools/leverage_suite.py
    - tools/leverage_suite_test.py
    - tools/leverage_page_test.py
  allowed_actions:
    - transferir bytes conforme os 24 registros before/after da revisão anterior
    - executar controles e registrar o resultado bruto das tentativas da integração
  forbidden_actions:
    - mudar esperado, tolerância, timeout ou gate para obter aprovação
    - editar o harness canônico, políticas, CI ou normas
    - apagar resultado histórico ou autovalidar o produto
acceptance_criteria:
  - identidade do before demonstrada contra a base integrada, incluindo ausência dos três bridges novos
  - after dos 24 registros coincide com os arquivos transferidos
  - delta e controles permanecem rastreáveis e separados do mérito financeiro
  - revisão independente e gates atuais antes da integração final
approved_tests:
  - comparação determinística before/after e controles negativos aplicáveis
  - suíte MT5 host e testes da página/distribuição
rollback:
  source:
    - base 7f082848 e registros de origem conservados
    - operação Git de retorno exige autorização específica
approved_by: proprietário, conforme contratos de origem e instrução atual de integração confirmados no packet
approved_at: null
expires_on:
  - qualquer hash, esperado, conjunto dos 24 registros ou escopo divergir
```

## Brief — compreensão específica

1. **Finalidade:** JP Wealth organiza fatos e risco financeiro; esta tarefa evita que o site ofereça uma versão antiga ou um compilado sem prova correspondente. PROJECT-CONTEXT distingue capacidade observada de finalidade.
2. **Responsabilidade:** o site distribui e explica o GENETRIX; o indicador Conta mostra sete leituras, o Monitor reúne histórico/monitoramento e ciclos contábeis, NoCuda é estudo técnico, Supervisor 7x é separado e opcional.
3. **Antes/depois:** a `main` representa 1.20.0 com EX5 historicamente vinculados. O candidate local passa a apresentar fontes 1.21.2, preservando as provas 1.20.0 em seu diretório histórico, sem colocá-las no download compilado atual.
4. **Impacto:** página GENETRIX, manifesto/download, fontes MT5, verificadores de distribuição/host e contexto consumido por agentes. Forex web, norma e dados operacionais não recebem nova regra.
5. **Invariantes:** cálculo 1.9.0; identidades, unidades, fórmulas, schemas, preferências, estudos, PENDING / NOT_HOMOLOGATED / BLOCKED e falhas anteriores. Monitor não envia ordens; nenhum Supervisor será armado.
6. **Evidência:** identidade por hashes, before/after dos juízes, testes host e web nos bytes finais, revisão independente e estados separados de compilação/runtime/instalação. História ou simulação não são testes nativos novos.

## Fontes e VERSION_CHECK inicial

| Fonte consultada | Identidade e passagem | Alcance |
|---|---|---|
| AGENTS.md | SHA256 `d0b77e12abb7dd7336e38c848fdcd8d4dec0142cd4c23289d2d46ef090a4b133`; autoridade, preflight e política Git | Núcleo do repositório lido; não concede autorização |
| Core externo relocalizado em `2 - TRABALHO/99 - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md` | SHA256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`; §§12–14,19,23–25,28–30,36–48 | Caminho antigo do AGENTS é pista; arquivo atual consultado por seções pertinentes |
| agentic-evolution-governance | SHA256 `b484b6a9a5ec2495ef7c37efbb2b92b74e73b9a52bae0964e06a773d8d915335`; IMPACT/RECONCILE e limites de propagação | Instrução local congelada, sem edição |
| GENETRIX_CORRECTIONS_1_21_2.md | SHA256 `e3c913376524b3240909c5c9049a034afb5b1d569ead95783a0b12f5d7dfa1e4`; revisão NoCuda e fronteiras | Documento canônico lido |
| harness/REPOSITORY_INTEGRATION.md | SHA256 `be532e1ddea267d1edfabfb2dd4cabb3e24da86ca1bc7d89b878fe7e38cde392`; fotografia 1.20 e R2/R5 | Histórico preservado, não descrição da nova integração |
| Manifesto e ZIP | 1.21.2,132 membros; hashes abaixo | Conferência de identidade, sem prova de execução nativa |
| Proveniência dos juízes | 24 registros; before/main/after rechecados | 72 comparações de hash; não julgamento semântico universal |

**Acesso:** fontes acima acessíveis, com leitura ou extração de campos efetivamente registrada. README, mapa/contexto e históricos foram consultados nos trechos pertinentes; não se alega leitura integral do repositório. **Atualização:** 1.21.2 é a edição encontrada e selecionada para este pedido, sem alegar busca global de todo acervo. **Vigência/adoção:** produto CANDIDATE; integração Git atual ainda não concluída neste checkpoint. **Conflitos:** cabeçalhos antigos no pacote são fotografias/aliases, mantidos; não escolher norma por número de versão. **Aplicabilidade histórica:** provas 1.20 valem para sua revisão, não para 1.21.2. **Autoridade:** nenhuma ratificação financeira deduzida de hash, nome ou pasta. Nova fonte/delta invalida somente as conclusões afetadas.

## Preflight, planejamento e rollback

Audit: `python3 tools/agent_preflight.py --mode audit` → PASS, com aviso de 88 alterações coordenadas e SOURCE REVISION UNKNOWN herdado. Edit sem `--allow-dirty` → bloqueado por árvore suja, preservado como tentativa. Após conferir a autoria declarada do lote e os registros de origem, `--mode edit --allow-dirty` → PASS, conservando os avisos. Nenhum arquivo foi limpo automaticamente.

As 88 entradas observadas são trabalho do coordenador: fontes/juízes/página/derivados autorizados, 33 EX5 antigos retirados do conjunto atual e arquivos novos da mesma integração. O número é uma fotografia antes desta edição documental, não uma contagem final. A origem de alterações novas deve continuar sendo conferida.

Plano: identidade e contrato → reconciliação de seis documentos → conferência documental → congelamento → gates e revisão independente do coordenador → Git autorizado. Os gates finais estão em execução externa; **NOT_RUN neste checkpoint documental**, sem antecipar PASS. Evidências devem identificar ambiente, candidate, ferramenta e resultado bruto. O preflight não demonstra carregamento real do Cockpit.

Rollback preserva Git da base, provas históricas e pacotes anteriores. Não executar reset/revert/remoção automática, reinstalar EX5 antigo, apagar bases ou trocar conta para “testar”.

## Impact assessment agêntico

**CHANGESET:** produto 1.20.0 na base 7f082848 → fontes 1.21.2 e distribuição source-only; juiz transferido em trilha N3 própria. **Natureza:** mudança material de produto/distribuição e reconciliação documental, separadas. **Impacto:** médio nas representações GENETRIX; alto no alcance dos juízes, sem alteração de autoridade normativa.

| Categoria / representação | Impacto | Ação local | Reconciliação e fundamento |
|---|---|---|---|
| Contexto operacional: CURRENT-STATE/ACTIVE-TASK | AFFECTED | REQUIRED | Novo bloco focal 1.21.2 substitui a leitura atual, conservando fotografias antigas |
| Mapa/registry documental: CONTEXT-MAP | AFFECTED | REQUIRED | Roteia para manifesto, instruções e integração atuais; não instala agente |
| Changelog / entrega informativa | AFFECTED | REQUIRED | Registra o evento e seus limites; resultado ainda pendente |
| Instruções raiz e bootstrap | AFFECTED | NOT_REQUIRED | Leem o contexto/mapeamento atualizado; autoridade e regras permanecem iguais |
| Harness e AGENTS locais entre 132 membros | AFFECTED | NOT_REQUIRED | Conteúdo canônico conserva bytes e classificação; aliases atuais ficam nesta integração, sem reescrever fotografia1.20 |
| Skills e routing | AFFECTED | NOT_REQUIRED | Procedimentos existentes tratam a nova revisão por referência; nenhuma skill criada/substituída |
| Juízes/gates GENETRIX | AFFECTED | REQUIRED |24 registros transferidos pelo coordenador; contrato N3 próprio, controles e comparação before/after |
| Contratos/arquitetura financeira e fontes M0 | NOT_AFFECTED | NOT_REQUIRED | Nenhuma regra, fórmula, schema, homologação ou permissão financeira é alterada |
| CI e proteções | NOT_AFFECTED | NOT_REQUIRED | Nenhum workflow/gate obrigatório/proteção modificado nesta transposição |
| Handoffs anteriores / auditorias1.20 / memória | AFFECTED | NOT_REQUIRED | Históricos mantêm data/alcance; não são fonte atual 1.21.2. Nenhuma memória persistente alterada |
| Índice/vetor/grafo persistente | UNKNOWN | NOT_REQUIRED | Nenhum mecanismo oficial de indexação foi demonstrado para esta tarefa; nenhum índice é criado ou refeito |

**AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS:** versões e disponibilidade compilada mudam representações consumidas pelo bootstrap; os seis documentos focais devem corresponder ao manifesto/ZIP e aos estados nativos. A cobertura acima separa alcance semântico de necessidade de escrita. **RECONCILIATION REQUIRED: SIM**, delimitada aos itens autorizados. **INDEX NOT REQUIRED neste escopo:** nenhuma operação de índice é necessária para conferir as referências documentais; mecanismo global não é presumido. **SYSTEM RECONCILED não declarado** antes da conferência final dos consumidores e gates.

## Resultado documental observado e handoff

Conferência desta autoria: 132/132 membros e hashes do ZIP coincidem com a árvore fonte; 24 before/after dos juízes conferidos (72 comparações); seis documentos salvos/reabertos, links existentes e histórias anteriores conservadas. `git diff --check` e preflight edit com árvore conhecida passaram. A suíte MT5 host R3 do coordenador foi lida e vinculada ao candidate: 40/40 PASS, 382 inputs sem alteração. Full web e auditoria final permanecem pendentes; nativo, instalação e armamento conservam NOT_RUN/BLOCKED. Resultados e hash do recibo em INTEGRATION.

A reconciliação documental focal foi aplicada e conferida dentro dos seis arquivos permitidos; não se declara coerência global, aprovação financeira, aceite operacional ou deploy. Nenhum Git foi executado por este autor. O coordenador incorpora seus recibos finais e revisa antes das operações Git autorizadas.

## Suplemento R8 — manutenção delimitada do control plane

A primeira CI expôs um defeito preexistente de linkage no juiz de risco: `SHA256` não resolvido em Linux porque o comando não incluía `-lcrypto`. Manutenção N3 de control plane dentro da integração/correções autorizadas, sem competência ou mudança financeira. [Contrato e autoridade existente](../validation/genetrix-1.21.2/evidence/LINKAGE-CHANGE-R8.md), [critérios congelados](../validation/genetrix-1.21.2/evidence/LINKAGE-CRITERIA-R8.json) e [parecer independente](../validation/genetrix-1.21.2/evidence/LINKER-SUPPLEMENT.md).

Só mudaram import `sys` e o acréscimo da biblioteca fora de Darwin. Foram mantidos fixtures, assertions, expectativas, flags estritos, fonte MQL, ZIP, regras e schemas. Gate obrigatório reexecutado: full R8 `57/57 PASS`, host R8 `40/40 PASS`; três processos novos de risco com `51 PASS` cada. Novo CI Linux, commit/push/merge possuem recibos posteriores. A tentativa CI anterior `39 PASS / 1 TEST_HARNESS_FAIL` permanece registrada, sem exceção ou aprovação transferida.
