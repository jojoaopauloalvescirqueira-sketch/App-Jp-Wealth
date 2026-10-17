# Revisão independente R2

Data 2026-10-15. Revisor manual_harness_review, independente do autor/construtor do kit. Escopo restrito: correções do parecer R1 e regressões introduzidas. R1 e parecer anterior preservados; nenhuma tentativa real executada.

## Veredicto

APROVADO para iniciar o piloto sintético sob a política congelada R2. Conformidade: PASS com limites documentados. Qualidade das correções: PASS com observação não bloqueante abaixo. Não significa aprovação comportamental, adoção ou validação MT5.

## Evidências e resolução

- Freeze R2: conferidos hashes de manifesto, rubrica, política de proveniência, 12 casos, 12 projeções e todos os arquivos declarados do kit. PASS.
- Snapshot R1: manifesto coincide com freeze original; os 12 expected são iguais em R1 e R2. Não houve ajuste de oráculo para produzir PASS.
- Testes desta revisão: 21/21 PASS em 0,826s. Checker completo contra PDFs originais cabe ao integrador; não duplicado aqui.
- P1 vazamento do gabarito: RESOLVIDO. Projeções têm exatamente id/topic/prompt/input, iguais aos campos originais. PILOT proíbe entregar cases completos. Operador ainda deve preservar payload completo para conferir ausência de acesso ao gabarito.
- P2 proveniência: RESOLVIDO antes das tentativas. Política lista observáveis obrigatórios, campos pós-julgamento e duas indisponibilidades opcionais justificadas. model_requested é target e não build efetivo; não inferir backend/reasoning escondidos. Falta de log obrigatório continua INCONCLUSIVE, mesmo quando saída está correta.
- P2 estados: RESOLVIDO para política atual. Adoption/nativo são validados; estado comportamental futuro exige revisão e recibo/hash. Quantidade de IDs não prova por si só cobertura 12×3, fresh, resultados ou independência: juiz deve verificar os registros, conforme explicitado no protocolo.
- Symlink loop: RESOLVIDO para caminho/raiz via captura RuntimeError; não é defesa de acesso concorrente hostil.

## Observação não bloqueante

validate_provenance assume unavailable_reasons como objeto. Reprodução somente memória: validate_provenance({'unavailable_reasons': None}) levanta AttributeError em vez de retornar lista de erros. O template correto e a política exigem mapa, e a função é auxiliar estrutural, não mecanismo de aprovação automática. Tratar recibo malformado como INCONCLUSIVE/erro de validação no operador; não gerar PASS nem deixar o processamento interrompido mascarar tentativas. Melhoria futura: validar tipo do recibo e desse mapa antes de .get. Não é necessário alterar freeze para executar este piloto com registros válidos e conferência independente.

## Calibração

Controles congelados julgados separadamente das tentativas reais; respostas preservadas em judge-calibration.json. Três veredictos de conteúdo concordam com controles. Calibração não fabrica proveniência de execução para exemplos nem conta no total de 36. Sessão revisora/juíza é distinta do autor e futuros construtores; mesmo modelo eventual não significa diversidade de modelo.
