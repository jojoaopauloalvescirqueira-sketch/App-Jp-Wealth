# Calendário e Mercados — integração aprovada

Base conferida: main a4bf278cd4dc38bbaa5b905ed17a79e33684fb67, checkout limpo. O proprietário autorizou o plano e especificamente a branch codex/calendario-mercados-20261024. Sem commit, merge, push ou publicação.

## Contrato de produto (N1)

Reunir Calendário e Agenda e Bolsas Globais em Ferramentas → Calendário e Mercados. Preservar tools-calendar; tools-market-hours passa a destino compatível que expande e ancora Bolsas depois da navegação aceita. Manter a lição tools-calendar e seu progresso.

Calendário e bolsas têm hosts irmãos; não reconstruir a agenda ao atualizar bolsas. Resumo inicial recolhido: até três abertas na ordem do catálogo e três próximas aberturas/retomadas nas24h na ordem início/fim/catálogo, contagens totais e desconhecidas separadas. Agora e data selecionada são referências distintas; filtros independentes. Atalho Bolsas agora no cabeçalho da página, inclusive celular. Modal do cabeçalho permanece agenda breve.

Explorar substitui resumo por exploração existente; recolher preserva nós, filtros, seleção, foco e rolagem interna. Clicar bolsa do resumo expande e seleciona sem limpar filtros. B3 inicial. Escolha de expansão vive somente na sessão.

Uma instância/catálogo/snapshot/scheduler. mount(host,{collapsed}) mantém comportamento full sem opções; setExpanded(boolean). FullDOM lazy; renderer não executado/instanciado antes da expansão e visibilidade. Pausar quadros/câmera/timers com mapa oculto, fora da viewport, diálogos, blur, saída e descarte. Preservar meio-dia/10s. No file sidecar pode ser lido junto, sem execução antecipada.

Resumo atualiza por minuto e limites de transição/janela/horizonte24h; espera aproximada em minutos, janelas com dois horários locais precisos/data quando necessário. Exploração conserva precisão atual. Falhas exibidas no resumo com retry explícito e dados não atuais identificados; não transformar falha em zero. Async atrasado não rouba foco/ressuscita conteúdo.

## Invariantes e limites

Sem novos cálculos de sessões, fontes, dependências, persistência, migração, escritores financeiros ou formato de backup. Preservar agenda/rascunhos, Planejamento, Notas, sino, calendário semanal e três minigames. Reutilizar CSS/tokens e gerador oficial; não editar biblioteca/globo gerado.

## Execução e evidência

1. RED da navegação, resumo e API no baseline; composição/rotas.
2. Resumo/expansão/ciclo de vida, focais e contraprovas.
3. Distribuições, matriz visual, revisão independente e full no candidate estável.

Verificar4layouts,2temas,320–1440px,zoom200%,teclado,toque,movimento reduzido; preservação financeira antes/depois. Capturas, latências/contagens, revisão independente e aceite humano separados. Documentar resultados reais em docs/validation/calendar-markets-20261024/. Rollback: diff reversível de produto, sem dados persistidos alterados.

## Contrato separado dos verificadores

Fonte: plano aprovado pelo proprietário24/10/2026. Antes: testes exigiam item independente tools-market-hours e child tools-market-hours. Depois: exigem somente tools-calendar visível com nome novo, destino antigo aceito/canônico tools-calendar e exploração aberta/ancorada; nenhuma dessas expectativas é financeira. Preservar guardas, descarte, foco, cobertura, precisão, distribuição e ausência de escrita. Novos casos identificáveis em tools/calendar_markets_test.py; adaptar apenas expectativas superadas dos testes de integração/navegação, com RED/GREEN, violações representativas rejeitadas e revisão independente. Runner/gates e política de aprovação inalterados. Não promover recibos antigos a evidência atual.

Consumidores de NoCuda e MiniGames também exigiam a lista antiga de seis destinos. Reconciliar somente essa lista e a adjacência de teclado NoCuda/Calendário, preservando todas as demais provas de downloads, jogos, dados e distribuições. O primeiro FULL com esses dois oráculos superados permanece vermelho e preservado; executar outro FULL após RED/GREEN e revisão independente dos ajustes.
