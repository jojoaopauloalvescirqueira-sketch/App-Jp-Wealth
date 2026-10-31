# Controles delimitados — Sessões Forex e B3

Implementação autorizada no plano humano31/10/2026; base69b6cb6. N3/A4 para a extensão de controles desta frente; não altera normas financeiras, permissões, aprovações ou limiares.

- Reusar `compile_market_hours.py` sem modificar seu compilador/validador para materializar um catálogoFXindependente e dias de exibição pela TZif congelada. O novo `compile_forex_sessions.py` não faz rede, não lê relógio nem dados reais.
- `rebuild_monolith.py` inclui a fonte e os insumosFX explícitos na identidade e gera envelope/manifesto/sidecar/portátil oficiais. A listaSW acrescenta somente o catálogoFX; waiting, ativação conservadora e políticaPWA permanecem.
- `market_hours_build_test.py` passa a exigir os bytes e fingerprintsFX além dos recursos anteriores. `market_hours_assets_test.py` acrescenta o recurso ao transporte sintético existente.
- A entradaFULL `calendar-distribution` mantém seus quatro casos e integra a consultaFX/B3 em cada distribuição. Depois executa obrigatoriamente os focais permanentes de modelo e UI; qualquer código nãozero permanece bloqueante. `quality_gate.py`, suas116entradas, limites, oráculos e prazos não são alterados.

Contraprovas: teste-modelo inicialmente rejeitou ausência da APIFX; testeUI executado emChromium rejeitou ausência das quatro linhas. Os novos casos exigem fronteiras exatas, domingoUTC, DST23/25h, fora de cobertura, fuso inválido, dados corrompidos preservados e recusa de gravação. Casos e recibos antigos não são apagados. Uma tentativa de inicializaçãoChromium dentro do sandbox foiENVIRONMENT_ERROR e nãoRED de produto. Uma fixtureHTML comcontent-type incorreto foiTEST_HARNESS_FAIL; uma corrida da fixture antes da entregaResizeObserver foi corrigida esperando a condição de layout real, sem relaxar geometria.

A entrada de distribuição registra comando,saída,código de cada focal no recibo; sucesso dos focais não transforma falha anterior emPASS. FULL final e auditoria independente são gates separados sob coordenação da raiz. Sem commit,merge,push ou publicação.

## Revisão independente e correção delimitada

A revisão encontrou três defeitos: unknown convertido em resumo zero; sobrescrita de preferência incompatível inserida depois da montagem; remoção do botão focado na troca assíncrona do resumo. O novo focal permanente `forex_sessions_review_test.py` reproduziu essas falhas antes da correção e passou depois, incluindo concorrência válida, readback e cobertura parcial. Não altera oráculos financeiros, tolerâncias de 2 px, dimensões aprovadas ou prazos. A entrada de distribuição executa agora três focais obrigatórios e registra cada resultado sem apagar falhas anteriores.

Medições da nova view usam caixas reais de bandeira, trilho, marcador e alvo; validam os desvios verticais internos de até 2 px, cores/temas, quatro larguras e o resize com foco. Zoom 200% utiliza Preferences de um perfil isolado do próprio Chromium, com outerWidth/innerWidth=2 e CSS zoom=1, também em headless. Não substitui toque físico, leitor de tela ou aceite humano. O teste de lifecycle mede chamadas ao motor real e sua suspensão/retomada; o renderer real continua comprovado nas quatro distribuições.

### Reauditoria delimitada antes do FULL

O mesmo N3/A4 cobre o fechamento da janela de integridade dos focais: o inventário anterior às execuções é conservado como `inputsAfterDistributions` e `sourceUnchangedBeforeFocals`, e `inputsAfter` passa a representar o instante posterior aos três subprocessos. `sourceUnchanged` exige as duas comparações; uma falha anterior permanece bloqueante. A duração final também inclui os focais, preservando separadamente a duração das distribuições. Nenhuma entrada, tolerância ou prazo do gate foi alterado.

Uma contraprova de fluxo do runner, com inventário/navegador/subprocessos sintéticos e mutação injetada no terceiro focal, reproduziu a falsa aceitação anterior. Após a correção, esse mesmo estímulo exige retorno nãozero e `sourceUnchanged=false`. Essa contraprova avalia o controle do runner; somente a matriz real comprova as distribuições do produto. A reauditoria também acrescentou casos permanentes para as fronteiras civis do Dispositivo e as medidas dos controles na camada externa de ajuda. As permissões de Git, FULL, publicação e aceite humano permanecem inalteradas.


### Registro final de validação — 31/10/2026

O FULL atual do build `1cad00952882d28b` concluiu **116/116 PASS** em 2026-10-31T12:03:28-03:00. O [recibo bruto copiado sem alterações](../validation/forex-sessions-20261031/FULL-RESULT.json) e a [validação final](../validation/forex-sessions-20261031/FINAL-VALIDATION.md) identificam este candidato. Incluem quatro distribuições, três focais obrigatórios e dez grupos de revisão. Fontes permaneceram congeladas durante a execução; esta atualização posterior limita-se a documentação e metadados dos sete registros próprios de memória, sem mudança em código, testes, gates ou derivados. Evidências e tentativas históricas continuam históricas.

A entrada inicial de memória é requisito novo (`new_contract_regression`); os seis defeitos reproduzidos/corrigidos usam `fixed_regression`, com causa real, RED/GREEN e build/recibo atuais. A enumeração do validador opt-in anterior não conhece contrato novo; os22erros preexistentes da base e esse limite são declarados, sem alterar o validador nem promover erro estrutural a PASS. Aceite humano, Git e publicação continuam separados.
