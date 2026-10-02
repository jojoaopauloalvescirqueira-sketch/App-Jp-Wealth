# CHG — GENETRIX 7x, ciclos contábeis e flutuante compensado

## Autoridade e alvo

- Estado: implementação isolada autorizada pelo pedido humano `PLEASE IMPLEMENT THIS PLAN: GENETRIX — Pesquisa, proteção em 7x e flutuante compensado`, de 01/10/2026. Isso não autoriza conta real, publicação, commit, push, merge ou integração no checkout paralelo.
- Risco de engenharia: N3 para executor/cálculos financeiros; N2 para persistência, recuperação e preferência visual. Não confundir com níveis normativos do modelo.
- Raiz de escrita: `/private/tmp/jpw-genetrix-risk-ledger-20261001`.
- Branch: `codex/genetrix-risk-ledger-20261001`; HEAD de base: `deffc5061fe2eff3d83b6f6e742fa105ac9c5b06`.
- A cópia inclui trabalho preexistente da frente do site; 644 arquivos capturados e 92 fontes MT5/normativas conferidas sem drift durante a captura. Fingerprint: `549502478dd4a9bf27543181abe31b13597eadc6d22e74b24dc47f216dc3c6d5`.
- Recibo externo: `outputs/jpw-genetrix-risk-ledger-20261001/BASELINE-INPUTS.json` no workspace desta conversa. Alterações herdadas não pertencem ao delta desta tarefa.
- Preflight `audit` e `edit --allow-dirty`: PASS na cópia; warnings de árvore herdada e SOURCE REVISION UNKNOWN preservados. O resultado não valida produto ou norma.

## Compreensão e fontes

O JP Wealth organiza governança de risco e execução rastreável. GENETRIX é o produto local MT5: o indicador apresenta leituras; o Observer observa e publica métricas, sem negociar. O site explica e distribui fontes, sem calcular ou comandar a conta.

A origem capturada declara produto 1.16.1 e cálculo 1.9.0. O guia local contém identificação histórica 1.10.1; não transportar sua validação histórica para este candidato. O master de engenharia foi relocalizado para `2 - TRABALHO/6C - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`.

Referências financeiras: Estatuto V11 SHA-256 `2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769`; Anexo T03 SHA-256 `6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23`. Arts. 4.2–4.5, 6.1, 7.1 e 8.4. Proteção 7x/Equity é adicional e derivada, não substitui bruto/min(SI,Equity), tetos por fase, RC ou estados PENDING/BLOCKED.

## Fronteira de escrita

Permitidos: novos núcleos, adaptadores, stores e EAs GENETRIX Risk/Ledger; integração de leitura no indicador/coordenador/apresentação/painel/prefs/ações exclusivamente visuais; testes novos dos mesmos núcleos; documentação própria, memória de cálculo, fixtures independentes; versão de produto e geração oficial de pacote isolado. Ajustes de adaptadores de testes existentes somente quando a interface aprovada os exigir, conservando critérios anteriores e registrando antes/depois.

Preservados: fórmulas existentes de Floating P/L, DD, Raiz N, stop risk e nocional; Observer anterior; stores antigos; fontes normativas; harnesses e gates; dados reais; site e checkout paralelo. Nenhuma negociação real, senha, registro pessoal ou credencial entra em fixture/pacote/log técnico.

## Contratos aprovados

1. Supervisor separado, inicialmente OBSERVE; execução somente em conta DEMO hedging, por armamento explícito da conta e sessão. Netting/FIFO não armam; reinício/troca de conta não rearmam.
2. Nocional bruto integral/Equity atual, gatilho estrito >7 não arredondado; LIFO por abertura em ms e identificador decrescente no empate. Fechamento integral do ticket exato, sem abertura ou modificação de SL/TP.
3. Pendentes de entrada: orçamento max(0,7E−N), menor prefixo LIFO para enquadrar soma projetada conjunta. Cenário, não preço garantido; excluir ordens de fechamento e SL/TP.
4. Uma intenção ativa; parcial confirmada conserva intenção de finalizar o ticket. Incerteza bloqueia novo envio até reconciliação. Cancelamento recusado permite poda das posições com alerta; fechamento recusado pausa sem pular LIFO. Sem repetição cega.
5. Ledger por conta/servidor/moeda, ciclos inferidos por símbolo/direção, membros por position identifier e pending order ticket; revisões auditáveis. Gênese original não é promovida. Pendentes mantêm ciclo sem posição; encerramento exige ausência confirmada de membros/executações em trânsito.
6. R=soma lucro/swap/comissão/fee atribuídos; U=soma preço/swap dos remanescentes; C=R+U; %=100C/saldo da mesma geração; atual somente quando a publicação é atual, Historical conserva data e saldo registrados. Custos não atribuídos tornam completude parcial; ausência não é zero. Sem impacto no RC.
7. Métrica com scope/ciclo, seleção explícita, detalhes e histórico; Floating P/L atual preservado. Preferência visual compatível V1/V2/V3; todos ocultos continuam todos ocultos.

## Validação e gates

Fixtures/esperados congelados antes dos testes. Núcleos reais exercitados no host com shim API explícito; testes de SQLite e recuperação; três processos novos por cenário crítico. Freeze de fontes e recibos antes das revisões cruzadas. Autores não aprovam o próprio módulo. Falhas e tentativas anteriores preservadas.

Host PASS não implica compilação MQL, interação no MT5, latência garantida ou negociação validada. Compilação nativa exige logs e hashes dos mesmos bytes. Demo exige ambiente separado e conta dedicada identificada; sem essa pré-condição permanece NOT_RUN. Conta real e integração pública são gates posteriores.

## Recuperação

Rollback restaura somente o delta GENETRIX identificado frente ao recibo BASELINE-INPUTS e regenera pacote isolado. Não executar reset/stash/limpeza no checkout original, nem apagar bancos locais. Não retirar bloqueios ou mudar fixtures para obter aprovação.

## Revisão candidata RC2

A conferência final identificou que os detalhes exibiam apenas contagens. A revisão RC2 acrescenta a lista canônica dos POSITION_IDENTIFIER observados por ciclo, incluindo membros fechados, com codec versionado compatível: publicações antigas sem lista permanecem indisponíveis nesse campo. O detalhe pagina a lista e exibe geração/data, sem inferir tickets atuais ou completude histórica. Valores monetários, política de risco, fixtures e estados normativos permanecem preservados. RC1 e suas tentativas são conservados em Revisoes/RC1. Novos hashes e testes pertinentes são exigidos para RC2.
