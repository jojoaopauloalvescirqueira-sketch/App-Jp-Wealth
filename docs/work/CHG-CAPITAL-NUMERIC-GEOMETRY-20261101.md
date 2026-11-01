# Correntes de Capital: números íntegros em largura estreita

Base: `7d216f41b22ce32d29fe64a76ca49725e39f00b3`, branch autorizada `codex/backup-unificado-20261031`, limpa antes deste delta. O usuário autorizou continuar a implementação, correções e integração Git após o aceite visual. A dispensa do Harness externo em favor dos contratos versionados permanece delimitada a esta implementação. Não há novo ajuste de CI, norma ou gate.

## Finalidade e compreensão

O JP Wealth organiza registros e ferramentas financeiras com preservação de dados. Correntes de Capital é um laboratório didático: seus valores descrevem um campo ilustrativo, não ordens reais. A apresentação vive em `src/styles/app.css`, enquanto motor, catálogo, controlador e progresso são consumidores preservados. O contrato `docs/architecture/CAPITAL-CURRENTS.md` exige controles utilizáveis, valores derivados e isolamento financeiro; `docs/governance/UI-VISUAL-QUALITY.md` exige ausência de cortes e preserva critérios de geometria/foco. O processo admite testes funcionais N1 sem alterar o juiz ou controles superiores.

Hoje: Linux FULL do SHA base tem **115 PASS e 1 PRODUCT_FAIL**, sem NOT_RUN. UI principal **413 PASS**, fontes estáveis; MT5 Host **62 PASS**. A matriz original de Capital falha em sidebar/390px/claro/CSSzoom2: root.clientWidth155, scrollWidth158. Arial adicional passa e não substitui a matriz original. Os recibos brutos permanecem intactos.

Diagnóstico Mac sintético, fontes de produto intactas: Verdana reproduz root155/scroll158. O cabeçalho já cabe; os flex items numéricos encolhem: output `+0,40` client42/scroll54 e dd `1,000` client35/scroll38. Uma única intervenção CSS descartável `flex-shrink:0` nesses valores produz root155/scroll155 e texto numérico integral. Não se afirma que Verdana seja a fonte efetiva do Linux.

Depois: manter a largura intrínseca dos valores numéricos de label/output e readouts/dd, permitindo ao texto descritivo ocupar a largura restante. Não ocultar overflow, reduzir fontes, quebrar números, modificar valores, persistência ou limites. Risco N0-V/N1, sem migração.

## Intervenção e validação

Arquivos autorizados: CSS local de Capital; fixture funcional tipográfica no teste existente; derivados oficiais; este CHG e recibos/contexto/memória focais. Preservar integralmente os 48 casos originais, Arial e todos os critérios existentes. Acrescentar Verdana e medição da integridade dos números, observar RED antes do produto, então aplicar o menor delta e verificar GREEN. Rebuild somente por `tools/rebuild_monolith.py --refresh-manifest`.

Nenhum motor, regra, parâmetro, dado real, escritor, schema, CI, quality_gate.py, oráculo UI central, norma, AGENTS ou skill pode mudar. Foco, alvos44px, isolamento financeiro, HTTP/file/portátil/PWA e ciclo de vida permanecem. Fontes pertinentes são versionadas no BASE_SHA acima; CSS base SHA256 `5a6cf3700729c1a8df76de35e999bf0e52b948cbb7180f530b2370d93d7ba052`.

Verificação: RED/GREEN da fixture real, diagnósticos numéricos e capturas sintéticas, teste Capital completo, reconstrução oficial, FULL local final, auditoria independente e FULL Linux do novo SHA antes do merge. O 115/116 anterior continua falho e não é promovido por testes locais. A4 anterior de 1800s apenas UI e 900s demais permanece intocado.

Rollback: reverter somente este delta e reconstruir derivados, preservando stores, originais e backups. Não excluir worktrees. Sem site/publicação nem operações financeiras. AGENTIC IMPACT DETECTED: reconciliar somente contexto/provas deste incidente; sem mudar autoridade, roteamento ou índices globais.


Primeiro FULL local desta correção:115PASS/1ENVIRONMENT_ERROR, zeroPRODUCT_FAIL. Capital passou; Notas/native200perdeu captura antes de pointerup. Código/teste de Notas idênticos à base, sem elementoCapital noDOMfalho. Usuário informou uso do mouse naquelehorário; compatível com interferência, sem alegar causa externa provada. Preservar LOCAL-FIRST-ENV/NOTES-INPUT-ENV e realizar um ensaio focal controlado inalterado; FULLnovo integral ainda obrigatório.


Ensaio focal controlado de Notas concluído19/19PASS, mesmos inputs/teste do evento interrompido e fontesestáveis. Capital nativo200% adicional32/32PASS (medidas/limites próprios). O ENV anterior permanece imutável; não alegar correção deprodutoNotas nem causa externa provada. Uma única nova execução FULL integral do mesmo candidato, após orientação de ponteiro parado em janelasnativas, é necessária para nova evidência;115nãoé116.


FULL local final do build33e26b5d9bb45c0b: **116/116 PASS**, matrizUI **413/413 PASS**, fontes estáveis. Recibos FULL-LOCAL.json/UI-LOCAL.json em docs/validation/capital-numeric-geometry-20261101/. Capital adicional nativo200%:32apresentações, outer/inner≈2 eCSSzoom1, presença/integridade numérica, canvas/44px/hits/teclado/finanças; sourceUnchanged deste ensaio cobre somenteCSS/testeCapital, não todoapp. Captura original em branco preservada somente como diagnóstico; legibilidade pintada verificada separadamente nos artefatos identificados em native-paint-review.json. Novo Linux do SHA final ainda necessário antes do merge; Linux115/1 anterior preservado.
