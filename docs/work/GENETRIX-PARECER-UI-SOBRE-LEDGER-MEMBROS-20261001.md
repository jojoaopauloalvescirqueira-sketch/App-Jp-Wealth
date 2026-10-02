# GENETRIX — Revisão independente do delta Ledger: membros

Data: 2026-10-01. Revisão READ-ONLY de Core/Store/Bridge e dos testes do ledger; nenhum arquivo de produção, fixture ou critério foi editado pelo revisor. O parecer anterior `GENETRIX-PARECER-UI-SOBRE-LEDGER-20261001.md` conserva seu escopo para os trechos inalterados. Este documento não aprova a UI de minha autoria.

## Escopo e contrato

O delta publica `member_identifiers` e `members_available` por ciclo. O primeiro é CSV numérico canônico crescente de POSITION_IDENTIFIER observados, incluindo Gênese e membros encerrados, distintos de tickets atuais. Disponibilidade é independente da cobertura histórica. CodecCycle v2 contém a projeção; v1 deve conservar resultados financeiros e apresentar a lista como indisponível, não como zero. Vazio disponível corresponde ao ciclo provisório antes da primeira execução.

## Achado material M01 — P2, aberto nesta edição

Core `JPWLedgerMemberListValid`, linha 162, aceita lista vazia disponível apenas por `!genesis_inferred`. Store `JPWLedgerDecodeCycle`, linhas 95–123, combina esse validador com reencodificação canônica, sem impor estado provisório/valor indisponível à lista vazia. Assim, um payload v2 canônico com `state=1`, `open_positions=1`, `genesis_inferred=false`, `amount_valid=true`, `percent_valid=true`, `members_available=true`, `member_identifiers=""` é aceito. Essa combinação viola o contrato de vazio disponível somente antes da primeira execução.

Reprodução independente, sem alteração das fontes: Core e Store reais traduzidos apenas na sintaxe/arrays e compilados em C++ host com o mesmo shim de strings/SQLite do runner. O programa de sondagem criou os campos acima, montante realizado/compensado 67 e percentual 6,7, chamou EncodeCycle/DecodeCycle e imprimiu:

```text
HOST_COMPILE_EXIT 0
PROBE_EMPTY_NONPROVISIONAL member_valid=1 decode=1 state=1 amount_valid=1 members_available=1
EXIT 0
```

É uma falha de validação de contrato, não evidência de que um fluxo normal do Build produza essa combinação ou de que haja um banco real corrompido. A UI possui defesa adicional e recusa o vazio disponível fora de `state=4 && !genesis_inferred`; isso não elimina a lacuna do codec para outros consumidores. O achado foi comunicado imediatamente ao autor e ao coordenador.

Proposta pontual: validar no decode final que lista disponível vazia exige estado 4, origem não inferida e montante/percentual inválidos. O helper usado antes da finalização do Build pode precisar de uma validação intermediária distinta; não restringir silenciosamente esse estágio sem testar o ciclo provisório real. Acrescentar o contraexemplo ao teste sem mudar expectativas financeiras.

## Demais observações confirmadas nesta versão

- ProjectMembers, linhas 194–205, enumera todos os JPWLedgerMember do ciclo, sem filtrar volume remanescente; portanto inclui Gênese fechada e posições encerradas. A origem individual não é promovida e os IDs são ordenados numericamente.
- MemberListValid impõe números positivos, representação decimal canônica, ordem estrita, limite de registros e inclusão da identidade da Gênese conhecida. MembershipProjectionValid rejeita repetição de cycle_id e identificador repetido entre ciclos na mesma projeção.
- Codec v1 é aceito com `members_available=false` e lista vazia; reencodificação não inventa disponibilidade. O v2 usa sentinel `-` para ausência/vazio textual, evitando depender de campo final vazio em StringSplit. O schema próprio do banco continua separado da versão do payload de ciclo.
- ReadProjection lê uma geração em ordem de rows, verifica hashes/reencodificação/contagem e nova consistência de membros. WriteProjection publica o payload junto com a geração existente; dados brutos/revisões financeiros não são migrados ou apagados por esse delta.
- Bridge continua abrindo store somente leitura, valida conta/moeda após leitura e depois do inventário, e conserva a distinção Current/Historical/N/A. Não reconstrói membros a partir de posições vivas nem promove ticket. A disponibilidade de IDs observados não concede cobertura histórica completa, tese formal ou autoridade V11.

## Testes executados pelo revisor

`python3 tools/jpw_genetrix_ledger_test.py`: 19 oráculos financeiros PASS, 124 assertions host PASS e 6 verificações de recuperação entre processos PASS. O runner executa Core/Store, ReadLive e Bridge reais com APIs controladas e SQLite host. Foram observados os novos testes de Gênese fechada, todos os membros, rollover/ticket, codec v1/v2, corrupção de CSV, duplicações, cache SQLite antigo, replay e isolamento de conta. Esse resultado não cobre M01; a sondagem independente acima mostrou o contraexemplo.

Fixtures financeiros permanecem com hash `a26fe59b37edfd4dbc4d8759e87dc6a9f6ffffce74d427e950c5e2bfd434fc1f`. Não foram executados compilador MQL, runtime/conta MT5, lease nativa, persistência no terminal ou negociação: NOT_RUN. Não declarar aprovação integral do delta enquanto M01 não for corrigido e reexaminado nos bytes novos.

## Hashes do candidate observado

| Arquivo | SHA-256 |
|---|---|
| `JPW_Genetrix_Ledger_Core.mqh` | `fa4a7dd0fc04bc88f7f181f692560617dd603f720d81da955b128b5f39ea7546` |
| `JPW_Genetrix_Ledger_Store.mqh` | `5e286bbbb7de261a4b60b67348eeb477697758ec2da1b0da9d308f34215fe632` |
| `JPW_Genetrix_Ledger_Bridge.mqh` | `391680d77672dd2b8b9e0b81a04a35258fd116c10c2abac695c8b081045ae104` |
| `JPW_Genetrix_Ledger_Terminal.mqh`, inalterado | `4efe9a62ab476f7add28ed7e3cf24eab85f4c2fa999ab64c3f03aaf61d75cbde` |
| `JPW_Genetrix_Accountant.mq5`, inalterado | `eff085079eca0cc7108ec18c01f120f06f4567d3daed650927681234e3e97e24` |
| `JPW_Genetrix_Ledger_Tests.mq5` | `08cb5b4414aaa2f78cb4c28a642e8c851d326e47a57d8fc5405256f8ab7695c1` |
| `tools/jpw_genetrix_ledger_test.py` | `e9a3ccdeadad6b110fbcea76f35a5b59d24ec9953086692b41d64f62bba86db1` |

Headers situados em `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/`; EA em `Experts/JPWealth/`, script em `Scripts/JPWealth/`, todos no candidate `/private/tmp/jpw-genetrix-risk-ledger-20261001`. Os hashes foram confirmados antes e após os testes; qualquer correção exige refreeze e adendo, preservando o achado anterior.

## Adendo de releitura — M01 corrigido no host

O autor corrigiu o achado e congelou novos bytes. Core passou a distinguir validação estrutural intermediária de validação final da publicação. `JPWLedgerMemberListValid` exige, para lista disponível vazia: state 4, origem não inferida/ambígua, genesis_identifier/deal iguais a zero, nenhuma posição aberta, montante e percentual inválidos. O codec continua chamando esse validador final; Build chama a validação estrutural ao projetar e a final depois de consolidar estado/valores. Isso preserva a construção legítima de pendentes provisórias e impede aceitar o contraexemplo publicado.

Repeti a mesma sondagem independente com Core/Store finais, acrescentando um ciclo provisório legítimo como controle positivo:

```text
HOST_COMPILE_EXIT 0
PROBE_EMPTY_NONPROVISIONAL member_valid=0 decode=0
PROBE_LEGITIMATE_PROVISIONAL member_valid=1 decode=1 state=4 amount_valid=0
EXIT 0
```

Executei novamente o runner efetivo: 19 oráculos financeiros PASS, 135 assertions host PASS e 6 verificações de recuperação entre processos PASS. O teste do autor agora cobre também variantes do vazio indevido e controles positivos. Executei ainda o focal UI com o novo struct: 10.396 PASS / 0 FAIL; os hashes da UI congelada permaneceram iguais. M01 está encerrado no escopo source/host para os bytes abaixo, sem apagar o achado ou seus resultados anteriores.

| Arquivo atualizado | SHA-256 final |
|---|---|
| `JPW_Genetrix_Ledger_Core.mqh` | `d329042d6bc612c209490f81a2d569fd54ec13b78874104a6297cce189b12d0b` |
| `JPW_Genetrix_Ledger_Tests.mq5` | `805c33daf4ba09be9c53a8ea9649ced243ea4cffad7467c40e231b5a1b04afd5` |
| `tools/jpw_genetrix_ledger_test.py` | `e27e3c5449d29191e8de998ae51f5df9e0dd641f9e3ba5339502fb00f57bf8f6` |

Store, Bridge, Terminal, Accountant e oráculo financeiro permanecem com os hashes da tabela anterior. Não identifiquei outro achado material aberto no delta de membros examinado. Limites anteriores continuam: nenhuma aprovação da UI própria, nenhuma homologação financeira e execução MQL/MT5 nativa NOT_RUN. Integração e gates finais do pacote permanecem a cargo do coordenador.
