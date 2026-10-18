# Relatório da contribuição harness / capítulo 10

Entrega no checkout `/private/tmp/jpw-stoikus-continuity-20261014`, sob `docs/knowledge/stoikus-mql5/`.

## Arquivos entregues

- `chapters/10-ia-propostas.md`: 3.148 palavras por split de whitespace, português avançado, propostas com benefício/custo/risco/dependências/provas, referências precisas de plataforma e notas de produto separadas.
- `research/harness-notes.md`: leitura direta por página, comparação histórica, decisões, TDD e limites.
- `harness-candidato/`: README, ENTRY, ARCHITECTURE, contexto por tarefa, quatro templates, quatro prompts, receitas de suítes, identidades PDF, manifesto, checker, onze testes, doze casos, rubrica, protocolo de piloto e template de tentativa.
- Recibo externo `/private/tmp/stoikus-mql5-research-20261015/harness-freeze.json`.

## Congelamento

Manifest SHA-256: `3df04b79519cde7965db7a0b7953b96ff54d30e7f201b9fd36914d95cbf81abf`. Aviso enviado ao integrador de que cases, rubric e kit estão frozen para o piloto. Nenhum arquivo do kit será alterado sem revisão/novo freeze; notas e este relatório ficam fora da raiz congelada.

## TDD / verificação

- RED inicial: script ausente, 8/9 falhas; caso 2 isoladamente não contava como prova.
- GREEN inicial: 9/9.
- RED required fields/status de JSON: 2 falhas novas por aceite indevido.
- GREEN final: 11/11, 0,423s na primeira rodada final e 0,446s repetição após freeze.
- Checker real: exit 0 INTEGRITY_OK contra kit e três PDFs originais.
- Argumento sources-root incorreto foi exercitado acidentalmente: exit 2 com os três nomes ausentes, depois corrigido sem alterar kit.
- Não mutação de bytes exercitada na fixture; checker usa leitura/stdout, sem escrita nem rede.

## Limitações materiais

0 significa integridade declarada, não semântica, segurança completa ou adoção. Manifesto não se autentica sozinho: freeze externo necessário, inclusive para confiar no checker. Kit não varre todo arquivo não declarado: manifesto delimita o universo verificável. Symlinks de arquivos/subdiretórios declarados são rejeitados; raízes explicitamente fornecidas são resolvidas para sua localização canônica. Required fields são estruturais; validade de conteúdo de casos e julgamento depende da revisão e do piloto. Estado de proveniência desconhecido não é inventado.

36 tentativas são plano, não execução desta contribuição. Autor definiu casos e não pode ser juiz independente de seu próprio piloto. Integrador executa sessões novas, calibra juiz e registra resultados fora do kit. Não houve execução do produto, MT5, EX5, instalação, publicação, modificação de fontes produtivas, AGENTS, CI ou commit. Suítes listadas em recipes foram conferidas por existência de arquivo e não executadas aqui. Resultado histórico GENETRIX FAIL preservado e explicitamente distinguido do novo candidato.
