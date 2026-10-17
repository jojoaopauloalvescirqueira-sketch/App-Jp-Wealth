# Edição documental curada Stoikus C2 — lote Git delimitado — 2026-10-16

O proprietário autorizou a ordem sugerida: primeiro commit e PR exclusivos da edição documental curada; depois, ensaio MT5 isolado e piloto IA em trilhas próprias. Este registro cobre a preparação documental atual. A cópia é N0-D informativa e opt-in; não instala o kit candidato nem altera obrigações, autoridade ou controles ativos.

A implementação local está autorizada em A2. A autorização específica de ação Git (A4 somente para a ação exata) cobre o controlador registrar o commit, enviar a branch e abrir o PR necessário desta entrega. Merge, deploy, publicação do site, adoção do harness e execução operacional MT5 não estão autorizados por este lote. O construtor documental não executa staging, commit, push ou outra mutação Git.

## Derivação C2 dentro do mesmo escopo documental

A primeira tentativa Git da C1 apresentou 13 marcadores de formatação herdados em nove Markdown (sete espaços finais e seis linhas vazias de EOF). Esse recibo é falha efetiva da tentativa R1 e permanece preservado externamente; não houve waiver, modificação de gate, Git config ou `.gitattributes`. A necessidade técnica foi resolvida por uma edição C2 separada, reversível e documental dentro da ordem já autorizada.

A C1, manifesto `50cd8c907139d968e903db0f624663711dbb9e54c70de3489ac845dec07b85f7` e ZIP `9d685313d0de7160e06babf9372d978e6ee5d07d4561f6db3b37be90fdce4531`, conserva seus bytes fora do Git. A C2 remove apenas os 13 marcadores indicados, sem mudar texto, espaços internos ou indentação, e atualiza três guias, identidade e rastreabilidade necessários. Os dados de derivação estão em `curadoria/TRANSFORMACOES.json`, seção `revision_c2`; os 37 testes permanecem byte-idênticos e o checker muda somente o literal esperado edition_id.

Não foi criado um arquivo físico de revisão: metadados existentes registram pais e deltas sem circularidade. A seleção continua com 213 arquivos/212 conteúdos. Os 870 originais, classificações, recibos e referências históricas permanecem preservados; mapas/índice identificam 188 PRESERVED, 15 TRANSFORMED, 663 EXTERNAL e quatro CACHE. Overlays distinguem hashes de cópias C1 e C2 sem reescrever consumidores históricos.

A preparação C2 ocorre externamente enquanto o candidato C1 é validado. Aplicação da C2, preflight final, gate completo, revisão independente, commit e PR têm seus próprios recibos do controlador. Este contrato não registra antecipadamente PASS ou ação futura. A autorização de edição/Git não autoriza merge, deploy, adoção ou execução operacional.

## Contrato recebido

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-STOIKUS-DOCUMENTAL-CURATED-20261016",
  "status": "approved",
  "objective": "Adicionar edição documental opt-in Stoikus 1.0.0-c2, derivada da C1 por correção mecânica de formatação e identidade/rastreabilidade, sem adoção ou mudança do control plane ativo",
  "risk_level": "N0-D",
  "authority_required": "A2",
  "target": {
    "root": "repositório App-Jp-Wealth, worktree existente jpw-stoikus-continuity-20261014",
    "branch": "codex/stoikus-continuity-20261014",
    "baseline_sha": "7e8b9a055503d514dd7ab91178f85b585df7b8b9"
  },
  "scope": {
    "allowed_files": [
      "docs/knowledge/stoikus-mql5-curated/1.0.0-c2/**",
      "docs/knowledge/stoikus-mql5-curated/README.md",
      "docs/work/CHG-STOIKUS-DOCUMENTAL-CURATED-20261016.md",
      "docs/work/ACTIVE-TASK.md"
    ],
    "forbidden_files": [
      "docs/knowledge/stoikus-mql5/**",
      "AGENTS.md",
      "CLAUDE.md",
      "README.md",
      "docs/governance/**",
      "skills/**",
      "tools/**",
      ".github/**",
      ".gitignore",
      "src/**",
      "mt5/**",
      "downloads/**",
      "docs/normative/**",
      "docs/decisions/**",
      "docs/knowledge/stoikus-mql5-curated/1.0.0-c1/**"
    ],
    "allowed_actions": [
      "Copiar os 213 arquivos finais C2 após derivação externa separada da C1: nove Markdown normalizados e metadados necessários; C1 preservada externamente",
      "Criar wrapper com pin e limites documentais",
      "Prependar somente resumo factual em ACTIVE-TASK preservando todo o corpo anterior",
      "Executar verificador e 37 testes documentais na cópia com -B e gates aplicáveis",
      "Controlador: commit e push exclusivos do lote documental para abrir PR autorizado"
    ],
    "forbidden_actions": [
      "merge",
      "deploy",
      "publicação no site",
      "adoção/instalação do harness candidato",
      "alterar EA ou regras financeiras",
      "alterar gates/control plane ativo",
      "reescrever histórico",
      "criar/trocar branch ou worktree"
    ],
    "regressions_forbidden": [
      "Alterar os 870 originais históricos",
      "Incluir os 852 arquivos não rastreados preexistentes no lote Git",
      "Transferir PASS documental para MT5/EA/piloto ou aceite humano",
      "Tratar prompts opt-in como instrução superior",
      "Alterar bytes da C1 selada ou suprimir sua falha de formatação R1",
      "Alterar os 37 testes ou critérios do checker; no checker muda somente literal edition_id c1 para c2"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "cópia byte-idêntica da edição C2 final congelada"
    ],
    "generation_commands": [
      "derivação externa C1 para C2, remoção de sete espaços finais e seis linhas vazias de EOF em nove Markdown, nova identidade e rastreabilidade; sem reconstrução do manual ou kit"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "GitHub jojoaopauloalvescirqueira-sketch/App-Jp-Wealth somente para commit/push/PR documental pelo controlador"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python 3 com -B",
      "Git somente leitura pelo construtor documental",
      "Gate full e operações Git autorizadas pelo controlador"
    ]
  },
  "acceptance_criteria": [
    "213 arquivos copiados com caminhos/tamanhos/hashes iguais à origem C2 congelada",
    "Manifesto pinado 08746937fe7228b5ad7fddaeb052328e683e202a2e7613e23227c45afb3312fa",
    "Verificador pinado e 37 testes documentais PASS na cópia",
    "870 originais e corpo anterior de ACTIVE-TASK byte-idênticos",
    "Wrapper com links locais válidos e estados CANDIDATE/NOT_ADOPTED/NOT_RUN/HISTORICAL_ONLY",
    "Diff restrito à allowlist documental e gate aplicável confirmado pelo controlador",
    "Kit 45, manual/formatos/figuras e 37 testes byte-idênticos à C1; checker somente literal edition_id",
    "Somente sete espaços finais e seis linhas vazias de EOF removidos nos nove Markdown",
    "188 PRESERVED e 15 TRANSFORMED no mapa original, mantendo as mesmas 870 classificações e referências históricas"
  ],
  "approved_tests": [
    "python -B verificar_edicao.py com --edition-root e --manifest-sha256",
    "python -B -m unittest discover -s tests -p test_verificar_edicao.py",
    "igualdade integral de inventários e hash dos originais",
    "links relativos do wrapper",
    "git diff --check",
    "quality_gate.py --tier full pelo controlador"
  ],
  "rollback": {
    "source": [
      "Remover somente a nova pasta curada e este CHG; restaurar ACTIVE-TASK ao hash anterior registrado, preservando todos os arquivos preexistentes"
    ],
    "application_state": [
      "Nenhuma alteração"
    ],
    "data": [
      "Nenhuma alteração"
    ],
    "environment": [
      "Limpar somente temporários de teste próprios"
    ],
    "verification": [
      "Conferir inventário externo anterior, 870 originais e hash anterior de ACTIVE-TASK"
    ]
  },
  "approved_by": "Proprietário nesta conversa: autorizo a ordem sugerida",
  "approved_at": "2026-10-16",
  "expires_on": [
    "mudança de raiz/branch/baseline material",
    "mudança de pin, escopo ou objetivo",
    "nova restrição ou dado sensível",
    "ação de merge/deploy/adoção não coberta"
  ]
}
```

## Compreensão e fontes — seis respostas

1. **Finalidade.** O JP Wealth organiza finanças, análise e gestão de risco; integridade e evidência têm precedência. Esta tarefa torna uma seleção de estudo consultável e verificável no repositório, sem alterar o produto (PROJECT-CONTEXT, seção Produto; AGENTS, Missão).
2. **Responsabilidade.** `docs/knowledge/stoikus-mql5-curated/1.0.0-c2/` guarda uma cópia congelada do manual 1.0.0, pesquisa e kit 0.1.0 CANDIDATE R3. O wrapper identifica os bytes e a leitura opt-in. `docs/knowledge/stoikus-mql5/` continua como origem histórica preservada e fora do lote Git.
3. **Antes/depois.** Antes, os 870 originais coexistem com 852 arquivos não rastreados e a curadoria final está externa. Depois, haverá 213 arquivos da revisão C2 idênticos ao seu novo freeze em pasta separada e um wrapper com pin integral; o corpo anterior de ACTIVE-TASK será preservado. A base observada é `7e8b9a055503d514dd7ab91178f85b585df7b8b9`; a main remota informada e conferida pelo controlador é `d6bbce7e5f42601c323598a86264ef87391c178d`, posterior à integração histórica PR 41. As fotografias antigas não recebem nova validação.
4. **Impacto.** Consumidores são leitores do manual e agentes que consultem explicitamente esta seleção. Os prompts são conteúdo documental candidato e não vencem AGENTS ou a instrução humana. Não há importação no app, mudança de runtime/EA, regra, dado, persistência, gate, CI, roteamento ou instrução global. O contexto operacional recebe somente o resumo factual autorizado com referência a este contrato.
5. **Limites.** Preservar os 213 arquivos curados, 870 originais, histórico de ACTIVE-TASK e fontes produtivas. Permanecem CANDIDATE, NOT_ADOPTED, native_mt5 NOT_RUN, novo piloto comportamental NOT_RUN e resultados históricos HISTORICAL_ONLY. Os 37 testes do checker não certificam EA, compilação, operação financeira, Windows, adoção ou aceite humano. Não incluir ZIP, livros-fonte ou logs brutos.
6. **Evidência.** Comparar inventários por caminho/tamanho/SHA-256, executar o checker com pin e a suíte de 37 testes na cópia, verificar links do wrapper, revisar diff e preservar inventário antes/depois externo. O controlador executa o full aplicável à integração documental antes das ações Git; este contrato não registra antecipadamente seus resultados nem um aceite humano.

## Identidades examinadas

| Fonte | SHA-256 / trecho e papel |
|---|---|
| `AGENTS.md` | `d839dd395a2d1b1dae4ca7885dd0fdb1e74f04cbcff56e82aa03ce7150b57c1b` — Missão; Autoridade; Bootstrap; Preflight; Política Git; Encerramento |
| `README.md` | `941f48bec4fa4f78e8f40a9e28797b0fac0c13b19bc9f55a7dbccbd0d9a14c5d` — abertura e fotografias preservadas da integração anterior |
| `docs/governance/CONTEXT-MAP.md` | `5919ce0aba9f3d4be4c33309b33ba42ee67fdbf804af5e37fa25e2f36d8c3144` — rota corrente e distinção entre histórico e candidato |
| `docs/governance/PROJECT-CONTEXT.md` | `37637ca60dd014e938d3156cba402bec3045b88d4ec5989d776ff23482dc9a27` — Produto; Contratos; Modelo de entrega |
| `docs/governance/CURRENT-STATE.md` | `987519ef909b601cc81f8184493a71b6d30a356165c85eb92a2913dfc0b7b86d` — abertura factual da integração anterior |
| `docs/work/ACTIVE-TASK.md` | `a83dee780f34db526f6e9817c3d0d38424e6ade38c06d12ebc72d3af1b3ef6a2` — corpo anterior integral, antes da adição factual |
| `docs/governance/CHANGE-PROCESS.md` | `5240dac3196ebeb74805be4864465e0037c8d58d7e09068a7db77f99554b6fcd` — Classificar; Verificar; Promover |
| `docs/governance/QUALITY-GATES.md` | `985139e137bb7b18185933255498280a4d3ddcf96fb21ce22e44a8238be72902` — Fast; Full para integração/candidato de release |
| `skills/jpw-change-control/SKILL.md` | `899391c76bc3b575b49d70ead9c668ad20324424b5f9d312e62a2268febf16c0` — Contract first; Edit; Verify |
| JP Software Engineering Harness, Master Specification, fonte canônica relocalizada | `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95` — §§12–14, 24, 28–30, 36–48 lidos; não alterada |
| Manifesto C1 pai, histórico externo | `50cd8c907139d968e903db0f624663711dbb9e54c70de3489ac845dec07b85f7` — 212 conteúdos mais manifesto; content ID `3111a6261c0fc3ba3582996f4f615bf8e9bbed7d9483a6b52dddddad716d1ea7` |
| Freeze C1 T2-R2 externo preservado | `68433f74da0ee270003a2d893a4144de72a0c92bf30146e9ca992e87bacc109d` — os 213 arquivos finais; não incluído na seleção |
| Parecer independente T1 externo preservado | `06b33fa7e0edd7ddc52ff71eb35086014ce7010fc4399b81d652953e653188b9` — PASS somente no escopo T1 e nos mesmos hashes |
| Parecer independente T2-R2 externo preservado | `6c940c20eb6369ef9e6adb23785673cc33091fbc91dbace652c5fd576f7aeac0` — PASS delimitado ao delta/freeze R2; sem certificação MT5/Windows/aceite |
| Manifesto C2 `1.0.0-c2/MANIFESTO_CURADO.json` | `08746937fe7228b5ad7fddaeb052328e683e202a2e7613e23227c45afb3312fa` — 212 conteúdos mais manifesto; content ID `f43f50c9e800a3852f26841df89d52a30788d3b3ea212d26e7b6e7677bab4d17` |

As fontes acima foram lidas e seus hashes calculados na preparação local. Freeze e pareceres privados permanecem externos; seus hashes permitem reconciliação por quem dispõe dos originais e não prometem disponibilidade pública. A qualificação anterior é evidência histórica dos bytes indicados. A C2 e sua cópia final exigem recibos próprios externos; os resultados da C1 não lhes são transferidos.

## Execução, autoria e reversibilidade

Autoria prévia examinada por histórico Git e inventário: o corpo existente de ACTIVE-TASK e a distribuição integrada pertencem às entregas anteriores. A árvore rastreada estava sem diff; os 852 não rastreados estavam exclusivamente na origem histórica conhecida. O preflight edit com `--allow-dirty` foi PASS para essa retomada explicitamente coordenada; a opção não concede autoridade e não dispensa verificar arquivos desconhecidos. Nenhuma limpeza do trabalho preexistente foi autorizada.

O plano aprovado adiciona a edição documental em pasta irmã versionada, este contrato, o wrapper e o resumo factual de ACTIVE-TASK. A C2 é derivada externamente da C1, com nove correções mecânicas de Markdown e metadados de edição necessários; o checker muda somente o literal edition_id. Esquema e critérios, manual, PDF/DOCX, figuras, kit de 45 arquivos e os 37 testes conservam seus bytes/contratos. Não há reconstrução do manual ou kit nem mudança funcional incidental. A allowlist completa por caminho, os inventários, comandos e freeze do lote ficam no relatório externo do controlador, sem logs novos no repositório.

A classificação N0-D descreve o efeito desta cópia documental opt-in. Os scripts e prompts preservados não são instalados, registrados ou adotados como control plane. Qualquer adoção futura é outra mudança, com autorização e validação próprias. A verificação documental usa fixtures descartáveis e biblioteca padrão, sem execução de EA ou dos scripts históricos do kit.

Rollback antes de commit: retirar somente as adições deste lote e repor o corpo anterior de ACTIVE-TASK conferindo o hash acima. Após commit, uma reversão específica depende da autorização Git correspondente. Os originais, dados do aplicativo e terminal de uso não participam do rollback.
