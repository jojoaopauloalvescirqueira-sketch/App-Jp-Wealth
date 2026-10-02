# Tabela de posições — JPW Cockpit 1.15.0

Base local 1.14.0 preservada, 593/593 hashes conferidos. A captura demonstra navegação de cartões e ausência de fechamento, mas não comprova a identidade dos EX5 instalados.

Substituir cartões grandes por tabela compacta na aba Stops, com todas as posições disponíveis e rolagem interna. Escopo da conta agrupado por símbolo exato e direção; filtro Operação conserva a atribuição do risco dos stops. Nenhum total de uma tese será ampliado para outro instrumento/direção. Ticket completo, volume remanescente e contribuição nocional/equity têm validade independente do SL e do EA.

A contribuição usa o mesmo núcleo, preços, conversões, escala contratual e equity da leitura da alavancagem total. Buy e Sell não se compensam. Netting representa posição agregada. Pendente não é exposição executada. Soma antes do arredondamento precisa reconciliar; ausência de dados será N/A.

Corrigir o fechamento criando objeto exclusivo para o cabeçalho; manter rodapé e Esc. Desenho, resize e navegação não coletam nem gravam dados financeiros. Revisões do NoCuda, Signal Copy e schemas permanecem intactos.

Validação: caracterização, replay financeiro e de interface real, focais, suíte MT5, full bruto, freeze e auditoria independente. Compilação e interação nativas somente em MT5 isolado utilizável; sem prova exata serão NOT_RUN. Fontes apenas, sem EX5 e sem prontidão operacional. Sem Git, publicação, instalação operacional ou envio a terceiros.
