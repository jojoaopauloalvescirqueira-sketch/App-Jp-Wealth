# Parecer independente final delimitado — proposta de tabela econômica

## Veredicto

As duas propostas podem ser apresentadas ao usuário para aprovação específica da aplicação e dos controles N3. Nenhum bloqueador material foi encontrado na revisão estática delimitada e no focal independente abaixo. Isso não autoriza aplicação, não aprova release e não converte os controles em validados integralmente.

Resultado de preparação/revisabilidade: apta para apresentação. Resultado de validação integral do candidate: AUDIT_INCONCLUSIVE, pois contraprovas novas, suites completas, distribuição gerada e execução nativa permanecem NOT_RUN. O repositório não recebeu alterações do revisor; somente arquivos em review-proposal foram escritos.

## Identidade confirmada diretamente por SHA256

- Produto JS: 1e2e518bef9dccca48790f9752c48ba62619cd64c128ec87c55c6c58c779c831
- Produto CSS: f1007dfe4122ac80aa2e8260b4db91079ad5291cec5f1b2dd6ab0aa3910beb38
- product.patch: 43614335e4a9043c7a2149dbe24d6ee118d18886c68c84bbc7a160591b7d9fea
- tests-candidate.patch: 37a46edbd8e2c56e6327ce8dc8e42cc034c1063c2ef6a55520effa53bc8a39c3
- Helper novo: 35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a
- calendar_agenda_test.py: 655556061f9fbbecd28f73de0861ac2e05741a658d7da0777b2591da28ab7ddd
- calendar_visual_quality_test.py: b883b966e1be638707da5c53999392cfc6ae02da36440500ddd18fc12970b95f
- calendar_distribution_test.py: cbaf54be1a5dd0ebecf80773158a86453f849fbf0ab8734a1ad32376065003a9
- ff_news_cache_test.py: f66f357830f04a2c9f6eeb92ac469d8e04c190b6aa1a42aad161f65ebde859a7

Candidate-hashes confirmado por cálculo independente, parsing AST dos cinco candidatos Python e comparação direta da base real dos sete arquivos de produto/testes. Recibo: independent-preservation.json. O helper novo continua inexistente no repositório.

## Revisão estática realizada

Li os dois patches, o helper completo, trechos finais dos handlers/foco/CSS, README e recibos de preservação. O delta de produto fica em19+CSS; não modifica queryRange, produtores, cache, persistência financeira, schema, backup ou consumidores semanais. Expansão é estado de instância, com identidade de observação exata e rejeição de ambiguidade. O novo controle tem ação economic-detail distinta da informação global e IDs de detalhe prefixados pelo host. Escape não recebe interceptação nova. O novo render não reconstrói formHost.

A tabela mantém sete células por evento; texto de Projeção/Anterior usa a string existente sem conversão numérica, incluindo zero em string. Atual sempre recebe travessão com explicação acessível. Fontes, horário original e referências oficiais ficam no detalhe; horário pendente, cancelamento, ausência na coleta e divergência continuam na linha. Saídas continuam por textContent; links novos restringem HTTPS e recusam credenciais.

CSS fixa mês308, usa container do painel para os700 úteis e container econômico para720. th/td reutilizam a mesma grade; números têm alinhamento à direita, valores compactos recebem rótulo visível e altura automática. A regra740 de container deriva dos40px de padding do corpo em viewport desktop. Os limites700/720 são medidos separadamente no teste proposto. Workspace320 recebe expansão local100vw para preservar sete dias44; prova do autor é focal, cobertura de viewport completa ainda pendente.

O teste economic_focus foi adaptado legitimamente para abrir o detalhe antes de focar o link. A asserção de observação alterada foi preservada/fortalecida, sem pedir link visível quando o contrato exige fechá-lo. Não há alteração proposta em quality_gate.py/ui_visual_quality_test.py, catálogo116, timeout900 ou tolerância2. Os IDs413 são preservados por estrutura; esta revisão não executa413 casos.

## Evidência executada independentemente

Comando: PYTHONDONTWRITEBYTECODE=1 <runtime existente> review-proposal/visual_positive_probe.py.

Chrome headless, origem local, bootstrap/transportes sintéticos, JS+CSS congelados servidos por overlay de memória. Quatro layouts (sidebar/topbar/glass/submenu), dois temas,1440×900, UTC. Foi chamada a geometry candidata com o mesmo helper visual existente, sem alteração de oráculos.

PASS8/8. Cada cenário comprovou exatamente dois eventos e duas entradas economic-detail no resultado de centered(...,'ink',True):16 medições de ícone em total. Portanto o guard rowcount>0 foi exercitado positivamente nos oito pares; não houve matriz de ícones vazia. Recibo visual-positive.json registra medidas e hashes finais. Isso comprova este recorte, não todos os viewports nem native200.

Primeira tentativa: TEST_HARNESS_FAIL. Rotas do overlay registradas antes do bootstrap foram sobrepostas, servindo a base antiga; o juiz rejeitou mês347 em lugar308 e campos ausentes. Recibo bruto visual-positive-first-harness-error.json preservado. A correção ficou somente no launcher scratch, registrando overlay após bootstrap; não foi correção de produto ou afrouxamento do juiz.

## Recibos de outros agentes inspecionados

- overlay-state-5.json: PASS2/2 do autor de testes; contém exatamente JS/CSS e helper/agenda finais. Cobre economic-focus e table-state com scroll48, recaptura, horário alterado, duplicata ambígua, dois hosts, rascunho/cursor e Escape legado. Leitura deste recibo não é execução própria.
- overlay-focal-3.json: PASS5/5 do autor, mas JS84862dcd… e helper1c32c6e3… anteriores. Deve permanecer evidência parcial histórica; não declarar cinco casos executados com os bytes finais. CSS é o final, e o delta posterior de produto foi de metadados/escopo do resumo; ainda assim a identidade de execução não é a mesma.
- O oráculo real th↔td e Range.right foi introduzido após um PRODUCT_FAIL documentado; o patch final conserva a tolerância2, em vez de aceitar o desalinhamento.

## Pendências que devem acompanhar a aprovação

1. Aplicação somente na branch e caminhos especificamente aprovados; contrato dedicado de produto e de controles N3. Não foi apresentado um CHG N3 final separado dentro dos pacotes desta revisão: a aprovação deve identificar o patch e seus hashes, escopo e limites, sem inferir autoridade do README.
2. Executar as contraprovas propostas pelo mesmo juiz, especialmente ausência/zero, ocultação compacta, cabeçalho deslocado, número à esquerda,720, avisos e identidade. Atualmente NOT_RUN.
3. Executar os novos testes focais completos nos bytes finais, pipeline v2/cache e distribuições após gerador oficial autorizado. Focais parciais não comprovam artefatos finais.
4. Executar FULL116 e a matriz visual413 conforme contrato,900s e2px preservados. Native200/nativos, leitor de tela, toque e aceite visual humano separados.
5. Na execução visual completa, conservar no recibo as entradas economic-detail já demonstradas neste focal. O guard pode permanecer para estados vazios, mas ausência inesperada de eventos não deve ser aceita como cobertura positiva dos novos controles. Não alegar que este focal de oito casos substitui a matriz.

Não executei FULL, janela nativa, rede externa, gerador ou mutação Git. Nenhuma proposta foi aplicada pelo revisor.
