# Domínio de dados e persistência

Parta do contrato vigente e dos consumidores reais. Vincule cada regra nova/alterada à fonte normativa e a uma proteção executável identificável. Caracterização de código legado não vira norma automaticamente. Preserve tipos, unidade, precisão, identidade, versão, relógio/datas, erros e idempotência. Ausente, vazio, zero, nulo e inválido podem ter significados distintos. Incompatibilidade requer cobertura aprovada; não silencie uma lacuna estreitando o domínio por conta própria.

Quando a mudança cruza uma fronteira de representação, confronte **valores admitidos → transformação → valores armazenados → valores recuperados**. Escolha sondagens pelas operações presentes:

- Tipo validado e tipo persistido podem divergir por coerção, adaptação ou serialização. Se subclasses/protocolos de conversão são aceitos, confira como se vinculam ao backend. Não suponha que uma validação por tipo garanta a representação final.
- Faixa e precisão da linguagem podem exceder o backend. Confira extremos pertinentes, overflow, arredondamento e comportamento de rejeição documentado.
- Texto não vazio pode ter restrições de codificação, normalização ou tamanho. Teste as fronteiras aplicáveis ao formato de armazenamento.
- Identidade/idempotência deve sobreviver à transformação e à reabertura: mesmo pedido retorna a mesma entrada; conflito produz o erro previsto, preservando dados.

Não execute uma lista universal de valores adversariais em toda tarefa. Essas propriedades se aplicam às fronteiras afetadas. Uma lacuna de contrato pede decisão proporcional: se for material e não resolvida pelas fontes, registre a dúvida, continue trabalho independente seguro e peça a definição necessária. Não altere testes ou documentação apenas para obter aprovação.

Na persistência afetada, escolha cenários de falha parcial, duplicação, concorrência, cancelamento/callback tardio, quota, corrupção, migração e recuperação pertinentes. Confira memória, armazenamento, histórico e recuperação conforme a promessa do produto; reload, nova instância e novo processo exercitam condições diferentes.

Não destrua a única cópia válida. Backup gerado, download solicitado, arquivo conferido e recuperação testada são provas distintas. Use dados sintéticos; dados pessoais/financeiros reais exigem autorização específica e minimização. Um resultado desconhecido exige conferência antes de repetir uma mutação que possa duplicar efeitos.
