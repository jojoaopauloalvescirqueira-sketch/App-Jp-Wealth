# Brief de tarefa

Fonte obrigatória: [AGENTS.md](../../AGENTS.md); roteamento: [CONTEXT-MAP](../governance/CONTEXT-MAP.md).
Preencher somente campos pertinentes, sem “contexto lido” genérico. O brief registra autoridade recebida; não a cria.

## Identidade e fronteira

- Título / solicitante / data:
- Objetivo e não objetivos:
- Raiz real / branch indicada / BASE_SHA / fingerprint do diff quando disponível:
- Trabalho preexistente e autoria concorrente:
- Nível de risco / autoridade recebida / evidência conversacional de aprovação:
- CHG/CTX e ações específicas aprovadas (criação de branch, testes, efeitos):
- Arquivos permitidos / proibidos:
- Operações Git/publicação autorizadas e expressamente não autorizadas:

## Síntese de compreensão — seis respostas com fontes

1. **Finalidade:** para que o JP Wealth existe e qual objetivo desta tarefa atende?
2. **Responsabilidade:** qual serviço prestam módulo/pasta/componentes ao usuário?
3. **Comportamento:** o que foi observado hoje e o que deve existir depois?
4. **Impacto:** quais regras, dados, entradas/saídas, consumidores e fluxos são afetados?
5. **Limites:** o que não pode mudar; quais invariantes, preferências, rascunhos, unidades e contratos antigos preservar?
6. **Evidência:** quais critérios e testes demonstrarão objetivo atendido e ausência de regressão?

| Fonte | Revisão/hash e trecho | Papel/validade | Origem e evidência de acesso | Fato ou decisão sustentada |
|---|---|---|---|---|
| caminho real pertinente | revisão examinada | atual / histórico / proposta | fornecida / lida / importada / metadado / declaração / inferência; comando, saída ou registro e limite | conclusão específica |

- Fonte normativa/decisão financeira ou engenharia pertinente:
- Dependências compartilhadas e consumidores fora da pasta:
- Lacunas materiais, efeito sobre a tarefa e leitura segura que pode continuar:
- Evento que exige revalidar contexto:

## Plano, programação e segurança

- Menor delta correto; responsabilidades e efeitos colaterais:
- Contratos/invariantes, entradas/saídas e compatibilidade com dados antigos:
- Fonte canônica de cada dado/regra; repetição legítima versus duplicação:
- Ausência/zero/vazio/erro, unidades/moedas/períodos/identidades:
- Falha parcial, cancelamento, gravação recusada e prevenção de operações duplicadas:
- Superfícies reais de segurança, validação/saída segura e dados sintéticos:
- Ferramentas/permissões e efeitos externos expressamente cobertos:
- Critérios de aceite:
- Testes prévios/focais/gate obrigatório e oráculos derivados das fontes:
- Candidate a congelar / auditoria independente quando exigida:
- Rollback/recuperação limitado ao próprio delta:

## Delegação, se houver

Objetivo/finalidade + raiz/branch/revisão + fontes + arquivos/autoria + consumidores + ações/limites + critérios/lacunas + evidência esperada. Referência: [AI-WORKFLOW](../governance/AI-WORKFLOW.md). Não presumir memória herdada nem delegar autoridade adicional.

## Evidências e encerramento

| Verificação/comando | Candidate/ambiente | Resultado único | Registro da execução e limite |
|---|---|---|---|
| execução ou NOT_RUN justificado | SHA/fingerprint | taxonomia de AGENTS | comando e saída/trace/artefato observável; não atribuir erro ou resultado a ação não executada |

Separar orientação escrita, comportamento observado e barreira técnica imposta.
Relatar causa, contrato aplicado, impacto persistido, cenários executados/não executados,
riscos e rollback. Teste/aceite manual do proprietário e autorização de commit/Git/publicação
continuam gates próprios. Atualização de contexto só dentro do CHG/CTX autorizado.
