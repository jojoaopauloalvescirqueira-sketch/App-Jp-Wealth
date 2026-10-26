# Proposta revisável — fechamento antigo do calendário após reabertura

**Somente candidato em scratch. Não aplicado ao projeto.** O FULL bruto do produto continua com a falha observada. Este pacote não autoriza edição, integração, commit, push, merge ou publicação e não constitui aceite visual humano.

## Problema comprovado e recorte

O evento nativo `close` é entregue depois do `dialog.close()`. Se o mesmo host é reaberto antes da entrega, o listener atual marca sua instância como inativa, cancela seu timer e limpa `aria-expanded`, embora o diálogo continue aberto. Atualizações posteriores passam a retornar zero instâncias ativas, deixando o marcador antigo de Revisar backup na tela mesmo quando a data de confirmação passa a ser futura/inválida.

A mini-reprodução anterior demonstrou o mesmo defeito no produto atual e no PORTABLE original build1b695b809fe80c26, sem depender do feed econômico: `../reports/calendar-lifecycle-minirepro.json`. O módulo calendário e o domínio agenda atuais estão íntegros, byte-exatos HEAD e presentes por inteiro no baseline1b. O módulo de persistência atual também está presente por inteiro nesse baseline anterior ao Dante. A falha não justifica trocar a expectativa legítima de zero marcador por um.

## Candidato mínimo de produto

`product.patch` modifica somente o listener `close` em `src/js/40-app/19-calendar-agenda.js`: `if(dialog.open)return;` ignora o fechamento anterior entregue quando uma nova abertura já está ativa. Fechamento real com `dialog.open=false` continua desativando instância, invalidando requisições, cancelando timer e atualizando o ícone original.

Cópia revisável: `19-calendar-agenda.proposed.js`. Não há schema, writer financeiro, regra de vencimento, seleção de conta, migração ou dado real alterado. Nenhum arquivo novo de produção é proposto.

## Regressão permanente proposta

`regression.patch` acrescenta ao **teste existente** `tools/calendar_agenda_test.py` o caso `lifecycle`, descoberto pelo runner padrão já ligado ao FULL. Não requer mudar quality_gate.py nem criar outro runner permanente. Cópia revisável: `calendar_agenda_test.proposed.py`.

Oráculos novos:

- Após fechar e reabrir no mesmo gesto, observar o `close` nativo antigo com o host já aberto; `refresh()` precisa alcançar uma instância ativa, timer precisa continuar único e `aria-expanded` precisa permanecer true.
- Alterar somente o timestamp da fixture sintética para uma confirmação futura deve produzir `dgBackupStatus().state==='unknown'` e remover o marcador1/nov após o refresh real. Mantido o oráculo de zero marcador.
- Botão Fechar original, Escape e evento nativo de fechamento real continuam produzindo host fechado, zero timer e zero instância atualizada. Botão/Escape preservam o retorno de foco ao ícone original.
- Captura do botão original: id/label/title, uma SVG, alvo44×44, estado `aria-expanded` e retorno de foco observados. Sem afirmação de aceite visual humano.
- Estado financeiro completo e bytes persistidos permanecem iguais nos gestos. Na variante do backup, apenas a mudança explícita do timestamp da fixture em memória é permitida; ela não é gravada na base.

Nenhum caso antigo, tolerância, timeout ou oráculo existente foi alterado. A nova configuração de timezone e clock do runner vale somente para o novo caso; os fluxos existentes permanecem como estavam.

## RED/GREEN e contraprovas executados

Comando executado na raiz real CloudDocs:

```sh
.superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3 /private/tmp/jpw-dante-20261024/calendar-fix-proposal/replay.py
```

Exit0 do **replay de proposta**, com a primeira falha esperada preservada no recibo; isso não é um PASS do FULL:

| Caso | Fonte servida | Resultado observado |
|---|---|---|
| RED-original-regression | arquivo real original | PRODUCT_FAIL esperado: CAL-LIFECYCLE-01, refresh da reabertura retorna0 |
| GREEN-patched-regression | resposta de source-route com a cópia candidata | PASS |
| original-close-counterproofs | arquivo real original | PASS nos três fechamentos reais |
| patched-close-counterproofs | source-route candidata | PASS nos três fechamentos reais |
| GREEN-original-edges-oracle-patched-source | source-route candidata + corpo `edges` existente, sem alteração | PASS, inclusive zero marcador em1/nov |

`replay.py` usa `index.html`, scripts, domínio, backend de armazenamento, controles e handlers reais. Somente a resposta HTTP do módulo19 é trocada pela cópia candidata nos casos GREEN; o arquivo do projeto não é tocado. A fixture econômica nominal continua a do teste existente. Cada contexto é descartável, viewport320×900, America/New_York, relógio sintético e Chromium headless. Sem teste headed, dados reais ou dependências novas.

Saída bruta: `replay.log`. Recibo com estímulos/fechamentos, ícone original, erros, hashes das cópias/patches e hashes de produto antes/depois: `replay-receipt.json`. `runtimeSourceUnchanged=true`. Os arquivos reais módulo19, teste calendário e build-id têm os mesmos hashes no começo e no fim. O replay não aplica os patches nem gera distribuições.

## Fronteira de autorização e custo de integração futura

AGENTS exige preservar o escopo e determina: “Não misturar correções adjacentes, refatoração ampla ou mudanças financeiras com a tarefa delimitada.” Este defeito pertence a Calendário, fora do contrato Dante aprovado. O pedido atual autoriza somente preparar esta proposta em scratch; a existência dos patches e o GREEN por route não ampliam essa autoridade.

Se o proprietário autorizar depois, a aplicação proposta toca **dois arquivos existentes**: módulo19 (produto funcional não normativo, N1) e teste calendário (proteção/control plane, N3 segundo AGENTS, exigência local A4 e CHG dedicado). A documentação e a entrada factual de regressão correspondentes deverão ser delimitadas no novo CHG, sem apagar a falha bruta deste FULL. Nenhum arquivo permanente novo é necessário para o teste, pois o runner padrão já o descobre.

Custo mínimo após autorização: aplicar delta revisado, executar focal `--case lifecycle` e `--case edges`, suíte calendário inteira, regressões de agenda/backup e reabertura do guia pertinentes, rebuild oficial, verificar fontes/distribuições/Service Worker e **repetir o FULL vigente no novo candidato**. O build/fingerprint muda; os recibos anteriores permanecem históricos e não aprovam os bytes novos. É um rebuild mais focais e um FULL completo; duração real será medida, não prometida. Revisão independente e aceite humano seguem separados.

Commit, push, merge, publicação e qualquer limpeza continuam proibidos sem a autorização humana específica de cada ação. Esta proposta não contém nem solicita essas operações.
