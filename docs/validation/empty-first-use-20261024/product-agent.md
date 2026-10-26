# Produto — primeiro acesso vazio

Branch: codex/primeiro-acesso-vazio-20261024. Base a4bf278. Alterações preexistentes de Calendário e Mercados preservadas.

Autorização: plano humano e branch específica; CHG-JPW-EMPTY-FIRST-USE-PRODUCT-20261024. Implementação iniciada somente após GO-RED do coordenador (EMPTY-BOOT-01 e, para checklist, EMPTY-CHECK-01).

## Delta de produto

- DEFAULTS sem contas/performance demonstrativas; saldos, ATRs, exposição-alvo e lote mestre null; início/perfil de período vazios; capital nominal não derivado.
- Checklist inicia com 15 respostas null, sem seleção, pontuação ou classificação final até resposta explícita de todos os itens. N=0 é incompleto. Classificações/limiares existentes conservados quando completo. Estado aria-pressed acompanha a resposta.
- Validação aceita null explicitamente no saldo inicial e nas respostas, distinguindo chave ausente/tipos inválidos. Saldo atual null não é substituído. Política histórica de saldo atual ausente/inválido → SI permanece fora deste delta.
- Normalização de perfil ausente/vazio conserva vazio; leitor ativo não presume Base quando não existe escolha. Catálogo e referências explícitas não mudaram.
- Campos de lote/exposição vazios permanecem null; lote calculado exige ambos operandos finitos. Não há multiplication null → zero.
- Valores pessoais ausentes são apresentados como Não informado no painel/resumo; fatores/lotes sem dados ficam Não calculável.
- Nova base na compatibilidade de finalização recebe o mesmo vazio; preservação de documento confirmado permanece igual.

## Arquivos alterados

src/js/00-core/01-risk-profiles.js
src/js/00-core/03-default-state.js
src/js/00-core/04-persistence.js
src/js/10-domain/04-stop-statistics.js
src/js/20-ui/03-main-render.js
src/js/20-ui/07-chart-crosshair-tooltip.js
src/js/20-ui/08-input-bindings.js
src/js/40-app/04-onboarding.js
src/js/40-app/07-finalize-session.js

Nenhuma mudança de engine, política, catálogos, CSS, testes, manifesto, artefatos, Git ou dados do operador por este agente. Mesmos nomes de contas já salvas não são usados para remoção ou identificação de demo.

## Verificações do agente

- python3 tools/agent_preflight.py --mode edit --allow-dirty: PASS (pendências conhecidas autorizadas; aviso histórico de freshness registrado).
- git diff --check: PASS.
- Node --check nos nove arquivos: 9/9 PASS.
- Leitura integral do próprio diff: concluída, alteração restrita.

Casos manuais/browser, roundtrip, importação antiga, invalidez, conflito, distribuições e suíte completa: NOT_RUN por este agente; coordenador/test-agent executam provas próprias. Nenhum aceite humano inferido.

## Casos que a validação integrada deve confirmar

1. Navegador novo sem bootstrap fixture: zero contas/períodos/performance e checklist não respondido.
2. Recarregar/checkpoint, efetuar gravação explícita não financeira e recarregar: null e ausência continuam distintos de zero.
3. Respostas parciais e lista sem itens: não concluído; todas0/1/2: classificações originais.
4. Saldo inicial null válido; campo apagado/texto/booleano inválidos; saldo explícito0 preservado.
5. Backup antigo e documento com nomes antigos: fatos/respostas preservados; nenhuma remoção retroativa.
6. Campos legados vazios sem zero, sem Base implícita e sem capital nominal derivado.

Rollback: reverter somente o delta deste agente sobre baseline-sources; não usar reset/stash nem apagar pendências.

## Delta complementar — cadastro explícito sem saldo informado

Após autorização do coordenador e inclusão de40-app/24-fx-consolidated-import.js no CHG, o caso EMPTY-CREATE-01 demonstrou RED em /private/tmp/jpw-empty-first-use-20261024/tests-red-registration.json. A linha de inicialização de novas/recadastradas contas passou de sini:0/satu:0 para sini:null/satu:null. Contas existentes no modo complete e seus saldos, inclusive zero explícito, não são alterados. Nenhuma fórmula ou leitor foi ampliado.

Original preservado antes do patch em baseline-sources/src/js/40-app/24-fx-consolidated-import.js. Node --check do arquivo e git diff --check: PASS. Prova GREEN integrada fica com coordenador/test-agent; nenhum rebuild por este agente.
