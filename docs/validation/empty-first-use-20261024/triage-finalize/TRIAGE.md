# Triagem somente leitura — Alladin / Finalizar sessão

Candidate: `1b695b809fe80c26`, base `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`, branch `codex/primeiro-acesso-vazio-20261024`.

## Resultado

**Causa demonstrada: fixture implícita obsoleta, não perda de contas observada no produto.** C8, C11 e C14 tratam `accounts.length === 0` como prova de finalização indevida. Esses casos não semeiam conta: com o primeiro acesso vazio aprovado, `S.accounts` já é `[]` antes do ato. A coleção permanece `[]` depois da recusa. As verificações de disco, preservação do Alladin, recusa de `save()` e persistência desbloqueada não falharam.

A saída bruta do runner Full2 continua `PRODUCT_FAIL`; este relatório não a altera nem apaga. Seu resultado é uma análise causal independente para orientar a correção da camada responsável.

## Comando de reprodução integral

```text
PATH=<Node existente>:$PATH JP_WEALTH_CHROMIUM=<Chrome 1223 existente> JPW_NODE=<Node existente> .superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3 tools/alladin_finalize_preservation_test.py
```

Comando executado por shell com saída integral em `current-raw.log`; exit 1. Python 3.12.14, Playwright 1.60.0. O teste usa `pw.chromium.launch()` sem `headless=False`; não abriu janela real. Os únicos erros finais são:

- C8: a sessão foi PARCIALMENTE finalizada — accounts foi zerado.
- C11: a sessão foi finalizada mesmo sem conseguir ler o estado persistido.
- C14: a sessão foi finalizada sem conseguir garantir a preservação.

Demais C1–C17 executados pela entrada original não adicionaram falhas. Nenhuma alteração de produto, teste, Git ou dados pessoais foi feita. Somente artefatos externos nesta pasta.

## Causalidade e contraprova

O script temporário `isolated-causal-probe.py` importa o teste original sem editar seus bytes, executando apenas C8/C11/C14. O recibo registra essa seleção explicitamente; sua linha de resumo legada não significa execução dos demais casos.

| Condição | Contas antes → depois | C8/C11/C14 |
|---|---|---|
| Original vazio aprovado | 0 → 0 | três falhas |
| Mesmos casos e asserts + uma conta sintética explícita | 1 → 1 | três PASS |
| Mesma conta + violação deliberada em memória limpando contas após a recusa | 1 → 0 | três falhas rejeitando a violação |

Nas três condições, o disco permaneceu `{documento truncado` em C8/C11 e ausente em C14; a persistência ficou desbloqueada. A causa é, portanto, a pré-condição não estabelecida pelo teste, e não uma alteração real de 1 para 0 na execução original.

Recibos completos: `original-empty.json`, `explicit-fixture.json`, `mutated-clear-on-abort.json`; logs correspondentes. Os cenários são integralmente sintéticos e em contextos isolados.

## Delta mínimo recomendado — NÃO implementado

Somente em C8, C11 e C14 de `tools/alladin_finalize_preservation_test.py`:

1. Semear uma conta sintética válida e identificável antes da gravação do Alladin já existente, comprovando que a pré-condição contém uma conta.
2. Capturar a coleção de contas antes do ato e exigir igualdade exata depois da recusa, além de manter a proteção contra esvaziamento. Isso preserva a intenção e detecta alteração de campos sem mudar a cardinalidade.
3. Manter todas as expectativas de disco ilegível/ausente, ausência de broadcast, Alladin, `save()` recusado, desbloqueio B3 e demais C1–C17.
4. Incorporar contraprova equivalente à limpeza indevida; não introduzir dados demonstrativos no produto para atender à fixture.

Os pontos atuais são linhas 425–426, 494–495 e 529–530. O setup de C8/C11/C14 injeta apenas Alladin e herda `accounts` dos padrões. Nenhuma fórmula ou comando de finalização precisa mudar para estas falhas.

## Dependências e próximos checks

- A adaptação delimitada de fixtures está prevista no CHG de testes aprovado; não exige alterar o produto, o gate runner, timeouts ou critérios de preservação.
- Após qualquer edição autorizada: revisão independente do diff, execução integral deste focal, contraprovas e novo Full sobre fingerprint novo. O Full2 atual permanece histórico.
- O caso separado `session-write-serialization` não foi investigado por esta triagem.
- Se outra falha aparecer, deve ser investigada por sua própria causa; este diagnóstico não generaliza para todas as validações de sessão.

## Identidade dos bytes

`fingerprint.json` confirma igualdade com o congelamento Full2 para o próprio teste, DEFAULTS, persistência, finalização, checklist e build-id. SHA-256 do teste original: `13e923d351b6e0e18cd7be5fb77c8c389d36ad04814157bb59da523d892ae2e6`.
