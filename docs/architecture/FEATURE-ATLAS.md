# JP Feature Atlas — piloto descritivo

> Integração do catálogo parcial autorizada com pendências: [registro](../work/ATLAS-V4-INTEGRATION-20260910.md). A proveniência/autoria histórica abaixo é preservada; não representa estado novo de validação ou fechamento de AUD-05/P2.

Este catálogo descreve capacidades e relações; não é fonte normativa, autorização, instalação aceita ou homologação financeira. Fonte editável única: este Markdown. Os blocos atlas-json são os metadados/arestas de cada ficha; tabelas e fluxos em prosa apenas os explicam, sem cadastro paralelo. Não há índice vetorial, grafo derivado ou consulta Graphify nesta autoria.

Base de produto: **484228189cc3f5f4c297f29f88f2b2ed541a3afd**, build **88c0cb1ce5520311**. Instruções de base: V4 experimental **5ca9e046a4c75a5bfe3da9b5d1f11b259d88cdd33ee4a56372601c99e2035642**, ainda não aceita; **AUD-05/P2 continua aberto**. Os hashes por fonte abaixo identificam os bytes inspecionados na cópia. Data da leitura: 2026-09-10 UTC (2026-09-09 local). Contrato do piloto: [FEATURE-ATLAS-PILOT](../work/FEATURE-ATLAS-PILOT.md); contexto do produto: [PROJECT-CONTEXT](../governance/PROJECT-CONTEXT.md); localização: [CODE-MAP](CODE-MAP.md).

**Evidência desta autoria: inspeção de código/documentos, sem execução de runtime, teste de navegador, gravação operacional ou consulta de rede.** Os resultados futuros serão registrados fora de docs, no diretório evidence do piloto, ligados ao candidate e ao comando realmente executados; sua existência ou aprovação não é presumida aqui. Gabaritos independentes e perguntas reservadas não foram lidos. O texto não substitui os arquivos originais; confirme fonte/hash antes de implementar.

## Inventário preliminar e cobertura

Denominador: **27 famílias identificadas no diagnóstico**, agrupamento funcional proposto, não universo exaustivo de todos os caminhos do software. Cruzamento inicial: mapa de código/manifest, responsabilidades/navegação documentadas e, nas três fichas, handlers, domínio, persistência e consumidores diretamente inspecionados. **3/27 famílias possuem ficha A–H; 24/27 aguardam aprofundamento; 0/27 foram observadas/testadas em runtime por esta autoria.** Três fichas foram inspecionadas para os hashes registrados, ainda aguardam validação independente. As quatro áreas-placeholder de Research ficam fora desse denominador e listadas separadamente. Não contar atalhos de uma mesma feature como novas capacidades.

IDs JPW-FEAT são propostas estáveis do Atlas, sem renomeação no runtime. Nesta tabela, “identificada” é apenas inventário preliminar; não representa cada comportamento validado. Rótulos têm três eixos: implementação (available/partial/internal/disabled/placeholder/proposed), evidência (declared/code-inspected/observed/tested), frescor (verified-for-revision/needs-review/historical). O frescor verificado das fichas é documental/estático, não prova de execução.

| ID | Responsabilidade | Família | Cobertura desta autoria |
|---|---|---|---|
| JPW-FEAT-0004 | Dashboard | Síntese dos módulos | Identificada; ficha pendente |
| JPW-FEAT-0005 | Dashboard | Status do sistema | Identificada; ficha pendente |
| JPW-FEAT-0006 | Forex | Preparação e conta | Identificada; ficha pendente |
| JPW-FEAT-0007 | Forex | Ordens e risco | Identificada; ficha pendente |
| JPW-FEAT-0008 | Forex | Cálculo de lote | Identificada; ficha pendente |
| JPW-FEAT-0009 | Forex | Apuração | Identificada; ficha pendente |
| JPW-FEAT-0010 | Forex | Finalização e histórico | Identificada; ficha pendente |
| JPW-FEAT-0011 | Forex | Planejamento FX | Identificada; ficha pendente |
| JPW-FEAT-0012 | Finanças Pessoais | Orçamento | Identificada; ficha pendente |
| JPW-FEAT-0013 | Finanças Pessoais | Dívidas e crédito | Identificada; ficha pendente |
| JPW-FEAT-0014 | Finanças Pessoais | Comparações | Identificada; ficha pendente |
| JPW-FEAT-0015 | Finanças Pessoais | Cenários | Identificada; ficha pendente |
| JPW-FEAT-0016 | Finanças Pessoais | Visão consolidada | Identificada; ficha pendente |
| JPW-FEAT-0003 | Research | NoCoda | [Ficha 0003](#jpw-feat-0003); code-inspected |
| JPW-FEAT-0017 | Research | Pivots | Identificada; consumidor do catálogo inspecionado, ficha pendente |
| JPW-FEAT-0018 | Alladin | Cadastros | Identificada; ficha pendente |
| JPW-FEAT-0002 | Alladin | Lançamentos e estornos | [Ficha 0002](#jpw-feat-0002); code-inspected |
| JPW-FEAT-0019 | Alladin | Saldos de caixa | Identificada; consumidor inspecionado, ficha pendente |
| JPW-FEAT-0020 | Alladin | Posições por quantidade | Identificada; consumidor inspecionado, ficha pendente |
| JPW-FEAT-0001 | Transversal | Calendário Econômico | [Ficha 0001](#jpw-feat-0001); code-inspected |
| JPW-FEAT-0021 | Transversal | Navegação contextual | Identificada; ficha pendente |
| JPW-FEAT-0022 | Transversal | Preferências e editor | Identificada; ficha pendente |
| JPW-FEAT-0023 | Transversal | Backup, importação e recuperação | Identificada; ficha pendente |
| JPW-FEAT-0024 | Transversal | Notas/Tickets | Identificada; ficha pendente |
| JPW-FEAT-0025 | Transversal | Consulta educacional e normativa | Identificada; ficha pendente |
| JPW-FEAT-0026 | Transversal | Galton Board | Identificada; ficha pendente |
| JPW-FEAT-0027 | Transversal | Offline e atualização PWA | Identificada; ficha pendente |

Totais por grupo: Dashboard 2; Forex 6; Finanças Pessoais 5; Research 2; Alladin 4; transversais 8. Calendário pertence a uma única família transversal apesar de seus acessos por módulos. NoCoda e Pivots permanecem features distintas que compartilham identidade de instrumento.

| Área Research separada | Estado de implementação | Evidência/frescor |
|---|---|---|
| Ações · B3 (stocks-br) | placeholder, sem conteúdo publicado | Rotas RESEARCH_VIEWS e texto de dmResearchHTML inspecionados nesta revisão |
| Stocks (stocks-global) | placeholder, sem conteúdo publicado | Mesmas fontes; não comprova pesquisa de ações implementada |
| REITs (reits) | placeholder, sem conteúdo publicado | Mesmas fontes |
| Others (others) | placeholder, sem conteúdo publicado | Mesmas fontes |

Exclusões: nenhuma auditoria financeira integral/V11, conta real, histórico operacional, segredo, backup privado, serviço econômico acessado ou completude do grafo. Integrações não encontradas no recorte não viram prova universal de ausência. A ampliação do inventário deve cruzar atos, persistência, boot/timers e testes pertinentes, além do menu.

## Como consultar e manter

Do usuário ao código: escolha ID/família, leia A–D e siga F/metadados. Do componente ao impacto: busque neste arquivo seu caminho ou símbolo; confira todos os endpoints origin/target e condições das fichas encontradas. A relação é direcionada: ler resultado não é gravar o produtor; dois consumidores não provam comunicação entre si. Os blocos abaixo registram relações reconstruídas por leitura, não traces de execução.

Uma mudança em fonte/hash, contrato, identidade ou consumidor material marca a ficha needs-review até cotejo direto; renomeação não equivale à remoção da capacidade. Não reescrever automaticamente o Atlas ou seus índices. Sugestão é proposta, não tarefa aprovada. Se índice estiver ausente, use busca textual e leitura dos originais; não invoque Graphify nem reconstrua caches. A revisão documental não substitui CURRENT-STATE/handoff e não fecha AUD-05.

<a id="jpw-feat-0001"></a>
## JPW-FEAT-0001 — Calendário Econômico compartilhado

### A. Identidade e finalidade

Oferecer eventos públicos de alto impacto como contexto informativo ao proprietário, sem emitir sinal ou autorizar operação. Acesso pelo widget em Forex/Visão Geral e seu modal, pelo workspace Research/Calendário e pela síntese Research do Dashboard. Há um pipeline/cache e um renderizador de agenda com duas raízes; essas superfícies não são calendários independentes. Comentários antigos que dizem “widget do Dashboard” não redefinem a localização reconciliada em CODE-MAP.

### B. Funcionamento atual — reconstrução estática

Fluxo: necessidade de contexto → abertura/seleção de agenda → leitura do cache validado → filtro/ordenação → renderização segura → eventos, ausência de dados ou vazio verdadeiro. Em paralelo, o domínio do feed decide a revalidação → fetch → validação → tentativa de cache → repintura comum.

- initFfNewsDomain instala listener online, ciclo de 5 minutos e tique de 1 minuto, repinta e chama ffNewsFetch(false) no carregamento. O ciclo de 5 minutos só solicita fetch com aba visível; o de 1 minuto só repinta. Intervalo de consulta não é idade máxima do cache.
- openEconomicCalendar chama ffNewsFetch(false); **researchSelectView('calendar') chama apenas o renderizador do workspace**, sem fetch próprio. Assim, selecionar Research não implica consulta imediata; o domínio compartilhado continua responsável por boot/poll/online e atualização manual.
- Cache estruturalmente válido com 10 minutos: ffNewsFetch(false) não busca. Com 40 minutos: considera desatualizado e tenta buscar, salvo solicitação em andamento. O limite é idade **maior que** 30 minutos. Atualização manual usa force=true, ainda respeitando in-flight.
- ffNewsFetch usa fetch com cache HTTP no-store, exige HTTP ok e JSON de formato válido. Sanitização aceita payload.version=1/events e filtra eventos com título/país/data válidos, impacto High e USD/EUR/JPY/GBP. ffNewsWriteCache guarda o payload recebido e fetchedAt; ffNewsReadCache sanitiza novamente ao ler. Não afirmar que a carga persistida é previamente reduzida à lista limpa.
- Sucesso e falha chegam ao finally, que libera in-flight e chama ffNewsRenderAll. Este repinta widget, chama ecalRenderIfOpen e agenda Dashboard. A ausência do widget não impede a atualização das outras superfícies.

| Condição | Comportamento lido | Limite |
|---|---|---|
| Rede falha, cache anterior legível | Cache não é apagado; lastError=true; repintura reutiliza o anterior | Dado antigo não vira atual; widget informa falta de conexão/dados anteriores |
| Rede falha, nenhum cache legível | ecalEvents retorna null; agenda mostra indisponibilidade | Não apresentar zero eventos como confirmação |
| Cache legível, lista/filtro vazio | Agenda informa ausência na fonte ou filtro; Dashboard pode dizer nenhum evento do dia | Vazio com evidência é distinto de cache ausente |
| Gravação do cache é recusada | ffNewsWriteCache captura a exceção; não há cache de payload novo em memória retornado ao renderizador | Próxima leitura pode reencontrar cache antigo ou nenhum; comentário de fallback em memória não prova sua existência |

### C. Dados e estados

Entradas: JSON público e preferência técnica de URL em jpwealth.ui.ffNews.sourceUrl; nenhum acesso externo ocorreu nesta autoria. Cache técnico: jpwealth.ui.ffNews.v1, fora de S e do backup financeiro. Tem fetchedAt local e generated_at da fonte; data de coleta não é autoridade normativa. Eventos carregam título, país/moeda, data, forecast e previous; estes últimos são textos, sem interpretação monetária. ecalEvents deriva Date e ordena por instante. Agrupamento e apresentação usam calendário/fuso local do navegador.

Filtros do modal e workspace são efêmeros e independentes. Abrir/reabrir modal reinicia filtro all, controla foco/teclado e remove listener ao fechar. ecalRenderIfOpen exige workspace presente, não hidden e dentro de screen.active. O snapshot de código não prova todas as sequências reais de foco/tempo.

### D. Limites e proteções

O recorte documentado é a **semana corrente**, sem consulta mensal nem seleção de semanas arbitrárias. O comentário de escopo em 17-economic-calendar.js:9–14 atribui isso à fonte ff_calendar_thisweek e à auditoria de 2026-08-11; é evidência documental herdada sobre o upstream, não uma consulta externa executada neste piloto. Na implementação inspecionada, ffNewsSanitizeEvents conserva forecast/previous e ecalRenderRoot apresenta Consenso/Anterior: não há campo actual nem coluna Realizado. A disponibilidade atual do provedor permanece não verificada, sem ampliar a rede da fixture.

Conteúdo externo é dado: agenda usa textContent; resumo escapa o título. Cache inválido é rejeitado. Nenhuma gravação em S/save foi encontrada neste pipeline; **abrir é consultivo para o estado financeiro, mas pode causar rede e escrita de cache técnico**. Não atribuir isolamento de rede, autorização operacional ou atualidade absoluta à existência da agenda. Sem cache, limites de atraso/desempenho e disponibilidade da fonte continuam não medidos.

### E. Integrações e implementação

15-ff-news concentra aquisição, validação, cache e agendamento; 17-economic-calendar fornece ecalEvents/ecalRenderRoot e as duas superfícies; 23-research-views seleciona a view; 25-dash-macro consome eventos na síntese. O produtor remoto não foi auditado. Relações canônicas e fontes com hash seguem no bloco; não há relação financeira entre Calendário e ledger Alladin demonstrada por esses caminhos.

### F. Evidências e verificação pendente

Fontes primárias: [feed](../../src/js/40-app/15-ff-news.js), [agenda](../../src/js/40-app/17-economic-calendar.js), [Research](../../src/js/20-ui/23-research-views.js), [síntese](../../src/js/20-ui/25-dash-macro.js). Trechos principais: ffNewsFetch/ffNewsReadCache/ffNewsRenderAll, openEconomicCalendar/ecalRenderRoot, researchSelectView e dmResearchHTML. O bloco inclui os hashes integrais examinados.

Runtime/testes desta ficha: **NOT_RUN**. Verificação futura autorizada: cache sintético fresco/antigo/inválido, erro HTTP/JSON, setItem recusado, widget ausente, overlay/workspace visíveis e ocultos, filtros, reabertura, consumidor Dashboard e título hostil. Registrar quantidade de fetch e alterações de S/cache separadamente. Testes existentes a consultar, sem presumir cobertura ou PASS nesta autoria: research_navigation_test.py, dashboard_macro_test.py e dashboard_forex_relocation_test.py em tools/.

### G. Qualidade e evolução — propostas, sem execução

Preservar pipeline/cache únicos, renderer parametrizado, estados de ausência e texto escapado. Problema demonstrado no código: falha de setItem é silenciada e lastError pode ser limpo após sucesso HTTP; a view relê armazenamento e pode continuar antiga/indisponível. Benefício de melhoria: transparência sobre cache não atualizado. Menor incremento futuro: explicitar resultado da gravação e representação da recusa, sem criar pipeline concorrente. Impacto: widget, agenda e Dashboard; risco N1 ou maior conforme alteração de persistência; teste: negar apenas cache técnico e observar mensagens/dados antigos sem falso sucesso. Não corrigido pelo Atlas.

### H. Manutenção

Responsabilidade funcional compartilhada entre informação operacional Forex, consulta Research e síntese Dashboard; nenhum responsável humano foi inventado. Revalidar após alteração de TTL, formato, URL, filtros, renderer, seleção de views, sanitização ou consumidor. Mudança em shell pode alterar acesso sem criar outra feature. Conservar limites do produtor externo e resultados de execução no registro externo do piloto.

```atlas-json
{
  "feature_id": "JPW-FEAT-0001",
  "name": "Calendário Econômico compartilhado",
  "implementation": "available",
  "evidence_level": "code-inspected",
  "freshness": "verified-for-revision",
  "revision": "484228189cc3f5f4c297f29f88f2b2ed541a3afd",
  "sources": [
    {
      "path": "src/js/40-app/15-ff-news.js",
      "sha256": "d2abc27527f5ee4145aa7f31152c8b54adb24e016e3e0c8628530f20971254a3",
      "symbols": [
        "ffNewsSourceUrl",
        "ffNewsSanitizeEvents",
        "ffNewsReadCache",
        "ffNewsWriteCache",
        "ffNewsCacheStale",
        "ffNewsFetch",
        "ffNewsRenderAll",
        "initFfNewsDomain",
        "FF_NEWS_CACHE_KEY"
      ]
    },
    {
      "path": "src/js/40-app/17-economic-calendar.js",
      "sha256": "79c88d7506e23a947a343cacb92e8bd0ee554f6e0b607915e63a2594c4432336",
      "symbols": [
        "ecalEvents",
        "ecalRenderRoot",
        "ecalRenderWorkspace",
        "ecalRenderIfOpen",
        "openEconomicCalendar",
        "closeEconomicCalendar"
      ]
    },
    {
      "path": "src/js/20-ui/23-research-views.js",
      "sha256": "09da5babc3957e15bf6b4db09263f7b998b28a1094b33dc396ad9ec1ca09473e",
      "symbols": [
        "researchSelectView",
        "RESEARCH_VIEW_RENDERERS"
      ]
    },
    {
      "path": "src/js/20-ui/25-dash-macro.js",
      "sha256": "4c4ea201d8beeb2f3149c2cdb98c75e3ffc41be4a62b73fa9856503e5ba7baea",
      "symbols": [
        "dmResearchHTML"
      ]
    }
  ],
  "relations": [
    {
      "origin": "src/js/40-app/15-ff-news.js#ffNewsFetch",
      "type": "CHAMA",
      "target": "src/js/40-app/15-ff-news.js#ffNewsCacheStale",
      "condition": "Sem force e sem solicitação em andamento: decidir se revalida pela idade/ausência do cache.",
      "evidence": "src/js/40-app/15-ff-news.js#ffNewsFetch"
    },
    {
      "origin": "src/js/40-app/15-ff-news.js#ffNewsFetch",
      "type": "VALIDA",
      "target": "src/js/40-app/15-ff-news.js#ffNewsSanitizeEvents",
      "condition": "Depois de HTTP ok e JSON recebido; carga estruturalmente inválida vai ao catch.",
      "evidence": "src/js/40-app/15-ff-news.js#ffNewsFetch"
    },
    {
      "origin": "src/js/40-app/15-ff-news.js#ffNewsFetch",
      "type": "CHAMA",
      "target": "src/js/40-app/15-ff-news.js#ffNewsWriteCache",
      "condition": "Somente após validar a estrutura; grava payload recebido, revalidado novamente nas leituras.",
      "evidence": "src/js/40-app/15-ff-news.js#ffNewsFetch"
    },
    {
      "origin": "src/js/40-app/15-ff-news.js#ffNewsWriteCache",
      "type": "GRAVA",
      "target": "src/js/40-app/15-ff-news.js#FF_NEWS_CACHE_KEY",
      "condition": "Tentativa localStorage.setItem; erro capturado não comprova cache novo.",
      "evidence": "src/js/40-app/15-ff-news.js#ffNewsWriteCache"
    },
    {
      "origin": "src/js/40-app/15-ff-news.js#ffNewsFetch",
      "type": "CHAMA",
      "target": "src/js/40-app/15-ff-news.js#ffNewsRenderAll",
      "condition": "No finally após sucesso ou falha; independe da presença do widget.",
      "evidence": "src/js/40-app/15-ff-news.js#ffNewsFetch"
    },
    {
      "origin": "src/js/40-app/15-ff-news.js#ffNewsRenderAll",
      "type": "CHAMA",
      "target": "src/js/40-app/17-economic-calendar.js#ecalRenderIfOpen",
      "condition": "Se a função existe; ela decide quais superfícies visíveis repintar.",
      "evidence": "src/js/40-app/15-ff-news.js#ffNewsRenderAll"
    },
    {
      "origin": "src/js/40-app/17-economic-calendar.js#ecalEvents",
      "type": "LE",
      "target": "src/js/40-app/15-ff-news.js#ffNewsReadCache",
      "condition": "Lê o cache sanitizado e deriva datas ordenadas; não inicia fetch.",
      "evidence": "src/js/40-app/17-economic-calendar.js#ecalEvents"
    },
    {
      "origin": "src/js/40-app/17-economic-calendar.js#ecalRenderRoot",
      "type": "CHAMA",
      "target": "src/js/40-app/17-economic-calendar.js#ecalEvents",
      "condition": "Para overlay e workspace, com filtro próprio por superfície.",
      "evidence": "src/js/40-app/17-economic-calendar.js#ecalRenderRoot"
    },
    {
      "origin": "src/js/40-app/17-economic-calendar.js#openEconomicCalendar",
      "type": "CHAMA",
      "target": "src/js/40-app/15-ff-news.js#ffNewsFetch",
      "condition": "Entrada modal chama false: não força cache ainda fresco.",
      "evidence": "src/js/40-app/17-economic-calendar.js#openEconomicCalendar"
    },
    {
      "origin": "src/js/20-ui/25-dash-macro.js#dmResearchHTML",
      "type": "CONSOME",
      "target": "src/js/40-app/17-economic-calendar.js#ecalEvents",
      "condition": "Resumo Research no Dashboard; cache nulo não autoriza zero eventos.",
      "evidence": "src/js/20-ui/25-dash-macro.js#dmResearchHTML"
    }
  ]
}
```

<a id="jpw-feat-0002"></a>
## JPW-FEAT-0002 — Lançamentos e estornos do Alladin

### A. Identidade e finalidade

Registrar fatos econômicos do patrimônio e sua correção por estorno, mantendo identidade e rastreabilidade. Entrada: Alladin/Lançamentos, botão de novo lançamento e ação de estorno elegível na linha. Actor: proprietário usando contas/instrumentos cadastrados; no piloto, somente dados sintéticos autorizados. Não confundir manutenção cadastral com edição do ledger: a economia de lançamento não é editada; correção cria REVERSAL.

### B. Funcionamento atual — reconstrução estática

Fluxo de criação: necessidade de registrar fato → abrir modal com write gate → preencher → Registrar → validação de presença/conversão de texto → EDITING para SUBMITTING → uma chamada ledger.addTransaction → validação/domínio/aldMutate → persistência confirmada ou recusa → aviso de sucesso com modal fechado ou rascunho mantido e erro.

initAlladinCrud delega clique ao alladinSubmit, que roteia pelo tipo do formulário. alladinTxSubmit ignora estado diferente de EDITING, lê campos e faz **uma chamada mutável ao domínio por submit que alcança essa etapa**. Dois fatos semelhantes não são automaticamente duplicados; dedupeKey é opcional no domínio, não fabricada pela UI. Uma contagem global de handlers ou cliques não foi medida.

Exemplo aritmético sintético pela leitura, **não executado**: DEPOSIT, conta BRL válida/ativa, data válida e texto “1.234,56” passam por alladinTxMinor → money.parse/aldParseMoney, obtendo amount=123456 unidades mínimas (centavos). A UI fornece evento/data/conta/valor e nota opcional; não fornece ID, recordedAt, status, flowScope ou currency como autoridade. O domínio resolve/revalida conta e moeda, exige inteiro seguro positivo, atribui POSTED, gera transactionId/recordedAt e deriva EXTERNAL para DEPOSIT. Campos financeiros não são determinados por rótulo da tela.

Fluxo de estorno: selecionar original → domínio/read-model localiza fato → modal mostra economia somente leitura → operador informa data própria, nota/motivo opcionais → uma chamada reverseTransaction → original revalidado → novo REVERSAL com economia copiada, reversalOf e reversedEventType → original marcado REVERSED → mesmo veredito de persistência. Não há remoção do original. Reverter REVERSAL ou repetir estorno é recusado; a revalidação final ocorre no domínio, mesmo que a elegibilidade visual esteja antiga.

| Estado/resultado | Efeito lido |
|---|---|
| Campo obrigatório ausente | Erro inline antes da chamada mutável |
| Validação/domínio recusam | Volta a EDITING; mantém formulário/rascunho, sem aviso de sucesso |
| save retorna valor diferente de true | aldMutate restaura agregado S.alladin e conteúdo anterior do changeLog; retorna ok=false/persistido=false |
| Sucesso do domínio | UI fecha modal e anuncia lançamento/estorno registrado |
| Cancelamento antes de submit | Fluxo de descarte/fechamento de modal; não cria ato econômico |
| Schema futuro ou integridade estrutural inválida | Write gate impede ato; UI/leituras têm estados de indisponibilidade próprios |

### C. Dados e estados

Persistido: S.alladin.transactions, schema suportado 6, referências permanentes, evento, status, datas, inteiro monetário em unidade mínima e moeda da conta. Runtime monetário inspecionado suporta BRL/USD, expoente 2; não implica suporte universal de moeda. Para BUY/SELL, quantity é string decimal preservada, fees/taxes são inteiros e flowScope não existe; informação não permitida é recusada, não reinterpretada. REVERSAL copia a economia e referências, mas data/nota/motivo próprios não são herdados como justificativa fabricada.

Os consumidores saldoDeCaixa e posicoes derivam resultados do ledger; posição por instrumentId+accountId usa aritmética decimal BigInt e quantity em string. Ausência de conta, carteira sem posições e BLOCKING são estados distintos. A UI lê/forma apresentação; não recalcula saldo, preço ou quantidade. Formulário é estado efêmero; log operacional genérico não equivale a Audit Trail normativo completo.

### D. Limites e proteções

aldMutate verifica schema/integridade antes de mutar, guarda snapshot e log e exige retorno true de save. save possui recusas por recuperação, resultado anterior desconhecido, bloqueio, serialização, concorrência entre abas e armazenamento. Isso sustenta o caminho de rollback por retorno examinado; não prova toda falha possível ou execução real nesta autoria. A distinção persistido:true/false é essencial: não importar por analogia o comportamento do NoCoda.

História: o começo de ALLADIN.md preserva o estado C3 “não há transação/posição”; a nota **Superado em 2026-08-31** logo abaixo e seções ALD-03/04/05 posteriores o substituem para a revisão atual. Confirmam ledger, trades, despesas, ajustes, posições quantitativas e UI de criação/estorno. Continuam ausentes holding persistido/consolidado, valuation/current value, custo médio/cost basis, P&L, performance, benchmark e integrações Trading/PF/FX. Abrir Posições não disponibiliza valor de mercado automático. Finalidade “consolidação” não significa patrimônio monetário completo. Aceites históricos não aprovam este Atlas.

### E. Integrações e implementação

24-alladin-views coleta e apresenta; aliases JPWAlladin.ledger/money/leitura apontam a 13-alladin; aldMutate chama save na persistência comum. Saldos e posições são consumidores indiretos dos fatos, não alterações persistidas por navegar. Ald/Forex podem compartilhar infraestrutura global sem integração econômica entre domínios; nenhuma API/cotação externa é chamada pelos caminhos descritos. Uma sugestão recuperada de valuation continua proposta, sem permissão de implementação ou de leitura de arquivos externos.

### F. Evidências e verificação pendente

[Contrato](ALLADIN.md), [domínio](../../src/js/10-domain/13-alladin.js), [UI](../../src/js/20-ui/24-alladin-views.js), [persistência](../../src/js/00-core/04-persistence.js). Trechos: aldNormalizeTransactionFields/aldActAddTransaction/aldActReverseTransaction/aldMutate, alladinTxSubmit/alladinTxReverseSubmit, alladinRenderPositions e save; hashes no bloco.

Runtime/testes desta ficha: **NOT_RUN**. Futuro piloto: criar/estornar dados sintéticos por UI e observar memória/disco/contagem de chamadas; negar gravação, provocar conflito, cancelar, repetir submit/estorno, testar schema futuro e conferir consumidores. Consultar focais existentes alladin_unit_test.py e alladin_ui_tx_write_test.py em tools/ quando aplicáveis, sem promover sua existência a PASS. A evidência precisa identificar execução/candidate e virá do registro externo, não da narrativa da ficha.

### G. Qualidade e evolução — propostas, sem execução

Preservar fronteira transacional, rascunho na recusa, identidade/append-only econômico e projeções sem cálculo na UI. Oportunidade documental demonstrada: o trecho C3 histórico pode ser recuperado sem seu aviso sucessor. Benefício: evitar falsa afirmação de capacidade ausente. Menor incremento: manter aviso e fonte sucessora juntos na unidade consultada, sem apagar história. Impacto: Atlas, recuperação e agentes; risco de promoção indevida, tratado pelo control plane; teste: pergunta histórica deve voltar à nota vigente e ao código. Valuation é oportunidade futura que exige contrato e decisão próprios; não é defeito a corrigir neste piloto nem entrega atual.

### H. Manutenção

Responsabilidade funcional Alladin/ledger, com consumidores UI, saldos, posições, backup e integridade. Revisar ficha se evento, schema, API, moeda, reversão, save/rollback ou read-model mudar; respeitar contratos aprovados e limites normativos, não a opinião do Atlas. A fonte externa de planejamento do domínio não foi acessada. Aceite e fidelidade da implementação do Atlas permanecem pendentes de avaliação independente.

```atlas-json
{
  "feature_id": "JPW-FEAT-0002",
  "name": "Lançamentos e estornos do Alladin",
  "implementation": "available",
  "evidence_level": "code-inspected",
  "freshness": "verified-for-revision",
  "revision": "484228189cc3f5f4c297f29f88f2b2ed541a3afd",
  "sources": [
    {
      "path": "src/js/20-ui/24-alladin-views.js",
      "sha256": "e5020166f5414ee9da96768e81889a32589f9b3e1d2ec0d6b157b7cca1939c8d",
      "symbols": [
        "initAlladinCrud",
        "alladinSubmit",
        "alladinTxLerFormulario",
        "alladinTxMinor",
        "alladinTxSubmit",
        "alladinTxReverseSubmit",
        "alladinRenderBalances",
        "alladinRenderPositions"
      ]
    },
    {
      "path": "src/js/10-domain/13-alladin.js",
      "sha256": "8ef16b541c80347a61b51a3724d7bc8ac027696004896c90dcc844dc6163f35b",
      "symbols": [
        "aldParseMoney",
        "aldNormalizeTransactionFields",
        "aldActAddTransaction",
        "aldActReverseTransaction",
        "aldMutate",
        "aldWriteBlockReason",
        "aldIntegridadeEstrutural",
        "aldSaldoDeCaixa",
        "aldPosicoes",
        "ALD_FLOW_POR_EVENTO"
      ]
    },
    {
      "path": "src/js/00-core/04-persistence.js",
      "sha256": "94ff842770930cef4466e51d34ffab189f7badff4abf5331c5c4c0224c3599bc",
      "symbols": [
        "save"
      ]
    },
    {
      "path": "docs/architecture/ALLADIN.md",
      "sha256": "3964ef8bc128d883cec9fe041f45a9a6c93d5e0136c832e3bbc6abc0dd9a309a",
      "symbols": [
        "Superado em 2026-08-31",
        "ALD-05 S2",
        "ALD-05 S3"
      ]
    }
  ],
  "relations": [
    {
      "origin": "src/js/20-ui/24-alladin-views.js#alladinSubmit",
      "type": "CHAMA",
      "target": "src/js/20-ui/24-alladin-views.js#alladinTxSubmit",
      "condition": "alladinForm.tipo transaction e estado EDITING.",
      "evidence": "src/js/20-ui/24-alladin-views.js#alladinSubmit"
    },
    {
      "origin": "src/js/20-ui/24-alladin-views.js#alladinSubmit",
      "type": "CHAMA",
      "target": "src/js/20-ui/24-alladin-views.js#alladinTxReverseSubmit",
      "condition": "alladinForm.tipo transaction-reverse e estado EDITING.",
      "evidence": "src/js/20-ui/24-alladin-views.js#alladinSubmit"
    },
    {
      "origin": "src/js/20-ui/24-alladin-views.js#alladinTxSubmit",
      "type": "CHAMA",
      "target": "src/js/20-ui/24-alladin-views.js#alladinTxLerFormulario",
      "condition": "Lê e valida presença dos campos antes de SUBMITTING.",
      "evidence": "src/js/20-ui/24-alladin-views.js#alladinTxSubmit"
    },
    {
      "origin": "src/js/20-ui/24-alladin-views.js#alladinTxMinor",
      "type": "CHAMA",
      "target": "src/js/10-domain/13-alladin.js#aldParseMoney",
      "condition": "Via JPWAlladin.money.parse, cujo alias é definido no domínio; extrai amount sem calcular moeda.",
      "evidence": "src/js/20-ui/24-alladin-views.js#alladinTxMinor"
    },
    {
      "origin": "src/js/20-ui/24-alladin-views.js#alladinTxSubmit",
      "type": "CHAMA",
      "target": "src/js/10-domain/13-alladin.js#aldActAddTransaction",
      "condition": "Uma chamada via JPWAlladin.ledger.addTransaction por submit que alcança o domínio.",
      "evidence": "src/js/20-ui/24-alladin-views.js#alladinTxSubmit"
    },
    {
      "origin": "src/js/20-ui/24-alladin-views.js#alladinTxReverseSubmit",
      "type": "CHAMA",
      "target": "src/js/10-domain/13-alladin.js#aldActReverseTransaction",
      "condition": "Uma chamada via JPWAlladin.ledger.reverseTransaction; campos econômicos não vêm do formulário.",
      "evidence": "src/js/20-ui/24-alladin-views.js#alladinTxReverseSubmit"
    },
    {
      "origin": "src/js/10-domain/13-alladin.js#aldActAddTransaction",
      "type": "CHAMA",
      "target": "src/js/10-domain/13-alladin.js#aldNormalizeTransactionFields",
      "condition": "Dentro do ato mutável, antes de gerar ID e inserir transação.",
      "evidence": "src/js/10-domain/13-alladin.js#aldActAddTransaction"
    },
    {
      "origin": "src/js/10-domain/13-alladin.js#aldActAddTransaction",
      "type": "CHAMA",
      "target": "src/js/10-domain/13-alladin.js#aldMutate",
      "condition": "Ato transaction_add passa pelo write gate e pelo veredito de persistência.",
      "evidence": "src/js/10-domain/13-alladin.js#aldActAddTransaction"
    },
    {
      "origin": "src/js/10-domain/13-alladin.js#aldActReverseTransaction",
      "type": "CHAMA",
      "target": "src/js/10-domain/13-alladin.js#aldMutate",
      "condition": "Ato transaction_reverse modifica o par dentro da mesma fronteira transacional.",
      "evidence": "src/js/10-domain/13-alladin.js#aldActReverseTransaction"
    },
    {
      "origin": "src/js/10-domain/13-alladin.js#aldMutate",
      "type": "CHAMA",
      "target": "src/js/00-core/04-persistence.js#save",
      "condition": "Após aplicar ato e log; retorno diferente de true restaura snapshot e conteúdo do log.",
      "evidence": "src/js/10-domain/13-alladin.js#aldMutate"
    },
    {
      "origin": "src/js/20-ui/24-alladin-views.js#alladinRenderBalances",
      "type": "CONSOME",
      "target": "src/js/10-domain/13-alladin.js#aldSaldoDeCaixa",
      "condition": "Via leitura.saldoDeCaixa; um read-model por conta, sem soma própria na UI.",
      "evidence": "src/js/20-ui/24-alladin-views.js#alladinRenderBalances"
    },
    {
      "origin": "src/js/20-ui/24-alladin-views.js#alladinRenderPositions",
      "type": "CONSOME",
      "target": "src/js/10-domain/13-alladin.js#aldPosicoes",
      "condition": "Via leitura.posicoes; BLOCKING não vira coleção vazia normal.",
      "evidence": "src/js/20-ui/24-alladin-views.js#alladinRenderPositions"
    }
  ]
}
```

<a id="jpw-feat-0003"></a>
## JPW-FEAT-0003 — Estudos NoCoda e catálogo compartilhado

### A. Identidade e finalidade

Guardar manualmente a memória técnica de três âncoras do canal NoCoda por instrumento, calcular range/subdivisão e permitir retomar o estudo. Entrada atual: Research → Forex → NoCoda, preservando o ID físico execNocoda legado. Não é scanner, backtest, sinal, previsão, conexão MT5 ou autorização operacional. O instrumento é compartilhado; o estudo pertence a S.nocoda.studies, não a um catálogo paralelo.

### B. Funcionamento atual — reconstrução estática

Fluxo: objetivo de estudar um instrumento → seletor derivado de instrumentCatalog → rascunho das três âncoras → digitação/prévia → validação explícita no Salvar → alteração das causas em memória → save → mensagem/novo cálculo. Trocar instrumento com ncDirty pede confirmação; cancelar mantém seleção/rascunho, aceitar carrega outro estudo. Essa guarda específica não é prova de preservação em toda saída de módulo.

renderNocodaStudies consome a lista operável. Sem itens mostra indisponibilidade; seleção inválida é substituída pelo primeiro item atual. ncBind atualiza ncDraft e prévia a cada input, sem persistir antes de Salvar. ncUpdateDerived usa JPWNocoda.geometry.compute, sem reconstruir o formulário a cada tecla. ncSaveStudy valida, exibe erros por campo e só então atualiza âncoras/updatedAt. A implementação chama save, mas **não examina seu retorno**: limpa ncDirty e mostra “parâmetros salvos” mesmo se save retornar false. Esse desvio é demonstrável por leitura; comportamento visível/disco sob falha requer teste sintético, não foi executado aqui.

### C. Dados e estados

S.instruments é a origem do catálogo; instrumentId normaliza o nome para maiúsculas alfanuméricas. instrumentCatalog deriva id/name/banned/unlocked, excluindo banned && !unlocked por padrão; all:true inclui os banidos. Não contém metadado de casas decimais por instrumento neste contrato. ncFormat apresenta até 8 casas, sem usar texto formatado como entrada do motor.

O estudo persiste anchor1/2/3 (datetime e preço normalizado) e updatedAt, um registro vigente por ID; rascunho/seleção/sujeira são efêmeros. Não persiste range, subdivisão ou 65 níveis. Instrumento removido/banido pode sair do seletor, mas seu estudo armazenado é preservado; ausência de acesso visual não é exclusão dos dados. Pivots tem estratégia distinta: pvInstrumentOptions une catálogo operável aos instrumentos já presentes nos seus estudos, mantendo-os acessíveis.

Geometria pura: âncoras 1/2 definem linha zero; projeta essa linha no tempo T3 e toma a distância da terceira âncora. Subdivisão é range/8. Timestamps sem fuso são interpretados em componentes UTC para aritmética determinística, sem conversão do carimbo exibido. Datas impossíveis, preços não finitos ou não positivos e T1=T2 são recusados; T3 fora do intervalo é permitido. Não substituir a projeção por abs(P3−P1/P2). Os preços são coordenadas do instrumento, não dinheiro/centavos, e não se deriva risco ou lote do estudo.

### D. Limites e proteções

O contrato declara que estudar/salvar não libera fase, clearance, ordens, alavancagem, LIFO ou quarentena. A matemática não usa DOM/S/rede; a UI consulta o motor. Dados de entrada e erros são tratados como texto/HTML escapado nos pontos examinados. save pode recusar por recuperação/concorrência/armazenamento, mas a UI NoCoda não propaga essa recusa nem restaura seu agregado nesse caminho. **Não afirmar que NoCoda tem o rollback de aldMutate.** O estado vivo pode conservar a alteração apesar de o disco não tê-la recebido; é risco derivado do fluxo estático, sujeito à caracterização controlada.

Fora do MVP conforme contrato: importação automática de âncoras, integração MT5, histórico versionado, comparação de estudos, desenho das 65 linhas, pips/ATR/equivalência monetária/sinais. A função levelPrice existir não prova desenho dessas linhas na interface.

### E. Integrações, consumidores e limites de impacto

Catálogo/identidade: 01-risk-instruments. Consumidores diretos de instrumentCatalog inspecionados: renderNocodaStudies, pvInstrumentOptions e dmResearchHTML (cobertura NoCoda no resumo Dashboard). Ordens usam **instFor → instrumentId**, por exemplo orderGateMsg; não afirmar que orderGateMsg chama instrumentCatalog. O Motor/ordens compartilham a origem/identidade operacional, não um catálogo mantido pelo NoCoda. Mudar instrumento/identidade pode afetar esses consumidores sem exigir editar todos os arquivos.

NoCoda chama geometria pura de 09-nocoda-geometry e save comum; não há evidência, nesses caminhos, de propagação de estudo para execução ou Alladin. Buscar componente → feature nos endpoints abaixo permite localizar NoCoda e seus consumidores; caminho próximo ou nome parecido não cria aresta.

### F. Evidências e verificação pendente

[Contrato NoCoda](NOCODA-STUDIES.md), [UI](../../src/js/20-ui/14-nocoda-studies.js), [geometria](../../src/js/10-domain/09-nocoda-geometry.js), [catálogo](../../src/js/10-domain/01-risk-instruments.js), [Pivots](../../src/js/20-ui/15-pivot-studies.js), [Dashboard](../../src/js/20-ui/25-dash-macro.js), [veredito de ordem](../../src/js/10-domain/03-phase-transitions.js), [persistência](../../src/js/00-core/04-persistence.js). Trechos e hashes no bloco; consumidores representam somente relações materiais inspecionadas, não todo uso possível de S.instruments.

Runtime/testes desta ficha: **NOT_RUN**. Futuro piloto autorizado: prévia sem save; estudo válido e reabertura; erro por campo; troca/cancelamento com rascunho; remoção/banimento do instrumento preservando estudo; consumidores Pivots/Dashboard; save recusado comparando S, disco, mensagem e ncDirty. Ferramentas existentes a consultar sem presumir resultados: tools/nocoda_test.py, tools/pivot_studies_test.py e tools/dashboard_macro_test.py. Relacionar comportamento observado ao trace, não à autodeclaração.

### G. Qualidade e evolução — propostas, sem execução

Preservar separação catálogo/geometria/UI, cálculo por causas e ausência de autorização operacional. Defeito estático identificado: ncSaveStudy não usa o veredito de save e anuncia sucesso após chamada. Benefício de correção futura: mensagem fiel, rascunho preservado e integridade memória/disco. Menor incremento a propor: tratar explicitamente recusa/resultado da gravação e recuperação do estado do próprio estudo, sem alterar motor/catálogo. Consumidores afetados: NoCoda, resumo de estudos e backup; risco ao menos N2 se modificar persistência/recuperação; teste focal deve negar save e provar que não há sucesso falso/perda de estudo antigo. **Nenhuma correção está autorizada ou implementada pelo Atlas.**

### H. Manutenção

Responsabilidade Research/estudos com coordenação do catálogo operacional compartilhado e persistência. Revalidar se identidade/filtro, schema do estudo, validação temporal, geometria, save, seleção, Pivots ou síntese mudarem. Não apagar registros de instrumentos ausentes para “limpar” o Atlas. Guardar data da inspeção efetiva; regenerar representação não revalida matemática ou gravação. Incertezas e novos consumidores descobertos entram como pendências do recorte, dentro do contrato autorizado.

```atlas-json
{
  "feature_id": "JPW-FEAT-0003",
  "name": "Estudos NoCoda e catálogo compartilhado",
  "implementation": "available",
  "evidence_level": "code-inspected",
  "freshness": "verified-for-revision",
  "revision": "484228189cc3f5f4c297f29f88f2b2ed541a3afd",
  "sources": [
    {
      "path": "src/js/20-ui/14-nocoda-studies.js",
      "sha256": "7dda7e700186309cf41d99da92b69c93140c268d06f6082b8f3586c13018e603",
      "symbols": [
        "renderNocodaStudies",
        "ncDraftFrom",
        "ncSelectInstrument",
        "ncUpdateDerived",
        "ncSaveStudy",
        "S.nocoda.studies"
      ]
    },
    {
      "path": "src/js/10-domain/09-nocoda-geometry.js",
      "sha256": "268858faa34378c4dd3c90827699e59d48a1022a1f2287e6bc840bf51265147f",
      "symbols": [
        "nocodaParseTime",
        "nocodaValidateAnchors",
        "nocodaGeometry",
        "nocodaProjectBasePrice",
        "nocodaLevelPrice"
      ]
    },
    {
      "path": "src/js/10-domain/01-risk-instruments.js",
      "sha256": "7dee71a663bd9f4bd2190673901df352db879b7d0379e1d81d079dc4e0d8e4e5",
      "symbols": [
        "instrumentCatalog",
        "instrumentId",
        "instFor",
        "S.instruments"
      ]
    },
    {
      "path": "src/js/20-ui/15-pivot-studies.js",
      "sha256": "2230065776716f26420ac5b90852f1703d7fb139a23144e864e96511d25279df",
      "symbols": [
        "pvInstrumentOptions"
      ]
    },
    {
      "path": "src/js/20-ui/25-dash-macro.js",
      "sha256": "4c4ea201d8beeb2f3149c2cdb98c75e3ffc41be4a62b73fa9856503e5ba7baea",
      "symbols": [
        "dmResearchHTML"
      ]
    },
    {
      "path": "src/js/10-domain/03-phase-transitions.js",
      "sha256": "d0741b26ed5701fcb6a758856ab4d679a7d054c1585492325c46975362fd90fd",
      "symbols": [
        "orderGateMsg"
      ]
    },
    {
      "path": "src/js/00-core/04-persistence.js",
      "sha256": "94ff842770930cef4466e51d34ffab189f7badff4abf5331c5c4c0224c3599bc",
      "symbols": [
        "save",
        "nocodaNormalizeState"
      ]
    },
    {
      "path": "docs/architecture/NOCODA-STUDIES.md",
      "sha256": "85becb521fef1dad0971cf54e0237dfbde7b7e980fb8b1b2ac9c2b6be65968da",
      "symbols": [
        "Modelo persistido",
        "Fora do MVP",
        "Precisão"
      ]
    }
  ],
  "relations": [
    {
      "origin": "src/js/20-ui/14-nocoda-studies.js#renderNocodaStudies",
      "type": "CHAMA",
      "target": "src/js/10-domain/01-risk-instruments.js#instrumentCatalog",
      "condition": "Sem all:true; seleciona instrumentos operáveis, preservando estudo armazenado fora do seletor.",
      "evidence": "src/js/20-ui/14-nocoda-studies.js#renderNocodaStudies"
    },
    {
      "origin": "src/js/10-domain/01-risk-instruments.js#instrumentCatalog",
      "type": "LE",
      "target": "src/js/10-domain/01-risk-instruments.js#S.instruments",
      "condition": "Deriva lista; filtro exclui banned && !unlocked, salvo all:true.",
      "evidence": "src/js/10-domain/01-risk-instruments.js#instrumentCatalog"
    },
    {
      "origin": "src/js/10-domain/01-risk-instruments.js#instrumentCatalog",
      "type": "CHAMA",
      "target": "src/js/10-domain/01-risk-instruments.js#instrumentId",
      "condition": "Produz a chave normalizada de cada item pelo nome.",
      "evidence": "src/js/10-domain/01-risk-instruments.js#instrumentCatalog"
    },
    {
      "origin": "src/js/10-domain/01-risk-instruments.js#instFor",
      "type": "CHAMA",
      "target": "src/js/10-domain/01-risk-instruments.js#instrumentId",
      "condition": "Resolve identidade usada por consumidores operacionais; não chama instrumentCatalog.",
      "evidence": "src/js/10-domain/01-risk-instruments.js#instFor"
    },
    {
      "origin": "src/js/10-domain/03-phase-transitions.js#orderGateMsg",
      "type": "CHAMA",
      "target": "src/js/10-domain/01-risk-instruments.js#instFor",
      "condition": "Resolve instrumento de o.par antes do veredito da ordem.",
      "evidence": "src/js/10-domain/03-phase-transitions.js#orderGateMsg"
    },
    {
      "origin": "src/js/20-ui/15-pivot-studies.js#pvInstrumentOptions",
      "type": "CHAMA",
      "target": "src/js/10-domain/01-risk-instruments.js#instrumentCatalog",
      "condition": "Pivots adiciona aos operáveis os instrumentos que já têm estudos próprios.",
      "evidence": "src/js/20-ui/15-pivot-studies.js#pvInstrumentOptions"
    },
    {
      "origin": "src/js/20-ui/25-dash-macro.js#dmResearchHTML",
      "type": "CHAMA",
      "target": "src/js/10-domain/01-risk-instruments.js#instrumentCatalog",
      "condition": "Denominador de cobertura dos estudos NoCoda no resumo Research.",
      "evidence": "src/js/20-ui/25-dash-macro.js#dmResearchHTML"
    },
    {
      "origin": "src/js/20-ui/14-nocoda-studies.js#ncUpdateDerived",
      "type": "CHAMA",
      "target": "src/js/10-domain/09-nocoda-geometry.js#nocodaGeometry",
      "condition": "Via JPWNocoda.geometry.compute; cálculo de prévia sem persistência.",
      "evidence": "src/js/20-ui/14-nocoda-studies.js#ncUpdateDerived"
    },
    {
      "origin": "src/js/20-ui/14-nocoda-studies.js#ncSaveStudy",
      "type": "VALIDA",
      "target": "src/js/10-domain/09-nocoda-geometry.js#nocodaValidateAnchors",
      "condition": "Via geometry.validate antes de modificar estudos.",
      "evidence": "src/js/20-ui/14-nocoda-studies.js#ncSaveStudy"
    },
    {
      "origin": "src/js/20-ui/14-nocoda-studies.js#ncSaveStudy",
      "type": "GRAVA",
      "target": "src/js/20-ui/14-nocoda-studies.js#S.nocoda.studies",
      "condition": "Altera memória com três âncoras e updatedAt após validação; não significa confirmação de disco.",
      "evidence": "src/js/20-ui/14-nocoda-studies.js#ncSaveStudy"
    },
    {
      "origin": "src/js/20-ui/14-nocoda-studies.js#ncSaveStudy",
      "type": "CHAMA",
      "target": "src/js/00-core/04-persistence.js#save",
      "condition": "Depois da alteração em memória; este chamador não examina o retorno.",
      "evidence": "src/js/20-ui/14-nocoda-studies.js#ncSaveStudy"
    },
    {
      "origin": "src/js/10-domain/09-nocoda-geometry.js#nocodaGeometry",
      "type": "CHAMA",
      "target": "src/js/10-domain/09-nocoda-geometry.js#nocodaProjectBasePrice",
      "condition": "Projeta linha zero no tempo da terceira âncora antes de derivar range.",
      "evidence": "src/js/10-domain/09-nocoda-geometry.js#nocodaGeometry"
    }
  ]
}
```
