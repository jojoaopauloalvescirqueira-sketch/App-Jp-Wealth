# Stoikus 1.22.1 — uso diário

O proprietário pediu a correção da experiência de instalação, configuração e abertura conjunta de Conta e NoCuda. Escolheu o Position Sizer da EarnForex como referência concreta de clareza: https://www.earnforex.com/metatrader-expert-advisors/Position-Sizer/. Este pedido autoriza a implementação local dessas correções; commit, integração na pasta original, publicação e negociação continuam separados.

## Resultado

Oferecer um pacote de fontes de uso com Monitor, Conta, NoCuda e uma ferramenta pontual para abrir os dois indicadores no gráfico de trabalho. Incluir todas as dependências e os recursos necessários. O pacote de engenharia conserva testes, laboratório, utilitários, harness e produtores legados. Não mover nem apagar os arquivos existentes na instalação do proprietário.

As Entradas dos três componentes ganham grupos e descrições em português, unidades e explicação de zero/vazio. Identificadores, tipos, ordem relativa e valores padrão permanecem iguais. Erros de inicialização explicam a correção necessária. Não reinterpretar declarações de cobertura como permissões de ativação.

A abertura conjunta verifica a presença dos indicadores antes de criar handles, aceita nomes antigos compatíveis e preserva configurações e estudos já carregados. Não substitui EA, não aplica template, não fecha gráficos, não negocia nem arma Supervisor. Falhas parciais são explícitas e a repetição não cria duplicatas.

O guia começa por dois gráficos: Monitor em apoio mantido aberto; Conta e NoCuda no trabalho. Explica o script que termina após abrir os painéis, os estados parciais e o bloqueio do Fibonacci importado. O site mantém as cinco abas e apresenta o pacote de uso antes da engenharia, com integridade verificada para cada download.

## Identidade e evidências

Produto 1.22.1, MQL 1.221, cálculo 1.9.0. Pacotes anteriores permanecem byte-idênticos. Geradores oficiais produzem novos ZIPs, manifesto, build global e portátil. A cópia 1.22.0 foi congelada em /private/tmp/jpw-stoikus-usability-baseline-20261013 antes de qualquer mudança.

## Aceitação

- Zero testes, laboratório, Supervisor ou produtores legados no pacote de uso; dependências locais completas.
- Todos os inputs originais preservados, com explicação pública e padrões utilizáveis.
- Abertura conjunta idempotente; falhas de criação/anexação, instalações legadas e componentes já presentes verificadas sem apagar estado existente.
- Download de uso e de engenharia verificados por tamanho e SHA-256, incluindo recusa de corrupção.
- Casos e oráculos existentes preservados; suíte de alavancagem e quality gate executados sobre candidato identificado.
- Construtores e críticos distintos. Comparação A/B da clareza de instalação e Entradas com referência real, registrando pistas de identidade e limitações.
- Compilação e interação MT5 somente passam com recibos nativos da revisão exata. Sem ambiente nativo, registrar NOT_RUN e entregar provas locais sem declarar liberação operacional.
