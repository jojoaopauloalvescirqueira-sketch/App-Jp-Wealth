# Regras executáveis e regressões permanentes

Use ao implementar. Reutilize infraestrutura equivalente; não instale um framework universal. As obrigações do SKILL.md também valem para correção pequena.

## Instruções e legitimidade

Leia instruções vigentes na raiz e nos diretórios afetados, incluindo overrides. Integre AGENTS.md sem sobrescrever conteúdo. Registre normas e fontes, comandos, índice das proteções e dívida do legado; detalhes extensos ficam referenciados por escopo. Confira o que está efetivamente carregado. Atualização escrita durante uma sessão precisa ser lida explicitamente; não presuma recarregamento automático.

Fontes normativas: decisão explícita do usuário, especificação aprovada, contrato público e instrução vigente aplicável. Descrição do comportamento atual é caracterização; hipótese e proposta não são obrigação aprovada. Conflito ou regra vaga pede apenas a definição material ausente, mantendo trabalho independente autorizado. Não transforme um exemplo deste pacote em regra do projeto.

O [modelo de AGENTS](../assets/AGENTS.template.md) organiza instruções ausentes. Use rastreabilidade existente; se faltar, mantenha junto aos testes um registro pequeno de ID, tipo, fonte, escopo, resultado esperado, casos/runner IDs e estado. O [manifesto de exemplo](../assets/protections.example.json) demonstra só o formato do helper; nomes e comandos devem ser adaptados ao projeto. Legado sem cobertura fica pendente, não ativo/protegido. A migração é progressiva; bugs corrigidos e regras novas/alteradas exigem proteção imediatamente.

## Cada correção e cada regra

- Bug: mantenha estímulo e asserção; capture RED pelo defeito real, corrija e capture GREEN do mesmo caso. Caso parametrizado é válido. Não confunda falha de importação/ambiente com reprodução de defeito existente. Se necessário, reintroduza o defeito em cópia descartável compatível, sem resetar trabalho do usuário. Sem contraprova, declare pendência.
- Regra: use oráculo baseado na fonte e independente do código. Exercite caso válido, inválido e limite pertinentes. Demonstre violação representativa rejeitada pela proteção. Conferir se o texto da regra existe não comprova que o comportamento a cumpre.
- Domínio: exemplos normativos e testes de propriedades quando acrescentam poder. Não derive o esperado da própria função testada. Ordenação não prova preservação do conteúdo; roundtrip sozinho pode aceitar dois lados com o mesmo erro.
- Estado/persistência: integração real para escrita, conflito, reabertura e recuperação prometidas. Modelo mais simples e independente pode verificar sequências; contrato de concorrência exige execução concorrente real com sincronização, não somente operações em série.
- Arquitetura: analise todos os elementos pertinentes, inclusive arquivos novos e caminhos alternativos. Prefira parser/análise estrutural disponível. Confira população não vazia e contraste módulo válido com violação; grep de um único arquivo não comprova regra transversal.
- Tipos/esquemas/estilo: reaproveite checadores existentes. Processo humano: confira registros e mecanismos de aprovação; um unit test não prova intenção humana ou autorização.

Contraexemplos gerados devem virar fixtures/casos estáveis versionados. Seed e cache do gerador não substituem registro permanente. Mutações focadas são opcionais por risco; evite instalar ferramenta ou exigir 100% em todo projeto.

## Execução local e CI

Mantenha um ponto de entrada de validação completa documentado no AGENTS.md. Ele executa suites obrigatórias, gera evidência atual e aplica os critérios também usados no CI. Focais durante edição; suite acumulada e matriz vigente antes da conclusão de cada correção/melhoria/versão. Não crie um segundo runner quando o atual suporta isso.

Confirme descoberta e execução por IDs/relatórios, não apenas exit0. Caso obrigatório removido, filtrado, skipped, xfail, todo ou desconhecido não está aprovado. Matriz precisa comprovar cada caso em cada ambiente aplicável. Seleção vazia e ausência de relatório são falha de validação, não sucesso. Defina timeout conforme projeto; preserve primeira falha, tentativas e interrupções. Retry de diagnóstico não transforma falha em PASS.

Identifique bytes reais de código, testes e configuração usados na prova; HEAD não identifica alterações não commitadas. Mudança integrante invalida evidência afetada. Cache não autoriza reutilizar relatório de outra identidade. Falhas preexistentes permanecem separadas: entrega limitada só conforme política vigente, sem rebatizar suite vermelha como aprovada ou liberar versão contra seus gates.

No GitHub Actions, uma etapa final com `if: always()` e `needs` deve conferir que todos os jobs/suites necessários realmente executaram e passaram, incluindo os relatórios. `skipped`/`neutral`, filtros e `continue-on-error` não podem liberar proteção obrigatória. Configure eventos adequados ao repositório; fila de merge exige `merge_group`. Reuse política/CI do provedor existente. Definir workflow, executar CI e exigir aprovação para integrar são três estados distintos. Verifique ruleset/proteção remota quando acessível e autorizado; caso contrário, registre imposição técnica pendente. Não presuma permissão para push, merge, deploy ou alteração administrativa.

## Preservação e revisão

Compare IDs, testes/casos, escopos, seleção do runner e asserções com a base anterior. Remover regra e teste ao mesmo tempo não elimina essa revisão. Renomear/refatorar pode preservar proteção; contrato aprovado pode substituir expectativa antiga. Registre fonte, motivo, substituição e revisão, preservando histórico. Não enfraqueça uma asserção para produzir verde. Proteções da infraestrutura também precisam de contraprovas.

O helper [verify_protections.py](../scripts/verify_protections.py) é opcional quando não existe equivalente. Ele valida manifesto e relatório normalizado, comparação com manifesto anterior, matriz, tentativas e identidade fornecida pelo controlador. Rode `--help` para API e campos. Não executa testes, não calcula identidade, não autentica aprovação nem interpreta equivalência semântica. Adaptador deve obter IDs/status reais do runner e calcular identidade atual; nunca fabricar PASS em JSON. Só copie o helper se houver ganho concreto; não introduza Python num projeto apenas para usar este exemplo.

Um exemplo válido de relatório e manifesto pode ser conferido sem modelo:

```text
python3 scripts/verify_protections.py --manifest assets/protections.example.json --report assets/report.example.json --candidate example:synthetic-only
```

O PASS desse exemplo comprova o formato; não valida nenhum projeto. No projeto real, falha do produto, harness inválido, dívida anterior, ambiente indisponível e não executado permanecem distintos. Revisão independente pertinente não é substituída por autorrelato. Encerre com comandos, resultados, identidade e limites materiais; evite documentos ou agentes adicionais sem utilidade.

## Fontes primárias

- [Regressão RED/GREEN — Django](https://docs.djangoproject.com/en/5.2/intro/contributing/)
- [Descoberta e hierarquia — Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Revisão de testes — Google Engineering Practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [Estado e invariantes — Hypothesis](https://hypothesis.readthedocs.io/en/latest/stateful.html)
- [Arquitetura e seleção vazia — ArchUnit](https://www.archunit.org/userguide/html/000_Index.html#_fail_rules_on_empty_should)
- [Execução vazia — OPA](https://www.openpolicyagent.org/docs/policy-testing)
- [Checks e jobs pulados — GitHub](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)

## Entrada completa e regras transversais
Documente uma entrada permanente que executa runner, descoberta/IDs obrigatórios e gates, chamada localmente e no CI. Contraprovas usam essa entrada. Sentinelas, contagem mínima, exit0 ou JSON informado não provam suíte completa. Regra transversal exige analisador capaz de tratar gramática/escopo prometidos; reutilize parser maduro pertinente. Ferramenta limitada exige pendência explícita. Não criar lexer improvisado somente para evitar dependência proporcional.
