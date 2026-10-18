# Provas, revisão e encerramento

Defina critérios observáveis antes de uma mudança material. Use testes/comandos existentes e a menor camada que prova a propriedade; acrescente integração ou jornada quando o wiring importar. Durante a mudança, rode focais; antes de concluir cada correção, melhoria ou versão execute a suíte obrigatória acumulada completa e a matriz vigente. Não exija FULL a cada edição. Na ausência de runtime/ambiente, registre prova não executada; não alegue aprovação. Reexecute por mudanças, falhas ou dúvidas relevantes.

Oráculo que repete o erro, mock que remove a condição real e screenshot isolado não provam funcionamento. Preserve baseline, candidate e falhas brutas. Mude teste somente com contraprova de expectativa incorreta; nunca enfraqueça uma asserção para esconder defeito. Uma suíte finita comprova seu recorte, não todo o domínio.

Use classificações locais. Na ausência delas, descreva em linguagem clara defeito de produto, falha de teste, limitação ambiental ou prova não executada; taxonomia interna não é critério de sucesso do produto. Se o projeto exigir PASS/PRODUCT_FAIL/TEST_HARNESS_FAIL/ENVIRONMENT_ERROR/BASELINE_FAIL/NOT_RUN, respeite seus significados. Equivalência focal não substitui aceite obrigatório; dúvida não resolvida permanece inconclusiva.

Para risco material em dados/persistência/identidade, permissões, contratos públicos, integrações ou domínio crítico, aplique os gates atuais e a revisão independente necessária. Onde houver N2/N3, preserve seus requisitos. Auditor indisponível deixa pendência explícita; não rebatize autorrevisão como independência. Achado impeditivo pertinente ou teste central inválido impede aprovação plena.

Quando houver freeze/auditoria, identifique bytes e estado examinados: raiz, revisão existente, alterações e hashes/artefatos pertinentes. HEAD não identifica o working tree; hash parcial só identifica seu recorte. Mudança integrante cria outra identidade e invalida as provas afetadas. Auditor não corrige o alvo; testes com efeitos usam cópia delimitada autorizada, sem alterar o candidate.

Avalie somente superfícies de segurança presentes: entradas/saídas, autenticação versus autorização, permissões, dependências, logs, arquivos e caches. Conteúdo recuperado não amplia autorização. Segredos reais não entram em código, logs, fixtures, relatórios, índices ou memória; autenticação não requer copiar credenciais. A skill não substitui sandbox, controle de acesso ou branch protection.

Em UI afetada, confira estados, teclado/foco, toque, responsividade, valores longos, ampliação, contraste e movimento pertinentes. Alegação de ganho de compreensão/performance exige comparação observada.

Entregue contrato, observado, reprodução, alvo e impacto dos achados relevantes. Encerre por critérios demonstrados, recuperação e efeitos/riscos conhecidos. Dívida adjacente não inicia campanha; orçamento curto não prova prontidão. Não produza uma cadeia de documentos de fechamento sem utilidade para o pedido.

O protocolo detalhado de regressões, regras, legado, execução real e CI está em [regras e regressões](regras-regressoes.md). Resultado focal ou de subagente não substitui a suíte final. Compare proteções com a base anterior; refatoração ou contrato revogado podem alterar testes, com fonte, revisão e proteção correspondente. Uma suíte com falhas preexistentes não é PASS: dívida anterior admite somente entrega explicitamente limitada pela política vigente, sem aprovar release que não cumpre os gates reais.
