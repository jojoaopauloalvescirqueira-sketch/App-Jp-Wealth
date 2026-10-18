---
name: jp-ai-engineering
description: "Aplicar os padrões de trabalho aprovados pelo usuário em tarefas de programação: intervenção mínima, investigação causal e evidência proporcional. Use quando solicitada para desenvolver, corrigir, diagnosticar ou revisar software."
metadata:
  version: "1.3.0"
---

# JP Engenharia com IA

Atenda ao objetivo pedido com o menor trabalho que preserve correção, segurança e contratos. Instruções superiores, autorização vigente e normas atuais do projeto prevalecem. A skill orienta decisões; não concede permissões nem substitui controles técnicos.

## Forma de trabalhar acordada

- Poupe explicações repetidas: aplique estes padrões sem pedir reconfirmação. Pergunte apenas por decisão material que o pedido e o projeto não resolvam; continue partes independentes autorizadas.
- Reutilize linguagem, arquitetura, bibliotecas, estilo e comandos existentes. Preferências novas precisam vir do usuário ou do projeto; não imponha escolhas pessoais presumidas.
- Preserve dados e trabalho preexistente. Faça o menor delta coerente, com testes pertinentes; evite manutenção adjacente, dependências, equipes e formalização sem benefício concreto.
- Entregue resultado, evidências e limites relevantes. Não alegue aceite, integração, instalação, modelo/esforço ou economia sem confirmação correspondente.

Pedido claro de criar/corrigir cobre implementação reversível necessária. Consulta pede resposta; proposta pede plano; diagnóstico e auditoria respeitam o resultado solicitado. Descubra alvo e regras aplicáveis antes de editar. Preserve entradas, saídas, erros e consumidores afetados; ausência, zero e inválido são diferentes. Encerre quando os critérios estiverem demonstrados; repita verificações somente com motivo.

## Proteções obrigatórias do projeto

**Ao implementar**, descubra a raiz, as normas e os `AGENTS.md`/`AGENTS.override.md` aplicáveis. Crie ou atualize o `AGENTS.md` da raiz sem sobrescrever regras ou trabalho existentes: padrões, contratos/fontes, comandos de preparo e suíte completa, índice das regras/proteções e pendências. Preserve escopos/overrides e confira a descoberta efetiva; criar arquivo não comprova carregamento. Consulta, plano e auditoria somente leitura não escrevem instruções nem infraestrutura.

**Cada bug corrigido deixa um caso automatizado permanente e identificável**, inclusive parametrizado. Primeiro demonstre que falha pelo defeito; depois que o mesmo estímulo/expectativa passa corrigido. Falha de ambiente/coleta não é RED. Correção já existente: reproduza em cópia descartável compatível, preservando trabalho. Sem demonstração, a proteção fica pendente e não declare correção plenamente validada.

**Cada regra nova/alterada deixa fonte normativa, escopo, oráculo e teste executável**; confirme caso válido e violação representativa. Código existente é evidência descritiva, não autorização para inventar regra. Regra vaga precisa de critério observável; não simule cobertura por texto, mock ou expectativa derivada da própria implementação. Inventarie regras antigas e migre a cobertura progressivamente, identificando pendências. Reutilize rastreabilidade existente; na ausência, mantenha manifesto pequeno junto aos testes, ligado pelo AGENTS.md.

**Durante a edição rode focais; antes de concluir cada correção, melhoria ou versão rode toda a suíte obrigatória acumulada e sua matriz vigente**, com os mesmos critérios localmente e no CI. Reutilize runner/dependências/diretórios existentes; se faltar CI, prepare integração adequada ao repositório. Confirme execução real dos casos obrigatórios e identidade do código/testes/configuração. Zero casos, proteção pulada/xfail, relatório antigo, timeout ou runtime ausente não são PASS. Preserve primeira falha; retry não a apaga. Falha anterior permanece separada e impede alegar suíte aprovada.

Compare proteções com a base: remoção, exclusão do runner e enfraquecimento exigem justificativa normativa e revisão; mudança autorizada de contrato pode substituir proteção obsoleta com histórico e cobertura correspondente. Não altere expectativas apenas para passar. Testes ficam versionados no projeto e rodam sem modelo. Gates técnicos dependem dos controles reais do repositório; não confunda configurar CI com bloquear integração. Termine com resultado, provas e pendências; não prometa ausência universal de bugs.

## Integração e exploração por personas

Antes de gerar testes, inventarie proteções por propriedade, fronteira, estado, oráculo e execução efetiva. Reutilize prova suficiente; unidade aprovada não comprova ligação UI/serviço/persistência. Para cobertura inicial ou jornada/fronteira/risco sem proteção, aplique [integração com personas](references/integracao-personas.md): exploradores com conhecimento distinto → engenheiro de integração → crítico independente, em contextos e dados sintéticos isolados. Papéis são acionados por lacuna; não imponha equipe completa a consultas, correções já cobertas ou cada build.

A exploração utiliza a aplicação executável; ações da conexão avaliada passam pela interface real. Cada caso aceito vira código versionado, reproduzível sem modelo, com expectativa de fonte aprovada e rejeição demonstrada de violação representativa. Nas entregas seguintes execute as proteções acumuladas. Com o Codex ativo, diagnostique e corrija regressão introduzida dentro da tarefa autorizada. Build/CI executam e bloqueiam; não iniciam IA automaticamente.

Use entrada completa permanente, local/CI: verificações de fonte → build oficial → suíte obrigatória e integração no artefato final. Vincule descoberta, resultados e bytes atuais; contraprovas passam pela mesma entrada. Teste pulado, relatório parcial/antigo e código alterado após validação mantêm bloqueio. Reparo de seletor preserva contrato; defeito do produto não autoriza enfraquecer expectativa, pular ou atualizar snapshot. Testes não provam todas as possibilidades nem substituem autorização de publicação.

## Carregamento por necessidade

Consulta autocontida usa esta entrada. Ao implementar ou avaliar proteções, leia [regras e regressões](references/regras-regressoes.md); use os modelos somente quando não houver equivalente no projeto. Leia as demais referências apenas pelo gatilho:

- Intenção ambígua, retomada, autorização material ou integração: [fronteiras](references/fronteiras.md).
- Causa incerta ou defeito intermitente: [diagnóstico](references/diagnostico.md).
- Domínio de dados incerto, persistência, serialização ou limites representáveis: [contratos](references/contratos.md).
- Risco material, segurança, UI afetada, freeze ou revisão independente: [validação](references/validacao.md).
- Delegação disponível e necessária: [orquestração](references/orquestracao.md).

O [perfil JP Wealth](references/jp-wealth.md) é opcional: carregue somente quando solicitado e confirmado pela identidade do projeto. Consulte [proveniência](references/provenance.json) ao atualizar/auditar a síntese; declarações históricas não ativam exceções atuais. Memória global só muda por pedido humano explícito.
