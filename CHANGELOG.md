# Changelog

## [Unreleased]

### Planejamento FX — candidato de 2026-08-11 (branch `feature/fx-planning`)

- Nova área **Planejamento FX** na tela Contabilidade: motor de planejamento
  patrimonial temporal para Forex com três camadas separadas — planejado
  (premissas), realizado (histórico contábil) e normativo (reservas do
  Estatuto) — e três séries: baseline congelado, forecast vigente (rolling
  forecast a partir do último fechamento real) e realizado imutável.
- Convenções documentadas e testadas: rentabilidade sobre o saldo de abertura
  com aportes após o resultado; realizado com a mesma álgebra do MEI-JP
  (`R_aj = (V_t − V_{t−1} − F_t)/V_{t−1}`); precedência de overrides
  mês > ano > padrão; horizonte livre (1–600 meses) com meses gerados
  programaticamente.
- Ledger cambial de aportes com custo médio ponderado
  (`Σ BRL ÷ Σ USD`); entradas USD-nativas (`affectsFxCostBasis:false`) nunca
  contaminam o custo; aquisição, valuation e projeção cambial são conceitos
  separados.
- A matemática FCR/FEO foi extraída de `reserveCalc()` (onboarding) para a
  função pura compartilhada `reserveRequirementsCalc()`
  (`src/js/10-domain/07-reserve-requirements.js`), com caracterização campo a
  campo; onboarding e Planejamento FX consomem a mesma fonte — nenhuma
  constante normativa duplicada, nenhum artigo alterado.
- Novo agregado aditivo `S.fxPlanning` (schemaVersion 1) em
  `jpwealth_v9_state`: guarda estrutural em `migrate()`, normalização profunda
  em cópia na camada de acesso, campos desconhecidos preservados, trilha
  própria de auditoria (podada em 400) e integração com o changeLog da
  governança de backup. Backup antigo carrega sem perda; builds antigos
  preservam o agregado dormente.
- **Tela principal própria**: o Planejamento FX é a quinta área da navegação
  (`#fxplan`, mesma mecânica `.tab`/`data-screen` da rail, pílula, menu móvel e
  teclado das demais telas), por decisão do gestor pós-revisão — a
  Contabilidade voltou ao estado estrutural anterior, sem restos da feature. O
  contrato do smoke test passou de quatro para cinco telas operacionais.
- Interface em quatro modos internos (Visão Geral, Planejamento, Realizado, Tabela) com
  badges REAL/PREMISSA, gráfico baseline × projeção × realizado com transição
  histórico⇥projeção e alternância USD/BRL, barras de rentabilidade, painel de
  reservas com déficits, tabela mensal BASELINE × VIGENTE e resumo anual
  derivado das datas. Resumos textuais acompanham os SVGs.
- O manifest passou de 53 para 59 scripts (mesmo padrão de anexação do Galton);
  `fx_planning_test.py` entrou no tier `standard` (agora 8; `full` 18).
- A feature deriva conceitualmente da planilha `Planejamento FX.xlsx`, mas as
  inconsistências históricas do Excel (FUNDO FIIS ≠ FCR, reserva como % do
  patrimônio, coluna de aporte instável, taxa única de dólar, blocos anuais
  manuais) foram deliberadamente NÃO reproduzidas; fixtures são sintéticas.

### Galton Board — candidato local de 2026-08-11

- Adicionado `Configurações > Laboratório de Probabilidade > Galton Board`, com
  física rígida 2D real, placa triangular, Canvas HiDPI, controles acessíveis,
  histograma empírico, estatísticas e referência binomial condicional.
- Física separada do render por passo fixo de `1/120 s`; seed determinística atua
  somente no jitter de soltura e na tolerância fixa dos pinos. Corpos assentados são
  contabilizados uma vez, removidos e conservados apenas como agregados.
- Planck.js `1.5.0` foi vendorizado sob licença MIT, sem CDN ou dependência transitiva
  de runtime. Proveniência, integridade publicada e SHA-256 local ficam em
  `src/vendor/planck/README.md`; o validador fixa o hash do artefato.
- Criada a chave auxiliar `jpwealth_galton_preferences_v1` para preferências úteis.
  Ela não altera o schema financeiro, não persiste resultados e integra a limpeza de
  `Finalizar sessão` sem usar `localStorage.clear()`.
- O manifest passou de 46 para 53 scripts; o validador agora exige equivalência entre
  todos os scripts do manifest e o precache do service worker.
- Corrigidas duas falhas de baseline diretamente relacionadas à integração: o PWA
  não precacheava `12-nav-style.js` nem `17-economic-calendar.js`, e o modal de
  Configurações era recortado em `390 x 844` por uma regra tardia de padding.
- Adicionados `tools/galton_board_test.py` ao tier `standard` e o benchmark explícito
  de 10.000 bolas em `tools/galton_board_benchmark.py`. O core registrou 10.000
  assentamentos, zero expirações, um corpo estático final e pico de 240 corpos ativos;
  tempo e comparação binomial permanecem diagnósticos, sem gate ou fitting.
- Preferências ilegíveis, incompatíveis, de schema futuro ou com `localStorage`
  indisponível permanecem preservadas/bloqueadas em memória; a interface só volta a
  gravar após restauração explícita. O wipe entre abas invalida controladores montados
  para que a chave removida não seja recriada.
- A emissão com colisão bola-bola aguarda espaço físico no funil, evitando corpos
  sobrepostos. Configurações relacionam jitter/tolerância ao raio e ao clearance;
  vencimentos físicos remanescentes são comunicados e excluídos do histograma.
- A descoberta de nova versão PWA ocorre pelo bootstrap do próprio aplicativo, sem
  takeover: o worker espera todas as abas antigas fecharem e então o build novo abre
  online/offline. Manifest e precache incluem os 53 scripts.
- `build-id.js` e o HTML portátil foram atualizados pelo gerador oficial para o Build
  ID `dbca7e887edd287b`; o portátil tem SHA-256
  `038f9bf948aca9cec41bed34af4f130865f57c327b5f975216ea411f929bb416`.
- Suites focadas Galton, Settings, Finalizar sessão, upgrade PWA e reproducibilidade
  do build passaram no candidato consolidado. O gate `full` fechou `PASS 17/17`, sem
  falha de produto, harness, ambiente, baseline ou verificação omitida.
- Nenhuma regra N3, fórmula financeira, perfil, fase, limite, LIFO, DD ou
  contabilidade foi alterada. Commit, push, merge e publicação não foram executados.

### Em revisao
- Adicionados contexto em camadas, niveis de autoridade/risco, stop conditions, roteamento de skills e gates de evidencia para agentes.
- Criadas oito skills locais JP Wealth, templates de tarefa/auditoria/ADR e uma fotografia auditavel do estado atual.
- Adicionados preflight somente leitura, orquestrador de qualidade e fallback Chromium para validacao JavaScript quando Node nao estiver disponivel.
- Atualizadas expectativas comprovadamente obsoletas do harness para a navegacao, cabecalho, Central de Configuracoes e termo de Base de Dados atuais.
- Corrigidos `hidden`, alvos de toque, sobreposicao do inspetor e menu contextual das Notas; suite completa de Notas voltou a passar em desktop, mobile e portatil.
- Completado o precache do PWA e impedido que o HTML portatil tente registrar um service worker externo inexistente.
- Mensagem de falha de exportacao agora orienta contingencia manual para preservar os registros recentes.
- As correções N2 posteriores levaram o baseline `d9510dbb55f0` a `standard` 6/6 e o
  ciclo anterior a `full` 16/16; resultados antigos não provam o candidato Galton.
- Nenhuma fórmula financeira ou schema principal foi alterado nesse ciclo de
  governança; a feature atual adiciona somente a chave auxiliar isolada descrita
  acima.

## [9.1-db-storage-governance.1] — 2026-08-08

### Governança de armazenamento da base (JPW-HJFGDE)
- Adicionado o agregado `S.dataGovernance` (termo de responsabilidade, metadados da pasta padrão, sequência de exportação, backup confirmado e auditoria resumida), com migração sem perda para bases antigas e envelope do backup inalterado.
- Exportação da base reescrita como orquestração assíncrona: nomenclatura progressiva `JP_WEALTH_DB_NNNNNN_AAAA-MM-DD_HHmm.json`, sequência incrementada somente após sucesso confirmado, proteção física contra sobrescrita e diálogo explícito quando a pasta configurada está inacessível — nunca fallback silencioso para Downloads.
- Pasta padrão de exportação via File System Access API (Chrome/Edge desktop): handle persistido em IndexedDB, reautorização ao expirar, reassociação explícita após importação em outro dispositivo; navegadores sem suporte usam o download tradicional com a mesma nomenclatura e a interface declara a limitação.
- Nova etapa 07 "Base de Dados" no questionário de início: termo de responsabilidade obrigatório (sem ele a configuração não conclui) e configuração opcional da pasta.
- Central de Configurações ganhou o cartão "Armazenamento da Base": status da pasta, verificação de acesso, última exportação, próxima sequência, último backup confirmado e alterações desde então; aviso discreto após 30 dias sem backup confirmado.
- Estado sem base (limpeza total, Finalizar Sessão) passa a abrir sempre a tela inicial canônica `DEFAULT_START_ROUTE` e remove a autorização local da pasta junto com a base.
- Testes permanentes em `tools/storage_governance_test.py`; arquitetura documentada em `docs/architecture/DB-STORAGE-GOVERNANCE.md`.

## [9.1-settings-modal.1] — 2026-08-04

### Central de Configurações
- Transformada a antiga tela de Configurações em uma central modal dedicada, aberta pela engrenagem do cabeçalho sem trocar a tela operacional ao fundo.
- Reorganizados os controles existentes em Sobre, Aparência, Interface, Editor, Educacional, Estatuto Operacional, Parâmetros e Calibração e Backup e Recuperação, preservando os mesmos nós, listeners e persistência.
- Adicionada uma base educacional local, curta e pesquisável sobre Forex, glossário e perguntas frequentes; ela não contém sinais, previsões ou recomendações operacionais.
- Dados do Período agora são acessados por resumo seguro em Parâmetros e Calibração, com retorno ao onboarding existente em modo de edição.
- A central não grava em `S`, não altera o checkpoint de Finalizar Sessão e mantém a coordenação de foco ao abrir subdiálogos legados.
- Incluídos os módulos da central no precache existente do PWA, sem alterar sua estratégia de atualização.

## [9.1-header-actions.1] — 2026-08-04

### Navegação do cabeçalho
- Movidos os acessos de Configurações e Finalizar sessão para ações icônicas compactas no canto superior direito do cabeçalho.
- Mantida a numeração das áreas operacionais restantes e reutilizados os fluxos existentes de navegação e Finalizar Sessão.
- Nenhuma regra financeira, persistência, backup, limpeza ou comportamento interno de Finalizar Sessão foi alterado.

## [9.1-finalize-session.1] — 2026-08-03

### Privacidade e encerramento local
- Adicionado o fluxo modal `Finalizar sessão`, com checkpoint determinístico, exportação confirmada e confirmação textual `APAGAR TUDO`.
- Removidas somente as chaves locais do JP Wealth identificadas na auditoria, incluindo cópias corrompidas e preferências auxiliares; chaves de outras aplicações são preservadas.
- Criado estado em memória genuinamente vazio após a exclusão, sem nomes, contas, ordens, lançamentos ou credenciais anteriores.
- Mantido o formato do backup completo, a política existente de senhas de investidor e o comportamento do reset administrativo `Limpar todos os dados`.
- O fingerprint passou a incluir preço e data dos instrumentos; falsos positivos de atualização cambial são aceitos deliberadamente para priorizar a preservação de dados.
- Adicionado gate de persistência com geração de sessão, coordenação entre abas e proteção contra callbacks assíncronos após a exclusão.
- A limpeza de caches do service worker agora é limitada ao prefixo `jp-wealth-`.
- Nenhuma regra financeira, cálculo, perfil, matriz ou contabilidade foi alterada.

## [9.1-empty-state.1] — 2026-08-03

### Estado inicial e onboarding
- Removida a série demonstrativa de 2026 do acompanhamento mensal quando não existem fechamentos no ledger.
- Retorno acumulado e DD máximo permanecem vazios (`—`) até o primeiro fechamento diário; com ledger real, o cálculo existente é preservado.
- Substituídos os placeholders pessoais do onboarding por `Preencher nome` e reforçada a validação obrigatória dos nomes.
- Verificados inicialização sem estado salvo e os dois fluxos de limpeza sem alterar regras financeiras ou dados salvos existentes.

## [9.1-icons.1] — 2026-08-03

### PWA e identidade visual
- Criada biblioteca local com os temas `flat-knight`, `relief-knight` e `marble-knight`.
- Criado um manifesto PWA independente por tema, mantendo nome, modo e escopo do app.
- Adicionado service worker com precache versionado de scripts, manifestos e ícones.
- Adicionada seção `Ícone do app` em Configurações e modal acessível de escolha.
- Registrada a limitação real do Safari/iOS: trocar o ícone exige remover e adicionar novamente o atalho.
- Corrigido o binding antecipado de `wipeAllData` no boot e tornado o runner de smoke compatível com Chromium no macOS/Linux.
- Nenhuma regra financeira, persistência principal ou dado operacional foi alterado.

## [9.1-structured.1] — 2026-08-03

### Estrutura
- Preservado o HTML monolítico original e seu hash SHA-256.
- CSS extraído para `src/styles/app.css`.
- JavaScript separado pelas seções já existentes no código, sem reescrita de lógica.
- Criado `src/js/manifest.json` para fixar a ordem de execução.
- Criadas documentação de arquitetura, governança, recuperação e testes.
- Incluídos Estatuto e organograma em `docs/normative/`.
- Criados scripts de validação, smoke test e reconstrução do HTML portátil.

### Regras financeiras
- Nenhuma regra, constante ou fórmula financeira foi deliberadamente alterada nesta etapa.
