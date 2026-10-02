# JPW Cockpit — falhas, auditoria de robustez e guia visual de download

- Pedido do proprietário: corrigir `PRODUCT_FAIL` verificáveis, aprimorar a área de download/instalação no site e auditar a robustez das funções existentes do MT5 com testes significativos.
- Worktree retomada: `/private/tmp/jpw-cockpit-ui-20260930`, branch `codex/jpw-cockpit-ui-20260930`, `HEAD`/base `deffc5061fe2eff3d83b6f6e742fa105ac9c5b06`. As 17 alterações encontradas no preflight pertencem ao candidate visual 1.10.2 deste trabalho; `--allow-dirty` passou depois da conferência. A pasta principal `main` e `sources/` do projeto ChatGPT permanecem intocadas.
- Fonte de autoridade: `AGENTS.md` SHA-256 `d0b77e12abb7dd7336e38c848fdcd8d4dec0142cd4c23289d2d46ef090a4b133`; `README.md` `dfc8da24db5435e50967cf29a39a553e85546d847101cd7c3cb37468dd9f5653`; `CONTEXT-MAP.md` `5b65576ca43103d08c4051276e8c4a419dc58472eafecc48d8bdb88d655d4f49`; guia MT5 `cc0015b4a908818a21c7d103abcce19d11efbcdc2e3a94dbea0c7a73c4e21c2a`. A aplicação é local-first e informativa; sua página distribui fontes, não lê a conta nem calcula as métricas do indicador.

## Contratos e risco

1. O site deve deixar inequívoco qual ZIP de fontes está disponível, onde vai cada arquivo, o que é MetaEditor/indicador/script/EA e que `.mq5/.mqh` exigem compilação; `.ex5` depende de prova nativa. Melhoria de apresentação e navegação é N0-V/N1, sem novo estado financeiro, script de carga, backend ou promessa operacional.
2. A suíte MT5 deve executar corpos do núcleo usado pelo produto com fixtures sintéticas, variando entradas/estados e invariantes (escala USC, completude, conta, invalidade, observador, apresentação). Teste host não equivale a compilação/execução MetaEditor/MT5. Fórmulas, unidades, seleção da Gênese, registros MDD/USC/Raiz N e EA não mudam sem autorização e evidência N3/N2 específica.
3. `standard` anterior do candidate: 45 PASS / 1 PRODUCT_FAIL; execução final anterior: 42 PASS / 4 PRODUCT_FAIL (`research-navigation`, `pivot-studies`, `usd-brl-quote`, `alladin-ui-tx-write`). Os quatro passaram isoladamente depois, sem reclassificar os recibos. Reparos limitam-se a causa reproduzida de N1; se exigirem regra financeira, schema, migração ou controle, registrar bloqueio e não editar esse contrato.
4. O pacote 1.10.2 e HTML portátil foram gerados; o guia `mt5/.../AGENTS.md` ainda se identifica como 1.10.1. Como guia de control plane, sua mudança é revisão N3 própria, não correção incidental de texto neste pedido.

## Critério de verificação e rollback

- Para cada falha: identificar condição inicial, reproduzir no teste original, distinguir intermitência de violação determinística, corrigir somente causa demonstrada e manter resultado bruto. Rodar focais e tier exigido, sem apagar testes nem ajustar oráculos válidos para obter PASS.
- Para MT5: pelo menos uma expansão de teste metamórfico/de integração sobre corpos reais da fonte, falhas de qualidade explicitadas, suite host e audit de caminhos não cobertos. X64 Regular e interação nativa permanecem `NOT_RUN` se não houver ambiente MT5 isolado; nenhum EX5 então.
- Para site: testar HTTP, `file:`, portátil e PWA offline, 320/390/1440 px, teclado, layout e tema; ZIP/hash/status vêm do manifesto. Regenerar derivados pelos geradores oficiais após a última edição de fonte.
- Rollback: restaurar apenas os arquivos desta revisão ao estado anterior do candidate 1.10.2; preservar os 17 arquivos do trabalho visual anterior e os recibos. Sem commit, push, merge, instalação operacional, publicação ou negociação nesta etapa.
