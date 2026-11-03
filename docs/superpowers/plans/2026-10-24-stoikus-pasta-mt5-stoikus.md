# Stoikus — fundação da próxima versão: pasta, regras, documentação e testes — plano

> **Para agentes:** plano aprovado como direção em 24/10/2026; **não autoriza execução**. Antes de qualquer frente abaixo: CHG próprio, autorização do proprietário no nível indicado, branch nova autorizada e preflight. Usar `repository-architecture` (modo MIGRATION), `jpw-change-control` e, para o AGENTS.md, `agentic-evolution-governance`.

**Objetivo:** preparar o Stoikus para desenvolvimento contínuo como projeto MT5 independente, sem alterar comportamento, cálculo ou dados. Quatro frentes:

1. Renomear a pasta `mt5/jpw-alavancagem-atual/` para `mt5/stoikus/`.
2. Reescrever o `AGENTS.md` local com o mapa atual.
3. Separar o README atual do histórico.
4. Dar uma pasta própria aos testes e ferramentas host do Stoikus.

**Decisões do proprietário (24/10/2026):**
- Opção A para a pasta: a renomeação é o **primeiro passo da próxima versão do Stoikus** (sucessora de 1.23.0/C5), executado **depois do teste nativo manual do C5** pelo proprietário. O caminho público `downloads/jpw-alavancagem-atual/` permanece.
- As frentes 2, 3 e 4 entram na mesma versão.

**Origem das frentes 2–4:** auditoria somente leitura de 24/10/2026 sobre o main `a4bf278`, resumida na seção Achados.

## Por que tudo na próxima versão

O nome da pasta faz parte da identidade da versão. Em `tools/build_leverage_package.py`, `stamp_source_build` calcula o `JPW_BUILD_ID` sobre o caminho completo de cada fonte (`relative.encode()`, com `PRODUCT = "mt5/jpw-alavancagem-atual/"`) e grava o resultado em `MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh`. Renomear muda esse fonte MQL, o build `406f16e7265f93dbd76f1c2b063090fa05520fdafc4322ca13ab5e0e0ae82161` e o fingerprint `26473298967abb055d077c3cc440cab1efc9f92e5e8f54f06bcc30ef2dc8f347`; o contrato do C5 passa a rejeitar a geração. O kit nativo `Kit_Windows_Stoikus_Painel_C5_D1.zip` também usa o caminho como chave (`source-freeze-R5.json`, 142 chaves; `Compile-Stoikus-UI.ps1`, linha 114) e deixaria de corresponder ao repositório durante o teste manual. A opção B (prefixo de identidade fixo nos geradores, para preservar o C5) foi recusada.

`AGENTS.md`, `README.md` e os `GENETRIX_*.md` estão em `sourceFiles` do manifesto e dentro do ZIP de fontes selado do C5 (inventário SDK 142 / uso 89). Editá-los ou movê-los no C5 quebraria a reprodutibilidade do pacote aprovado. Numa versão nova, build, inventários, pacotes e pins são recalculados de qualquer forma.

**Proteção até lá (fora deste plano, proposta):** aviso no `docs/governance/CONTEXT-MAP.md` da raiz de que o mapa ativo do `AGENTS.md` local está desatualizado. A raiz não entra no ZIP do Stoikus.

## Achados da auditoria de 24/10/2026

| Prioridade | Achado | Evidência |
|---|---|---|
| P0 | `AGENTS.md` local quatro versões atrás | Abre com "Mapa ativo — GENETRIX 1.20.0"; última alteração `f4b84b7` (1.20); cita `JPW_Genetrix_Monitor` e `JPW_Genetrix_Supervisor`, renomeados para `JPW_Stoikus_*` na 1.22.0; lista de testes host só com `leverage_*` |
| P1 | Estado atual enterrado no histórico | `README.md` com 1.403 linhas e 51 títulos, só os primeiros sobre o C5; 10 `GENETRIX_*.md` históricos na raiz da pasta |
| P1 | Testes do Stoikus fora do Stoikus | 91 arquivos em `tools/` (testes, juízes, executores host, geradores, fixtures), misturados aos 324 do app web |
| P1 | Sem rotina de prova nativa | Compilação MetaEditor e os 24 scripts `*_Tests.mq5` NOT_RUN no C5 |
| P2 | Manutenção | Prefixos `JPW_Alavancagem_*` e `JPW_Stoikus_*` misturados, 76 includes planos; `JPW_Alavancagem_Presentation.mqh` 2.362 linhas, `JPW_Alavancagem_Coordinator.mqh` 1.895; manual MQL5 curado (`docs/knowledge/stoikus-mql5-curated/`) sem link; status do harness "1.0.0 candidato" ambíguo |

A prova nativa e os itens P2 ficam fora deste plano. Prefixos e divisão de arquivos mexem em `#include` e no código, e pedem projeto próprio.

## Restrições globais

- Somente estrutura física, referências de caminho e documentação. Fórmulas, cálculo 1.9.0, schemas, stores, preferências, oráculos e expectativas de teste não mudam; trocar caminho não pode enfraquecer nenhuma verificação.
- `downloads/jpw-alavancagem-atual/`, os 18 ZIPs publicados, as prévias e os root-pins históricos permanecem byte a byte. Os ZIPs já retiram o prefixo da pasta (caminhos internos começam em `AGENTS.md`).
- Registros históricos mantêm o nome antigo: `docs/validation/**`, `docs/work/**`, `CHANGELOG.md` e `docs/knowledge/**` (edição congelada; ver Frente 1, Tarefa 1.5).
- Artefatos gerados (`manifest.json`, `build-id.js`, `src/vendor/downloads/*-payload.*`, `dist/`) só pelos geradores oficiais; nunca edição manual.
- `git mv` para toda movimentação. Nenhuma exclusão: histórico vai para `historico/`.
- Commit, push, PR e merge exigem autorização própria, frente a frente.
- Compilação MetaEditor e execução MT5 continuam provas separadas; NOT_RUN não vira PASS.

## Classificação e ordem

| Frente | Risco | Autorização | Ordem |
|---|---|---|---|
| 1. Pasta `mt5/stoikus` | N3 (geradores, distribuição, testes) | A4 | 1ª |
| 4. Pasta de testes | N3 (testes, runner, gate, CI) | A4 | 2ª |
| 3. README atual/histórico | N0-D, mas muda o inventário do pacote | A2 + aceite do novo inventário | 3ª |
| 2. AGENTS.md | N3 control plane (instruções) | A4, auditoria independente | 4ª |

Uma frente por commit, cada uma com baseline e verificação próprias. O AGENTS.md vem por último porque descreve o estado final: pasta, testes e documentos já no lugar. O candidate de instruções não pode ampliar a autoridade do próprio executor.

## Pré-condições

- [ ] Teste nativo manual do C5 concluído pelo proprietário, com resultado registrado.
- [ ] Decisão de escopo `docs/decisions/2026-10-22-stoikus-escopo-projeto-independente.md` integrada ao main. Em 24/10 ela existe só na branch `codex/stoikus-delimitacao-20261022`, commit `a0c1005`.
- [ ] Próxima versão definida (número, revisão e escopo) e CHG da versão aberto.
- [ ] CHG desta fundação, autorizações por frente e branch nova a partir do main.
- [ ] Preflight `--mode edit` PASS; árvore limpa; BASE_SHA registrado.

## Baseline comum

- [ ] `python3 tools/leverage_suite.py --scope all --artifact docs/validation/<pasta-da-versao>/before/mt5-all.json` (Python com `requirements-dev.txt`; referência: 62 PASS em 24/10, [recibo](../../validation/stoikus-mt5-all-20261024/)).
- [ ] `python3 tools/quality_gate.py --tier full`, registrando os resultados brutos.
- [ ] Hashes dos 18 ZIPs, prévias e root-pins.
- [ ] Inventário `git grep -l "mt5/jpw-alavancagem-atual"`: em 24/10 eram 77 arquivos fora de `docs/` e 316 no total.

## Frente 1 — Renomear para `mt5/stoikus`

- [ ] **1.1** `git mv mt5/jpw-alavancagem-atual mt5/stoikus`; `git status` só com renomeações (similaridade 100%).
- [ ] **1.2 Geradores:** trocar só o valor da constante de prefixo em `tools/build_leverage_package.py` (`PRODUCT`), `tools/build_stoikus_window_native_kit.py` (`PREFIX`), `tools/build_stoikus_interface_kit.py` e `tools/render_stoikus_brand.py`.
- [ ] **1.3 Executores host:** `tools/leverage_host_layout.py`, `tools/leverage_host_runtime.py`, `tools/stoikus_window_host.py`, `tools/stoikus_window_nocuda_host.py` e `tools/leverage_suite.py`. O próximo kit nativo usa `mt5/stoikus/` nas chaves do freeze e no `Compile-Stoikus-UI.ps1`; o kit C5-D1 continua como está.
- [ ] **1.4 Testes:** cerca de 60 em `tools/` (maior: `leverage_package_test.py`, 88 referências), trocando somente o caminho. Os arquivos que só citam downloads não mudam: `.gitignore`, `sw.js`, `src/js/20-ui/31-tools-services.js`, `tools/rebuild_monolith.py`, `tools/stoikus-installer/prepare_payload.py`, `tools/local_launcher_test.py`, `tools/stoikus_daily_package_test.py`, `tools/stoikus_download_test.js`, `tools/stoikus_installer_test.py` e `tools/stoikus_interface_delivery_test.py`. Testes de pacotes históricos continuam exigindo os bytes antigos.
- [ ] **1.5 Proveniência e documentos vigentes:** `assets/stoikus/raster-provenance.json` (8 BMP), `tools/regression-memory.json` (`source.path` das entradas vigentes; evidências antigas mantêm o caminho), `README.md` da raiz (3), `docs/governance/CONTEXT-MAP.md` (9), o campo Localização da decisão de escopo e `mt5/stoikus/harness/REPOSITORY_INTEGRATION.md`. `docs/knowledge/stoikus*` (cerca de 230 referências) fica como histórico, com nota no CONTEXT-MAP; confirmar com o proprietário.
- [ ] **1.6 Regenerar:** `tools/build_leverage_package.py` para a nova versão (novo `JPW_BUILD_ID`, fingerprint, pacotes e pins, como identidade da versão nova); `tools/rebuild_monolith.py` quando aplicável.
- [ ] **1.7 Verificar:** `git grep` do caminho antigo só nos históricos aprovados; MT5-all e FULL sem regressão; ZIPs e pins históricos idênticos.

## Frente 4 — Pasta própria para os testes do Stoikus

**Destino proposto: `tools/stoikus/`.** Os testes são ferramentas host em Python/Node, rodadas pelo `leverage_suite.py`, pelo gate e pelo CI. Ficam na área de tooling do repositório, separados do app web, e fora de `mt5/stoikus/`, cujo conteúdo é distribuído aos usuários. Os testes MQL5 `*_Tests.mq5` continuam em `mt5/stoikus/MQL5/Scripts/JPWealth/`, porque rodam no MT5. Alternativa: `mt5/stoikus/tests/`, que exige garantir a exclusão dos pacotes; decidir no CHG.

- [ ] **4.1 Inventário exato:** 91 arquivos em `tools/` com prefixos `leverage_`, `stoikus`, `jpw_stoikus_`, `jpw_nocuda_`, `jpw_personal_`, `jpw_signal_`, `jpw_positions_`, `jpw_mt5_`, `core_`, `build_leverage_`, `build_stoikus_`, `render_stoikus_` e `personal_history_`. Inclui testes, juízes, executores (`leverage_host_*`, `leverage_source.py`, `stoikus_window_host.py`), geradores, fixtures (`stoikus_hud_fixture/`, `stoikus_panels_fixture/`, `personal_history_host/`) e o instalador (`stoikus-installer/`). Classificar um a um; o que é compartilhado com o app web fica em `tools/`.
- [ ] **4.2 Mover** com `git mv` o conjunto inteiro de uma vez. Os testes importam módulos vizinhos (por exemplo `from leverage_source import expanded_source`); manter o grupo junto preserva esses imports.
- [ ] **4.3 Ajustar a raiz do repositório:** 69 dos arquivos montam caminhos com `Path(__file__).parents[1]`, `parent.parent`, `../` ou `tools/`. Trocar para a nova profundidade, sem mudar asserções.
- [ ] **4.4 Chamadores:** `tools/leverage_suite.py` (`HOST`, `HOST_VARIANTS`, `DISTRIBUTION`, `ROOT / "tools"`), `tools/quality_gate.py` (`stoikus-downloads`), `.github/workflows/mt5-host.yml` (linhas 36 e 38), `protection.path` em `tools/regression-memory.json` (validado por `tools/jp_engineering_integration_test.py`) e as rotas de teste no AGENTS da raiz, se houver.
- [ ] **4.5 Verificar:** a suíte MT5-all roda o mesmo número de verificações da baseline, com os mesmos nomes, todas PASS; FULL sem regressão; integração JP Engenharia PASS; nenhum `tools/<arquivo movido>` remanescente fora dos históricos.

## Frente 3 — README atual e histórico separados

- [ ] **3.1 Criar `mt5/stoikus/historico/`** e mover para lá, com `git mv`, os 10 `GENETRIX_*.md` e `STOIKUS_RENAME_1_22_0.md`.
- [ ] **3.2 README em dois:** `mt5/stoikus/historico/README-ANTERIOR.md` recebe o README atual integral, byte a byte. O novo `mt5/stoikus/README.md` fica curto e atual: o que é o Stoikus, os programas e onde instalar cada um, versão vigente, como testar (host e nativo), onde está o guia de uso (`STOIKUS_USO_DIARIO.md`) e link para o histórico.
- [ ] **3.3 Inventário do pacote:** o SDK e o pacote de uso mudam de inventário (C5: SDK 142 / uso 89). Os novos números entram como identidade da versão nova, com aceite explícito; testes de inventário são atualizados para a versão nova sem afrouxar a regra de inventário exato.
- [ ] **3.4 Links:** atualizar os links para os arquivos movidos nos documentos vigentes; históricos não mudam.

## Frente 2 — Reescrever o `AGENTS.md` local

N3 de control plane: CHG dedicado, comparação antes/depois, auditoria independente e aceite humano. Não misturar com mudança de produto no mesmo commit.

- [ ] **2.1 Preservar:** `git mv` do arquivo atual para `mt5/stoikus/historico/AGENTS-ANTERIOR.md`, byte a byte.
- [ ] **2.2 Novo `mt5/stoikus/AGENTS.md`** com:
  - subordinação às regras do repositório, ao Estatuto e à autoridade humana, sem conceder permissões;
  - mapa atual dos programas: Monitor (`JPW_Stoikus_Monitor`, observador, não negocia), Conta (`JPW_Alavancagem_Atual`), NoCuda (`JPW_NoCuda_Channels`), Abrir Painéis (`JPW_Stoikus_Abrir_Paineis`), Supervisor opcional (`JPW_Stoikus_Supervisor`) e produtores legados (Observer, Accountant), conferidos contra os fontes reais;
  - a seção "Invariantes de cálculo e unidades" copiada **sem alteração** do arquivo anterior, com conferência de bytes; qualquer mudança nela é N3 financeiro e sai deste plano;
  - fronteiras de persistência, preservadas do arquivo anterior;
  - rotas de teste reais: `leverage_suite.py --scope all`, a pasta da Frente 4 e os scripts `*_Tests.mq5`;
  - prova nativa: MetaEditor x64, MT5 isolado, conta demo; NOT_RUN sem ambiente;
  - distribuição pelos geradores oficiais e o caminho público de downloads;
  - links para o README, o histórico, o guia de uso, o harness e o manual MQL5 curado (`docs/knowledge/stoikus-mql5-curated/`).
- [ ] **2.3 Status do harness:** o arquivo se declara "1.0.0 candidato". Decidir com o proprietário se está ativo, candidato ou histórico; o AGENTS registra a decisão e não a presume.
- [ ] **2.4 Verificar:** todo nome de programa e arquivo citado existe; todo link resolve; a seção de invariantes é idêntica; auditoria independente compara antes e depois e procura permissão ampliada.

## Rollback

Cada frente tem seu próprio commit. Antes do commit: descartar a branch. Depois: reverter o commit da frente; `git mv` preserva o histórico. Nenhum dado de uso é afetado: preferências, estudos e históricos ficam no terminal MT5, não no repositório.

## Critérios de aceite

- `mt5/stoikus/` contém os arquivos da pasta antiga com os mesmos bytes, exceto o `JPW_BUILD_ID` gerado e os documentos das Frentes 2 e 3; o histórico está em `historico/`, sem exclusões.
- Testes e ferramentas host do Stoikus em uma pasta própria, com o mesmo número e nome de verificações da baseline.
- Downloads públicos, ZIPs e pins históricos inalterados.
- MT5-all e FULL sem regressão em relação à baseline.
- `AGENTS.md` descreve só programas, testes e caminhos que existem; invariantes de cálculo idênticas; auditoria independente e aceite humano registrados.
- Nenhuma referência ativa a caminho antigo fora da lista histórica aprovada.
