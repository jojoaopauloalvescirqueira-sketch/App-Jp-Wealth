# Stoikus engineering kit 0.1.0 — CANDIDATE — revisão R3

Kit operacional opt-in, sem ativação por AGENTS ou CI. Integridade não representa aprovação comportamental. Não envia ordens, instala dependências, acessa rede nem modifica produto. Leia ENTRY.md, escolha um contrato e crie registros em uma pasta de execução separada. Versões do produto, cálculo, MQL e kit são independentes.

## Verificação

```sh
python3 -B "$KIT/check_harness.py" --kit-root "$KIT" --repo-root "$REPO" --sources-root "$SOURCES"
python3 -B -m unittest discover -s "$KIT/tests"
```

Defina KIT como esta pasta, REPO como checkout escolhido e SOURCES como pasta com os três PDFs de source-identities.json. Todos os argumentos são explícitos; nenhum caminho temporário é canônico. Códigos: 0 integridade; 1 inconsistência; 2 dependência ausente. Inconsistência prevalece sobre ausência. O programa só lê e emite JSON em stdout; não baixa nem repara arquivos. Referências admitem apenas kit/repo/sources, caminhos relativos sem .. e arquivos sem symlink. O manifesto não inclui seu próprio hash, evitando ciclo. Seus bytes devem ser congelados externamente antes do piloto. Confira também a identidade do próprio script com o recibo externo: um verificador adulterado não se autentica sozinho.

Os testes negativos usam diretório temporário independente. Seus arquivos não são fontes produtivas. Saída 0 não demonstra conteúdo semântico correto, extração integral dos PDFs, compilação, execução MT5 ou aceitação humana.

## Piloto

Doze casos sintéticos novos em cases/, três sessões novas por caso, total planejado 36. Nenhuma tentativa é presumida executada. Procedimento em PILOT.md, rubrica em rubric.json, recibo em attempt-template.json. Outputs devem ficar fora desta pasta congelada. Autor do kit não julga o piloto como avaliador independente.

Revisão R2 corrige isolamento do construtor com builder-inputs/, define proveniência obrigatória/opcional antes do piloto e valida estados declarados do manifesto. Cases completos são exclusivos do juiz. R1 permanece no snapshot externo de pesquisa; nenhum piloto foi executado para esta revisão. Política detalhada em provenance-policy.json e PILOT.md.

R3: pasta separada, fixture S01 com handle obrigatório explícito; dispatch legível completo e hash obrigatórios ANTES dos spawns; infraestrutura registrada. Validador de proveniência aceita tipos malformados como erros controlados. Use validate_provenance(receipt,evidence_root) para conferir bytes dispatch; forma com um argumento é somente estrutural. Nenhum piloto aprovado é alegado nesta preparação.
