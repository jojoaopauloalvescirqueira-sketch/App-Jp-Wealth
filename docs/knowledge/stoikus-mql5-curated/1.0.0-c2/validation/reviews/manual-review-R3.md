# Parecer R3 — deltas do piloto e revisão visual R5

**Conteúdo de 10.6 APROVADO no escopo documental demonstrado. Formato R5 REQUER REPAROS nas páginas 2, 17 e 26. Pesquisa integral permanece com P1 aberto.**

MANUAL.md SHA-256: `b60bb4569430a5eeeb7dab7360c56b64dd392396f71dcb06b2c5914eab217c3c`.

## Reconciliação do piloto

Li os parágrafos novos 10.5/10.6, a qualificação externa R3, o parecer independente pilot-judgment-R3.md e os metadados/contagens de judgments.json R2/R3. Não refiz os 72 julgamentos nem abri as respostas brutas; esta é auditoria de coerência do relato e vínculo da prova.

Os hashes reais conferem com a qualificação: manifesto `004f96cc9a4a094d1dfdeebd803c83ebaf4482d8af07a3d0e1984124ec0328b6`, freeze `73b70d83c22d17cb6fbad37ed9d1b8e8e0c1b16221339dd26bfe5152e8ad6da7`, judgments `dccc55bf9809f0e288d3df7baab7c16178711294bb1b32bd656bb5ae57816674` e relatório independente `f0164913ec4f6f8a629cfe5b869e1396021363894b00f5f683d9a34fb57a6f58`.

R2 conserva formalmente 19 PASS/17 INCONCLUSIVE e conteúdo 33 PASS/3 conflitos S01. R3 registra 36 PASS, 12 casos com três tentativas, sem compensação por média. O texto explica alteração da precondição handle_required e da captura, impedindo comparação causal. SELF_RECORDED, filesystem compartilhado, contextos fresh e target de modelo versus backend efetivo estão explicitamente separados. A distinção entre manifesto imutável pré-piloto NOT_RUN e qualificação externa posterior PASS é correta; CANDIDATE/NOT_ADOPTED e nativo NOT_RUN permanecem coerentes.

Observação P3 opcional em 10.7: “a segunda prioridade é testar o kit completo nas fixtures congeladas” soa ainda pendente após o resultado novo. Pode ser atualizada para manter/repetir essa qualificação quando houver mudança e depois estudar tarefas reais. Não invalida os números ou a qualificação, pois 10.6 explica a conclusão com clareza.

## Achados de formato com reparo concreto

**P2 — Figura 2 perdeu conteúdo semântico (R5 p17).** O Mermaid original de 3.6 contém oito transições rotuladas, incluindo Auditando → Auditando: próxima fatia, além do estado inicial. A imagem mostra somente caixas e setas sobrepostas, sem rótulos e sem loop identificável. Leitor de Word/PDF recebe informação inferior à fonte Markdown. Reparar o render para preservar todos os nós, direções e rótulos, com trajetos distinguíveis; alternativamente acrescentar uma tabela completa de transições compartilhada nos três formatos e uma figura coerente. Reinspecionar a página alterada e eventuais páginas refluídas.

**P2 — Figura 3 perdeu decisão e ramos (R5 p26).** O nó D{Concluído?} virou caixa “D”; as ligações D → sim → Anunciar geração utilizável e D → não → Preservar anterior e motivo desapareceram, deixando destinos desconectados. Reparar parser/render de nós de decisão e arestas rotuladas, ou desenhar explicitamente esse diagrama completo. Não basta mudar a legenda: a lógica precisa reaparecer.

**P2 — Sumário preliminar incompleto (R5 p2), já conhecido.** Capítulos 4 e 6 aparecem sem números; conferir também os demais números após render final. R6 previsto pelo coordenador resolve somente se a página nova for inspecionada e conferida contra os títulos reais.

## Escopo visual e evidências

Abri individualmente todos os PNGs de páginas 1–28 de render-r5. O JSON format-pages1-28-R5.json registra cada SHA-256 e observação. Fora dos três achados, não observei corte de caracteres, invasão de margem, colisão com cabeçalhos/rodapés ou equação ilegível. Figura 1 p7 e equação p10 são legíveis. Os códigos p8, p11, p17 e p26 preservam operadores e indentação. A struct Reading atravessa p7–8, sem perda; mantê-la unida é melhoria opcional. Páginas curtas 4/18/28 decorrem de abertura de capítulo seguinte em nova página e não provam omissão.

Não aprovo páginas 29–56 por inferência, nem afirmo que esta inspeção comprove abertura nativa no Word ou equivalência completa dos pacotes. Um PNG idêntico por hash pode reutilizar este parecer visual; PNG alterado precisa nova inspeção. R5 p2/p17/p26 não têm aprovação reutilizável.

## Pesquisa

P1 de leitura global permanece aberto enquanto REF não tiver cobertura semântica completa documentada. O coordenador informa conclusão agregada TRD/NN; não refiz sua auditoria global nesta revisão de deltas. Nenhum PASS de piloto ou render compensa cobertura textual faltante. Somente os dois pareceres solicitados foram escritos; kit, produto e Markdown permaneceram intocados.
