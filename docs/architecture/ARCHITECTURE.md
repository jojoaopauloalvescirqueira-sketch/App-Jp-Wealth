# Arquitetura do sistema

## Visão geral

O JP Wealth Risk Terminal é uma aplicação web cliente, sem backend obrigatório. O navegador carrega `index.html`, os estilos e os scripts clássicos ordenados. O estado operacional é persistido em `localStorage`.

## Camadas

### 1. Apresentação
- `index.html`
- `src/styles/app.css`
- `src/js/20-ui/`

### 2. Domínio financeiro e operacional
- `src/js/10-domain/`
- Perfis de risco, instrumentos, cálculo de risco, transições de fase, stops, corretoras e quarentena.

### 3. Contabilidade e estatística
- `src/js/30-accounting/`
- Fechamento diário, projeções, MEI-JP e simulação patrimonial.

### 4. Infraestrutura local
- `src/js/00-core/`
- Estado inicial, migrações, persistência e helpers.

### 5. Orquestração
- `src/js/40-app/`
- Navegação, tema, onboarding, reset, limpeza e boot.

### 6. PWA e identidade visual
- `icons/` contém os masters derivados das referências visuais e as variantes `favicon`, `apple-touch-icon`, `180x180`, `192x192` e `512x512`.
- `manifests/` mantém um manifesto por identidade, com o mesmo app e `start_url` diferenciado por `?icon=`.
- `src/js/40-app/06-app-icons.js` controla somente a preferência visual local, atualiza os links de manifesto/ícone e explica a limitação de instalação no iOS.
- `sw.js` faz precache dos scripts, estilos, manifestos e ícones. A constante `CACHE_NAME` deve mudar quando os ativos offline forem alterados; nesta implementação ela está em `jp-wealth-pwa-v9.1-icons-20260803-r2`.

## Modelo de execução

A versão estruturada preserva scripts clássicos, não ES Modules. A ordem registrada em `src/js/manifest.json` é parte do contrato de execução. A separação atual reduz o tamanho de cada contexto para IA sem alterar o comportamento global legado.

## Persistência

- Chave principal: `jpwealth_v9_state`.
- Preferências auxiliares usam outras chaves locais.
- A preferência do ícone usa `jpwealth_v9_icon_theme` e não é misturada ao estado financeiro.
- A função `migrate()` mantém compatibilidade entre schemas.
- O arquivo HTML ou o repositório não contém automaticamente o histórico real do navegador.

## Dependência externa

A atualização cambial usa a API Frankfurter. A aplicação deve continuar operando com os últimos preços salvos quando a rede estiver indisponível.

## Limite desta etapa

A arquitetura foi organizada, mas ainda não convertida em módulos encapsulados. A modularização real deve ocorrer gradualmente, com testes de caracterização por domínio e sem misturar refatoração com mudança normativa.
