# Brief — Stoikus 1.22.0

Raiz: `/private/tmp/jpw-stoikus-renaming-20261012`. Branch: `codex/stoikus-renaming-20261012`. BASE_SHA: `0f247215cc20829fdba40c3b33458ee976c17ea1`; árvore inicial limpa. O proprietário aprovou o plano e, em resposta separada, a criação de branch e worktree. Produto N1/A2, gerador/verificadores e contexto N3/A4 têm contratos próprios. Commit, push, merge, publicação e operação MT5 permanecem separados.

## Compreensão e fontes

1. **Finalidade:** o JP Wealth organiza leitura financeira e gestão de risco. Stoikus é o novo nome da suíte local MT5. Fontes: PROJECT-CONTEXT, seção Produto; README MT5 da base, linhas1–48.
2. **Responsabilidades:** Conta/Cockpit apresenta; Monitor observa a conta e produz histórico/contabilidade; NoCuda organiza estudos; Supervisor separado mantém seu contrato restrito. O site apresenta e distribui. Fontes: GENETRIX_CORE_1_20_0, linhas5–31; INTEGRATION1.21.2, linhas21–35; entrypoints/consumidores examinados na varredura.
3. **Antes/depois:** GENETRIX1.21.2, MQL1.212 e cálculo1.9.0,132membros, apenas fontes. Depois: Stoikus1.22.0/MQL1.220,29nomes MQL/recursos e5ferramentas remapeados; novo documento de transição, total133membros. NoCuda, logo JP Wealth, slogan e cálculo1.9.0 mantidos.
4. **Efeitos:** marca, shortnames/admissão de instância, includes/recursos, downloads, gerador, verificadores e contexto focal. A compatibilidade das publicações continua dependente de um conjunto coerente de programas/includes; não relaxar presença, locks ou cobertura.
5. **Invariantes:** não alterar fórmulas, unidades, políticas, schemas, chaves, bancos, locks, inputs, preferências, IDs DOM, APIs, funções, tipos ou macros. Pacotes/manuais/harness/recibos antigos ficam intactos. Reconhecer aliases antigos no novo indicador não modifica um binário legado; retirar componentes antigos antes de futura instalação autorizada. Nenhum dado real ou terminal operacional nesta tarefa.
6. **Prova:** conferir o mapa34, todas as referências, invariantes financeiros e hashes históricos; executar código efetivo de admissão em host e contraprovas; verificar aba/foco/downloads HTTP/file/portátil/PWA; hostall, full, oracle separado e auditoria independente do candidate congelado. Compilação e execução nativas permanecem NOT_RUN.

## Autoridade de engenharia

AGENTS da base0f24721 e Master original relocalizado em `/Users/joaoalvescirqueira/Library/Mobile Documents/iCloud~md~obsidian/Documents/3 - Prompts&Skills/9 - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`; §§12–19,24,28–30 e36–48 lidos. A referência antiga no AGENTS é dívida preexistente; não foi alterada incidentalmente. O harness MT5 distribuído foi lido integralmente na investigação anterior; seus bytes permanecem os da mesma base e seu estado CANDIDATE/piloto histórico não é modificado.

Preflight audit/edit PASS com aviso preexistente de quatro caminhos posteriores à source revision7b73a97. A nova camada focal não declara reconciliação global do projeto. A baseline inicial externa guarda 919 hashes e o mapa de 34 nomes. A enumeração inicial sem separador NUL omitiu oito nomes Unicode escapados pelo Git; o suplemento posterior confrontou seus bytes diretamente com HEAD, sem encontrar alteração. Os freezes posteriores usam `git ls-files -z`; diretórios que não são arquivos não recebem hash de conteúdo.

## Execução e recuperação

MQL, verificadores/gerador e documentação têm autores e allowlists distintos nos CHGs. Root coordena HTML, navegação, manifesto, derivados e freeze. O reviewer final não é autor desses deltas. Dados sintéticos e runtime descartável já autorizado; nenhuma dependência do projeto foi instalada ou alterada. Rollback limitado ao delta, sem apagar bancos ou evidência; qualquer operação Git de recuperação depende de sua autorização própria.

## Âncoras de compreensão na base 0f24721

Os hashes abaixo pertencem aos bytes anteriores ao delta, preservados na baseline externa.

| Fonte | SHA-256 da base | Trecho pertinente |
|---|---|---|
| `docs/governance/PROJECT-CONTEXT.md` | `37637ca60dd014e938d3156cba402bec3045b88d4ec5989d776ff23482dc9a27` | “aplicação web local/PWA para organizar a vida financeira e apoiar análise, planejamento e gestão de risco” (Produto) |
| `mt5/jpw-alavancagem-atual/GENETRIX_CORE_1_20_0.md` | `0d494acfc9f0d54a81d50fe83e7094d8fcaca5b080d8647223ebb87b5c84746b` | “reúne monitoramento e histórico com contabilidade de ciclos” e “nunca apagar locks ou bancos para forçar titularidade” (Organização recomendada) |
| `mt5/jpw-alavancagem-atual/README.md` | `c66401dfc747fdd605d1fc33122591c78991a1d358eea0e9877e4fdc78f9d379` | Produto 1.21.2, MQL 1.212 e cálculo 1.9.0; CANDIDATE, sem aceite nativo da revisão (abertura histórica) |
| `docs/validation/genetrix-1.21.2/INTEGRATION.md` | `22bf8483d0842062758b85c2b201a1875a48d090d1562a921269e407077af069` | Integração e proveniência da revisão anterior; não transferir compilação ou execução para bytes novos |
| `AGENTS.md` | `d839dd395a2d1b1dae4ca7885dd0fdb1e74f04cbcff56e82aa03ce7150b57c1b` | “Editar, testar, revisar, commitar, enviar, integrar e publicar são gates distintos” (Classificação e autoridade) |
