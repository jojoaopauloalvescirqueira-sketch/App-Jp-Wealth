# Parecer independente — site R2, bytes finais

**Escolha global: B. R2 PASS para clareza das instruções e percurso web de distribuição dos fontes.** B supera A na orientação de instalação e localização das Entradas para iniciante MT5. Os problemas impeditivos de versão/download, nomes em Ctrl+I, definição de isolamento e compatibilidade legada foram resolvidos no material final examinado. Isso não constitui validação ou instalação operacional no MT5: compilação e interação nativas continuam **NOT_RUN**.

## Evidência e independência

Examinei HTML completo e texto primário de A; HTML completo da área Stoikus, conteúdo de todas as cinco abas, detalhes recolhidos, guia e capturas de B. Os HTML completos foram lidos e processados para extração textual, preservada nos recibos desta pasta. Conferi os hashes do pacote comparativo e a identidade de `index.html` e guia vivos com B antes e depois do teste próprio.

Não consultei mapping nem pareceres de outro crítico. O cegamento é **parcial**: A identifica Position Sizer/EarnForex; B identifica Stoikus/JP Wealth/GENETRIX. Esses nomes, o idioma e a composição dos programas revelam autoria/produto. Não alego cegamento completo. A não tem screenshot externo renderizado; todas as preferências A/B são documentais. Examinei a apresentação móvel de B com suas capturas reais e com capturas próprias, sem inventar um resultado visual de A.

Os produtos são diferentes. Comparei qualidade e completude das instruções necessárias a cada um, sem premiar B por possuir mais componentes e sem comparar fórmulas, funcionalidades econômicas ou desempenho financeiro.

## Escolha por dimensão

| Dimensão | Escolha | Motivo |
| --- | --- | --- |
| Saber qual pacote escolher | **B** | O pacote de uso tem prioridade explícita, versão 1.22.1 e quatro programas identificados; engenharia e compilado ficam em detalhes separados. O download real foi confirmado. A também separa MT4/MT5 claramente, mas não explica o contexto de preparação do ambiente tão bem. |
| Localizar a instalação e copiar arquivos | **B** | B manda abrir a pasta de dados do MT5 correto, explica Parallels e define pasta separada antes da cópia. Proíbe substituição de MQL5 inteira e preserva os arquivos existentes. A informa Experts e lista dependências, mas presume a localização da pasta de dados. |
| Saber o que compilar e conferir | **B** | B nomeia os quatro .mq5, separa .mqh/imagens, explica F4/F7, 0 errors e geração de .ex5. A é clara sobre compilar apenas o arquivo principal, mas F7 e recuperação de erro ficam parcialmente na FAQ/vídeos. |
| Abrir o programa no lugar correto | **B** | B dá os caminhos do Navegador e a sequência Monitor no apoio → abridor no trabalho → Ctrl+I. A explica o que acontece ao anexar o EA, mas não fornece no texto principal de instalação o mesmo passo explícito para quem ainda não sabe anexá-lo. |
| Distinguir tarefa pontual e apresentação contínua | **B** | B explica repetidamente que o abridor termina, os indicadores permanecem e o Monitor precisa do gráfico aberto. A não precisa de roteiro para um script inexistente; a vantagem de B é tornar seu próprio percurso complexo verificável. |
| Coexistência com outros programas | **B** | B distingue um EA por gráfico, Monitor em apoio e dois indicadores no trabalho; o abridor preserva o EA do trabalho e não inicia o Monitor. A não explicita o efeito de anexar seu EA num gráfico que já possui outro EA. |
| Encontrar e entender as Entradas | **B** | Há caminho de acesso, 20 rótulos em português, identificadores secundários, padrões, unidades e significado de zero/vazio. A documenta muitos parâmetros e controles com detalhe, mas pressupõe mais conhecimento da localização dos inputs. |
| Recuperar falha do percurso inicial | **B** | B cobre script removido, abertura parcial, monitor ausente, .ex5, include, parâmetros e legado, indicando Experts e Ctrl+I. A tem FAQ útil e boa solicitação de versões/build/logs, mas sua recuperação inicial é menos abrangente. |
| Concisão e explicação da primeira apresentação | **A** | A descreve diretamente o estado inicial após anexar e os próximos controles. B ainda combina bastante conteúdo técnico, limites e estados antes do bloco completo de Entradas. Essa preferência é textual, sem julgamento visual de A. |

**Maior lacuna restante de B:** concisão e leitura das tabelas em 320 px. É uma melhoria editorial, não um impedimento do percurso verificado. O iniciante já consegue escolher o ZIP, localizar arquivos, compilar os quatro programas, saber onde anexar e encontrar parâmetros/erros.

## Correções verificadas

- **Versão e entrega coerentes:** texto observado, manifesto, guia e nomes dos ZIPs dizem 1.22.1. Os downloads reais foram capturados pelos botões do site; nome, tamanho e SHA-256 correspondem ao manifesto. O ZIP de uso possui quatro .mq5 e LEIA_PRIMEIRO idêntico ao guia, sem Tests/Lab ou EX5. O SDK também não contém EX5. Compilado continua desabilitado com motivo explícito.
- **Ctrl+I:** os passos de confirmação, Entradas e remoção usam `Stoikus · Cockpit 1.22.1`/versão do componente e `Stoikus · NoCuda Channels`. Os nomes técnicos permanecem nos lugares adequados, como arquivo e Navegador. Correspondem aos shortnames declarados no MQL; não afirmo que observei a lista dentro do MT5.
- **Isolamento:** a definição está visível antes do passo 1. Conta demo na mesma instalação é diferenciada de outra instalação com pasta de dados separada. Não é preciso abrir engenharia para entender esse requisito.
- **Legado:** o bloco longo está recolhido depois do percurso diário. A ajuda e o guia falam em nomes legados reconhecidos, pedem conferência independente de versão/compatibilidade/funcionamento e não prometem atualização pelo abridor.
- **Entradas:** os 12 rótulos de Conta, 5 de NoCuda e 3 do Monitor coincidem, na ordem, com os comentários de apresentação dos inputs MQL. Identificadores Inp* estão secundários no HTML. Defaults e limites revisados correspondem aos fontes; não houve alteração de lógica para acomodar a documentação.
- **Estados e dados:** `false / false / vazio` permite começar com cobertura desconhecida; não é apresentado como ativação financeira nem completude comprovada. Saúde técnica, qualidade de amostra e cobertura são diferenciadas. Dados, locks, estudos e preferências continuam preservados; limpeza de programas exige inventário/backup e identificação explícita. Não há instrução para apagar MQL5/Files ou resetar registros.
- **Limites nativos:** a documentação conserva UNVERIFIED_NATIVE, NOT_RUN, instalação NOT_RUN e aceite INCONCLUSIVE/BLOCKED. Registros antigos de compilação estão identificados como históricos e não homologam a revisão atual. Presença/listagem do programa não é descrita como prova de dados atuais ou funcionamento.

## Recibos próprios dos bytes finais

O [recibo independente](/private/tmp/jpw-stoikus-usability-evidence-20261013/site-critic-R2/independent-receipt.json) contém conferência dos hashes de todos os arquivos comparativos, 20 inputs, 15 verificações de abas e downloads reais. O SHA-256 do HTML final de B é:

`2ca2f277177cb8673420e19b8195300ac77cae30dab81db5b5b3e5df5430e61b`

| Artefato baixado pelo site | Tamanho | SHA-256 |
| --- | --- | --- |
| JPW_Stoikus_Uso_Fontes_v1.22.1.zip | 441.516 bytes | `5b2c7ca40736dda976fe97a91a2677d190eb1ccfdf9527703fd471ee702a11e5` |
| JPW_Stoikus_Fontes_v1.22.1.zip | 773.801 bytes | `03ccb37824175511108b36e9abb5c9fa0dc28d89a338caea1dc7bf02508b9cae` |

- Visão geral, Instalar, Recursos, Validação e Ajuda abriram por seus controles em **1440, 390 e 320 px**, com um painel ativo e sem overflow horizontal da página. As cinco abas também ficaram acessíveis pelo teclado. Em largura pequena a faixa de abas rola horizontalmente; o acesso foi exercitado, não presumido pela primeira imagem.
- As três tabelas podem ser abertas e recolhidas. Rótulos portugueses estão legíveis e os nomes técnicos são menores. A leitura é longa em 320 px, especialmente no primeiro rótulo de Conta, mas não há corte horizontal do conteúdo.
- O teste próprio não registrou pageerror nem alteração de S/localStorage. HTML e guia permaneceram idênticos aos bytes comparativos após o percurso e os downloads.
- O [recibo do link corrigido](/private/tmp/jpw-stoikus-usability-evidence-20261013/site-critic-R2/touch-link-receipt.json) confirma alvo de aproximadamente **256 × 44 px** em 390 e 320 px. O clique abre Instalar e a seção de uso esperada, sem overflow. Não resta o alvo de 18 px dessa correção.
- O teste de uso fornecido foi executado independentemente e passou para conteúdo, 20 rótulos, detalhes por teclado, ajuda, mobile e preservação dos dados web. Essa execução precedeu o ajuste final de uma classe do link; os recibos acima foram executados depois e correspondem ao HTML final.

Os testes usaram servidor loopback e Chromium local. As gravações são apenas scripts/recibos/capturas da crítica nesta pasta e arquivos temporários de download. Não executei geradores, rebuild, MT5, instalação operacional ou Git mutante. Não reivindico resultado da suíte completa em execução por outra tarefa.

## Melhorias P3, sem bloqueio

1. **Tabela móvel:** a primeira coluna ocupa 36% e os rótulos longos produzem muitas linhas em 320 px. Uma apresentação por entrada empilhada ou uma distribuição mais favorável ao rótulo pode reduzir a leitura, preservando todos os rótulos e unidades. Não abreviar o rótulo principal a ponto de perder a correspondência com o fonte.
2. **Compilação diária:** o parágrafo que manda compilar somente quatro programas ainda menciona Supervisor, Observer, Accountant e rollback. Esses nomes cabem melhor no detalhe de engenharia; o comando inicial já é suficiente para o uso diário.
3. **Entradas e interpretação:** há bastante explicação de sete métricas e estados antes das tabelas completas. Um atalho direto para Entradas após abrir os indicadores ajudaria o primeiro uso. A ajuda já oferece um caminho funcional, portanto não é uma lacuna impeditiva.
4. **Ramo USC:** a dependência de engenharia está declarada, mas poderia oferecer um salto direto para obter/copiar/compilar o utilitário antes de mandar executá-lo. Não retirar o bloqueio de unidade por ausência do perfil.

**Conclusão:** B vence a referência A no escopo solicitado e não apresenta P1/P2 aberto no percurso web de fontes examinado. Os P3 não justificam outra rodada para esta tarefa. O resultado é documental/web; compilação, cliques, desenho, persistência e instalação no MT5 dos mesmos bytes permanecem **NOT_RUN**.
