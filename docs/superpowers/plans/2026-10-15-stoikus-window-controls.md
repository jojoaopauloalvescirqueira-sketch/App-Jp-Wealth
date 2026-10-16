# Stoikus — alinhamento, proporções e controle das janelas

Plano autorizado pelo proprietário em15/10/2026; implementação local, sem commit, push, site, instalador ou publicação.

## Restrições globais

- Base1.22.3, candidato1.23.0/MQL1.230, cálculo1.9.0. Worktree existente /private/tmp/jpw-stoikus-continuity-20261014, branch codex/stoikus-continuity-20261014; preservar trabalho preexistente.
- Preservar assinatura Stoikus by JP Wealth, identidade NoCuda, fórmulas, bancos/locks, estudos, permissões, produtores e oráculos financeiros. Nenhuma negociação/armamento.
- Apenas preferências visuais novas e separadas; legadas intactas, máscaras/IDs/atalhos1–7 preservados; carregar/pintar não grava.
- Host, compilação, interação nativa e aceite humano são evidências distintas. Windowsx64 depende de ambiente disponível.

## Task 1: Estudo visual e prévia

Criar inventário das telas e nova prévia navegável independente, dados fictícios identificados, temas claro/escuro, estados normal/carregando/bloqueado, textos longos e gráficos pequenos. Aplicar grade4/8/12/16, Arial10pt resumo/11pt painéis, alvos36px lógicos, marca aprovada. Conta720x520, NoCuda680x500, máximo85%área; cartões e conteúdo alinhados à esquerda, badges proporcionais, descrições até2linhas+detalhes, valores completos, nav6emlinha/3+3/seletor. Pager comum, ações separadas. HUD compacto280px largura manual até480 ou área, altura automática; leverage+stoprisk+qualidade/escopos, modoCompleto sete métricas, minimizarConta, mover, transparência0–100passos10 padrão30 no fundo com texto opaco. Consulta sólida, movimento e resizebidirecional, minimizar distinto de cancelar. Criar teste de interação/overflow da prévia com ferramentas existentes. Revisão independente.

## Task 2: HUD e controles

Comprovar viabilidade nativa ARGB/clique/DPI/reserva primeiro, sem mascarar ambiente indisponível. Implementar resumoCompacto/Completo, respeitar máscara existente inclusive0, canonicalIDs0leverage/5risk, e fallback single-metric separado do modoCompacto. Minimizado botãoConta sempre acessível e independente da janela. Largura inicial280 lógica, máximo480ouárea, mínimo medido, altura natural; fallbackbotão quando não cabe. Arrasto cabeçalho e larguraborda, boundsclique independentesalfa. Canvas ARGBreal fundo30%transparente default, ajuste0–100/10, textocontrolesopacos. Recursos reutilizados/limposporowner, fallbackopacoexplícito sefalhar. Não deixar interação do gráfico alterada nofim/cancel/deinit. PreferênciasvisuaisV1separadascodecV3legado, unidadeslógicasnovas semreinterpretar offsets físicos anteriores, validação/preservação inválidos, gravar só término gesto/ação explícita, semaplicarrascunhos financeiros. Atualizar detecção da reservaHUDnoNoCuda para bitmap+rectanglelegado e retângulo real mesmo100%transparente/recolhido. Novos testes comportamentais red→green com MQLreal traduzido/seams nativos honestos e falhas derecurso/persistência/gestos. Revisão independente.

## Task 3: Janelas completas

Aplicar grade, medidas/fonte válida/DPIúnico e composição da Task1 em Conta seisabas, Histórico, NoCuda manual/Fibo e diálogos/estadosMonitor. Headermarca+título+controles centralizadosverticalmente, títuloscardesquerda, badgesmedidos, descrição2linhas+detalhe, valoresunidadesescopos completos. Nav6linha/3+3/seletor, pageralinhadoeaçõesseparadas. Conta720x520/NoCuda680x500novospadrões85%, preservarvisualvalidolegado. Movimento porheader e resizebordas comclamping/paginaçãoeuma coluna ondepreciso, minimizar/restaurar consistente, preservar rascunhos emRAM/estudos/auditoriaativa; reapresentar semaplicardraft e revalidarcontextofinanceiro. Somente umownerteclado, Cancelar/Fechar mantêmsemântica. Preferênciasvisuaisporgráfico/template nãoincluemrascunhosfinanceiros. Regressões DPI100/125/150/200%, fonts, longtext/largevalues, gráficospequenos, foco/teclado/mascaras, falhas, auditoria, fontemudouantesconfirmação. Revisão independente.

## Task 4: Candidato e validação

Versão1.23.0/MQL1.230, buildID/hash próprios calculados peloshelpersoficiais; não alterarmanifest/R4publicado nemgeradoresjuízes para forçaraprovação. Gerar pacotesSDK/daily separados com inventário transitivo e novosheaders/helpersdeUI, preservarbytespacoteshistóricos. Rodar leverage_suite.py --scope host, regressões novas e identidadereprodução dezip; interpretar falhasdojuizliteral quando contratoUIfoiaprovado em trilha própria semenfraquecercasosfinanceiros. Compilar4programasemstageguestisolado usandoMetaEditorinstalado, hashsource/EX5/logs/build e ensaioMT5demo separado, nenhum EX5distribuído sem provaexata. Windowsx64NOT_RUN seindisponível. Guia de ensaio novice e relatório evidências/limites, aceitehumanopendenteatéteste. Revisão integral/fingerprintfinal. Integrarsite/instalador/publicar açõesseparadas.

## Precisão de leitura do limite inicial

Texto do plano do proprietário: “Usar tamanho inicial de 720×520 pixels lógicos para Conta e 680×500 para NoCuda, limitado a 85% do gráfico disponível. Preservar configurações válidas existentes.” O teto de 85% aplica-se aos novos padrões iniciais. O resize explícito e configurações legadas válidas podem usar a área inteira disponível, sempre com retângulo contido no gráfico. A maquete HTML é mais restrita durante resize; isso não amplia nem reduz os contratos nativos ou a escolha Maximizada já existente.
