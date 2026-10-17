# Revisão independente do harness candidato e capítulo 10

Revisor: agente independente manual_harness_review. Data: 2026-10-15. Escopo: BRIEF, relatório do autor, todos os documentos do kit, checker/testes, capítulo 10 e recibo externo. Não executou o piloto, Git, MT5 ou suítes produtivas; não editou o candidato nem os oráculos. Única entrega persistente: este parecer.

## Veredictos

- Integridade congelada: PASS. Manifesto, rubrica e 12 hashes de cases coincidem com harness-freeze.json. Todos os arquivos kit declarados no manifesto coincidem com seus SHA-256.
- Testes existentes: PASS, 11/11, 0,416 s nesta revisão. Cobrem negativos significativos de hash, raiz, escape, status estrutural, dependência e campos JSON; não são prova comportamental ou nativa.
- Delimitação CANDIDATE/NOT_ADOPTED e não alteração de AGENTS/CI/produto: adequada documentalmente. A revisão não certifica toda a árvore fora do escopo nem mudanças históricas.
- Capítulo 10: adequado como capítulo avançado de propostas; separa plataforma, produto, norma, proposta e execução. Não representa auditoria da extensão 20–30 mil palavras do manual completo nem dos formatos DOCX/PDF.
- Prontidão do protocolo do piloto: COM RESSALVAS relevantes abaixo. Não inferir PASS do piloto ou prontidão produtiva. A infraestrutura deve demonstrar sessões novas, captura de proveniência e julgamento independente.

## Achados e decisões exigidas antes do piloto

### P1 — orientação nos cases permite entregar o gabarito ao construtor

Local: cases/S01.json a S12.json, campo fixture_isolation. Todos dizem `copy_this_json_only_into_new_session`; o JSON contém `expected`, incluindo valores corretos e forbidden, e referência à rubrica. PILOT.md passo 3 manda omitir expected/rubrica específica. Um operador que segue o campo do caso literalmente entrega o oráculo e contamina as 36 tentativas. O resultado deixa de medir resposta independente.

Recomendação: preservar o freeze atual e registrar procedimento operacional externo que projeta somente id/topic/prompt/input e contexto permitido. Registrar os bytes exatos entregues e conferir ausência de expected. Se optar por corrigir os JSON, gerar nova revisão/freeze antes de qualquer tentativa. Não remover o gabarito do juiz nem mudar seu conteúdo. A contradição existe mesmo quando o operador consegue contorná-la corretamente.

### P2 — regra estrita de proveniência precisa ser aplicada literalmente

Local: PILOT.md passo 4, attempt-template.json, rubric.json e capítulo 10. O protocolo afirma que campos desconhecidos permanecem null e tornam a proveniência insuficiente; a rubrica classifica proveniência ausente como INCONCLUSIVE. O template pede model_version, reasoning_setting, tool_versions, autor/juiz/sessão, entre outros. Infraestrutura que só revela nome do modelo pode não fornecer versão exata. O capítulo fala apenas de registrar a limitação, o que é menos explícito que o protocolo.

Não é autorização para inventar metadados nem flexibilizar após ver resultados. Aplicar INCONCLUSIVE aos registros insuficientes. Se a intenção for aceitar campos indisponíveis não essenciais, definir previamente critérios por campo e novo freeze antes do piloto. Não transformar esse ajuste em PASS retroativo. A calibração julga exemplos de conteúdo; ela não dispensa recibos reais das tentativas.

### P2 — INTEGRITY_OK não valida estados adicionais do manifesto

Local: check_harness.py, validação inicial do manifesto. O checker valida schema_version/version/status, mas ignora adoption, behavioral_pilot e native_mt5, embora o manifesto real os declare. Reprodução em fixture temporária independente: manifesto com status CANDIDATE, adoption ADOPTED, native_mt5 PASS e behavioral_pilot PASS retorna exit 0 e INTEGRITY_OK.

O freeze externo detecta a adulteração do manifesto original, portanto isto não invalida o freeze atual. É limite importante de reutilização: não apresentar o checker isolado como validador desses estados. Recomendável testar/validar também tais campos em futura revisão, ou explicitar que apenas o status principal é verificado. Não alterar a versão congelada durante o piloto.

## Código e testes

O checker é curto, usa biblioteca padrão, leitura e stdout, sem instalação/rede/reparo. As três raízes são explícitas e canônicas. locate rejeita raiz desconhecida, path absoluto, `..`, escapes resolvidos e symlinks nos componentes declarados. Raiz fornecida por symlink é resolvida intencionalmente; isso não contradiz a política descrita no relatório. Os hashes são comparados com SHA-256 real; o manifesto não autentica a si mesmo, e a cadeia externa manifesto → hash do checker está presente. Referências repo sem hash apenas comprovam existência, não identidade da revisão produtiva.

Códigos 0/1/2 e precedência de inconsistência sobre ausência são implementados para entradas tratadas. O conjunto não cobre todas as patologias de filesystem: loop de symlink pode levantar RuntimeError em Path.resolve, fora dos except presentes, e o CLI pode emitir traceback em vez de JSON. Não foi necessário criar esse cenário para concluir o limite estático. Não recomendar este script como defesa contra mutação concorrente/ambiente hostil; existe intervalo entre resolução e leitura. Nenhuma dessas observações equivale a evasão demonstrada no kit atual.

Os 11 testes têm oráculos úteis, mas faltam exemplos explícitos de symlink interno, componente intermediário, duplicação, mistura missing+inconsistent e raiz canônica por symlink. O teste nonmutation compara bytes de arquivos da fixture e executa runcheck novamente, que regrava seu manifesto; prova preservação de conteúdo, não timestamps/inodes nem ausência de acessos fora da fixture. O código observado sustenta ausência de escritas pelo checker, com esse limite experimental.

## Casos, juiz e validade

Os doze casos são novos e sintéticos; resultados esperados principais são coerentes com os inputs (inclusive S04 = 2 ticks, 4 por lote, 2,5 lotes, risco 10; S09 = 107 e dois deals). S01 pressupõe que o handle é obrigatório no contrato de inicialização; numa tarefa real essa precondição teria de ser explicitada. A simplicidade dos casos mede preservação de limites, não programação MQL5 completa.

Há três repetições por caso, 12/12 casos exigidos, 10/10 por tentativa, proibições críticas sem compensação, três exemplos de calibração e retenção de FAIL/INCONCLUSIVE. Sessão de juiz distinta do autor e do construtor é exigida; mesmo modelo não implica diversidade. Logs e IDs precisam comprovar essas condições, e não apenas uma declaração de fresh. O autor não pode julgar seu próprio kit como independente. A revisão estática atual não conta como uma tentativa ou calibração do piloto.

## Conferência das fontes do capítulo

Conferi diretamente o texto extraído das páginas citadas do corpus primário: REF 1263 (ArraySetAsSeries), 2082 (OnInit), 2088 (OnTick), 2098 (OnTimer), 2106 (OnTradeTransaction), 2226 (CopyBuffer), 2665 (FileOpen) e NN 222–224 (3.9). Os trechos sustentam as afirmações correspondentes. Em especial, o texto distingue ordem física/indexação, EA/indicador em INIT_FAILED, coalescência de eventos, request/result apenas em REQUEST e parâmetros de normalização/targets futuros. Não conferi visualmente render de cada página nem fiz releitura integral dos livros. A leitura pontual não é cobertura semântica integral.

A recomendação cronológica/anti-leakage é corretamente identificada como proposta; não atribuída integralmente ao livro NN, que menciona divisão aleatória. O histórico GENETRIX é atribuído a documento local, não aos PDFs nem ao piloto novo. A diferença entre resultados históricos e novas provas é explícita.

## Conclusão operacional

Pode ser entregue como kit CANDIDATE com este parecer e limitações. Antes de executar, documentar a projeção sem gabarito e resolver a disponibilidade de proveniência conforme critérios congelados. Qualquer alteração de protocolo/kit exige nova revisão identificada antes da rodada. Nenhuma recomendação deste parecer autoriza adoção, AGENTS, CI, instalação ou operação; nenhum resultado aqui representa validação nativa MT5.
