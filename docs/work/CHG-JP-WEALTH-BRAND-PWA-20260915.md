# CHG — marca conjunta do cabeçalho e PWA

- **Data:** 2026-09-15
- **Solicitante:** proprietário do JP Wealth
- **Branch / base:** `codex/jp-wealth-brand-pwa-20260915` / `e7a6e15f65168489b3fc28a4577825b62caa34d4`
- **Autoridade:** o proprietário autorizou nesta conversa criar a branch e a worktree indicadas e implementar o plano completo. Commit, push, merge e deploy permanecem sem autorização.
- **Classificação:** N1 para a escolha de marca e sua apresentação; N3/A4, explicitamente delimitado pelo plano aprovado, para os manifests, precache, fingerprint e validação estrutural do PWA.

## Objetivo

Substituir a marca principal do cabeçalho e os ícones PWA pelas variantes Vermelho e Preto fornecidas, coordenadas por uma única escolha em **Configurações → Aparência**. `primary` equivale a Vermelho e `secondary` a Preto; Vermelho é o fallback quando a preferência está ausente ou inválida.

## Fontes e evidência de entrada

| Fonte | Identidade observada | Uso autorizado |
|---|---|---|
| `ChatGPT Image 15 de set. de 2026, 19_50_20.png` | SHA-256 `2f0de503b5f2d6fac326444e8e12915a783f87d5a70b7d8d0f7ef5c714bf9e51` | wordmark Vermelho, recorte transparente sem redesenho |
| `ChatGPT Image 15 de set. de 2026, 19_58_12.png` | SHA-256 `59871caa9294a14bfe162a8b57bfb76c21b585c749fcd557cc67c81b1e019405` | wordmark Preto, recorte transparente sem redesenho |
| `ChatGPT Image 15 de set. de 2026, 13_58_06.png` | SHA-256 `4983d22fcbe577e674cad92d9c63eee74024e36c9edf7dd5e5dd462ff8a24551` | ícone PWA Vermelho |
| `ChatGPT Image 15 de set. de 2026, 13_59_40.png` | SHA-256 `2f458a60e859718cba59c74cafd93fcd2fe268542a865b35a9c4c0a9984665ce` | ícone PWA Preto |
| `AGENTS.md` §§ Bootstrap, classificação, PWA e Git | lido nesta branch/base | limites, N3/A4 e gates |
| `docs/architecture/PWA-UPDATE-LIFECYCLE.md` | lido nesta branch/base | precache atômico e ativação conservadora |

## Fronteira e invariantes

**Permitidos:** assets de marca, `index.html`, `src/styles/app.css`, `src/js/40-app/06-app-icons.js`, busca de Configurações, manifests, `sw.js`, gerador, validador, testes/documentação PWA e este contrato/task brief.

**Proibidos:** regras financeiras, dados de contas/Forex, `DEFAULTS`, migração, schema, backup, qualquer segredo, dependência remota, alteração da política de ativação do service worker, edição manual de `dist/` e operações Git posteriores à criação autorizada da branch/worktree.

- A chave `jpwealth_v9_icon_choice` continua auxiliar, fora de backup e removida por Finalizar Sessão.
- Aplicar modifica marca do cabeçalho, favicon, `apple-touch-icon` e manifesto ativo sem reload.
- A troca de manifesto instrui somente instalações futuras. Instalações existentes podem requerer reinstalação conforme o navegador.
- O tema não escolhe a marca; o wordmark Preto recebe placa clara somente quando o cabeçalho é escuro.
- O worker novo não ganha `skipWaiting`, takeover ou mudança de scope.

## Prova planejada e rollback

Criar os dois manifestos locais com id/start/scope idênticos; validar composição e troca em desktop/celular, claro/escuro, teclado, persistência e limpeza da preferência. Executar focais de Settings/PWA, regressões pertinentes, FULL, reprodutibilidade e teste de upgrade do worker. Congelar candidate, diff e recuperação antes de pedir aceite humano. Reverter por commit posterior restaura somente os assets e superfícies listados; nenhum dado operacional exige recuperação.

## Revisão visual da mesma branch — margem do shell e lateral longa

O proprietário pediu, depois do primeiro candidate congelado, reduzir a demarcação da borda superior e da divisória esquerda para se aproximar da captura FxPro e corrigir a lateral que termina ao fim da primeira viewport na captura JP Wealth. Esta revisão é **N0-V**: somente a composição do shell em `src/styles/app.css`, com prova de navegação curta/longa, temas e largura móvel. O candidate anterior em `../evidence/candidate-final.*` permanece imutável; esta revisão receberá nova identidade em evidência separada.

Comportamento de entrada: `#appSidebar` tem `height:calc(100dvh - 60px)`, adequado à navegação sticky mas incapaz de pintar uma página longa; a borda posterior escurece o token semântico com `color-mix(... var(--ink))`. Comportamento de saída: o trilho de fundo/divisória é um item visual no grid do documento inteiro, enquanto o conteúdo da lateral conserva rolagem e posição sticky; a borda de 1px usa uma mistura mais discreta do token de linha com a superfície, retornando ao token pleno sob preferência de alto contraste. Em telas móveis a gaveta mantém sua própria borda, sem trilho no conteúdo.

Não alterar rotas, preferências do Editor, tamanho/posição dos controles, dados, cálculos, processos PWA ou gates. Gerar novamente `build-id.js` e portátil pelo gerador oficial após a CSS; verificar que a nova barra acompanha a altura real do documento sem cobrir o conteúdo nem impedir acesso à lateral. Recovery repõe apenas o delta novo sobre a revisão visual anterior, por cópia seletiva verificada, nunca por reset/stash de outras worktrees.
