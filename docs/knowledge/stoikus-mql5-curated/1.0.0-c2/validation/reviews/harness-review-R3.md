# Revisão independente R3

Veredicto: APROVADO para iniciar a nova rodada sintética de 36 sessões, sob o freeze R3. Não é aprovação comportamental, adoção ou prova nativa. Revisor/juiz /root/manual_harness_review, distinto do autor e dos construtores. R2 e seu piloto permanecem inalterados.

## Conferências

- Manifesto R3 SHA-256 004f96cc9a4a094d1dfdeebd803c83ebaf4482d8af07a3d0e1984124ec0328b6 confere com freeze; rubrica, política e todos os arquivos declarados também conferem.
- 30/30 testes PASS nesta revisão, 0,734 s. Testes negativos cobrem hash, path escape, symlink/loop, estados, falta de dispatch e tipos inválidos; verificação de bytes dispatch exercita positivo e adulteração. Checker completo contra PDFs fica no recibo do integrador; não foi duplicado aqui.
- Conferência independente dos 12 expected R2 versus R3: igualdade integral. Única alteração de input: S01 acrescenta handle_required=true. Os demais inputs são iguais. Todas as projeções builder têm exatamente id/topic/prompt/input, sem gabarito.
- S01 agora explicita a precondição ausente: handle inválido e obrigatório durante OnInit sustenta INIT_FAILED; limpeza continua limitada ao que foi adquirido. Nenhum oráculo foi adaptado para aceitar outputs antigos.
- validate_provenance trata recibo não objeto, mapa de razões null/lista e metadados/ferramentas de tipo indevido como erros controlados. Reprodução adicional dos formatos antes problemáticos não levantou exceção.
- Com evidence_root explícita, validador rejeita escape/symlink e confere hash dos bytes do dispatch e existência do registro de infraestrutura. Não confere automaticamente os hashes de input/output/tools nem conteúdo/ordem temporal da infraestrutura; juiz deve fazê-lo. Forma de um argumento é apenas estrutural. Essa distinção está documentada e não bloqueia o piloto.
- Checker segue stdlib e leitura/stdout; caminhos canônicos, códigos 0/1/2 e regras de candidato mantidos. O freeze R2 ainda coincide com o manifesto original. Não houve edição de kit, R2, respostas, produto, AGENTS ou CI.

## Condições operacionais já exigidas pela R3

Antes de cada spawn, salvar payload legível completo, incluindo texto do wrapper, bytes efetivos de ENTRY/contexto e projeção, target/model e fresh config. Um JSON que contenha somente o caminho do input não basta sozinho para a exigência de bytes completos: manter o conteúdo integral no registro prévio ou pacote de evidência inequivocamente vinculado e congelado antes do dispatch. Calcular dispatch_sha256 sobre o arquivo real no domínio declarado; não repetir ambiguidade entre hash da string message e do envelope.

Preservar recibo de escrita/hash anterior e timestamp/recibo real da chamada spawn. Timestamps preenchidos depois ou mtime isolado não provam ordem. Não reconstruir payload após saída. Manter sessões novas e IDs distintos, input/output/tools reais e juiz independente. O validador não autentica a si mesmo nem garante completude de log SELF_RECORDED.

## Observações editoriais não bloqueantes

PILOT ainda conserva título “Política de estados R2”; rubric.inconclusive menciona “frozen R2 policy”, embora provenance_policy aponte ao arquivo local R3 e o prompt judge exija R3. O regime de campos opcionais é o mesmo, portanto não há conflito material de aceitação. README conserva narrativa R2 com “nenhum piloto foi executado para esta revisão”: deve ser lida como estado de preparação R3, nunca como negação da rodada real R2 preservada. Registrar esses resíduos; não editar freeze durante a rodada.

## Calibração e comparação entre revisões

Controles R3 relidos com casos S04/S12/S06 e julgados antes de tentativas R3: positivo PASS 10/10; negativo FAIL por falsa prova nativa; insuficiente FAIL por campos ausentes. Ver judge-calibration-R3.json com respostas, razões, hashes e horário. Esses controles não contam no piloto nem reclassificam R2.

A R3 altera simultaneamente a entrada S01 e o processo de captura. Se obtiver melhor resultado, isso não demonstra causalmente melhoria do modelo ou eficácia geral do harness. Há mudança de fixture, condições de evidência e novas amostras. Reportar resultados de cada rodada separadamente; os 17 INCONCLUSIVE e três divergências de conteúdo S01 da R2 continuam válidos em seus respectivos contratos. Nenhum PASS pode ser migrado da R2 para R3.
