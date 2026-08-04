# Changelog

## [9.1-settings-modal.1] — 2026-08-04

### Central de Configurações
- Transformada a antiga tela de Configurações em uma central modal dedicada, aberta pela engrenagem do cabeçalho sem trocar a tela operacional ao fundo.
- Reorganizados os controles existentes em Sobre, Aparência, Interface, Editor, Educacional, Estatuto Operacional, Parâmetros e Calibração e Backup e Recuperação, preservando os mesmos nós, listeners e persistência.
- Adicionada uma base educacional local, curta e pesquisável sobre Forex, glossário e perguntas frequentes; ela não contém sinais, previsões ou recomendações operacionais.
- Dados do Período agora são acessados por resumo seguro em Parâmetros e Calibração, com retorno ao onboarding existente em modo de edição.
- A central não grava em `S`, não altera o checkpoint de Finalizar Sessão e mantém a coordenação de foco ao abrir subdiálogos legados.
- Incluídos os módulos da central no precache existente do PWA, sem alterar sua estratégia de atualização.

## [9.1-header-actions.1] — 2026-08-04

### Navegação do cabeçalho
- Movidos os acessos de Configurações e Finalizar sessão para ações icônicas compactas no canto superior direito do cabeçalho.
- Mantida a numeração das áreas operacionais restantes e reutilizados os fluxos existentes de navegação e Finalizar Sessão.
- Nenhuma regra financeira, persistência, backup, limpeza ou comportamento interno de Finalizar Sessão foi alterado.

## [9.1-finalize-session.1] — 2026-08-03

### Privacidade e encerramento local
- Adicionado o fluxo modal `Finalizar sessão`, com checkpoint determinístico, exportação confirmada e confirmação textual `APAGAR TUDO`.
- Removidas somente as chaves locais do JP Wealth identificadas na auditoria, incluindo cópias corrompidas e preferências auxiliares; chaves de outras aplicações são preservadas.
- Criado estado em memória genuinamente vazio após a exclusão, sem nomes, contas, ordens, lançamentos ou credenciais anteriores.
- Mantido o formato do backup completo, a política existente de senhas de investidor e o comportamento do reset administrativo `Limpar todos os dados`.
- O fingerprint passou a incluir preço e data dos instrumentos; falsos positivos de atualização cambial são aceitos deliberadamente para priorizar a preservação de dados.
- Adicionado gate de persistência com geração de sessão, coordenação entre abas e proteção contra callbacks assíncronos após a exclusão.
- A limpeza de caches do service worker agora é limitada ao prefixo `jp-wealth-`.
- Nenhuma regra financeira, cálculo, perfil, matriz ou contabilidade foi alterada.

## [9.1-empty-state.1] — 2026-08-03

### Estado inicial e onboarding
- Removida a série demonstrativa de 2026 do acompanhamento mensal quando não existem fechamentos no ledger.
- Retorno acumulado e DD máximo permanecem vazios (`—`) até o primeiro fechamento diário; com ledger real, o cálculo existente é preservado.
- Substituídos os placeholders pessoais do onboarding por `Preencher nome` e reforçada a validação obrigatória dos nomes.
- Verificados inicialização sem estado salvo e os dois fluxos de limpeza sem alterar regras financeiras ou dados salvos existentes.

## [9.1-icons.1] — 2026-08-03

### PWA e identidade visual
- Criada biblioteca local com os temas `flat-knight`, `relief-knight` e `marble-knight`.
- Criado um manifesto PWA independente por tema, mantendo nome, modo e escopo do app.
- Adicionado service worker com precache versionado de scripts, manifestos e ícones.
- Adicionada seção `Ícone do app` em Configurações e modal acessível de escolha.
- Registrada a limitação real do Safari/iOS: trocar o ícone exige remover e adicionar novamente o atalho.
- Corrigido o binding antecipado de `wipeAllData` no boot e tornado o runner de smoke compatível com Chromium no macOS/Linux.
- Nenhuma regra financeira, persistência principal ou dado operacional foi alterado.

## [9.1-structured.1] — 2026-08-03

### Estrutura
- Preservado o HTML monolítico original e seu hash SHA-256.
- CSS extraído para `src/styles/app.css`.
- JavaScript separado pelas seções já existentes no código, sem reescrita de lógica.
- Criado `src/js/manifest.json` para fixar a ordem de execução.
- Criadas documentação de arquitetura, governança, recuperação e testes.
- Incluídos Estatuto e organograma em `docs/normative/`.
- Criados scripts de validação, smoke test e reconstrução do HTML portátil.

### Regras financeiras
- Nenhuma regra, constante ou fórmula financeira foi deliberadamente alterada nesta etapa.
