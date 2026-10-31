# Backup unificado — candidato final de 31/10/2026

Branch `codex/backup-unificado-20261031`, base `69b6cb677de2486be5c30681e4b2e02d4180d704`, build `a12473da33d804a4`. Contratos versionados usados conforme autorização humana; sem commit, merge, push ou publicação.

O recibo FULL bruto copiado nesta pasta contém **116/116 PASS**, iniciado em `2026-10-31T16:52:05-03:00` e encerrado em `2026-10-31T17:31:21-03:00`. SHA-256 `bab1673aa2a42f2af479543730eb6efbdca3be145364d0fe4c23e981b364f13e`. UI: **413/413 PASS**, fontes estáveis durante a execução e idênticas ao candidato após a rodada. Runner, 116 entradas, prazo de 900 s, limites geométricos e zoom nativo preservados.

Antes da rodada final, foram corrigidos oráculos/consumidores do formato anterior: preferência mensal agora somente no workspace v3; captura real do ZIP e decodificação independente sem remover asserções de domínio; dois consumidores indiretos conservam recuperação bruta; scanner de credenciais aceita somente a linha exata do guard que recusa segredos, mascarando apenas o lexema e preservando quatro guards/32 injeções/12 contraprovas de alteração, remoção e duplicação. REDs, GREENs, diffs e revisões estão nos recibos externos das rodadas4–7. As tentativas interrompidas/falhas continuam preservadas e não recebem PASS retroativo.

Este FULL valida a worktree isolada. A composição de leitura dos produtores reais de Hedge/fuso com o backup tem prova separada; não representa FULL de quatro branches integradas. IndexedDB/localStorage não são uma transação única. O ensaio Safari mede capacidade e acesso a originais, sem comprovar toda a restauração pela interface. A limitação do inicializador HTTP para o precache, fragilidades das fixtures e inconsistências documentais anteriores continuam registradas.

O checker opcional JP Engenharia, fora das116 entradas, possui22 erros comprovados na base e rejeita a taxonomia `new_contract_regression` das entradas próprias. Não foi alterado ou declarado aprovado. Contexto global antigo foi preservado. Aceite visual humano e integração Git permanecem pendentes.

Após a execução, somente este registro, cópia literal do recibo, metadados das entradas próprias e nota de contexto foram atualizados. O recibo histórico escrito como efeito do teste engine foi preservado externamente e restaurado literalmente à base. Nenhum código, teste ou gate foi modificado depois do FULL.
