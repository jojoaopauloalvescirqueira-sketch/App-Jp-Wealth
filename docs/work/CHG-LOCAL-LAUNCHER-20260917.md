# Abrir JP Wealth no Safari — 2026-09-17

Pedido aprovado: criar um atalho dentro da pasta do software que inicia um
endereço local fixo e abre o Safari. O diagnóstico nativo observou o ícone
genérico em file:// e o ícone JP Wealth com os mesmos arquivos em HTTP.

- Base de desenvolvimento: `6ef8d7689130b8476c64fd90881e00050b2725e9`, árvore
  limpa, branch existente `codex/nocuda-tools-20260917`. A pasta principal está
  em `e02a655903ae5059bec1615b86e1a2473bea3bd6` (mesmo conteúdo integrado).
- N1/A2: inicializador local, sem dependência nova. A instalação dos arquivos
  do inicializador na pasta principal é parte expressa do pedido; sem commit,
  push, merge, troca de branch ou publicação remota.
- Fontes: `AGENTS.md`, README/Início rápido, CONTEXT-MAP/rotas PWA e persistência,
  PROJECT-CONTEXT/produto, CURRENT-STATE/fotografias históricas,
  COMPLETE-BACKUP/importação, PWA-UPDATE-LIFECYCLE e `tools/serve.py`.
  Harness §§12–14 e 36–48: SHA-256
  `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`.

## Compreensão e escopo

O JP Wealth organiza dados financeiros locais; o inicializador cuida apenas da
abertura e entrega de seus arquivos públicos. Hoje `tools/serve.py` exige uso
manual do terminal; o novo atalho calcula sua própria pasta, inicia ou reutiliza
um servidor restrito a 127.0.0.1:8765 e abre o Safari. Conflito de porta deve
falhar claramente, nunca escolher outra origem e aparentar perda dos dados.

Arquivos permitidos: `Abrir JP Wealth.command`, `tools/launch_local.py`,
`tools/local_launcher_test.py`, instrução de uso em README, este registro e nota focal em ACTIVE-TASK.
Nenhum script do app, schema, regra, build, manifesto, service worker ou ícone
será alterado. Não ler armazenamento do Safari por shell. A transferência dos
dados usa somente Exportar/Importar backup completo já existentes e conserva
o arquivo original e a origem file://. Nenhum backup real entra no repositório.

## Verificação e recuperação

Testar partida/reabertura, identidade da pasta, conflito de porta, caminho com
espaços/acentos, resposta dos assets, rejeição de arquivos privados, travessia e
symlinks externos; executar gate aplicável e verificar o ícone no Safari nativo.
A cópia instalada precisa corresponder aos bytes testados. O servidor não inicia
no login e pode ser encerrado sem apagar dados; voltar ao arquivo original
preserva a base anterior. Remover somente os arquivos novos desfaz o atalho.

## Resultados observados

- `python3 tools/local_launcher_test.py`: PASS, 6 testes sem skips; 122 recursos
  do runtime/precache servidos por HTTP com hashes iguais aos originais. Partida,
  reabertura, pasta com espaços/acentos, conflito de porta, Host/Origin, métodos de
  escrita, caminhos privados, traversal e symlinks externos/internos exercitados.
- `zsh -n 'Abrir JP Wealth.command'`, compilação Python e `git diff --check`: PASS.
- Revisão independente identificou symlink público apontando a arquivo privado
  interno; a validação também do destino resolvido corrigiu o caso e sua regressão.
- Dois arquivos novos instalados na pasta principal, sem substituir arquivos
  rastreados. Hashes iguais aos testados: `.command`
  `69cca54e246f053acafd043b486a66c2aecf1845e5dffec8421ab7adfa6702ac`;
  helper `52868b661a6fee34bebf5cdb087f101c38ed61f3b631ac2c9509b7fea268039a`.
- Executado o atalho instalado com `--no-open`: PASS. Servidor real em
  `127.0.0.1:8765`; HTML, PNG do ícone, JS e manifesto respondem 200 com seus MIME.
- Safari foi confirmado pelo proprietário como origem mais atual. A tentativa
  de acessar o backup encontrou interação simultânea do usuário; a ferramenta
  recusou agir sobre a interface alterada. Transferência, teste de duplo clique
  nativo e conferência visual no novo endereço: pendentes de disponibilidade da UI.
  Nenhum dado real foi exportado, importado, apagado ou copiado por scripts.
- Gate standard concluído: **41 PASS / 5 PRODUCT_FAIL**. Relatório original em
  `tools/.artifacts/local-launcher-standard.json`, preservado sem reclassificação.
  Dashboard Macro, Estatuto documental, navegação PF, orçamento PF e leitura
  Alladin excederam o tempo de espera de inicialização/sonda no navegador.
  Navegação PF passou na main e em repetição do candidate sem editar código.
  Leitura Alladin voltou a falhar no candidate (dependência `read` indisponível)
  e na main (timeout). As outras três falhas não foram reexecutadas isoladamente;
  a causa dos timeouts não foi estabelecida. Os arquivos do app, manifests, SW
  e build-id são idênticos aos da main, e essas suítes não usam o novo servidor.
  Não há alegação de aprovação integral do gate nem correção dessas suítes.
  Logs de comparação em `tools/.artifacts/local-launcher/`.
- Sem commit/push/merge. A entrega local do inicializador é distinta de uma
  homologação geral do aplicativo ou da transferência dos dados reais.

## Impacto agêntico

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED

BASIS: o inicializador acrescenta uma forma de abertura consumida via README e
ACTIVE-TASK por agentes/preflight. Ambos apontam para o contrato focal atualizado.
Agentes e skills herdam essa informação sem mudar instruções; routing e registries
não ganham componentes; fontes financeiras, backup e lifecycle PWA não mudam.
Arquitetura só é alcançada na inicialização opcional. Não requer alterar fotografias
históricas globais, índices, memória ou vetores. Revisão independente confirmou esse
raio; a instalação local é distinta da integração Git e da transferência de dados.
