# Hedge didático — implementação delimitada de 31/10/2026

Raiz: worktree `work/trees/hedge`, branch `codex/hedge-didatico-20261031`, BASE_SHA `69b6cb677de2486be5c30681e4b2e02d4180d704`. O proprietário aprovou o plano e as quatro worktrees nesta conversa; aprovou o uso dos contratos versionados após a fonte externa antiga não ser encontrada na migração. A autorização cobre esta implementação e validações sintéticas. Não cobre operações Git, publicação, negociação nem alterações das instruções/gates globais.

Preflight edit executado antes da edição: PASS, zero alterações; aviso de deriva contextual histórica mantido. O preflight não é aceite humano nem prova financeira. Os recibos desta fase ficam fora do repositório em `work/implementation/hedge/` da sessão.

## Compreensão e fontes

1. O JP Wealth preserva capital, dados e rastreabilidade. Esta ferramenta explica hipóteses financeiras sem executar operações (`AGENTS.md`, missão).
2. A pasta `32-prop-firms` separa motor puro e interface. O motor atual calcula cenários sintéticos de perda fixa (`HEDGE-PROP-FIRM.md`, contrato educativo).
3. Antes: campos textuais, cartões e rascunhos RAM. Depois: sliders sincronizados, fluxo esquemático, modo Instant, catálogo factual e guia confirmado.
4. Consumidores: navegação Tools, finalização, backup workspace, PWA/arquivo/portátil e testes do motor/UI. O store independente usa apenas a chave `jpwealth_hedge_guide_v1`.
5. Invariantes: `01-engine.js` byte-idêntico; nenhuma fórmula/lote/ordem/escritor financeiro, DEFAULTS ou migração. Parâmetros não são preenchidos pelo catálogo. Ausência/zero/erro não são equivalentes.
6. Provas: store puro/roundtrip e falhas de gravação; UI real de sliders, foco, Instant, confirmação/reload, mobile/temas; oráculos anteriores; distribuição. FULL e revisão final ficam sob coordenação da raiz.

## Fronteiras

N0-V/N1 apresentação; N2 progresso confirmado e backup próprio (produto aprovado A3). Controles permanentes e encadeamento nos testes existentes possuem CHG dedicado N3. Arquivos autorizados: UI/CSS da frente, testes `hedge_*`, este brief/contrato e índice de regressões. Derivados são reconstruídos pelo gerador oficial; não mudar o runner, CI, política ou skills.

Uma configuração confirmada por vez, substituível somente após confirmação explícita. O registro anterior permanece até confirmação por releitura. Cada etapa adiciona um marco; navegar/consultar/arrastar não grava. Persistência inválida/futura, mudança concorrente ou resultado desconhecido preserva a entrada em RAM e exige conferência; nenhum reset silencioso. Reset de navegador ou máquina só é recuperável com cópia externa efetivamente exportada.

Rollback: retirar somente este delta de UI/store e restaurar seus derivados oficialmente, após guardar o registro do guia em Backup Completo compatível. Versão anterior não compreende a nova chave; mantê-la opaca, sem apagar. Não usar reset/stash/clear. Não remover evidências nem trabalho anterior.
