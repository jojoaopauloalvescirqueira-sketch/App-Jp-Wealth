# Fluxo Git do JP Wealth — guia simples

Este guia explica, em linguagem acessível, como o trabalho no JP Wealth flui entre você, o GitHub Desktop e o Claude Code. Não é preciso experiência prévia com Git para entender.

## A ideia central: uma pasta, várias "versões" dentro dela

A pasta do projeto no seu computador (`App JP Wealth`) não muda de lugar nem se multiplica. O que muda é **qual versão do código está "em exibição" dentro dela** — isso se chama **branch**.

- **Branch não é uma segunda pasta.** É uma "gravação" diferente do mesmo projeto, guardada dentro do próprio Git.
- **A mesma pasta exibe a branch atualmente selecionada.** Quando você troca de branch, os arquivos dentro da pasta mudam para refletir aquela versão — mas o caminho da pasta no Finder continua o mesmo.
- **O GitHub Desktop é quem seleciona a branch.** É lá que você escolhe em qual branch está trabalhando.
- **O Claude confirma a branch pelo comando Git**, antes de tocar em qualquer arquivo — ele nunca troca de branch sozinho.

## O passo a passo completo

```text
main
  → criar branch pelo GitHub Desktop
  → abrir Claude Code na mesma pasta
  → confirmar branch
  → analisar
  → implementar
  → testar
  → revisar diff
  → testar manualmente
  → commit autorizado
  → push da branch
  → integração à main
```

### 1. `main`
É a versão oficial e estável do JP Wealth — a que já foi aprovada e testada. Ninguém trabalha direto nela.

### 2. Criar branch pelo GitHub Desktop
Antes de começar uma tarefa nova, você cria uma branch a partir de `main`, com um nome que descreve a tarefa (por exemplo `fix/pwa-upgrade` ou `ui/settings-modal`). Isso é feito no GitHub Desktop, não pelo Claude.

### 3. Abrir Claude Code na mesma pasta
Você abre o Claude Code apontando para a mesma pasta `App JP Wealth`. Como a branch já foi selecionada no GitHub Desktop, é essa versão que o Claude vai encontrar.

### 4. Confirmar branch
O Claude roda comandos de leitura (`git branch --show-current`, `git status --short`) para confirmar que está na branch certa e que não há sobras de trabalho de outra tarefa. Se algo não bater, ele para e avisa — não segue em frente sozinho.

### 5. Analisar
O Claude lê o código e a documentação relevante para entender o que precisa mudar, sem editar nada ainda.

### 6. Implementar
O Claude faz a alteração, do jeito mais enxuto possível, dentro do escopo combinado.

### 7. Testar
O Claude roda os testes automáticos disponíveis (validação, smoke test, etc.) e informa o resultado — inclusive se algum teste não pôde ser executado.

### 8. Revisar diff
O Claude mostra exatamente o que mudou (`git diff`), arquivo por arquivo, para você conferir antes de qualquer coisa ser gravada.

### 9. Testar manualmente
Você abre o app e confirma, na prática, que o comportamento esperado está correto.

### 10. Commit autorizado
**Só depois da sua autorização explícita**, o Claude registra a alteração localmente com um commit. Um commit é como uma fotografia daquele estado do código, guardada no histórico da branch.

### 11. Push da branch
O **push** envia os commits feitos localmente para o GitHub, para que fiquem salvos na nuvem e visíveis para você em outro computador, se precisar. Isso também é feito com sua autorização — pelo GitHub Desktop ou pelo Claude, apenas quando você pedir.

### 12. Integração à `main`
Quando a branch está pronta e aprovada, ela é incorporada a `main` — isso se chama **merge**. É esse passo que torna a mudança parte oficial do projeto. Normalmente feito pelo GitHub Desktop ou pelo GitHub, depois de revisão.

## Resumo dos termos

| Termo | O que significa, em uma frase |
|---|---|
| **Branch** | Uma versão paralela do projeto, dentro do mesmo repositório — não é uma pasta nova. |
| **Commit** | Uma gravação local de uma alteração, com uma mensagem explicando o que mudou. |
| **Push** | Enviar os commits salvos localmente para o GitHub, na nuvem. |
| **Pull** | Trazer para o seu computador o que já está no GitHub. |
| **Merge** | Incorporar o conteúdo de uma branch a outra — normalmente, de uma branch de tarefa para `main`. |
| **Working tree limpa** | Não há nenhuma alteração pendente sem salvar naquele momento. |

## O que o Claude nunca faz sozinho

O Claude nunca cria, troca ou apaga branch, nunca faz commit, push, pull, merge ou qualquer operação que grave ou envie alterações — isso sempre depende de você pedir explicitamente, na conversa. Ver `CLAUDE.md` para a lista completa.
