Fecho independente: **REVIEW_PASS documental e de rastreabilidade**, sem achado pendente neste escopo. Compilação MetaEditor e interação MT5 permanecem **NOT_RUN**. Esta rodada conferiu documentos, recibos existentes e identidade dos bytes; não repetiu testes funcionais ou gates aprovados, não editou produto/Git e não instalou ferramentas.

Conferi a versão final de INTEGRATION e NATIVE-CHECKLIST, os dois registros CHG de uso/contexto, CURRENT-STATE, o prefixo focal de CONTEXT-MAP, ACTIVE-TASK, README, SESSION_HANDOFF, CHANGELOG e o fecho do plano. Os textos distinguem execução local do host/browser de funcionamento MT5 e não transferem aprovação da 1.22.0 para a 1.22.1. Dados, instalação operacional, aceite do proprietário, Git e publicação conservam fronteiras próprias.

| Prova existente conferida | Resultado bruto |
| --- | --- |
| `host-all-R4.json` | 44 checks PASS, todos exit 0; MT5_HOST_SYNTHETIC; compilação/runtime nativos NOT_RUN; prontidão BLOCKED_NATIVE_VALIDATION |
| `full-R4.json` | 57 checks PASS, todos exit 0; branch/base declaradas correspondem ao candidate |
| `fast-context-final.json` | 4 checks PASS, todos exit 0, após reconciliação documental |
| `context-final.log` | Controles positivos e 101 negativos rejeitados; limite estrutural explícito |
| `fast-context-sandbox-environment.json` | Tentativa anterior preservada: 3 PASS e 1 ENVIRONMENT_ERROR; não apagada nem convertida em resultado do produto |

As cópias de full-R4 e host-all-R4 em `docs/validation/stoikus-1.22.1` são byte-idênticas aos originais. O CODE-REVIEW copiado corresponde exatamente ao meu parecer anterior. Não consultei mapeamento privado nem parecer/recibos de outro crítico nesta rodada.

O recibo full canônico não inclui hashes dos inputs. A redação final passou a explicitar isso: ele é independente do campo `web_full_gate` da suíte host, e a invariância dos inputs tem checagem separada. Conferi `full-input-binding.json`: hash do recibo full correspondente; snapshot R4 registrado antes do início do full; 394 hashes após execução; fingerprints antes/depois iguais. Recalculei os hashes dos 394 arquivos atuais e comparei com FREEZE-R4. A cópia do freeze e a cópia desse vínculo também são idênticas aos originais.

| Identidade | Valor conferido |
| --- | --- |
| Inputs R4 | 394; fingerprint `4abcb1e1b47c6f25b524ed67ecf2f9f83a3c47059e26879caa6e8dec86ef675d` |
| Uso diário 1.22.1 | 441516 bytes; SHA-256 `5b2c7ca40736dda976fe97a91a2677d190eb1ccfdf9527703fd471ee702a11e5` |
| SDK 1.22.1 | 773801 bytes; SHA-256 `03ccb37824175511108b36e9abb5c9fa0dc28d89a338caea1dc7bf02508b9cae` |
| Build MQL | `b4031d96f5d180aa35c6285ad8baec97f017d162e7ea0499d38df339571d81db` |
| Fingerprint MQL recomputado | `8c35c3c02e9049b7727d8d0595c12ca424df04f8052d64c0aced92b587438894` |

Todos os 135 sourceHashes correspondem aos fontes atuais. MQL, manifesto e ZIPs conservam os bytes do meu parecer funcional anterior, portanto não foi necessária nova revisão funcional. Os dois ZIPs históricos permanecem idênticos, e as cinco fotografias históricas de CURRENT-STATE, CONTEXT-MAP, ACTIVE-TASK, SESSION_HANDOFF e README correspondem byte a byte à baseline 1.22.0. Os claims de preservação dos núcleos/inputs remetem à comparação anterior; o texto reconhece que preservação de estados exercitada no host é sintética e não prova persistência nativa.

Duas precisões documentais levantadas durante este fecho foram resolvidas. Rollback agora significa reverter somente o delta 1.22.1 e restaurar bytes/derivados verificados da baseline 1.22.0, sem tocar dados ou desfazer a renomeação. Os campos approved_at agora são explicados também perto dos blocos duplicados de ACTIVE-TASK: hora do registro documental da autorização conversacional, não timestamp extraído da mensagem humana. O log estrutural afirma expressamente que campos de aprovação preenchidos não provam autorização humana.

NATIVE-CHECKLIST é um roteiro futuro dos mesmos hashes. Ele pede compilação dos quatro programas e execução após o script terminar, referência nativa dos handles, OnInit/OnDeinit reais, estudos/preferências, falhas parciais, legados e indicadores reconhecidos porém inativos. Esse roteiro não foi apresentado como ensaio já executado. A limitação de comando no Parallels foi registrada pelo executor; esta rodada não reproduziu o comando Windows. Ausência de EX5 distribuído, nativeArtifact nulo e os estados pendentes do manifesto mantêm a lacuna operacional visível.

Resultado limitado a documentação e rastreabilidade local do candidate. Este fecho não concede aceite humano, homologação financeira, prontidão MT5, instalação ou publicação. Recibo detalhado: `final-closing-audit.json`.
