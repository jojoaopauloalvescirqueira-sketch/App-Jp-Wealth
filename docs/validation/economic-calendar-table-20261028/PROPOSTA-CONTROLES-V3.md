# Aprovação dos verificadores — proposta final V3

**Branch e produto já autorizados e aplicados.** Esta proposta solicita somente a aprovação específica dos cinco arquivos de testes e a validação posterior. Substitui a proposta inicial de hash37a46edb, que não foi aplicada. Nenhum verificador foi alterado no repositório.

O produto reconstruído é `bc08298ef8320bb0`, disponível na [prévia local](http://127.0.0.1:59411/index.html?v=bc08298ef8320bb0). Permanece igual ao patch revisado: JS1e2e518b e CSSf1007dfe. A base e as133alterações anteriores continuam preservadas. A janela nativa já foi autorizada após aviso; ainda não começou.

## Patch solicitado

[Patch consolidado V3](proposal/controls-v3/tests-candidate-v3.patch), SHA256 **7c9ca1442b18cbd5081ee2a56179a3697062637da3be119825a983d53cec9159**:

| Arquivo | Delta autorizado proposto |
| --- | --- |
| tools/calendar_economic_table_contract.py | Novo helper dos sete campos, valores, limites, alinhamento e estado |
| tools/calendar_agenda_test.py | Casos novos e abertura do detalhe no teste de foco existente |
| tools/ff_news_cache_test.py | Projeção/Anterior sintéticos no pipeline; consulta das fontes após abrir i e verificação explícita de aviso pendente visível |
| tools/calendar_visual_quality_test.py | Medidas dos novos elementos nos casos existentes |
| tools/calendar_distribution_test.py | Sete campos nas quatro distribuições existentes |

Os outros quatro candidatos são idênticos à proposta inicial. O candidato FF final tem SHA256 `a3f3a00c5a1ff8e1059bc7eb1fd8c69870a5ecf48d1ea2020b8033503194862a`. Não altera quality_gate.py, ui_visual_quality_test.py,116checks,413casos,900segundos,2px, schemas, fixtures financeiras ou os dados do usuário.

## Por que a versão final mudou

Após o rebuild, a proposta inicial revelou duas expectativas antigas no teste de integração do feed: ele procurava links de fonte sempre visíveis e o texto anterior do aviso de horário. A interface aprovada recolhe as fontes no i. O RED bruto ficou em `applied-ff-cache.json`:184PASS/2FAIL. A reprodução isolada confirmou o ponto da falha. A adaptação exige agora abrir e conferir individualmente a fonte de CAD e USD por observação/href, e exige que o aviso **Horário a confirmar.** esteja efetivamente visível. Não elimina a proteção de proveniência nem de incerteza.

## Evidências e limites

- Cinco novos focais do helper/agenda final passaram, incluindo limites700/720, estado/foco/rascunho e leitura sem gravação financeira.
- Doze contraprovas do helper foram rejeitadas pelo oráculo correto após correção de um erro do launcher scratch. O recibo inicial e sua classificação incorreta permanecem preservados; a auditoria não os transforma em aprovação.
- Distribuição reconstruída passou em HTTP, PWA-offline, arquivo local e portátil, com os campos e os detalhes recolhidos.
- V2 de FF passou186/186, mas não exigia explicitamente visibilidade do aviso; é evidência parcial histórica.
- V3 final passou dois cenários nominais1440/390 e rejeitou aviso oculto pela mesma asserção de visibilidade. [Recibo V3](proofs/tests-proposal/ff-expectation-v3/pipeline-and-counterproof-v3.json).
- [Revisão independente V3](proofs/review-proposal/ff-v3-review.md): apta para autorização específica, sem bloqueador delimitado. O FULL, execução integral FFV3, matriz413, zoom nativo e aceite humano permanecem pendentes.

Após autorização: aplicar somente os cinco arquivos identificados, registrar CHG N3 próprio, executar focais atuais e FULL no candidato estável, com aviso antes das janelas reais. Sem commit, merge, push, publicação, novas dependências ou ativação externa.

O [AGENTS.md:81](</Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/AGENTS.md:81>) determina para controles N3: **“Requer CHG dedicado, comparação antes/depois, auditoria independente e aceite humano”**. A aprovação de branch/produto não foi tratada como aprovação desse patch.
