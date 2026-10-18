# Harness visual — compilação otimizada — 18/10/2026

## Autoridade e escopo

Registro da autorização humana específica recebida nesta conversa: **“Autorizar patch e validação completa”**, em resposta à proposta `PROPOSTA-HUD-COMPILER.patch`. Este documento registra a decisão; não concede autoridade ao executor. Risco N3/control plane, A4. Trilha separada do produto e de seus critérios de aprovação; branch existente `codex/stoikus-installer-20261014`, raiz `/private/tmp/jpw-stoikus-installer-20261014`, base `bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4`.

O JP Wealth distribui componentes financeiros cuja apresentação no MT5 deve conservar valores, escopos e estados. O helper `tools/leverage_host_layout.py` compila replays C++ de geometria e rasterização para testar fontes MQL no host. Não é o compilador de produção MetaEditor nem um oráculo de resultado financeiro.

Permitidos neste delta: este CHG e `tools/leverage_host_layout.py`. Alteração autorizada: acrescentar somente `-O2` e comentário explicativo ao comando C++ compartilhado. Não alterar casos, asserções, contraprovas, prazos, classificações, MQL, fórmulas, dados, AGENTS, CI, gates, preferências globais ou regras de aprovação. Não portar a alteração para outras árvores antes da revisão e da integração correspondente.

## Problema, comparação e crítica anterior

O HUD_TARGETS original da main não modificada excedeu 60s neste ambiente, assim como a execução do candidato anterior. O C++ retido nas duas execuções tem 95.232 bytes e SHA-256 `d85d90037fcc6a4229f443210eb78480e68595adc1459aee672caf8b85d68c99`. Compilado externamente com somente `-O2` adicional, terminou em 7,743s, com 8.192 combinações e 293.191 verificações, zero falhas. Isso é diagnóstico externo, não PASS do juiz alterado.

A crítica independente conferiu a identidade do C++, as verificações explícitas que não dependem de macro assert, as contraprovas no mesmo programa e o escopo compartilhado de compile_cpp. A proposta preserva `-Wall`, `-Wextra` e timeout de 60s; não inclui NDEBUG, fast-math ou supressão de warnings. Os recibos originais continuam falhos e preservados; nenhuma exceção de auditoria inativa é aplicada.

Evidências privadas: `jpw-consolidacao-worktrees-20261018/host-timeout-diagnosis/`, com UNMODIFIED-MAIN.json, O2-DIAGNOSTIC.json, C++ retido, patch e plano. O Harness canônico consultado possui SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`; AGENTS exige CHG próprio, antes/depois, auditoria e aceite humano para este N3.

## Critérios e validação exigida

1. Diff limitado aos dois arquivos permitidos; comparação textual e hashes antes/depois.
2. Comando C++ mantém todos os demais argumentos e prazo; nenhuma mudança nos geradores de casos ou oráculos.
3. Executar a suíte host inteira do candidato congelado, incluindo contraprovas. Falha obrigatória continua bloqueante.
4. Executar gates de integração pertinentes e obter revisão independente após aplicação; vincular resultados à identidade exata.
5. Distinguir host, construção do instalador, execução Windows/MT5, aprovação financeira e aceite humano. Compilação otimizada do teste não aprova produto em runtime.

## Preservação e rollback

As oito árvores e o Git comum foram copiados integralmente e conferidos antes das alterações. Reversão limitada a retirar `-O2` e seu comentário; conservar este registro e todos os recibos. Não retirar casos, ampliar prazo ou converter falhas antigas em PASS. O pedido geral de commit/push/merge permanece condicionado aos gates aplicáveis.

**AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED.** A configuração de compilação do runner visual muda; critérios, contratos, fontes financeiras, instruções globais, CI e ativação do Harness permanecem. Não há reindexação automática. O índice focal do produto pode citar este CHG como trilha independente sem ampliar autoridade. Estado ao registrar: aplicação e provas oficiais pendentes.
