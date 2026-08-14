# Tarefa ativa — Correção dos achados `Medium` da auditoria de segurança

- Data de abertura: 2026-08-13
- `BASE_SHA`: `a5d7b93` (`main` limpo)
- Branch de implementação: `fix/security-medium-findings`
- Nível: **N1** (fronteira de confiança da importação e propagação entre abas) +
  **N0-D** (testes e reconciliação)
- Autoridade: **A2**, autorizada pelo gestor após apresentação dos achados
  verificados. Ver a nota de classificação abaixo.
- Git/publicação: branch e implementação autorizadas. **Commit, merge e push não
  foram executados.**
- Estado: implementação e validação técnica concluídas; aguardando teste manual.

## Origem

Auditoria de segurança sobre `main@1959024`, sete fronteiras de confiança.
Quarenta achados, verificados adversarialmente em dois passes — 14 no primeiro,
13 no segundo. **Nenhum `High` ou `Critical` sobreviveu à verificação**: o único
`High` reportado foi derrubado para `Low` porque a âncora de confiança dos gates
mora no mesmo commit que o atacante postulado controlaria, o que retira do
controle qualquer propriedade adversarial.

Sobraram três `Medium` sustentados, todos com o mesmo vetor: um backup
adulterado — inclusive o próprio backup do operador alterado numa pasta
sincronizada, que é o cenário realista.

## Nota de classificação — por que isto não é N3

Levantei antes de implementar que a correção da matriz poderia tocar faixa N3,
por ser parâmetro normativo, e o gestor autorizou. Registro o raciocínio:

A mudança **não introduz, altera ou remove** nenhum percentual, fator ou limite.
Ela muda *quem tem autoridade* sobre esses valores — a fonte oficial passa a
prevalecer sobre o arquivo importado. É restauração de aderência ao Estatuto,
não alteração dele. O código já aplicava exatamente esta doutrina às chaves
estruturais das fases e aos tickers de instrumento, e o comentário que a enuncia
está no próprio arquivo desde antes desta tarefa: *"catálogo fechado, nascem em
DEFAULTS e só de lá"*. A matriz simplesmente ficara de fora.

## Correções

1. **Matriz Quadrifásica aceita verbatim do backup** —
   `00-core/04-persistence.js`. A guarda existente validava a FORMA (quatro
   linhas, campos numéricos) e por isso deixava passar qualquer VALOR. Um
   arquivo com `ddmax:0.99`/`alav:99` atravessava e passava a definir fase
   vigente, teto de risco e teto de alavancagem — o terminal exibiria
   "COERENTE" com exposição muito além do limite estatutário. Corrigido em
   `canonicalizeStructuralMetadata()`.
   Ressalva do verificador, registrada por honestidade: guilhotina e alarme não
   vêm da matriz (leem `S.params.mdd`), então o dano ficava na faixa de 0 a 13%
   de drawdown — real e silencioso, porém não ilimitado.
2. **XSS armazenado em `S.params.inicio`** — `40-app/04-onboarding.js:2418`.
   O campo chegava a `innerHTML` sem escape no resumo do onboarding, enquanto
   todos os vizinhos usavam `esc()`. Varri o template inteiro depois de
   corrigir: os demais candidatos são ternários booleanos, coerção numérica ou
   já escapam internamente (`segmentation`). Era a única omissão.
3. **Zona de Perigo não propagava entre abas** — `40-app/05-wipe-all.js` e
   `40-app/07-finalize-session.js`. O epoch de persistência protegia apenas a
   aba que executou a limpeza; outra aba mantinha o `S` inteiro em memória e a
   primeira gravação dela ressuscitava a base apagada. Reutiliza o canal da
   Finalização de Sessão (BroadcastChannel + fallback por `storage` + dedup por
   token) com **tipo e handler próprios**, porque as semânticas não são
   intercambiáveis: a Finalização remove auxiliares e cópias de recuperação, a
   Zona de Perigo preserva as duas — e o texto que o operador confirma promete
   exatamente isso.

## Fora de escopo — não tocado

Fórmulas, perfis, fases, DD/MDD, lote, LIFO, stops, quarentena, contabilidade,
MEI-JP, Planejamento FX, Estudos NoCoda, Motor de Lote, schema, `schemaVersion`
e chaves de storage. Os demais achados da auditoria (5 `Low` sustentados e os
informativos) não foram corrigidos.

## Evidência

| Verificação | Resultado |
|---|---|
| `python3 tools/import_xss_security_test.py` | PASS — estendido com a matriz adulterada e o payload em `params.inicio` |
| `python3 tools/storage_governance_test.py` | PASS — seção 9 nova, duas abas em contexto compartilhado |
| `python3 tools/validate_project.py` | PASS — 63 scripts, 392 IDs, zero duplicados |
| `python3 tools/quality_gate.py --tier full` | ver `CURRENT-STATE.md` |
| Navegador real | NOT_RUN |

O teste de importação **reprovou antes do rebuild**, apontando
`[portatil/load] STORED XSS: handler do payload EXECUTOU` — o `dist/` ainda
carregava o código vulnerável. Só passou depois de regenerado. Isso prova que a
asserção não é vazia.

## Defeitos próprios corrigidos junto

- `ACTIVE-TASK.md` afirmava que commit e merge do Motor não foram executados,
  quando foram (`792b705`, merge `043da1b`).
- A source revision do `CURRENT-STATE.md` ficara em `60ec561`, o que disparava
  aviso de frescor material no preflight.
- `SECURITY-MODEL.md` declarava 53 scripts no precache; são 63.

## Riscos residuais

- Nenhuma das telas recentes foi inspecionada visualmente por um humano.
- Um operador cuja base tenha matriz divergente de `DEFAULTS` por qualquer
  motivo legítimo verá os valores oficiais restaurados no próximo load, sem
  aviso. Não há caminho conhecido pelo qual isso ocorra — nenhuma tela escreve
  a matriz —, mas a restauração é silenciosa por construção.
- Os 5 `Low` sustentados seguem abertos, com destaque para: `publish="."`
  expondo governança e harness, o build legado em `archive/` servido na mesma
  origem, e o feed de terceiro sem revisão nem action pinada.
