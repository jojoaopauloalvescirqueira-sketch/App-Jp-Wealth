# CHG — transparência dos ícones PWA

- **Data / solicitante:** 2026-09-16 / proprietário do JP Wealth.
- **Raiz / branch / base:** `/Users/joaopauloalves/.codex/pwa-icon-transparency/20260916/product`; `codex/pwa-icon-transparency-20260916`; `b3a84e3eee8d9b62e7576e1083ee3fd213e3b321`.
- **Autoridade:** o proprietário aprovou o plano e ordenou sua implementação. O plano autoriza branch/worktree isoladas, edição dos assets, manifestos, cache, testes, documentação e rebuild oficial. Commit, push, merge e publicação permanecem sem autorização nesta tarefa.
- **Risco:** N0-V nos pixels; N1 no manifesto/seleção; N3/A4 somente no control plane necessário para atualizar precache, fingerprint e validação, já delimitado pelo plano aprovado.

## Síntese de compreensão

1. **Finalidade:** o JP Wealth é uma aplicação financeira local-first; esta tarefa corrige a apresentação da identidade instalada sem tocar no domínio financeiro.
2. **Responsabilidade:** os PNGs representam a marca; os manifestos escolhem os tamanhos instaláveis; `06-app-icons.js` alterna a variante; `sw.js` mantém o conjunto coerente offline; rebuild/validador vinculam o artefato ao build.
3. **Comportamento:** as matrizes de 1254 px eram RGB opacas e continham uma placa branca/cinza. Depois, os cantos são transparentes, o quadrado vermelho/preto e o lettering permanecem, e os manifestos oferecem 192/512 px.
4. **Impacto:** favicon, Apple icon, instalação futura, cache PWA, versão portátil, fingerprint e testes de identidade. A identidade `id/start_url/scope` e a preferência `jpwealth_v9_icon_choice` permanecem.
5. **Limites:** nenhuma regra financeira, persistência, schema, backup, credencial, rota ou política de ativação do worker. Sem `skipWaiting`; sem edição manual de `dist/`; sem moldura, fundo ou halo incorporado.
6. **Evidência:** inspeção RGBA, cantos alfa zero, centro opaco, ausência de halo claro, dimensões reais/declaradas, troca de variante no Chromium, precache, offline/rebuild e gates aplicáveis.

## Fontes e contratos

| Fonte | Revisão/trecho | Fato sustentado |
|---|---|---|
| `AGENTS.md` | base `b3a84e3`, seções PWA/Git | worker conservador, gerador oficial e gates separados |
| `README.md` | base `b3a84e3`, PWA e distribuição | variantes Vermelho/Preto e `dist/` derivado |
| `docs/architecture/PWA-UPDATE-LIFECYCLE.md` | base `b3a84e3` | bump conjunto de cache e rebuild |
| `assets/pwa-icon-primary.png`, `assets/pwa-icon-secondary.png` | `sips`: 1254 × 1254, `hasAlpha: no` | causa observada: fundo incorporado aos PNGs RGB |
| captura fornecida pelo proprietário | 2026-09-16 | placa branca visível no ícone reduzido |

## Implementação, segurança e recuperação

A matriz preserva os pixels internos originais. A área externa conectada foi removida, o limite foi recuado para eliminar o halo claro e o canal alfa recebeu antialiasing. Exports 192/512 derivam da matriz; ambos os manifestos declaram `purpose: any`. Uma variante `maskable` opaca foi deliberadamente descartada porque recolocaria um fundo externo contrário ao pedido; launchers ainda podem aplicar máscara/placa própria que o aplicativo não controla.

Os testes usam somente assets públicos e dados sintéticos. Rollback restaura os seis PNGs, os dois manifestos, links/versionamento, testes/documentação e executa o gerador oficial novamente. Nenhum dado do usuário exige migração ou recuperação.

## Critérios

- PNG RGBA 8-bit; quatro cantos transparentes; centro opaco; nenhuma borda parcial quase branca.
- 192/512 reais e iguais ao manifesto; Vermelho/Preto com mesma identidade PWA.
- troca de favicon/Apple/manifesto preservada; todos os assets no precache versionado.
- rebuild reproduzível; focais de marca e validação aprovados; revisão visual em fundos claro/escuro e tamanho pequeno.
- aceite manual, Git e publicação continuam posteriores.

## Evidência final e auditoria

- `brand_identity_contract_test.py`: **PASS** — seis PNGs RGBA, dimensões, transparência dos cantos, centro opaco, ausência de halo e precache.
- `brand_identity_browser_test.py`: **PASS** — Vermelho/Preto atualizam favicon, Apple icon e manifesto sem reload.
- `profile_gallery_test.py`: **PASS** — modular, portátil e offline após atualização do nome do recurso permitido.
- `build_reproducibility_test.py`: **PASS** — build canônico `a3c585de3fe49edb`, novos exports incluídos no fingerprint.
- `service_worker_upgrade_test.py`: **PASS** — waiting conservador, duas abas, build íntegro e abertura offline.
- `quality_gate.py --tier full`: **55 PASS**, **2 PRODUCT_FAIL**, nenhum `TEST_HARNESS_FAIL`, `ENVIRONMENT_ERROR` ou `NOT_RUN`. As duas falhas foram reproduzidas sem este delta na `main@b3a84e3`: MIME `application/octet-stream` no teste documental e `tarfile.extractall(filter=...)` indisponível no Python 3.9 no teste-base do Alladin. São limitações preexistentes do ambiente/oráculo, não regressões do candidate.
- Prancha em `/Users/joaopauloalves/.codex/pwa-icon-transparency/20260916/evidence/pwa-icons-light-dark.png`; relatórios JSON no mesmo diretório.

**AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED**

**BASIS:** o delta altera o inventário PWA, os inputs do fingerprint e os contratos estruturais que validadores e futuros agentes usam. O universo examinado incluiu `AGENTS.md`, skills/roteamento, contexto operacional, arquitetura, manifestos, índice de hashes, gerador e memória. `ACTIVE-TASK.md`, `ARCHITECTURE.md`, o ciclo PWA, `src/js/manifest.json`, gerador e validadores foram reconciliados com os novos assets. Autoridade, routing, agentes, skills, normas financeiras, memória e indexação externa ficaram `NOT_AFFECTED`; não existe reindexação aplicável. Nova revisão material: sim, limitada à apresentação/contrato de assets PWA. Estado: `SYSTEM RECONCILED` para o candidate local.
