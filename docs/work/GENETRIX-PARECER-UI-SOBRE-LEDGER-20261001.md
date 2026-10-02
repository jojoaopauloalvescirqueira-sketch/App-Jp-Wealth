# Parecer independente sobre o Ledger — 2026-10-01

## Escopo e conclusão

Revisão de leitura de Core, Store, Terminal, Bridge, EA Accountant, fixtures e ferramenta host, exclusivamente em `/private/tmp/jpw-genetrix-risk-ledger-20261001`. O revisor escreveu a UI consumidora, mas não os módulos Ledger examinados. Não constitui aprovação da própria UI, homologação normativa, comprovação de integridade de conta real ou validação de execução financeira.

Foram localizados dois achados P2 nas fronteiras de recência e isolamento. O autor alterou Core/Terminal/Bridge durante a revisão; os deltas foram relidos e testados nos corpos reais com APIs sintéticas. A solução atual corrige os cenários específicos observados. O teste final obteve 19 oráculos financeiros, 103 assertions no host e seis assertions de recuperação em processo novo, sem falha. Isso não prova o comportamento das APIs nativas, da corretora ou dos callbacks MT5.

Origem e cobertura de custos continuam **DECLARADAS**, condicionadas à referência do operador e à conta capturada na inicialização. Não passam a ser automaticamente verificadas por HistorySelect, persistência, hashes, lease, saúde técnica ou resultado favorável dos testes. Na leitura final não identifiquei outro defeito material demonstrado; a ausência de achado nesta amostra não é um aceite completo. Compilação/runtime MQL, APIs de terminal, lease/singleton nativos e aplicação a conta permanecem `NOT_RUN` neste parecer.

## Identidade antes e depois

Paths relativos ao checkout isolado. O revisor não alterou estes fontes, a ferramenta, expected ou oráculos.

| Arquivo | SHA-256 inicial | SHA-256 final relido |
|---|---|---|
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Core.mqh` | `37c635128bf74330ad3c3053887e96edf856e4ff3b5843140e1ce05ade80479c` | `89480ace885080fbdeb43250402596a373f7d18eaed77efed6671e2ec4ade8e7` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Store.mqh` | `47e2d6084dca31aa218b0f631e985b922e50559c1d1b699d501772e0183f7733` | igual |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Terminal.mqh` | `a199623ad6546e9ef74c42ea79c3c395596efda717c255ec79d4317fddee524c` | `4efe9a62ab476f7add28ed7e3cf24eab85f4c2fa999ab64c3f03aaf61d75cbde` |
| `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Ledger_Bridge.mqh` | `92d61c0f397fb7c5e91350b91a53f759fd20e0e90fa7470091f455fd70adab7c` | `be1251ce39790edf1bec86ea99b33e434030a4dfacc3ccd04ae32785345d3a3a` |
| `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Genetrix_Accountant.mq5` | `eff085079eca0cc7108ec18c01f120f06f4567d3daed650927681234e3e97e24` | igual |

Identidades adicionais finais: script `JPW_Genetrix_Ledger_Tests.mq5` SHA-256 `1d2b9098143c75471f1d8d1cc83f7249b3e9260125279f3dcef9a6e07e7255b0`; `tools/jpw_genetrix_ledger_test.py` SHA-256 `fe419150a36b5e94f4bfc7e5afea8c273fed6a463d623d6156646d42941617fd`; `tests/fixtures/genetrix/ledger-oracles-v1.json` SHA-256 `a26fe59b37edfd4dbc4d8759e87dc6a9f6ffffce74d427e950c5e2bfd434fc1f`.

Um Bridge intermediário `ff0e7dd…` ainda conservava os dados antigos como Historical no mismatch de conta após a leitura Live. O parecer final refere-se ao hash `be1251ce…`, que limpa os dados e recusa o resultado nesse caso.

## Achados materiais

1. **LEDGER-R01 — P2, recência; corrigido na fonte e nos cenários host específicos.** Terminal inicial, linhas 85 e 101, multiplicava o relógio em segundos por 1.000 e recusava qualquer tick em milissegundos numericamente posterior ao começo daquele segundo. Exemplo: relógio 1.000,000 s e tick 1.000,900 s tornavam `fresh=false`, apesar da diferença de precisão. Isso podia apresentar dados recentes como históricos ou impedir Current. O Core novo, linhas 90–95, usa a convenção da matemática base: até 2.000 ms de diferença futura e 30.000 ms de idade. Terminal 101 invoca esse helper. O runner final compila e executa `JPWLedgerReadLive` real e cobre tick fracionário, tick velho, futuro excessivo e relógio inválido. Integração de relógio/tick do MT5 nativo: NOT_RUN.

2. **LEDGER-R02 — P2, inventário/conta; corrigido na fonte e nos cenários host específicos.** `ReadLive` inicial, linhas 81–112, lia as contagens iniciais sem reconfirmá-las; adicionar posição/ordem durante a última enumeração podia aceitar um prefixo antigo. O Bridge inicial reconfirmava identidade somente antes da leitura Live. No delta intermediário, uma conta diferente depois do censo apenas rebaixava a observação para Historical, mantendo dados da conta anterior, contrariando o contrato de contexto inválido devolver false/arrays vazios/N/A. Terminal final 112–114 recusa contagens alteradas e esvazia o prefixo; Core 96–101 contém o predicado. Bridge final 32–34 reconfirma identidade/moeda depois do censo e limpa/recusa no mismatch; 35–43 reconfirmam modo, saldo e conexão, separando histórico da mesma conta de conta inválida. O runner final executa ReadLive real com adição de posição/ordem e o Bridge real com SQLite e troca de conta durante Live. Esses cenários passaram. Não cobrem todas as corridas de mesmo tamanho, ABA, callbacks perdidos ou atomicidade da corretora; os guards finais não são uma promessa de veto ou snapshot de servidor atômico.

## Origem e continuidade

- O grupo econômico é símbolo exato/direção; não é tese, flag GÊNESE, Operação formal V11 ou dupla confirmação. Primeira execução inferida atribui a Gênese contábil; fechar seu identificador não promove outro enquanto ainda existirem membros/pedidos do ciclo (Core final 181–217 e 296–358).
- Pendente anterior à primeira execução cria metadado provisório, estado 4, sem montante/percentual financeiro válido (Core 263–284 e 414–416). Com posições zeradas mas pendentes ativas, o ciclo continua, estado 2. O encerramento contábil exige membros zerados, pedidos resolvidos e ausência de rollover aguardando; é distinto do encerramento formal (Core 197–213).
- Pendentes preenchidas só permitem a transição quando deals vinculados e volume executado reconciliam; execução faltante mantém a ordem ativa e baixa completude (Core 274–284). Saída sem abertura, direção/volume inconsistentes ou posição viva sem origem impedem total completo (Core 344–358 e 382–399).
- Empate na primeira execução deixa origem AMBÍGUA e identificadores da Gênese zero; o total financeiro agregado pode continuar válido se a extensão do ciclo estiver comprovada. Empate entre zeragem e nova entrada, com fronteira desconhecida no mesmo milissegundo, baixa a completude e o montante fica indisponível (Core 302–338 e 417–419). Isso preserva a distinção entre ambiguidade do primeiro membro e ambiguidade da fronteira contábil.
- Custos tardios e reabertura técnica do mesmo identificador conservam o ciclo original, mesmo encerrado. Não se abre outro ciclo só por pagar comissão/swap ou ordenar o replay de maneira diferente (Core 215–217 e 286–374).

## Valores, cobertura e correções

- O compensado soma realizado de preço, swap realizado, comissões, taxas, preço remanescente e swap remanescente com sinal original. A comissão de entrada é contabilizada integralmente no deal, sem nova alocação por volume de saída parcial. Moeda original é preservada, inclusive USC; nenhuma conversão financeira é refeita na UI (Core 3–5 e 405–410).
- Percentual usa o saldo da **amostra publicada**, inclusive ao recalcular um ciclo encerrado; não representa SI, saldo no encerramento, RC ou capacidade de nova exposição. Saldo zero/negativo invalida somente o percentual, mantendo montante conhecido quando pertinente (Core 407–410).
- Custos sem vínculo e trade cancelado sem correção explicitamente ligada impedem completude de custos. O Terminal não inventa `adjustment_of`: ele permanece zero quando não há ligação comprovada (Terminal 39 e Core 360–376). Nesse caso pode haver subtotal conhecido, marcado partial; não é NET completo. Origem/histórico incompletos invalidam o montante (Core 402–416).
- Terminal 193–198 deixa os dois flags de cobertura false por padrão. Accountant inputs 6–8 são opt-in, referência vazia por padrão. `JPWLedgerApplyDeclaredCoverage`, Core 102–116, exige texto substantivo limitado e a mesma chave da inicialização. Isso valida o vínculo sintático, não lê ou audita a referência nem prova completude do broker. Divergência observável no volume/histórico continua sobrepondo a declaração. Troca de conta não reutiliza a declaração sem nova inicialização (Accountant 56, 75–92).
- Store upsert idempotente por payload mantém revisão auditada de cada mudança. Um DEAL_UPDATE reconstitui o total; ausência em consulta não se transforma em delete. Tombstone exige evento de delete testemunhado; origem de delete desconhecida e perda de fila deixam fault persistido (Store 160–181 e 323–379). Broker restaurações/correções podem substituir o tombstone com uma nova observação explícita.
- Raw, revisões e geração derivada têm uma transação conjunta e releitura. Schema incompatível, digest/raw/auditoria divergentes ou geração danificada são recusados sem reset/migração silenciosa (Store 142–158, 183–230 e 325–382). A cache de projeção pode rotacionar; revisões financeiras não são apagadas para reduzir histórico.

## Isolamento e evidência de leitura

Chave deriva de servidor/login/moeda/instalação (Terminal 5–12). Writer/DB são locais e exclusivos por sessão da conta; a troca fecha o anterior, invalida lease e descarta deletes do contexto anterior (Accountant 18–49 e 73–80). O consumidor abre SQLite `DATABASE_OPEN_READONLY`, lê uma geração em transação e reconfirma conta/currency; nenhum OrderSend ou comando financeiro existe no Accountant/Bridge (Store 142–158, Bridge 6–44).

Current exige geração íntegra, publisher/lease, idade até 30 segundos, conta hedging, conexão, saldo e composição compatíveis. É uma captura recente observada, não cálculo a cada redraw nem confirmação de atividade contínua do contador. Preços/P/L podem variar após a amostra; observação histórica tem data e saldo próprios. A lease é mecanismo local; comportamento nativo dos callbacks/CAS ainda precisa de evidência.

## Testes e limites finais

Executado, sem alterar fontes e sem receipt-dir: `python3 tools/jpw_genetrix_ledger_test.py`. Resultado final **19 oráculos PASS**, **103 assertions host sem falha**, **6 assertions de recuperação em processo novo sem falha**. O runner usa corpos reais de Core/Store/ReadLive/Composition/Bridge e APIs de terminal/lease/identidade sintéticas; a persistência usa SQLite host real e processos separados para seed, interrupção de transação não confirmada e recovery. Os 19 resultados são comparados aos valores Decimal e estados do JSON congelado. Não é replay de conta real. A primeira execução intermediária tinha 97 assertions; a final acrescentou fronteiras ReadLive/Bridge e substitui essa identidade de teste.

**NOT_RUN:** compilação e ABI MQL nativas; EX5; reconciliação completa HistorySelect/API de corretora; Accountants/transactions MT5; native file lock/lease/CAS; crash/persistência no terminal real; UI/visualização; execução demo/real. O teste de processo host evidencia rollback SQLite no cenário especificado; não comprova durabilidade de disco ou funcionamento de locks no MT5.

As correções específicas foram verificadas documentalmente e no host. Uma mudança posterior exige novo congelamento/revisão/testes pertinentes. Os estados PENDING/NOT_HOMOLOGATED/BLOCKED do modelo não são alterados por este parecer.
