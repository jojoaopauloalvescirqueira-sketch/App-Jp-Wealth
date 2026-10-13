# Stoikus 1.22.1 — prova nativa pendente

Estado em 2026-10-13: compilação MQL5 e execução MT5 **NOT_RUN**. O comando de execução no Windows foi recusado pela edição instalada do Parallels, que exige Pro ou Business para essa função. Testes C++ com APIs simuladas e testes do navegador não cobrem o ciclo real dos indicadores.

Use a instalação MT5 de demonstração com pasta de dados separada descrita em `STOIKUS_USO_DIARIO.md`. Este roteiro registra um ensaio futuro; não é um recibo de execução nem autorização para operar.

## Identificar os mesmos bytes

- Pacote de uso: `JPW_Stoikus_Uso_Fontes_v1.22.1.zip`, SHA-256 `5b2c7ca40736dda976fe97a91a2677d190eb1ccfdf9527703fd471ee702a11e5`.
- SDK: `JPW_Stoikus_Fontes_v1.22.1.zip`, SHA-256 `03ccb37824175511108b36e9abb5c9fa0dc28d89a338caea1dc7bf02508b9cae`.
- Build MQL: `b4031d96f5d180aa35c6285ad8baec97f017d162e7ea0499d38df339571d81db`.
- Produto/MQL/cálculo: `1.22.1 / 1.221 / 1.9.0`.

Conferir o hash do ZIP antes da extração e dos fontes contra `manifest.json`. Registrar versão do terminal, versão/arquitetura do compilador, comandos, fontes e SHA-256 de cada EX5 produzido. Um executável anterior ou apenas o número da versão não satisfaz esse vínculo.

## Compilação e comportamento

1. Compilar Monitor, Conta, NoCuda e Abrir Painéis, separadamente, com todas as dependências do mesmo pacote. Registrar logs integrais, zero erros, avisos e os quatro hashes EX5. Não distribuir esses executáveis sem revisar o recibo.
2. Na instalação demo, manter negociação algorítmica desativada e nenhum Supervisor armado. Anexar Monitor a um gráfico de apoio, usando false/false/evidência vazia. Confirmar partida e motivos de dados pendentes, sem converter ausência em completude.
3. Num gráfico de trabalho vazio, executar Abrir Painéis. Confirmar em Ctrl+I os nomes curtos, renderização, botões, timers e resposta a cliques de Conta e NoCuda **após o script terminar**. Isso prova o ponto que o teste host não consegue provar: `OnInit`/`OnDeinit`, referências e objetos reais após `IndicatorRelease`.
4. Personalizar Entradas dos dois indicadores e criar estudos sintéticos. Registrar antes/depois: indicadores, EA já presente, objetos manuais/Fibonacci, preferências e estudos. Repetir o abridor e confirmar nenhuma recriação, substituição ou alteração desses estados. Também testar sub-janelas e indicadores alheios.
5. Remover apenas o companheiro ausente em um fixture próprio, simular EX5 faltante e falha de inicialização. Confirmar mensagem visível com erro, sucesso parcial preservado e retomada sem duplicação. Testar instância reconhecida porém inativa; presença não deve aparecer como confirmação de saúde.
6. Em fixture separado, testar nomes legados e misturas: nenhum segundo produtor de conta junto ao Monitor, aviso de versão e preservação pelo abridor. A atualização de uma instância antiga é manual e separada; não inferir compatibilidade pelo nome.
7. Conferir Entradas no terminal: 12 Conta, 5 NoCuda, 3 Monitor; grupos, rótulos, limites e padrões preservados. Confirmar PERIOD_CURRENT recusado pelo NoCuda e cadência solicitada com os limites reais de 30 s/5 s, sem exigir cronômetro exato do timer.
8. Confirmar que Fibonacci importado continua `UNVERIFIED_NATIVE`, que os motivos de risco indisponível continuam explícitos e que não houve envio de ordem nem alteração de schema, bancos ou locks.

Guardar capturas e logs com identificação do candidato e estado de cada caso: PASS, FAIL ou NOT_RUN. Falhas exigem correção e nova prova dos bytes resultantes. Instalação operacional e aceite do proprietário continuam etapas separadas.
