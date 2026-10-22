# Qualidade visual obrigatória do JP Wealth

Fonte: plano humano aprovado [Planejamento — controles e regra visual](../superpowers/plans/2026-10-21-planning-controls-visual-quality.md). Control plane N3/A4: [regra](../work/CHG-JPW-UI-VISUAL-RULE-20261021.md) e [verificador/gate](../work/CHG-JPW-UI-VISUAL-GATE-20261021.md). Esta regra não amplia autoridade nem substitui fontes financeiras, testes anteriores ou aceite humano. O plugin JP Engenharia permanece congelado.

## Contrato para cada superfície de interface alterada

1. Botões comuns centralizam seu conteúdo nos dois eixos; opções de menu alinham texto à esquerda; botões de ícone centralizam o desenho na área clicável. Medir conteúdo interno, incluindo texto e desenho SVG, não somente a caixa externa.
2. Centralização e alinhamentos declarados admitem desvio máximo de **2 px CSS**, inclusive com zoom. Nenhum controle pode ficar sobreposto, cortado ou inacessível; rolagem intencional deve permitir alcançá-lo integralmente.
3. Ordem visual corresponde à leitura e navegação por teclado. Elementos equivalentes mantêm espaçamentos consistentes; grupos diferentes podem ter separação própria identificada. Exceções visuais deliberadas precisam de contrato e oráculo próprios, não de tolerância ampliada silenciosamente.
4. Conferir estados vazio, preenchido, erro, aberto, selecionado e indisponível pertinentes ao delta. Incluir teclado/foco, largura móvel, altura baixa, temas/layouts afetados, zoom nativo200% e movimento reduzido. Não substituir zoom do navegador por transform CSS.
5. Cada alteração identifica componente, fonte do critério, estímulo, medição, execução e limites. Nova regra demonstra caso válido e violação representativa rejeitada pelo mesmo oráculo. Ausência de casos, skip, fixture quebrada ou receipt antigo não comprova aprovação.

## Cobertura executável e pendências

O verificador reutilizável [ui_visual_quality_test.py](../../tools/ui_visual_quality_test.py) mede a cobertura inicial de **Planejamento**: menu Stoikus, formulário, fechar, previsão, controles auxiliares e rodapé nos casos declarados pelo teste. Ele é obrigatório em **standard** e **full**, mantendo as95 verificações preexistentes.

**Dashboard, Research, Forex, Finanças Pessoais, Alladin, Ferramentas/MiniGames/Bolsas Globais, Configurações, Notas e demais superfícies continuam pendentes de casos próprios neste verificador.** Ter regra escrita não significa cobertura automatizada integral do legado. Ao modificar essas superfícies, acrescentar os casos pertinentes e evidenciar seus estados conforme a autorização vigente; não promover a cobertura sem execução real. Testes antigos continuam obrigatórios e podem demonstrar outras propriedades.

## Procedimento e evidência

Antes da correção, reproduzir o defeito com dados sintéticos quando praticável. Executar o mesmo estímulo e expectativa após a correção. Revisar capturas antes/depois e medições internas, conferir ausência de gravações e invariantes funcionais. Identificar candidate/build, hashes das fontes, teste e configuração; mudanças materiais invalidam provas afetadas.

Executar `python3 tools/ui_visual_quality_test.py --out <diretório-de-evidência>` e a suíte obrigatória no pacote final. O runner propaga saída nãozero como falha; o check não é aprovação de todos os pixels/superfícies. Revisão independente compara fonte aprovada, comportamento e qualidade do próprio oráculo. Teste humano e aceite visual permanecem separados da automação.

Instruções, critérios e gates somente mudam por CHG dedicado, autorização específica, contraprovas, comparação antes/depois, auditoria independente e aceite humano. Não remover checks nem reduzir expectativas para obter verde. Relatar PASS/PRODUCT_FAIL/TEST_HARNESS_FAIL/ENVIRONMENT_ERROR/BASELINE_FAIL/NOT_RUN conforme evidência, preservando tentativas anteriores.
