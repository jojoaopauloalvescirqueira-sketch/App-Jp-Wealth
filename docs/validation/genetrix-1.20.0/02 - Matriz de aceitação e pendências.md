# Matriz de aceitação — CORE-AC01…24

Critérios originais preservados em evidence/CORE-ACCEPTANCE.json. Esta matriz é resultado separado; não altera aquele arquivo. Resultados de processo, atendimento, qualidade financeira e estado normativo são eixos distintos. Nenhum caso completo recebe aprovação por média ou por compilação. Três processos locais não substituem as três sessões nativas críticas. Todos os24 casos permanecem incompletos no escopo total.

| Caso | Evidência local disponível | Verificação ainda necessária | Execução / julgamento completo |
| --- | --- | --- | --- |
| CORE-AC01 | Scheduler/projeção3 processos, revisão do lifecycle, closure sem trading | EA e módulos com dados no MT5 | INCOMPLETE / INCONCLUSIVE |
| CORE-AC02 | Replay multi símbolo/direção3 processos; loops account-wide conferidos | Captura nativa fora do instrumento do gráfico | INCOMPLETE / INCONCLUSIVE |
| CORE-AC03 | Reader sem produção e diagnóstico account-scoped; estados/leases simulados | Vários gráficos nativos, seleções e único escritor real | INCOMPLETE / INCONCLUSIVE |
| CORE-AC04 | Closure sem Supervisor/trade; módulos disponíveis sem execução | Sessão com AutoTrading desligado e Supervisor ausente | INCOMPLETE / INCONCLUSIVE |
| CORE-AC05 | 19 vetores +300 cenários exatos vs cálculo legado,3 processos | Dados/broker nativos e sequência de coleta | INCOMPLETE / INCONCLUSIVE |
| CORE-AC06 | Fixtures parciais/custos/Genesis e witness de custos3 processos | Rollover/custos tardios reais | INCOMPLETE / INCONCLUSIVE |
| CORE-AC07 | Replay ciclos/pendentes/empates e seleção preservada | Seleção e mudança de ciclos na interface nativa | INCOMPLETE / INCONCLUSIVE |
| CORE-AC08 | Defaultsfalse e Partial reais; UI/status3 processos | Cobertura vinculada e motivos no terminal | INCOMPLETE / INCONCLUSIVE |
| CORE-AC09 | Revisão de isolamento, probes de integração do autor | Falhas injetadas com observação saudável no MT5 | INCOMPLETE / INCONCLUSIVE |
| CORE-AC10 | Legacy135SQL e recuperação; staging/rollback/revisões3 processos | Corrupção/bancos reais em sandbox MT5 | INCOMPLETE / INCONCLUSIVE |
| CORE-AC11 | SQLite busy/recovery3 processos; fences antigas conferidas | Locks de arquivo/leases nativas entre produtores | INCOMPLETE / INCONCLUSIVE |
| CORE-AC12 | Disconnect não vira zero; aging/status3 processos | Desconexão e recuperação nativas | INCOMPLETE / INCONCLUSIVE |
| CORE-AC13 | Legacy recuperação entre processos + preparação sem transação aberta | Interromper/reiniciar EA durante preparação real | INCOMPLETE / INCONCLUSIVE |
| CORE-AC14 | Preparação rejeita mudança de conta3 processos; declaração original conferida | Troca em sandbox sem mudar a conta operacional | INCOMPLETE / INCONCLUSIVE |
| CORE-AC15 | Lock/lease/CAS conferidos e codecs simulados | Duas instâncias nativas, apenas um escritor/notificador | INCOMPLETE / INCONCLUSIVE |
| CORE-AC16 | Reuso dos locks/leases legados, revisão independente | Concorrência Monitor versus legados no MT5 | INCOMPLETE / INCONCLUSIVE |
| CORE-AC17 | 50mil deals/50mil ordens separados, replay3 processos; staging do autor | Coleta/SQLite e tempos nativos nos limites atuais | INCOMPLETE / INCONCLUSIVE |
| CORE-AC18 | Witness de correções3 processos; delete/missing/queue do autor | Rajadas finitas/eventos reais e conclusão estável | INCOMPLETE / INCONCLUSIVE |
| CORE-AC19 | HistorySelect externo resetado entre todas as fatias; custo samecount3 processos | Listas compartilhadas na API nativa | INCOMPLETE / INCONCLUSIVE |
| CORE-AC20 | Scheduler fairness/clock/500ms e progresso3 processos | Latência indivisível/IO e não suprimir alertas no terminal | INCOMPLETE / INCONCLUSIVE |
| CORE-AC21 | UI lógica33asserts3processos +manual; HIS-AC20 bruto falha também na base | Interação/tema/DPI/rascunhos e detalhe nativos | INCOMPLETE / INCONCLUSIVE |
| CORE-AC22 | IDs/Actions/foco/NoCuda bytes preservados e19comparações3processos | Templates/preferências após reinício nativo | INCOMPLETE / INCONCLUSIVE |
| CORE-AC23 | Heartbeat/captura,Partial,age e registros Supervisor separados3processos | Reader financeiro/leases e presença real | INCOMPLETE / INCONCLUSIVE |
| CORE-AC24 | Lifecycle/manual distinguem Cockpit de apoio | Minimizar/fechar/substituir gráfico e consumo nativos | INCOMPLETE / INCONCLUSIVE |

Uma falha obrigatória demonstrada bloqueia o respectivo aceite; insuficiência produz INCONCLUSIVE. A dívida HIS-AC20, erros de julgadores, raw gates e controle da base estão preservados em evidence/independent/legacy-regression. Os resultados favoráveis das partes locais permanecem favoráveis somente no escopo executado.

## Três sessões críticas previstas

| Sessão | Execução | Conta/instalação isolada | Evidências exigidas |
| --- | --- | --- | --- |
| NATIVE-01 | NOT_RUN | Não iniciada | Inicialização, dois módulos e consumidores, fontes/logs, captura e persistência |
| NATIVE-02 | NOT_RUN | Não iniciada | Reinício, conflitos/legados, falhas independentes, histórico/custos |
| NATIVE-03 | NOT_RUN | Não iniciada | Rajada/50mil/progresso, UI/NoCuda, minimização/fechamento, alertas |

Aplicação operacional:NOT_RUN. Não houve troca de conta, ativação de negociação ou instalação. O acesso visual disponível mostrou a instalação anterior; isso não comprova o núcleo1.20.
