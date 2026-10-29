# Revisão independente R3 — fechamento dos controles e integração

R1 e R2 permanecem históricos. Esta revisão usa o contrato humano aprovado, o CHG de controles e a comparação com o manifesto anterior à tarefa; não compara o candidato inteiro com HEAD como se suas alterações herdadas fossem deste calendário.

## Parecer delimitado

Não identifiquei blocker técnico remanescente nos bytes de produto e nos juízes delimitados que examinei. A entrega global ainda depende dos focais em andamento, reconstrução/fingerprint estável, FULL final e aceite visual humano. Publicação, ativação externa, execução agendada e confirmação jurídica da permissão não são resultados desta revisão.

## Lacunas de R2 resolvidas

- O check mensal permanente chama o juiz de runtime e agora exige JSON parseável, suite correta, 24 casos únicos numerados 01–24, todos PASS e summary exato24/0. O watchdog de5segundos do NOVO juiz mantém o processo Node vivo para classificar um Promise que não termina. Ele não altera o limite de900segundos nem qualquer caso antigo. Executei independentemente24/24 no candidato scratch de hash2162c48cdd0b7d945a9e2dfb2c57a1fabf34191f4ff8d98f81f12acd9233b07f, agora idêntico ao juiz aplicado. Os4 mutantes de lifecycle têm recibos do construtor com exit1; examinei-os, sem alegar que os reexecutei. O incidente anterior de exit0 sem recibo permanece TEST_HARNESS_FAIL, não contraprova aprovada.
- O ciclo dispose/resume foi revisto: init não reativa sessão encerrada; a retomada pública é explícita e acionada após as guardas de abertura/montagem aceitas. O caso24 resolve o GET antigo depois de resume e antes de qualquer GET novo, impedindo que uma nova requisição mascare a invalidação da antiga. Timers e listener online têm controles de unicidade. A retomada deste cache público não renova autoridade de gravação financeira.
- Li o teste real HTTPv2→adaptador15→consulta16→agenda/marcador. Os16 cenários anteriores de cache/falhas continuam; a igualdade de HTML mensal superada foi substituída por identidade do host, mês e seleção preservados, enquanto2 casos novos exercem atualização verdadeira, CAD/USD/High, exclusão deMedium, recorte legado, rascunho/foco/cursor, requisição compartilhada, falha com último cache e S/documento financeiro intactos. Recibo do focal executado pelo root:186PASS/0PRODUCT_FAIL em18 casos. O primeiro NameError de importexpect é falha do harness preservada, não falha do produto nem prova de ambiente externo.
- Li o caminho de Backup Completo: nove moedas são exportadas pelo Blob, lidas como File, normalizadas e comparadas no snapshot de retomada, byte a byte. O cache público existe no estímulo e permanece excluído. A preferência antiga de cinco e os seis inválidos continuam cobertos. O focal do root registrou2PASS; o root posteriormente informou os8 casos de recovery aprovados. Não interpreto normalização/importação sintética como teste humano de recuperação de um backup pessoal.
- Li o caso incluir novas moedas: preferência válida antiga de cinco é preservada sem gravação na abertura; só a ação explícita inclui as nove, mantendo impactos/conteúdos e dados financeiros. O focal do root foi informado PASS.
- O CHG N3 agora inclui o caminho exato do template externo. A ausência de ativação continua explícita.

## Adaptação de fixtures e oráculos aprovada para os próximos focais

A fixturecalendar_packet usava sourceId:null para coberturas GBP/JPY/NZD/CHF. O leitor atual verifica vínculo real sourceId→moeda; esses registros não são coberturas válidas. É apropriado declarar quatro fontes sintéticas explícitas e ligar os quatro intervalos a elas. Não enfraquecer esse vínculo no produto. Preservar atribuição/licença/URL da fonte original e validar cinco links exatos, sem inventar licença para as fontes pendentes.

Os filtros GBP-only devem desmarcar todas as oito outras moedas do catálogo aprovado e restaurar a seleção anterior exata. Deixar quatro novas moedas marcadas deixaria de testar GBP-only. O conjunto esperado deve permanecer independente da implementação.

Confirmei quatro oráculos de texto em feed_recovery, nas linhas210,222,228,231 da leitura pré-ajuste. A troca de “Atualização da fonte:” por “Referência do pacote:” é semântica deliberada: os mesmos in/not-in devem preservar diagnóstico, último conteúdo e isolamento por contexto. Não mudar nenhum estado esperado para contornar falha.

O teste canônico de distribuição pode receber FEED503 controlado antes da carga para exercer o pacote embarcado/fallback e conservar IDs, nomes, URLs, atribuições e licenças EXATOS. Preservar os quatro modos HTTP/PWAoffline/file/portátil, CRUD, hash dos módulos, origens inesperadas e a prova de resposta pelo service worker. Esse503 não comprova ausência de chamadas de rede; é estímulo explícito de falha e não deve engolir requests inesperados. O teste de transportev2 separado é obrigatório e cobre o caminho de atualização. Não mudar produto nem expectativas canônicas para acomodar o bootstrap vazioV1.

## Critérios preservados

Revalidei por SHA os mesmos bytes anteriores à tarefa em tools/quality_gate.py, tools/ui_visual_quality_test.py, tools/calendar_visual_quality_test.py e AGENTS.md. Portanto permanecem os mesmos116IDsFULL, ordem,413 critérios visuais existentes, tolerância2px e timeout900segundos; o inventário anterior confirma FAST4/STANDARD71/FULL116. Nenhum novo check requer retirar outro: os juízes novos são chamados pelo check mensal já ligado a STANDARD/FULL.

O snapshot de hashes desta leitura está em review-r3-file-snapshot.json. Build observado3b97e856fae34c44; qualquer rebuild posterior deverá ter recibo próprio. O coletor955906... e juizcb0737... coincidem com os32 casos que executei pessoalmente. Fonte pública, pacote e foco não são provas de dados financeiros reais, cobertura mensal completa ou ausência de risco.

## Limites de atuação

Nenhum arquivo do repositório, memória, branch ou dado pessoal foi alterado pelo revisor. Somente relatórios/helpers novos externos. Nenhuma suíteFULL, Chrome nativo, operaçãoGit, coleta real, ativação ou publicação executada por esta revisão. FontesFF semanais continuam parciais por intervalo; ausências de evento não são cancelamentos, e consulta recente não renova coleta antiga. A aprovação final deve citar os recibos do candidato reconstruído em vez de derivá-la deste parecer focal.

## Adendo — bytes das duas adaptações finais da fixture

Li os deltas aplicados antes da nova execução do root: FEED503 controlado também em calendar_packet, somente nos casos UI sintéticos, instalado após bootstrap e antes da carga; transporte186 permanece em outro teste sem esse isolamento. install_bootstrap continua recusando recursos externos inesperados. A asserção de orientação de impacto exige agora tanto “classificação Forex Factory” quanto “curadoria editorial JP Wealth”, em vez de atribuir tudo à classificação editorial. Edges conserva os cinco paresID/href exatos, atribuição original e licençaURL. Ambas as mudanças deliberadamente substituem pressupostos superados sem relaxar estados de falha, filtros ou contagens.
