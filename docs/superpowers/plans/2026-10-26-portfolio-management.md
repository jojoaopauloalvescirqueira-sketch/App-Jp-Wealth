# Portfólio e Gerenciamento — plano humano aprovado

Fonte: pedido humano PLEASE IMPLEMENT THIS PLAN de26/10/2026 e decisões de planejamento nesta conversa. A planilha original é referência autorizada para leitura; valores pessoais não entram no produto/fixtures.

## Objetivo
Research vira Portfólio; research-forex vira Análise contendo somente Estudos Nocuda/Pivots. Gerenciamento independente contém Reservas e Contabilidade e vem após Portfólio. Remover placeholders públicos, preservar aliases aceitos, dados, progresso, ordens personalizadas e comportamento de congelamento.

## Fonte e adaptação aprovada
Todas!A2:R329 do XLSX SHA256621a4e5bdefc467bede301b94e2c6f60aa05c78df3613cfac3908ef8d0c9084a. Planejado/real lado a lado, metas, 261dias/52subtotais na fonte histórica, input de resultado diário monetário. Calendário novo é ano civil, segunda–sexta, exclusões explícitas, semanas civis; não preservar datas inconsistentes nem quantidade fixa261. Programação Q=daysWeek*52*monthsYear/12; f=eligible(start..Dec31)/eligible(Jan1..Dec31); targetPartial=(1+annualTarget)^f-1; Qpartial=Q*f; monthsPartial=monthsYear*f; taxas são as raízes correspondentes sem segundo redutor. Extrapolação real mensal=daysWeek*4 e anual=240 permanecem. Termômetro busca aproximada por aberturas projetadas, dias=dateEquivalent-reference; cores <14verde,14..29amarelo,>29vermelho, independente do texto avanço/atraso. Sem domínio válido mostrar motivo.

## Fluxo e dados
Uma configuração por conta+período+ano. Seleção Gerenciamento em memória independente da operacional Forex. Usar moeda confirmada, sem conversão. Abertura confirmada/proveniência: openingBook ou último fechamento anterior; revisar e confirmar, sem substituir fatos. Apenas resultado diário é editável; Salvar/Cancelar, prévia/confirmação, motivo para correção/anulação e efeitos posteriores. Escritor canônico recordAccountLedger; nenhum segundo armazenamento de resultados reais. Ausência não é zero. Declarar dia sem resultado exige ato explícito não contraditório, sem alterar programação. Fechamentos observados preservados. Curvas/metas não alteram políticaForex.

## Anos e fechamento
Ano atual refhoje, passado ref31/12, futuro ainda não iniciado. Fechamento anual somente após31/12 com pendências resolvidas, conferência e confirmação; guardar snapshot+dependências+at. Não encerra Forex. Correções conservam snapshot e exigem reconferência. Configuração opcional managementAnnual v1, histórico/snapshots e declarações no BackupCompleto/recuperação, sem planos automáticos nem exclusões de dados antigos.

## Entrega
Navegação → motor/paridade/tabela → fechamentos/integração. Verde/azul adaptados aos temas; tabela densa lado a lado ampla, trêscolunas+detalhes estreita. Testes sintéticos datas/leap/exclusões/ratios/13,14,29,30/negativo/zero/null, ano aberto/fechado/conflito/UNKNOWN, aliases/guardas/disponibilidade/seleção independente/nenhuma escrita em consulta. Quatro layouts, temas,320–1440,teclado,toque,zoom200,alinhamento2px. Contraprovas+revisão independente em controles, reconstruçãooficial,HTTP/offline/file/portátil eFULL. Semdependências,Git/publicação ou mudançaV11. Aprovação102anterior histórica.
