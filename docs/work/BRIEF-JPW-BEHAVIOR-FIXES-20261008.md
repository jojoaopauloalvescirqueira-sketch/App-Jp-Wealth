# Brief: correcoes de comportamento e auditoria independente

Base 7f0828488b2fc0ea62dc7c421174799cda47a34a; build f70839305b2d7fb8; raiz /private/tmp/jpw-behavior-fixes-20261008/candidate; branch herdada codex/onboarding-first-access-20261007. Pedido humano: Pedido humano nesta conversa: corrige todas as falhas, implemente todas as melhorias, e refaca os testes e auditoria. Registro do reconhecimento desta autorizacao, nao aceite do candidate final.
Nao criar/trocar branch nem realizar commit/push/merge/publicacao. Copia isolada preserva origem e main; arquivos Git copiados somente para leitura de historico.

## Compreensao

1. JP Wealth organiza fatos financeiros e leitura de risco; esta tarefa corrige identidade/confirmacao/recuperacao, nao altera normas.
2. Ledger projeta fechamentos; planejamento consome ACTUAL e reservas; PF mostra/captura edicao; writer confirma fatos.
3. Antes: FIN01 consulta B dependeA, FIN02 UI semconfirmacao, FIN03 reservaperiodolegado, PF perde texto aposrecusa, Notasajuda contradizbackup. Depois: contexto explicito sem trocar operacional, confirmacao manual enviada, resolvedor canonico, edicao recuperavel eorientacao fiel.
4. Consumidores: conta/periodo, monthlyActual/forecast, reservas, captureWorkspace/restore eFinalizar. Testes antigos usam contratos superados; testar mesmo comportamento e separar alteracao da fixture da correcao produto.
5. Preservar20alteracoes, schemas, formulas, guarda import/finalizacao, origem, moedas, CONFIRMED/REFUSED/UNKNOWN, MT5bytes, dados reais e autoridade. FCR/FEO segue aberto.
6. Prova: baselinevermelho/candidateverde nos mesmos dados; recarga/concorrencia/recusa, fontes canonicas iguais; novos focais/177 inventariados/gates bruto/revisao independente congelada.

Harness pertinente: /Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/99 - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md; SHA256 b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95; §§12-14/19/24/28-30/36-48. §19.1 permanece inativo. A4 reconhecida somente para correcao/reconciliacao local/testes explicitamente solicitados, nunca Git ou homologacao.

| Fonte | SHA256 baseline | Escopo da evidencia |
|---|---|---|
| AGENTS.md | d0b77e12abb7dd7336e38c848fdcd8d4dec0142cd4c23289d2d46ef090a4b133 | fonte baseline lida, nao validacao dos novos bytes |
| docs/governance/PROJECT-CONTEXT.md | 37637ca60dd014e938d3156cba402bec3045b88d4ec5989d776ff23482dc9a27 | fonte baseline lida, nao validacao dos novos bytes |
| docs/governance/CHANGE-PROCESS.md | 5240dac3196ebeb74805be4864465e0037c8d58d7e09068a7db77f99554b6fcd | fonte baseline lida, nao validacao dos novos bytes |
| docs/architecture/FOREX-V11-ENGINE.md | 2ae8cd8061ae9f4f9e6cc966d54d386211fb950b23a7ecf40b335d5ad9125184 | fonte baseline lida, nao validacao dos novos bytes |
| docs/architecture/COMPLETE-BACKUP.md | 32cbcbc6dbfa1eed2170b94a4edc834887460f753f2a946e5a95a5e5cc1ee336 | fonte baseline lida, nao validacao dos novos bytes |
| docs/architecture/PERSONAL-FINANCE.md | 461458417486806f20ea8727e954058e37b2393addbd69ae905f5bf8e72c8046 | fonte baseline lida, nao validacao dos novos bytes |
| src/js/30-accounting/01-daily-ledger.js | 8d87a15cb78ea814d81ec8798286deeac16e17c58f5fb1105aad82b14e7db78b | fonte baseline lida, nao validacao dos novos bytes |
| src/js/30-accounting/05-fx-planning/03-fx-state.js | 0b8f3bde46820b639d1dc364ec42e6f1b45e0269946c92500f5bdcf246e7a5b8 | fonte baseline lida, nao validacao dos novos bytes |
| src/js/20-ui/18-finpes-budget.js | 2a99714bdea59e6c7ddde327b7bb745833f35e743e1d6668a6b539c49daee350 | fonte baseline lida, nao validacao dos novos bytes |

## Organizacao do trabalho

Financeautor: tres scripts accounting+novo regression. Draftautor: PFscript/indexapenasajuda+novo regression. Harnessautor: somente fixtures/testes existentes comprovados. Root: contratos, contexto, Atlasmanual, geradores oficiais e gates. Revisores nao sao autores da alteracao avaliada.

Snapshot/hashantes e resultadosanterior fora do produto: /private/tmp/jpw-behavior-fixes-20261008/baseline-snapshot.tar.gz e baseline-fingerprint.json. Logs/recibos/capturas novos em evidence. Rollback restaura apenas delta novo; nao altera20deltas/origem ou dados pessoais.

## Agentic impact delimitado

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: ACTIVE-TASK semCHG/CTX, Atlas14hashes divergentes, CURRENT-STATE omite source revision e orientacoeslegadas deFinalizar contradizem contratoatual. Estado/contratos/Atlas requerem reconciliacao; skills/router/precedencianaomudam (AFFECTED porreferencia, LOCAL ACTION NOT_REQUIRED). Indice externoGraphifyhistorico: INDEX NOT REQUIRED nesta manutencaomanual textual; semreindex/servico. Naoexpandir27familiasAtlas nempromoverhasharuntimePASS.

## Lacunas e gates

Todos testes afetados terao receiptatual. Native MT5/Safari/AT/toquefisico/pastareal impossiveis sem ambiente proprio ficam NOT_RUN. Pacote Genetrixintegro nao significa execucao nativa. Aceitefinal/integracao ainda separados. Source revision ehashcontrole serao congelados aposgeracao; mudancas materiais invalidam afetados.
