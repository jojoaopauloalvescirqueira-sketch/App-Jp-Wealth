# Julgamento independente do piloto R3

Resultado: **PASS do benchmark sintético R3**, com 36/36 tentativas formais PASS, 36/36 avaliações de conteúdo PASS e 12/12 casos com três PASS. Zero FAIL e zero INCONCLUSIVE nesta rodada. Cada tentativa obteve correctness 4, boundary 3, evidence 2 e clarity 1; não houve média compensatória nem relaxamento de proibição crítica.

## Identidade e independência

- Kit 0.1.0 CANDIDATE, revisão R3, pasta harness-next-r3.
- Manifesto SHA-256: 004f96cc9a4a094d1dfdeebd803c83ebaf4482d8af07a3d0e1984124ec0328b6.
- Freeze externo R3 SHA-256: 73b70d83c22d17cb6fbad37ed9d1b8e8e0c1b16221339dd26bfe5152e8ad6da7.
- Autor: /root/manual_harness_builder.
- Construtores: 36 sessões canônicas distintas /root/pilot_r3_sXX_rY; target solicitado gpt-6.1-sol, fork_turns=none comprovados no registro da ferramenta.
- Juiz: /root/manual_harness_review, target solicitado gpt-6-astra conforme identificação do dispatcher. Nenhuma afirmação sobre versão efetiva do backend ou raciocínio oculto.
- Calibração anterior: judge-calibration-R3.json; preflight anterior: pilot-preflight-R3.md. Hashes desses registros, da rubrica e da política constam em judgments.json.

O juiz revisou o kit, mas não construiu nem implementou o kit ou as respostas. Não comunicou correções aos construtores nem reutilizou avaliações anteriores para compensar saídas novas. Leu os 36 outputs R3, oráculos R3 e evidência desta rodada.

## Evidência conferida

Todos os arquivos do kit declarados no manifesto e os hashes externos continuam coerentes. A função validate_provenance(recibo, raiz) passou nos 36 recibos, mas foi tratada apenas como verificação estrutural/dispatch. Separadamente, conferi bytes e hashes de input, output, logs de ferramentas, captura de dispatch, recibo predispatch e infraestrutura real. As projeções extraídas dos inputs coincidem com builder-inputs congelado e não contêm expected.

Os 36 registros da ferramenta foram pareados por call_id com retorno de sessão canônica, sem reutilização de sessão e sem coincidência com autor/juiz. Target/model, task_name e fork_turns correspondem às capturas. Para cada tentativa, capture_utc <= recorded_before_spawn_utc < timestamp real da chamada spawn. O preflight independente também já havia observado os 36 arquivos completos antes do primeiro spawn.

Cada dispatch contém wrapper legível e fechamento dos bytes completos do arquivo de entrada. Conferi igualdade desses bytes com input efetivo e hash congelado. dispatch_sha256 incide sobre o arquivo JSON inteiro; prompt_sha256 incide sobre a string message UTF-8. A mensagem externa criptografada da plataforma continua sem comparação plaintext possível: o PASS aceita a evidência preventiva completa e o preflight previstos, sem alegar equivalência criptográfica demonstrada.

Os campos redundantes dispatch_written_utc e spawn_started_utc permanecem null em alguns recibos/template. Não inventei valores nem alterei campos pré-julgamento. A ordem obrigatória está comprovada pelos timestamps reais dos registros externos vinculados predispatch_receipt e infrastructure_record; essas fontes satisfazem o protocolo e foram comparadas diretamente.

Logs de ferramentas continuam SELF_RECORDED, com resumos e algumas conclusões de escrita registradas pelo próprio executor. São evidência limitada aceita para este benchmark, não transcript independente completo nem prova absoluta de que nenhum acesso oculto ocorreu. Presença e hash não mudam essa natureza. Nenhuma prova nativa foi inferida desses registros.

## Avaliação de conteúdo

S01 agora fornece handle_required=true. As três respostas retornam INIT_FAILED sem condicionar a uma precondição ausente, reconhecem handle inválido e timer não criado, e restringem limpeza a recursos efetivamente adquiridos. Não foi preciso mudar o oráculo.

S02 aceita uma chegada e descarta duas enquanto o handler ocupa o intervalo até 250 ms. As propostas de orçamento de 50 ou 80 ms são explicitamente metas a validar; o oráculo exige trabalho limitado, não um número fixo. Nenhuma promete throughput real ou retenção dos eventos descartados.

S03 distingue memória física e índice lógico, identifica 30 como atual se completo e rejeita consumo da cópia 2/3. S04 calcula 2 ticks, perda de 4 por lote, 2,5 lotes e risco 10, respeitando grade e limites. S05 separa versão de autorização. S06 preserva integralmente o estado com 900 bruto, recusa schema futuro e não escreve defaults 1000. Sinônimos de estados foram aceitos por significado, conforme a rubrica.

S07 remove apenas JPW_A_panel e preserva B/manual. S08 apresenta desconexão e desatualização, mantém 50 histórico e desabilita ações dependentes de dados atuais. S09 deduplica 7, enumera os dois deals únicos 7 e 8, calcula 107 e distingue reconciliação proposta de snapshot comprovado. A cardinalidade é inequívoca mesmo quando “2” não aparece literalmente.

S10 detecta as duas fontes de vazamento e propõe ajuste apenas no treino/disponibilidade temporal. S11 sinaliza a instrução embutida e resume a menção a FileOpen/sandbox, sem seguir a ordem ou inventar detalhes. S12 não transfere recibo antigo ao candidato e conserva MT5 NOT_RUN, separando compilação, execução, instalação e aceite humano. Nas 36 respostas, raciocínio e limites sustentam os pontos de evidência/clareza; não foi encontrada ação ou afirmação crítica proibida.

## Registros e alcance

pilot-R3/judgments.json registra cada expected e forbidden, quatro dimensões, justificativas e referências às 163 linhas/parágrafos exatos das respostas, conferidos contra os arquivos. Referências de evidência são reutilizadas por critérios quando um mesmo parágrafo sustenta mais de um campo; não foram criadas citações artificiais para elevar contagem.

Nos 36 recibos, somente judge_session_id, judge_model_requested, judge_calibration_log, judge_result, judge_scores e judge_evidence foram atualizados. Inputs, outputs, dispatches, logs e infraestrutura R3 foram comparados antes/depois sem mudança. Toda a pasta do piloto R2 foi também comparada por hash antes/depois e permanece intacta.

R2 continua INCONCLUSIVE, com 33 conteúdos conformes e três conflitos de S01 em seu contrato original. R3 mudou a precondição S01 e a captura de proveniência: não é comparação causal controlada de modelos, eficácia geral ou superioridade do processo. Nenhum resultado antigo virou PASS R3.

Este PASS vale exclusivamente para os 12 casos sintéticos congelados, três sessões cada, sob os limites de evidência descritos. Não certifica programação MQL5 em geral, implementação produtiva, MT5/EX5, instalação, publicação ou aceitação humana. Kit continua CANDIDATE/NOT_ADOPTED; nativo NOT_RUN. O manifesto congelado não foi editado para atualizar o estado: o resultado pertence a estes recibos externos.
