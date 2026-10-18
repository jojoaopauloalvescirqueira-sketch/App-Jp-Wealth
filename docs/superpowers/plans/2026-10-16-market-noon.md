# Plano executável — Bolsas Globais —16/10/2026

Fonte normativa desta entrega: plano completo aprovado pelo usuário nesta conversa, “Bolsas Globais — próximas aberturas e orientação pelo meio-dia”. CHG/CTX-JPW-MARKET-NOON-20261016 delimitam autorização, fontes e rollback. Sem Git/publicação, dependências ou dados persistidos. Mesmo candidato e branch, preservando3minigames e macOS.

## Tarefa1 — calendário e consulta

Testes permanentes antes da implementação. Preparar índices de próximas entradas regulares uma vez; snapshot at inclui nextRegularOpen:{earliestUtc,latestUtc,kind:open|resume} ou null. Reutilizar isRegularOpen; ignorar razões textuais para inferência. Desconhecimento atual/intermediário e fim da cobertura conjunta são barreiras. Retoma exige intervalo anterior ou leilão intradiário precedido por contínua/intervalo conhecido; demais Abre. Só transição agregada nãoaberta→aberta, sem anúncio para já abertas. Cobrir mistura de grupos/janelas sobrepostas/feriado/lacunas/fim de cobertura.

View: ordem Abertas,Todas,Sem confirmação; inicial Abertas. Na aba Abertas separar Abertas agora/Próximas24horas, somente nãoabertas cuja próxima janela confirmada termine dentro das24h (limite incluso); ordenar início/fim/catálogo. Contagem somente abertas agora. Abre em2h15min/Retoma em25min; intervalos com ambos limites/segundos quando necessário; durante a janela mostrar exatamente “Janela de abertura em andamento”, sem contagem negativa (também para retomada). Vazio exato: “Nenhuma abertura confirmada nas próximas 24 horas”. Busca/fase afetam ambas. Uma linha estável por praça, sem duplicação; preservar seleção/foco/scroll ao migrar. Seleção futura normal. Manter B3 inicial e Mostrar na lista.

## Tarefa2 — adapter geográfico

Testes permanentes antes. Estender Aisol com focusLocation({lat,lng},{animate}) e callback opcional onInteraction, isolando exceções. Preservar focusMarker, geometry/defaults, engine.js e seleção. Movimento angular pelo caminho mais curto; instantâneo reducedmotion. Eventos aceitos de down/up/cancel/teclado; movimento pressionado bloqueia retorno. Cancelar focusTarget imediatamente na nova manipulação. Hover/foco e teclas sem efeito não contam. SVG fallback recebe orientação sem inventar manipulação própria. Sem build por builder; root executa builder oficial depois de integrar.

## Tarefa3 — controlador do meio-dia

Testes com relógio controlado antes. UTC longitude wrap180(180−15×horaUTCdecimal), lat0; meio-dia solar médio aproximado, horários oficiais continuam em seus fusos. Orientação inicial sem mudar B3; atualizar referência somente uma vez/minuto visível, sem rotação contínua. Date.now para UTC, performance.now para prazo10s. Down mantém gesto; up/cancel inicia espera; última tecla manipuladora reinicia. Seleção explícita da lista centraliza cidade por10s. Interação interrompe retorno; calendário/hover/foco não reiniciam. Ocultar/recolher/diálogo/route/blur cancelam timers/RAF; retomada verifica prazo monotônico, conserva exploração se vigente senão centraliza referência atual. Descarte terminal. Mesma regra fallback. Sem persistência.

## Tarefa4 — integração e provas

Adaptação justificada dos testes legados para novo default/API, mantendo seus oráculos. Revisão independente de cada fronteira e final. Builder Aisol oficial com Three0.186.1/esbuild0.25.12 existentes, depois rebuild_monolith.py --refresh-manifest. Focais permanentes, macOS/redesign/engine/catalog/assets/interaction/recovery/performance/distribuição HTTP+PWAoffline+file+portátil,4layouts/temas/mobile/native200, validação/reprodutibilidade/FULL. Sem enfraquecer limites de desempenho ou zero trabalho oculto. Cadência visível admite somente atualização pontual de minuto/retorno por novo contrato.

## Tarefa5 — registros e entrega

Contrato, ajuda, CHANGELOG e três agregadores factuais com histórico intacto. Vincular bytes/testes/revisões no relatório, mapa final e mapa de entrega. Preservar recibos falhos e incidentes anteriores em aberto. Não confundir avaliação automática, heurística e compreensão/aceite humano. Prévia funcional nova versão, entrega local sem operaçãoGit.
