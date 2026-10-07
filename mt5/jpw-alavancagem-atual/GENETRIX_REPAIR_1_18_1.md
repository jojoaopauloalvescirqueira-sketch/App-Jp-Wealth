# GENETRIX 1.18.1 — candidato de correção e design

Revisão isolada da base integrada `a47ebee5a041e990b627dd3319f382ff0fc14add`. Não é certificação acadêmica. Produto 1.18.1, MQL 1.181, cálculo financeiro 1.9.0. A versão não comprova o executável instalado. Verifique o manifesto, hashes e o relatório externo antes de usar.

## Comportamento corrigido

| Área | Comportamento desta revisão |
| --- | --- |
| Histórico: resumo | Contagens, cobertura e máximos pertencem ao mesmo snapshot de leitura. |
| Histórico: registros | Tipos, categorias, vínculos e metadados recebem validação adicional; inconsistência é recusada sem reset ou rehash. |
| Histórico: cobertura | Origem temporal inválida é recusada; indisponibilidade não vira zero. |
| NoCuda: Pausar | A sessão pausa imediatamente mesmo com gravação recusada; o aviso distingue pausa local e durável. Retomar exige ação explícita. |
| NoCuda: visibilidade | Falha mantém a obrigação de restauração da origem identificada; timer retenta sem transferir a obrigação à nova seleção. |
| Histórico: navegação | Mudança de conta, filtro, página ou detalhe invalida dados e ações anteriores. A resposta é aceita somente para o pedido vigente. |
| Ciclos compensados | Cópia por elemento preserva campos string da estrutura; validação nativa ainda pendente. |
| ATR | O ATR fechado é relido em cada captura, incluindo correção do conteúdo sem mudança nos metadados da série. |
| Stop risk | Mantém fórmula e denominador; evita overflow intermediário quando o percentual final é finito. |

## Como consultar

1. Abra o Cockpit pelo botão Genetrix e escolha **Histórico Pessoal**. Ocultar a janela não interrompe o EA observador.
2. Confira conta atual/histórica, horário UTC da consulta e presença do produtor. Consulta histórica não troca a conta operacional.
3. Em **Resumo**, confira o início da cobertura, episódios e máximos `Current` e `Estimated`, apresentados separadamente. Eles são máximos observados desde a ativação, não máximos absolutos da vida da conta.
4. Use ocorrências e recordes para consultar registros e detalhes. Aguarde a leitura após navegação; linhas antigas deixam de estar selecionáveis.
5. Diferencie **carregando**, **nenhuma ocorrência confirmada** e **consulta indisponível**. A última não demonstra ausência de episódios ou exposição.
6. CSV é para consulta; backup JSON v1 é para preservação e reconstrução em sandbox. Nenhum registro real é substituído automaticamente.

Na pausa NoCuda, “gravação não confirmada” significa que a interrupção é apenas desta sessão. Antes de reiniciar, confirme a gravação. A restauração de objetos depende das APIs do MT5 e da identidade observável (nome e horário de criação); recriações com a mesma identidade temporal podem ser indistinguíveis. Ao remover o indicador, um aviso de restauração pendente exige conferência manual porque não há mais timer para retentar.

## Integridade e desempenho

Schema SQLite 1 e backup JSON v1 permanecem. Não há migração, limpeza ou recalculação silenciosa dos hashes antigos. O digest legado sela o payload; o envelope recebe validação semântica, **não um novo selo criptográfico integral**. Uma adulteração coerente de todos os campos não é comprovadamente detectável nesta revisão.

As leituras auditam o journal com limites de 100 mil registros e 2 segundos por auditoria. Isso prioriza recusa explícita e pode tornar uma consulta indisponível em histórico grande. O limite não garante latência total de coleta; a medição no MT5 real é pendente. Falha ou capacidade insuficiente preserva registros. Não há eliminação automática do histórico.

## Validação e uso controlado

O relatório externo acompanha baseline, critérios congelados, falhas brutas, testes dos autores, revisão independente, tentativas de falsificação e hashes. Testes locais exercitam corpos MQL em adaptadores host e SQLite; não substituem compilação MQL nem comportamento do terminal/corretora. Testes antigos que exigem reuso de dados ou ATR em cache devem ser triados sem ocultar seus resultados.

Compilação nativa, `.ex5`, popup, som, inspeção do gráfico e execução em MT5: `NOT_RUN`. Não distribua binário de outra versão como se correspondesse a estes fontes. Para validação futura, use terminal isolado, conta demo dedicada e os percursos críticos em três sessões novas; conserve todas as tentativas. O supervisor 7x continua separado, padrão observação e armamento explícito demo. Esta revisão não arma o supervisor, coloca SL, fecha posições, altera normas ou homologa `PENDING`/`NOT_HOMOLOGATED`/`BLOCKED`.

## Rollback

A instalação operacional não foi alterada. Para abandonar o candidato, deixe de utilizar esta pasta e retorne aos fontes congelados da base preservada. Se futuramente instalar em ambiente isolado, guarde os fontes e binários exatos anteriores; remova apenas os programas candidatos de teste e recoloque a versão verificada. Preserve os bancos e backups: não apagar, substituir ou rehash para “voltar versão”. O backup de fontes da baseline e o manifesto externo documentam os bytes anteriores.

## Referências técnicas

- [MetaQuotes — ArrayCopy](https://www.mql5.com/en/docs/array/arraycopy): restrições de cópia de estruturas que exigem inicialização.
- [MetaQuotes — tipos e classes](https://www.mql5.com/en/docs/basis/types/classes): inicialização de membros string.
- [MetaQuotes — DatabaseTransactionBegin](https://www.mql5.com/en/docs/database/databasetransactionbegin): transações para leitura consistente.
- [MetaQuotes — OnCalculate](https://www.mql5.com/en/docs/event_handlers/oncalculate): mudanças de dados históricos e recálculo.
