# GENETRIX 1.20.0 — implementação e validação do candidato R1

6 de outubro de 2026 · Produto1.20.0 · MQL1.200 · Cálculo1.9.0

O candidato reúne Observer e Accountant em **um `JPW_Genetrix_Monitor`**, para uso em gráfico de apoio dedicado. Isso elimina a necessidade de alternar os dois EAs no mesmo gráfico. **A compilação nativa está comprovada; a aplicação no seu terminal e o aceite operacional continuam pendentes.** O controle visual do Windows não demonstrou receber/responder a F4 e ao clique no IDE. Nenhum arquivo ou EA da instalação operacional foi substituído.

## O que mudou

| Componente | Entrega |
| --- | --- |
| Núcleo | Novo EA observacional, dois módulos habilitados, um lifecycle/timer; conta inteira, sem envio de ordens |
| Monitoramento | Runtime extraído do Observer; Stop Risk, Histórico Pessoal e snapshots históricos com estados separados |
| Contabilidade | Coleta, ordenação, replay e codificação em etapas retomáveis; TEMP/RAM; publicação financeira transacional |
| Execução cooperativa | Orçamento500ms por handler, fatia contábil100ms; prioridades e promoção de tarefas preteridas; duração real registrada |
| Diagnóstico | Armazenamento técnico aditivo; presença, captura, qualidade, motivo, progresso e gráfico de origem separados |
| Cockpit | Quadro Componentes da conta em Sistema, usando cache, envolvimento de texto e paginação existentes |
| Compatibilidade | Observer e Accountant anteriores preservados para rollback; locks financeiros e defaults de cobertura continuam |

Nos gráficos de trabalho permanecem **Genetrix · Conta** e **NoCuda · Gráficos**. O Supervisor7x é separado e opcional; não foi instalado, executado ou armado. Fechar o Cockpit não encerra o núcleo; fechar/substituir o gráfico de apoio interrompe a coleta. Minimização ainda exige teste nativo.

Os núcleos matemáticos Ledger Core, Ledger Terminal, alavancagem, NoCuda e fluxos de ações/foco permanecem idênticos à base onde a comparação de bytes se aplica. Ledger Store recebeu funções aditivas de staging e commit; schemas financeiros anteriores e contratos de leitura foram preservados. O build/versionamento mudou; isso não é alteração de fórmula.

## Evidência realmente executada

| Verificação | Resultado e denominador | Limite |
| --- | --- | --- |
| Replay independente | 23.925 assertivas em cada um de3 processos;19 vetores legados,300 cenários sintéticos e50mil deals/50mil ordens em ensaios separados | Produção Replay compilada no host; não é coleta MT5 ou conta real |
| Preparação/commit independente | 748 assertivas em cada um de3 processos; SQLite real, queries/transações fechadas entre fatias, correções de custos em fases distintas, troca de conta, geração divergente, rollback, busy e recuperação | Origem/clock/API controlados |
| Scheduler/status independente | 61 assertivas em cada um de3 processos | API/lease simuladas; IO host real |
| Projeção de status independente | 37 assertivas em cada um de3 processos,12 cenários | Função real com seams controlados |
| UI independente | 33 assertivas +19 comparações de preservação em cada um de3 processos | Collector/texto/wrappers reais; fontes/layout/interação MT5 não executados |
| Pacote/manifesto independente | 263 verificações em cada um de3 processos | Hashes, ZIP, closure sem negociação e defaults; não prova runtime |
| Ledger legado |19 vetores Decimal,135 assertivas SQLite e6 de recuperação entre processos | Ensaio host independente preservado |
| Stop Risk legado adaptado |3 processos favoráveis;9 assertivas numéricas e recuperação SQLite por processo | Adaptação apenas do caminho do Runtime; MAIN/SHIM/asserts intactos |
| MetaEditor nativo | **33/33 programas,0 erros e0 avisos por programa**, MetaEditorbuild6230, X64 Regular; EX5 novos vinculados a fontes/logs | Compilação não executa o EA, UI, alertas ou persistência no terminal |
| Sessões críticas MT5 | **0/3 realizadas — NOT_RUN/BLOCKED** | Controle visual do Windows sem resposta verificável |
| Migração e conferência final | **NOT_RUN** | Instalação operacional preservada |

Essas contagens descrevem verificações estreitas; não são uma nota agregada nem aprovação dos24 casos completos. Cada caso e seu restante estão na matriz. Os autores também fizeram probes de debug, separados das revisões independentes. Os pareceres nunca aprovam o próprio módulo do revisor.

## Gauntlet e falhas preservadas

Critérios CORE-AC01…24 congelados antes da implementação, hash `990cbeb7800091895ba01aa3930fca5a9d9d0b55dfde899bbc4e76ebb0b23b64`. A base1.19R3 foi preservada. Rodada R0 recebeu contraprovas, correções e novos freezes; R1 contém fontes estabilizados. As revisões dos julgadores são independentes da revisão do produto.

Quatro achados foram corrigidos: Raiz N permanecia Preparando sem trabalho; diagnóstico poderia consumir tempo antes das tarefas prioritárias; contabilidade incompleta poderia aparecer Current; Stop Risk poderia declarar Current após falha conhecida de observação/lease. A contabilidade recebeu uma terceira leitura integral da origem depois da codificação para detectar correções de custos sem alteração de contagem. Os critérios não foram relaxados.

Erros de preparação/extratores dos julgadores foram guardados como erros do avaliador, com zero assertivas executadas quando aplicável. O gate StopRisk antigo ainda procura cálculos no EA que virou wrapper; o gate do pacote guarda versão fixa1.17.0. Seus resultados brutos foram conservados, e as adaptações/verificações novas têm critérios e recibos próprios. O preflight web do espelho isolado continua **BLOCKED/ENVIRONMENT_ERROR** por requisitos de Git/contexto web ausentes; não foi convertido em PASS ou satisfeito por arquivos inventados.

**Dívida pré-existente: HIS-AC20 mantém `PRODUCT_FAIL` bruto em3/3 tentativas do juiz antigo.** O mesmo resultado ocorre na base1.19R3 em3/3 controles. O teste tenta clicar no detalhe após navegar, antes de concluir a leitura; a produção limpa rows/buttons e exige dados disponíveis, enquanto o seam do render não conclui essa leitura. O delta1.20 não altera esses corpos. A análise identifica uma precondição incompleta do ensaio; conserva a falha bruta e não atribui aprovação ao caso. A interação real continua pendente. Não foi feita correção incidental ou reescrita do resultado esperado para obter aprovação.

## Limites e decisão

O histórico MT5 não é snapshot transacional universal. Três passagens de conteúdo, epoch de eventos, composição e geração-base reduzem as janelas observáveis, mas não demonstram ausência universal de alteração sem callback entre a última conferência e a gravação. Chamadas indivisíveis podem exceder500/100ms; não existe promessa de latência pontual. O ensaio50mil de replay não comprova duração de coleta nativa50mil ou cada corretora.

Custos/histórico continuam falsos até evidência vinculada; `Partial`, `N/A`, `PENDING`, `NOT_HOMOLOGATED`, `BLOCKED` e `UNVERIFIED_NATIVE` não são suprimidos. Presença não comprova resultado atual, homologação, fase ou disciplina. O núcleo não implementa o controlador completo V11 nem certifica eficácia financeira.

**Decisão: candidato auditável e compilado, validação parcial; aceite completo INCONCLUSIVE e migração NOT_RUN.** Antes de aplicação, executar as três sessões críticas isoladas, registrar persistência/concorrência/alertas e conferir no seu gráfico resumo, Cockpit e ambos os módulos juntos. Nenhum Supervisor será armado, conta trocada ou pacote publicado nessa etapa.

## Identidade e arquivos

Build `8a01094f354dc52ed37e14d585b6625d11dc62614a5019aa74d5dc8da7497f1e`. Fingerprint MQL `1290186a730aaaf8f1d5645318ff8c814a7dc821e419d9eb3c16015cadf1d783`.

Fontes ZIP SHA256 `be5899a1a9b86b781c8108468096a4a2b47fb173e80ef50977aa7afef580639f`. Compilados ZIP SHA256 `4f7f5c8b593a53611dc94bda387a69355d1677b3f5fac66446d990a99d516105`.

Manual ilustrado:8 páginas renderizadas e inspecionadas,4 esquemas didáticos;124 parágrafos/células conferidos contra o Markdown sem omissão. Nenhuma ilustração representa prova de MT5. Manifesto, logs e pareceres na entrega identificam os bytes exatos; as referências históricas não transferem aceite.
