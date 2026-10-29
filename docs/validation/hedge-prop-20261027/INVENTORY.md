# Inventário da entrega — Hedge Prop Firm

## Produto

- Nova entrada Mesas Proprietárias antes de MiniGames; primeiro tópico Hedge Prop Firm.
- Engine puro de uma/duas avaliações e financiada, com reembolso explícito e custos por caminho.
- Interface em memória com exemplos opcionais, razões não executáveis, orçamento incluindo taxa e fontes datadas.
- Guia Dante aditivo; descarte na finalização; controles de navegação e disponibilidade preservados.
- Dois scripts locais registrados no manifesto, precache e portátil pelo gerador oficial.

## Preservação

Baseline recuperável em /private/tmp/jpw-hedge-prop-20261027, hashes de3310 arquivos. Nenhum arquivo baseline foi removido. Apenas compartilhados autorizados receberam delta aditivo; restantes conservaram bytes. preservation-and-gate.json é a fotografia inicial, preservada antes dos ajustes posteriores dos verificadores. O confronto após a tentativa5 está em [FULL5-AUDIT.json](FULL5-AUDIT.json):28caminhos baseline alterados,1621inputs congelados sem delta e86protegidos idênticos. Contas, períodos, ledger, seleção operacional, regras V11, backups, normas, skills e AGENTS não são alterados por esta tarefa.

113 checks anteriores preservados; três entradas novas em standard/full: hedge-prop-engine, hedge-prop-browser, hedge-prop-distribution.

## Achados e correções

1. RED: rota ausente. GREEN: rota/host e navegação independente.
2. RED: prejuízo de meio centavo aparecia sem sinal. GREEN: −US$0,01 e classe negativa.
3. RED: mensagem de validação deslocava campos da mesma linha. GREEN: trilhos compartilhados no grid; comparação geométrica em2px.
4. RED: intenção de montagem pendente podia ressuscitar UI descartada. GREEN: montagem somente no ato de entrada aceita, sem intenção tardia.
5. Juiz: agrupamento pela coordenada do input podia aceitar deslocamento24px. Corrigido para pai semântico e contenção; duas contraprovas permanentes rejeitadas.

Falhas intermediárias de coleta/redação/hash dos testes novos permanecem em browser-triage.json; não são apagadas pelo GREEN. Um teste local suplementar antigo, navigation_local_contract_test.py, fora do FULL, também falha contra a fonte baseline por expectativas de eventos/alias anteriores ao Gerenciamento/retirada Nocuda. A única adição experimental deste delta nesse teste foi revertida; arquivo permanece byte idêntico ao herdado. Diagnóstico/recibo baseline estão em /private/tmp/jpw-hedge-prop-20261027/baseline-local-nav-result.txt, sem correção adjacente nesta tarefa.

## Estados de validação

Engine15/15, contraprovas matemáticas4/4, browser12grupos/80combinações/5contraprovas e distribuição4/4 possuem recibos próprios. A tentativa5 executou116checks:114PASS,1PRODUCT_FAIL e1TEST_HARNESS_FAIL; não está aprovada. Os três checksHedge passaram, incluindo8casos de zoom nativo200%. Alladin e Proporções passaram depois em focais originais com proteção temporária contra suspensão. Esses focais não substituem a repetição integral nem encerram as causas históricas. Aceite visual humano separado.
