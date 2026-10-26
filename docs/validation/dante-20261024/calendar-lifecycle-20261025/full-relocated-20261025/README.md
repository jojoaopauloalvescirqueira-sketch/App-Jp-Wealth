# Validação completa com saídas temporárias isoladas — 25/10/2026

Build `8c127c2f92de375e`, branch `codex/dante-guia-20261024`, HEAD `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`.

A entrada oficial terminou com **101 PASS, 0 PRODUCT_FAIL e 1 ENVIRONMENT_ERROR**, exit 1. Os 102 checks foram executados entre 15:33:33 e 16:20:03, horário de São Paulo; tempo do processo 2.790,959 segundos. O gate permanece **não aprovado**: `ui-visual-quality` atingiu 900,026 segundos. [Agregado bruto](full-relocated.json), [log](full-relocated.log), [comando e exit observados](full-relocated-command.json).

O arquivo temporário próprio desta rodada foi mapeado para scratch após o handshake documentado. [Mapeamento](redirection-mapping.json), [wrapper exato](redirect_full.py), [revisão independente](output-configuration-5eada/ZOMBIE-GUARD-REVIEW.md) e 46 contraprovas estão preservados. O preflight produziu `PREFLIGHT PASS`, com branch e HEAD esperados; não se presumiu sucesso pelo estado do processo auxiliar.

Todos os 679 inputs congelados permaneceram iguais. Não houve alteração no aplicativo, gate, limite, fixtures ou oráculos nesta rodada. As cópias e seus hashes estão em [integridade](evidence-copy-integrity.json). Os relatórios posteriores são documentação de execução fora desse inventário; o ACTIVE-TASK permanece congelado e em andamento.

A matriz visual produziu saídas PASS parciais, inclusive até os oito casos compact-native200, mas não concluiu seu recibo e sua validação de cobertura. [Saída parcial bruta](ui-timeout-output-tail.txt) não equivale a 413/413. O focal anterior 413/413 em 853,471 segundos continua prova separada. A nova execução também expirar com outputs físicos em scratch não comprova a causa das diferenças de duração.

Os demais 101 checks passaram nesta execução: guia com Dante, calendário e recuperação, Planejamento, persistência, backup, finalização, Notas, notificações, Forex, PF, Alladin, downloads, reprodução oficial, atualização do service worker e os três jogos. O resultado de cada um está no agregado, sem combinar rodadas para obter aprovação global.

As duas preparações abortadas antes desta rodada estão em `setup-attempt1/` e `setup-attempt2/`, com classificações brutas preservadas. O FULL completo anterior 101/1, a repetição interrompida e a matriz isolada continuam nos respectivos arquivos históricos.

Foi preparada e revisada uma [proposta para reduzir chamadas repetidas do verificador](visual-budget-proposal/README.md). O patch **não foi aplicado**. Altera a forma de medir do próprio juiz e exige CHG e autorização específica pelo AGENTS.md, linhas 81 e 93. Ganho de tempo e equivalência no navegador permanecem NOT_RUN; não há promessa de caber no limite. Sem alteração de critérios, tolerância de 2 px, 413 casos, 102 checks ou 900 segundos na proposta.

As janelas de teste terminaram e o Mac foi liberado. Aceite visual humano, reconhecimento/fidelidade do Dante, leitor de tela real, Safari e toque físico permanecem separados. Sem commit, merge, push, publicação, dados reais ou mudança de memória global.

## Revisão independente desta rodada

[A auditoria dos recibos](full-relocated-independent-audit.json) confirma 102 IDs e ordem, comandos equivalentes após normalização exclusiva da pasta de saída, corpo e exit do preflight, 679 hashes e 160 fontes visuais sem divergência, calendário14/14 com lifecycle uma vez e presença dos24 destinos de evidência. As cópias principais coincidem com os originais. Trata-se de auditoria de presença/cabeçalhos e identidade, sem comparação exaustiva dos payloads pesados. O veredito continua **FULL executado com erro de ambiente, não aprovado**; não existe recibo UI413 desta rodada.
