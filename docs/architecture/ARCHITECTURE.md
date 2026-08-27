# Arquitetura do sistema

## Visão geral

O JP Wealth Risk Terminal é uma aplicação web cliente, local-first e sem backend
obrigatório. O navegador carrega `index.html`, `src/styles/app.css` e 65 scripts
clássicos na ordem e com os hashes fixados por `src/js/manifest.json`. O estado
operacional é persistido localmente; artefatos portáteis e PWA são derivados das
mesmas fontes rastreadas.

Norma e domínio financeiro continuam separados das superfícies educacionais. Código
de simulação não ganha autoridade normativa por coexistir com o terminal.

## Camadas

### 1. Apresentação

- `index.html`
- `src/styles/app.css`
- `src/js/20-ui/`

### 2. Domínio financeiro e operacional

- `src/js/10-domain/`
- Perfis de risco, instrumentos, cálculo de risco, transições de fase, stops, corretoras e quarentena.

### 3. Contabilidade e estatística

- `src/js/30-accounting/`
- Fechamento diário, projeções, MEI-JP e simulação patrimonial.

### 4. Infraestrutura local

- `src/js/00-core/`
- Estado inicial, migrações, persistência e helpers.

### 5. Orquestração

- `src/js/40-app/`
- Navegação, tema, onboarding, Configurações, dashboards, reset, limpeza, boot e
  experiências educacionais isoladas.

### 6. PWA e identidade visual

- `assets/pwa-icon-primary.png` e `assets/pwa-icon-secondary.png` são as duas
  variantes locais de ícone.
- `manifests/jp-wealth.webmanifest` descreve o PWA.
- `src/js/40-app/06-app-icons.js` controla somente a preferência visual local entre
  as duas variantes e explica a limitação de instalação no iOS.
- `sw.js` faz precache dos scripts, estilos, manifesto e ícones. `CACHE_NAME` é
  derivado de `JP_WEALTH_BUILD_ID`, portanto muda com o conteúdo reconstruído.
- `tools/validate_project.py` compara todo script do manifest com o precache; a
  divergência é falha estrutural, não uma condição aceita para operação offline.

### 7. Laboratório de Probabilidade

- `src/js/40-app/18-galton-board/` contém configuração/geometry, PRNG, estatística,
  física, renderer e controller sob o namespace único `window.JPWGalton`.
- `src/vendor/planck/planck-1.5.0.min.js` é o build UMD oficial vendorizado do motor
  Planck.js, versão 1.5.0, licença MIT e SHA-256
  `69c6675a04121ec4042921b7d3d298058617d3211c243d8ea4d940a58af99974`.
- `src/js/40-app/09-settings-modal.js` oferece o caminho
  `Configurações > Laboratório de Probabilidade > Galton Board` e apenas coordena a
  montagem/pausa do controller.
- O mundo usa unidades normalizadas e passo fixo de `1/120 s`, separado do render.
  O default tem 10 linhas, espaçamento horizontal `1`, vertical `0.82`, raio de pino
  `0.09`, raio de bola `0.14`, densidade `1`, restituição `0.28`, atrito `0.22`,
  gravidade `9.81`, jitter de soltura `0.07`, tolerância de pinos `0` e colisão
  bola-bola desligada.
- A geometria possui chute superior, guias simétricas que acompanham o envelope
  triangular e abertura de soltura normalizada limitada ao corredor seguro. Uma
  placa de `N` linhas cria `N + 1` compartimentos.
- Aleatoriedade determinística atua somente na soltura e na tolerância fixa dos
  pinos; nenhuma decisão esquerda/direita é sorteada durante a trajetória.
- Canvas é projeção visual; controles, estatísticas e alternativa por compartimento
  permanecem em DOM acessível. O contrato completo está em `GALTON-BOARD.md`.

## Modelo de execução

A versão estruturada preserva scripts clássicos, não ES Modules. A ordem registrada
em `src/js/manifest.json` é parte do contrato de execução. Planck e os seis módulos do
Galton Board foram anexados ao fim da lista, sem reordenar os 46 scripts de baseline.
A separação reduz o tamanho de cada contexto para IA sem transformar incidentalmente
o escopo global legado em framework ou bundler.

## Persistência

- Chave principal: `jpwealth_v9_state`.
- Preferências auxiliares usam outras chaves locais.
- A preferência do ícone usa `jpwealth_v9_icon_choice` e não é misturada ao estado financeiro; `jpwealth_v9_icon_theme` é apenas uma chave legada removida pelos fluxos de limpeza.
- O Galton Board usa exclusivamente `jpwealth_galton_preferences_v1` para preferências
  úteis. Bolas, fila, histograma, estatísticas e estado intermediário nunca são
  persistidos; recarregar ou reabrir começa com a placa vazia.
- A chave do laboratório integra `JP_WEALTH_AUX_STORAGE_KEYS`: `Finalizar sessão` a
  remove, enquanto uma limpeza deliberadamente configurada com
  `removeAuxiliary:false` preserva preferências auxiliares.
- Falha de parse ou escrita da preferência fica contida no laboratório; não chama
  `save()`, não substitui `S`/`DEFAULTS` e não toca `jpwealth_v9_state`.
- `jpwealth_base_epoch_v1` é **control plane, não data plane**: identifica a
  GERAÇÃO da base. Sem PII, sem conteúdo financeiro, compartilhada entre abas.
  **Não** integra `JP_WEALTH_AUX_STORAGE_KEYS`, **não** entra em backup
  (`dgBuildBackupBlob` clona apenas `S`) e **não** é restaurada por importação —
  restaurar uma geração morta reabriria o replay que ela existe para fechar.
  Sobrevive a `Finalizar Sessão`; `wipeAllData` e a importação integral
  **rotacionam** seu valor, sempre ANTES da mutação destrutiva.
- Bootstrap determinístico: ausente ⇒ grava o sentinel reservado `BASE-V0-LEGACY`
  e relê. Todas as abas gravam o mesmo literal, então não há corrida de
  identidade. Rotações posteriores usam `crypto.randomUUID()`/`getRandomValues`,
  nunca `Date.now()` — relógio de parede não é monotônico e empata no mesmo
  milissegundo.
- Protocolo cross-tab: `jpwealth-session-finalized-v2` (versionado, **não**
  atravessa builds — o handler legado zerava `S.alladin`), `jpwealth-base-wiped`
  e `jpwealth-base-imported` (tipos inalterados, **devem** atravessar: ignorá-los
  deixaria uma aba operando sobre base que já não existe). Mensagem de geração
  diferente da corrente é recusada. Deduplicação operacional por `tipo:token`,
  limitada a 32 entradas em memória — não é mecanismo de segurança.
- Durante a janela mixed-build, `Finalizar Sessão` **não sincroniza entre
  protocolos**, por desenho. A garantia causal integral só existe quando todas as
  abas executam o protocolo novo.
- A função `migrate()` mantém compatibilidade entre schemas.
- O arquivo HTML ou o repositório não contém automaticamente o histórico real do navegador.

## Dependências e rede

- A atualização cambial usa a API Frankfurter. A aplicação deve continuar operando
  com os últimos preços salvos quando a rede estiver indisponível.
- O feed de notícias usa somente dados públicos documentados em `infra/ff-news-feed/`.
- Planck.js é uma dependência de runtime local, pinada e vendorizada; o laboratório
  não usa CDN, telemetria, credenciais, API financeira ou download em runtime.

## Fonte versus gerado

- Fontes editáveis: `index.html`, `src/`, `sw.js`, `manifests/`, `docs/`, `tools/`.
- Gerados: `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`.
- O único fluxo autorizado para os gerados é `tools/rebuild_monolith.py`; uma mudança
  de fonte invalida evidência anterior do portátil até o rebuild e o teste de
  reprodutibilidade.

## Limite desta etapa

A arquitetura financeira não foi convertida em módulos encapsulados. A modularização
real deve ocorrer gradualmente, com testes de caracterização por domínio e sem
misturar refatoração com mudança normativa. O Galton Board é uma feature N1/N2
delimitada e não resolve nem altera as dez pendências N3 registradas em
`CURRENT-STATE.md`.
