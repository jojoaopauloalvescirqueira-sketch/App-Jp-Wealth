# Nome do produto — 2026-09-17

Pedido: “Quero que voce mude isso para Jp Wealth Built on Method”.
N0-V/A2, texto de apresentação; não é migração de versão ou de dados.

## Contexto e fronteira

- Raiz: `/Users/joaopauloalves/.codex/nocuda-tools/20260917/product`.
- Branch existente: `codex/nocuda-tools-20260917`.
- Base/HEAD: `6ef8d7689130b8476c64fd90881e00050b2725e9`.
- Preexistentes preservados: README, ACTIVE-TASK, atalho, helper, teste e CHG
  LOCAL-LAUNCHER. Snapshot anterior em `tools/.artifacts/product-name/before`.
- O JP Wealth organiza finanças e gestão de risco locais. Esta tarefa altera
  somente sua identificação pública, atualmente dispersa no título HTML,
  marca legada, rodapé, Sobre e dois manifests de identidade visual.
- Nome desejado: **Jp Wealth Built on Method**; nome curto **Jp Wealth**;
  subtítulo **Built on Method**. A marca gráfica JP WEALTH continua existente.
- Consumidores: aba do navegador, metadados Apple/PWA, Configurações e portátil.
  O atalho conserva nome/caminho e origem fixa; entrega os arquivos da pasta
  principal, que só receberá este delta após integração.

Fontes: AGENTS/preflight; README/Início rápido; CONTEXT-MAP/Interface e PWA;
PROJECT-CONTEXT/Produto e contratos; CURRENT-STATE/fotografia histórica;
CHANGE-PROCESS/N0-V; index/header e settings/Sobre; manifests e gerador oficial.
Harness §§12–14 e 36–48, hash
`c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`.

Arquivos permitidos: index, settings-modal, manifests PWA, descrição package,
título README, metadado/hash do manifest JS, build-id e portátil gerados,
este CHG e nota em ACTIVE-TASK. Sem CSS, ícones, storage, migração, schema,
regra financeira, service worker, gates ou dependências novos/alterados.
Preservar package.name/version, versão de backup V9.1, nome técnico do portátil,
id/start_url/scope do PWA e ordem dos 94 scripts.

## Critério e recuperação

Verificar nome no título e em Sobre, ausência do nome antigo na apresentação,
nomes dos manifests e identidades estáveis. Rodar gate fast, contrato de marca,
smoke e conferência em desktop/mobile e temas claros/escuros com dados sintéticos.
Gerar portátil pelo builder oficial e verificar seu título/conteúdo.
Reversão: reaplicar somente os bytes do snapshot desta mudança e regenerar;
preservar pendências do launcher e todas as bases reais.

## Resultados

- Build `85531f89d1d01b68`, gerado por `python3 tools/rebuild_monolith.py`: PASS.
- `python3 tools/quality_gate.py --tier fast --artifact tools/.artifacts/product-name/fast.json`: PASS, 4 verificações.
- `python3 tools/brand_identity_contract_test.py`: PASS.
- `python3 tools/smoke_test.py`: PASS.
- `python3 tools/settings_modal_test.py`: PASS; log em `tools/.artifacts/product-name/settings.log`.
- Navegador interno via CUA, origem isolada `http://127.0.0.1:8872/index.html`:
  título e Sobre com nome exato; inspeção visual em 1440×1000 e 390×844,
  claro/escuro, nome inteiro e legível. Somente base vazia de teste.
- Comparação exata do portátil com o anterior mais substituições nome/build:
  PASS; nenhum delta adicional. Conferência de versões, ordem dos scripts e
  id/start_url/scope: PASS. Diff integral das fontes e `git diff --check`: PASS.
- Revisão independente: sem achados; launcher/helper/teste preservam hashes.
- Standard/full: NOT_RUN nesta alteração exclusivamente textual; falhas do
  standard anterior do launcher continuam registradas naquele CHG.
- Renomeação de instalações já existentes do PWA/Safari: NOT_RUN; nenhum
  armazenamento real, instalação ou atalho existente foi modificado nesta etapa.
- Commit, push e integração: não executados. O atalho principal ainda abre a
  versão integrada anterior. Esta prévia não implica atualização da main.

## Impacto agêntico

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED

BASIS: o título do README e o metadado project do manifest são representações
consumidas por agentes e agora usam o nome solicitado. ACTIVE-TASK aponta para
este registro e distingue a prévia da main. IMPACT focal: agentes, skills,
routing, registries, normas e arquitetura não mudam de comportamento ou fonte;
PROJECT-CONTEXT/CURRENT-STATE conservam fotografias datadas e identificadores
legados válidos. Nenhuma propagação de instruções, memória ou reindexação se
aplica. INDEX NOT REQUIRED. O escopo reconciliado é somente a nomeação local;
não há alegação de reconciliação global ou integração.
