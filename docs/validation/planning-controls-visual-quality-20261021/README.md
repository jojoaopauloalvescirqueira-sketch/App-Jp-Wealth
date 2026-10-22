# Planejamento — controles e qualidade visual

## Entrega local

[Prévia a9713063cd241820](http://127.0.0.1:8000/index.html?v=a9713063cd241820).

- **Stoikus:** as 13 ações foram organizadas em cinco grupos verticais, com texto à esquerda, rolagem, posicionamento junto ao botão e navegação por teclado.
- **Formulário:** Fechar usa SVG simétrico na área de 44 × 44 px; Ver sua previsão e os demais controles locais têm alinhamento próprio.
- **Regra permanente:** [UI-VISUAL-QUALITY](../../governance/UI-VISUAL-QUALITY.md), referenciada no AGENTS, exige medir textos e desenhos internos com tolerância máxima de 2 px CSS.
- **Verificação:** novo teste obrigatório em standard/full, preservando as 95 verificações anteriores. Cobertura inicial: Planejamento. As demais áreas permanecem explicitamente pendentes de seus próprios casos.

Perguntas, opções, fórmulas, rascunhos, confirmações, escritores e formatos de backup foram preservados. O teste da jornada observa escritores e comandos reais e confere ausência de gravação antes da confirmação.

## Antes e depois

| Achado reproduzido | Correção e prova |
|---|---|
| Menu horizontal de 636 px, sem os grupos/ordem aprovados | Cinco grupos verticais; largura até 320 px e 12 px de margem; teste de ordem, geometria interna, rolagem e teclado |
| Texto Ver sua previsão 5 px acima do centro | Conteúdo centralizado nos dois eixos; medição do texto real |
| Fechar tipográfico; teste antigo avaliava só sua caixa | SVG simétrico; teste mede desenho e área clicável. A caixa anterior estava centralizada, o que não provava o desenho |

[Menu anterior](captures/before-regression-stoikus-vertical-groups.png) · [Menu atual no desktop](captures/final-menu-1440-dark.png) · [Menu atual no celular](captures/final-menu-320-light.png) · [Formulário atual no celular](captures/final-form-390-light.png) · [Formulário atual no desktop](captures/final-form-1440-dark.png).

O mesmo verificador final rejeitou os três defeitos nos bytes anteriores preservados: [RED e proveniência](RED-FINAL-PROVENANCE.json), [resultados](RED-FINAL-COUNTERPROOF.json). No candidato corrigido, a execução focal passou em 98 de 98 casos: [FOCAL-GREEN](FOCAL-GREEN.json). Inclui quatro layouts, dois temas, 320–1.440 px, telas baixas, zoom nativo de 200%, foco, teclado, toque simulado e contraprovas deliberadamente desalinhadas.

## Situação da suíte completa

O resultado corrente está exclusivamente em [FULL-RESULT.json](FULL-RESULT.json), com [raw](FULL-RAW.json), [inventário](INVENTORY.md), identidades de fontes/runtime/testes/runner e [revisões](REVIEWS.md). NOT_RUN, falha ou execução parcial não aprovam o pacote. A execução final será registrada com seu próprio horário, identidade e saída real; resultados de tentativas diferentes não serão somados como aprovação.

1. [Tentativa 1](attempt-1/README.md):95 PASS / 1 TEST_HARNESS_FAIL, saída 1. O teste antigo contou o novo ícone de Fechar como sexto gráfico. A adaptação revisada troca somente o seletor para os cinco gráficos reais, preservando quantidade, dimensões e critérios. [Diff](LAYOUT-COMPAT-SELECTOR.patch), [contraprovas](LAYOUT-COMPAT-COUNTERPROOF.json) e 24 casos de regressão aprovados preservam o contrato.
2. [Tentativa 2](attempt-2/README.md):95 PASS / 1 PRODUCT_FAIL, saída 1. Caso F do teste de Alladin teve tempo limite ao carregar uma versão histórica, antes das verificações de rollback. Não foi demonstrado defeito financeiro, nem causa de ambiente; a classificação bruta permanece. A reprodução exata do caso F e o teste completo de Alladin sem alterações passaram, mas **a causa do incidente permanece desconhecida**. [Diagnóstico e limites](ALLADIN-TRIAGE-triage-result.json).
3. **Confirmação completa final: 96 PASS de 96, saída real 0**, sessão 62593. Início 2026-10-21T18:19:43-03:00; fim 2026-10-21T18:47:32-03:00. Mesmos bytes congelados, nenhuma alteração de teste ou tempo limite após a tentativa 2. Esta execução não encerra o incidente anterior nem aprova retroativamente as tentativas com falha. [Saída real](FULL-PROCESS-EXIT.json), [verificador visual 98/98](FULL-VISUAL-QUALITY.json) e recibo corrente vinculam esta prova ao candidato a971.

## Revisão e limites

Produto e regra/verificador receberam [revisão independente](REVIEWS.md), além dos testes automáticos. A [revisão final delimitada](FINAL-INDEPENDENT-REVIEW.md) aprovou a alteração e a execução final, mantendo o incidente e os aceites humanos separados. Capturas e medições do agente **não são aceite visual humano**. Safari, leitor de tela real, toque físico e compreensão do usuário permanecem provas próprias. A estrutura das instruções correntes passou com 101 contraprovas; isso não demonstra carregamento pelo cliente nem aceite humano da mudança N3.

Somente dados sintéticos foram usados. Sem novas dependências, configuração do AI Memory, alteração do plugin congelado, commit, merge, push ou publicação. [Conferência HTTP](PREVIEW-HTTP.json) comprova arquivos servidos, sem afirmar atualização do cache do navegador do proprietário.

## Preservação e recuperação

Base preservada: build 0dc016f9c7618385, branch codex/planejamento-patrimonial-20261020, HEAD ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34. Backup de 1.712 arquivos e 8 links, hashes e inventário local em .superpowers/sdd/planning-controls-visual-quality-20261021; 109 pendências anteriores preservadas.

Rollback delimitado: recuperar somente os arquivos deste delta pelo backup 0dc, comparar hashes/invariantes e reconstruir oficialmente. Preservar pendências e recibos; não executar reset/limpeza Git ou alterar armazenamento pessoal. O FULL 95/95 anterior e sua tentativa 93/95 permanecem evidências históricas da tarefa de proporções, sem transferir aprovação ao candidato atual.
