# Correção R2 do harness 0.1.0 CANDIDATE

Resposta ao parecer independente FAIL em reviews/harness-review.md. Não houve piloto, adoção, execução nativa ou alteração de produto/AGENTS/CI/Git.

## Preservação

Snapshot completo R1 em harness-revisions/R1/kit, com harness-freeze-R1.json, harness-report-R1.md e capítulo 10 anterior. harness-freeze.json e harness-report.md originais preservados. Hash do manifesto da cópia R1 conferido contra freeze original: coincide.

## Correções

P1: doze arquivos builder-inputs/S01..S12.json possuem somente id/topic/prompt/input e são a única projeção permitida para construtor. Cases completos permanecem com juiz, com novo campo fixture_isolation sem contradição. Teste confere exatamente quatro campos, igualdade dos dados projetados e ausência de expected/rubric. Conteúdo dos oráculos expected não foi mudado. PILOT e capítulo atualizados.

P2 proveniência: provenance-policy.json R2 define antes do piloto os obrigatórios observáveis: sessão, target/model_requested, fresh_mode, hashes input/output, logs raw e tools, lista tools_used e IDs da tentativa. Depois do julgamento exige identidade/calibração/evidência do juiz. Campos opcionais model_backend_exact_build e reasoning_hidden podem ser null somente com justificativa não vazia; não se infere build nem configuração oculta. Obrigatório ausente continua INCONCLUSIVE. Log de ferramentas é obrigatório mesmo sem uso: arquivo vazio explícito e lista vazia. A função validate_provenance testa estrutura; juiz precisa verificar existência/conteúdo/hashes e fresh real. Templates, rubrica, prompt juiz e capítulo concordam.

P2 estados: manifesto exige revision, state_revision, validation_policy, adoption, native_mt5 e behavioral_pilot. MANUAL_CANDIDATE exige NOT_ADOPTED e nativo NOT_RUN. state_revision=1 exige piloto NOT_RUN. Revisão de estado futura admite enum IN_PROGRESS/PASS/FAIL/INCONCLUSIVE com recibo local SHA-256, identidade de revisão/estado e tentativas únicas; PASS exige 36 IDs. Isso permite avanço futuro sem fixar piloto NOT_RUN para sempre. Recibo de estado é validado estruturalmente, não transforma IDs em prova semântica de julgamento. A adoção/nativo exigem política/revisão autorizada, não troca de string.

Symlink loop: RuntimeError em raízes ou referências vira JSON controlado exit1, sem traceback. Continuam rejeitados symlinks declarados e escapes; raízes fornecidas explicitamente continuam canônicas.

## TDD

harness-R2-red.log: 21 testes, nove falhas observadas antes das correções (adoption/native/pilot/enum ignorados, ausência builder-inputs, loop symlink com traceback e ausência validador de proveniência). Positivo de estado futuro foi incluído para impedir engessar NOT_RUN.

harness-R2-green.log: 21/21 PASS, 0,752s. Execução final do checker com kit/repo e três PDFs originais: exit0 INTEGRITY_OK. Kit não autentica sozinho o manifesto: freeze externo R2 necessário. Não houve suíte host produtiva nem tentativa de modelo.

## Freeze e limites

Novo recibo externo harness-freeze-R2.json, separado de R1, inclui manifesto/rubrica/cases/projeções builder/política de proveniência. A revisão R2 deve receber nova revisão independente antes do piloto. Nenhum resultado R1 foi reclassificado. Capítulo permanece na meta 3–4 mil palavras; contagem exata emitida no comando de freeze. 36 tentativas continuam planejadas, zero executadas nesta contribuição.
