# Planejamento — Consolidado organizado e tabela mensal compacta

> Para execução: superpowers:subagent-driven-development; construtor e crítico separados. Plano aprovado pelo proprietário na conversa. Reutilizar branch e candidato; sem commits/worktrees novas ou exclusão de evidências.

**Objetivo:** agrupar o Consolidado e substituir 18 colunas mensais por sete/três colunas com todos os dados preservados em detalhes.
**Arquitetura:** apresentação em03-ui.js/CSS local; engine e state intocados, APIs públicas existentes. Fonte monetária exclusivamente read-model; campos existentes reposicionados sem clones.
**Stack:** JavaScript clássico/CSS, Python/Playwright/Chromium e Node existentes; gerador oficial.

## Restrições globais

- Raiz CloudDocs real, branch codex/planejamento-patrimonial-20261020, HEAD ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34. Base a9713063cd241820 e117pendências preservadas.
- Sem engine/state, fórmulas, schema, migração, persistência nova, dependências, AI Memory, skills/plugin congelado, commit/merge/push/publicação. Três abas públicas; Comece aqui/formulário/Stoikus preservados.
- UI financeira não recalcula. Ausência/zero/vazio/pendente diferentes. Navegar/expandir/redimensionar não grava. Preservar confirmações, rascunhos, foco e regras de fechamento.
- Regra visual existente: desenho/texto internos, alinhamento declarado até2pxCSS, sem cortes/sobreposição e ordem visual/leitura/teclado coerente.
- Preservar96checks e98casos visuais anteriores; não enfraquecer critérios. N3 de testes em contrato dedicado, contraprovas e revisão. Incidentes históricos permanecem abertos conforme seus recibos.
- Artefatos só via tools/rebuild_monolith.py --refresh-manifest. Dados sintéticos, contextos isolados; não acessar perfil/cache/armazenamento do proprietário.

### Task 1: Proteções RED e contrato de apresentação

Arquivos permitidos desta tarefa: tools/planning_compact_table_test.py (novo), tools/ui_visual_quality_test.py (ampliar), tools/planning_parity_test.py (somente expectativa da grade antiga), tools/planning_ui_test.py (somente leitor de apresentação e duas localizações de current_month_journey, preservando todas as afirmações financeiras) e tools/planning_parity_layout_test.py (somente se necessário adaptar propriedade deliberadamente alterada, mantendo geom/foco). Não editar produto ou outros testes/runner.

- Criar regressões reproduzíveis para: três grupos do Consolidado; ano calendário atual destacado/rotulado independentemente projeção; grade7colunas quando largura útil>=900 e3 abaixo; ausência deoverflowX; detalhes completos; moedas agrupadas; fase/subtotais/120meses; estados calendário/fechamento separados; controle único e preservação de rascunho/foco em mudança de modo.
- Antes de alterar expectativa18colunas, rodar novos casos contraa971 e guardar falhas por defeitos concretos com fontes estáveis. Nenhum erro de setup/selector é RED. Depois adaptar o teste antigo mantendo todos os demais fluxos/asserts e prova de que os dados retirados do cabeçalho continuam acessíveis por mês.
- Integrar novos casos à execução default do verificador visual, conservando98IDs/guardas/casos anteriores. Runner e96IDs/comandos permanecem iguais. Reutilizar infraestrutura/fixtures; não duplicar os98casos em nova suíte.
- Cobrir4layouts×2temas,320–1440/telas baixas, largura útil899/900/901, zoom nativo200, toque/teclado/foco. Cenários: passadofinalizado/pendente, atualaberto/finalizado, futuro/provisório, semcâmbio, zero/vazio/negativo e valores grandes. Leitura/toggle/resize observamwriters/comandos reais e snapshot financeiro.
- Contraprovas pelo mesmo oráculo: overflow provocado, controle duplicado, ano errado ou mês passado não confirmado rotuladoFinalizado; cada violação deve falhar. Não contar testes antigos aprovados como prova do delta.
- Relatório task-1-report.md: resultados reais/exit/fontes/comandos/casos/limites, RED armazenado, diff exato de qualquer teste antigo, instruções para focais. Produto inalterado ao terminar esta tarefa.

### Task 2: Interface consolidada e mensal responsiva

Arquivos permitidos: src/js/30-accounting/06-planning/03-ui.js e src/styles/app.css somente; não editar testes/engine/state/generated. Ler task-1-report e executar focais novos.

- Consolidado: Posição confirmada (patrimônio/aportes/resultado e mês de fechamento); Projeção e objetivos (projeção/seletor doano/metasatuais/sonhos); Referências de câmbio (preçomédio/dólar e origem disponível). Títulos/espaçamento/separadores suaves, semcaixa por número. Manter gráficos/tabelas/comparações existentes.
- Visão anual: linha do ano local vigente em verde suave nos2temas, textoEm andamento, semconfundir seleção/período financeiro. Usar monthNow local existente; renovar emrender/ativação. Ano não exibido não gera linha artificial.
- Grade ampla: Mês (estado), Saldo inicialUSD, Resultado(percentual+USD/BRL), SaqueUSD, AporteUSD, PatrimônioUSD/BRL, Finalizado. US$principal/R$secundário somente onde já existem no modelo. Fase nos grupos dos12meses; situação juntoao mês; preservar120linhasmensais/subtotais de ciclos, distintos de anoscivis.
- Grade compacta: Mês, Resultado, Patrimônio. Abaixo900px úteis, independenteviewport/layout. Botão do mês abre detalhe inline; uma expansão por vez, comsaldo/percentual/saque/aporte/finalização. SemoverflowX emprincipal/detalhes, semellipsis/abreviação financeira, fonte legível; rolagemYpermitida.
- Detalhes em ambosmodos: Pago no mês, Câmbio utilizado, Preço médio dos aportes, Última cotação disponível, Variação cambial, Cobertura e situação do custo. Não inventar fontes/datas/conversões ausentes; indicar indisponibilidade.
- Mover nós/controles existentes entre slots em vez de clonar. Guardar identidades/foco/seleção/valores parciais e scroll. Se campo focado migrar para detalhe, expandi-lo antes. Delegação/comandos iguais; noresize só reposicionar, não salvar. Observador de largura com cleanup emdeactivate/dispose; nenhuma persistência/loop contínuo novo.
- Estado: atualverde/texto; passadofinalizado símbolo+Finalizado; passadonãofinalizadoPendente; futuroProjetado+pendências quando pertinente. Atualfinalizado mostraambos; seleção própria. Não finalizar pelo relógio, manter reopen/finalize/correções existentes.
- Preservar PDF próprio completo, não imprimir DOMcompacto como substituto. Nenhuma novaaba/APIs financeiras.
- Relatório task-2-report.md: delta/focais/limites e fontes; pedir reconstrução oficial ao controlador, não tocar gerados manualmente.

### Task 3: Revisão, construção, freeze e entrega

Controlador: contratos/brief/backup primeiro; revisão independente dos oráculos e produto, semautoria apresentada como teste humano. Revisar diff contraa971 e preservação das117pendências.

- CompletarGREEN/contraprovas/matriz após buildoficial; conciliar exatamente os testes velhos impactados semreclassificar primeira falha. Atualizar memória factual local de regressões e documentação contratual/estado/handoff autorizada, preservando histórico. Nenhuma mudança de instrução/AGENTS ou gate/runner adjacente.
- Validar HTTP/offline/file/portátil/PDF, engine/state/backup, menu/formulário/Notas e minigames/Bolsas. Congelar inputs oficiais, runtime, testes/runner/contratos, e executar quality_gate.py --tier full com96checks. Mudança material invalida prova afetada; saída real e timestamps vinculados ao candidate.
- Revisão independente final de escopo/fontes/resultados; relatórios/capturas/prévia versionada. Reavaliar HTTP byte-match, git diff --check e invariantes. Aceite visual humano separado; incidentes anteriores não se encerram por repetição bem-sucedida. Sem Git/publicação.
