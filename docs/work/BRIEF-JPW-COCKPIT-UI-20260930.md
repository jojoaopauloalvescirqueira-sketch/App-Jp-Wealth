# JPW Cockpit — estabilidade do HUD e leitura do painel

- Solicitante: proprietário, 2026-09-30. Pedido: ampliar a janela central, aprimorar a hierarquia visual e corrigir a oscilação do bloco no gráfico.
- Raiz: `/private/tmp/jpw-cockpit-ui-20260930`; branch `codex/jpw-cockpit-ui-20260930`; base `deffc5061fe2eff3d83b6f6e742fa105ac9c5b06`.
- Risco: N1 (apresentação e navegação), autorizado pelo pedido atual. Não alterar fórmulas, coleta, estados financeiros, registros, preferências salvas ou negociação.
- A pasta principal `main` tem 151 mudanças anteriores alheias a este pedido; este checkout iniciou limpo. Commit, push, merge, instalação e publicação não fazem parte desta implementação.

## Compreensão e fontes

1. O JP Wealth organiza dados e apoia gestão de risco sem transformar a interface em autoridade financeira (`docs/governance/PROJECT-CONTEXT.md`, SHA-256 `37637ca60dd014e938d3156cba402bec3045b88d4ec5989d776ff23482dc9a27`). Esta tarefa serve à leitura confiável do Cockpit MT5.
2. `mt5/jpw-alavancagem-atual/` contém indicador, EA observador e auxiliares; o guia local (SHA-256 `cc0015b4a908818a21c7d103abcce19d11efbcdc2e3a94dbea0c7a73c4e21c2a`) separa matemática, coleta, apresentação e persistências. `Panel.mqh` define geometria; `Presentation.mqh` desenha HUD e janela.
3. No fonte de apresentação da base (SHA-256 `3acc2b12d9e9b1e88c801e7023bdb8c8497834d62a0ea8b892c7a3a41703340e`), `JPWRenderHUD` mede texto vivo e usa `max_text` para largura; um valor longo alterna lista/resumo. O timer torna a mudança intermitente. Depois, a geometria dependerá só do gráfico, fonte e preferência; valores ainda mudam, mas não o retângulo.
4. O Cockpit central solicita 760 × 620 px na base. Ampliação limitada à área do gráfico, superfícies agrupadas e hierarquia de título, valor, estado e motivo afetam somente objetos do gráfico, navegação e testes de apresentação. Fórmulas, unidades e dados persistidos permanecem os mesmos.
   A reserva horizontal do HUD limita-se a 45% do gráfico salvo o espaço mínimo do botão; em espaço excepcionalmente estreito, o texto cede lugar ao botão. O corpo dos cartões recebe a mesma navegação do título.
5. Preservar seis métricas, motivos `Current`/`Estimated`/`N/A`, valores integrais ou acesso claro ao detalhe, contraste claro/escuro, botão Fechar, teclado, cantos e rascunhos. O design usa composição e superfícies sólidas da filosofia X1 (SHA-256 `fcc11d3eab563f3464e84e5b8886ddb9ee4784cff75530702f07776d19e0dff7`); não insere animação em números financeiros.
6. Evidência: teste sintético de sequência de valores curtos/longos com geometria constante; gráfico redimensionado muda geometria; 320/390/1440 px, quatro cantos, DPI e navegação; testes focais e gate aplicável. Interação e medição nativas MT5 são uma verificação distinta.

## Delta e limites

- Arquivos de produto: `JPW_Alavancagem_Panel.mqh` e `JPW_Alavancagem_Presentation.mqh`.
- Testes: `tools/leverage_panel_test.py`, `tools/leverage_geometry_test.py` e apenas outros focais de interface se a regressão demonstrar necessidade.
- Sem novas entradas, preferência persistida, objetos financeiros, rede, dependência ou alteração de calendário/EA.
- O guia `mt5/jpw-alavancagem-atual/AGENTS.md` permanece idêntico ao da base: mudar uma instrução ou seus metadados seria uma revisão própria de control plane N3/A4, fora do pedido visual. O ZIP 1.10.2 o inclui como guia existente, sem alegar revisão do guia.
- O ZIP é artefato externo ignorado por `.gitignore`. Um release HTTP precisa transportar o arquivo exato e conferir seu SHA-256 com o manifesto; a página portátil incorpora bytes pelos geradores existentes. Este candidate local não equivale à publicação.
- Rollback: restaurar os dois includes e testes a partir de `deffc506`, sem tocar registros do terminal.
- Gate histórico da base: host específico verde após `deffc506`; full local anterior 50 PASS / 7 PRODUCT_FAIL; MT5 nativo não executado. Resultados novos serão relatados pelo candidate exato.
