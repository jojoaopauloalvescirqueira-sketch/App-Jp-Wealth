# JP Wealth Risk Terminal V9.1

Repositório estruturado a partir do HTML portátil preservado do JP Wealth. A reorganização desta versão é **estrutural**: HTML, CSS e JavaScript foram separados sem reescrever as regras financeiras nem alterar a ordem de execução do código.

## Prioridade do projeto

1. Preservação do capital e integridade dos dados.
2. Aderência ao Estatuto JP Wealth e às decisões formais aprovadas.
3. Correção dos cálculos normativos.
4. Rastreabilidade de cada alteração.
5. Evolução da interface e da arquitetura somente depois dos itens anteriores.

## Início rápido

```bash
python3 tools/validate_project.py
python3 tools/smoke_test.py
python3 tools/serve.py
```

Acesse `http://127.0.0.1:8000`.

## Estrutura principal

- `index.html`: composição da interface.
- `src/styles/app.css`: estilos extraídos do HTML original.
- `src/js/`: lógica separada por domínios, mantendo a ordem original em `manifest.json`.
- `icons/`: biblioteca local de ícones PWA, com três temas e variantes técnicas.
- `manifests/`: um manifesto independente por tema de ícone.
- `sw.js`: service worker local com precache versionado dos arquivos do app e dos ativos PWA.
- `docs/normative/`: Estatuto e organograma — fontes de autoridade do projeto.
- `docs/architecture/`: arquitetura, estado e mapa do código.
- `docs/governance/`: regras para trabalho humano e por IA.
- `tests/`: validação e smoke test.
- `tools/`: servidor, validação e reconstrução do HTML portátil.
- `archive/original/`: original imutável para comparação e recuperação.
- `data/backups/`: backups JSON locais; não versionar dados reais ou credenciais.
- `dist/`: HTML portátil reconstruído.

## Regra de segurança

Nenhuma IA deve alterar constantes financeiras, fórmulas normativas, migrações de estado, regras de exclusão ou dados reais sem uma tarefa explicitamente delimitada e revisão humana.

## Persistência

O estado operacional é mantido no `localStorage` sob a chave `jpwealth_v9_state`. O código está no repositório; os dados reais do operador precisam ser exportados do navegador e guardados separadamente em `data/backups/`.

Em computador de terceiros, use `Finalizar sessão` no alto da barra lateral. O fluxo verifica o checkpoint da sessão, exige backup confirmado quando necessário e remove apenas as chaves locais pertencentes ao JP Wealth; não usa `localStorage.clear()` e não fecha a aba do navegador.

O fingerprint inclui também `instruments[].preco` e `instruments[].updated`. Uma atualização automática de câmbio pode, portanto, produzir um falso positivo deliberado de alteração; esta versão prioriza evitar perda silenciosa de dados e não tenta distinguir origem manual de automática.

## Ícone e instalação PWA

Em `Configurações → Ícone do app`, escolha uma das três identidades: `Knight Flat` (atual), `Knight Relief` ou `Knight Marble`. A escolha usa a chave local `jpwealth_v9_icon_theme`, separada do estado operacional, e atualiza o manifesto correspondente:

- `manifests/jp-wealth-flat-knight.webmanifest`
- `manifests/jp-wealth-relief-knight.webmanifest`
- `manifests/jp-wealth-marble-knight.webmanifest`

No iPhone e iPad, o Safari não troca retroativamente o ícone de um atalho já instalado. Depois de escolher, remova o atalho atual e use `Compartilhar → Adicionar à Tela de Início` novamente. Em desktop e Android, o comportamento depende do navegador. O PWA precisa ser servido por HTTP/HTTPS; o HTML portátil em `dist/` continua destinado a distribuição de arquivo único e não substitui a publicação da raiz do projeto.
