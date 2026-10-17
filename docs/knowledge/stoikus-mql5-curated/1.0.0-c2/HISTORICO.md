# Histórico preservado fora da seleção

O snapshot original tem 870 arquivos: 866 de entrega histórica não-cache e quatro caches Python. O manifesto histórico `DELIVERY_MANIFEST.json` descreve 865 entradas e exclui a si mesmo. Ele continua preservado com o restante do snapshot e não representa esta edição menor.

O arquivo histórico completo, denominado `Stoikus_Engenharia_MQL5_Manual_e_Harness_CANDIDATE.zip`, tem SHA-256 `2305ea13523b10904106c0bd1056c34cb4181640f00cebea67467ea3ddb64b0c`. A localização privada e a cópia durável são controladas em recibo externo. O pacote curado contém o mapa de identidades, não o ZIP histórico nem seus conteúdos opacos.

Todos os 870 caminhos originais e seus hashes constam de `curadoria/MAPA_ORIGEM.json`. EXTERNAL quer dizer omitido desta seleção e retido no histórico privado; CACHE quer dizer cache identificado na triagem e não distribuído. PRESERVED identifica cópia idêntica e TRANSFORMED identifica uma cópia com alterações documentadas.

Os registros textuais selecionados em `validation/`, o plano original e o relatório final original são **HISTORICAL_ONLY**. Conservam a sucessão de revisões, falhas, resultados e limites. As referências a `harness-next-r3/`, rodadas R1/R2/R3, snapshots, recortes, renders e logs localizam elementos do histórico. Esses caminhos não devem ser usados como se estivessem incluídos nesta seleção.

A qualificação R3 preservada declara 36/36 PASS em casos sintéticos. Esta curadoria não repetiu os 36 ensaios, não reconstruiu capturas, não verificou novamente a proveniência de todas as tentativas e não transforma o resultado em validação corrente do EA ou do kit. As ressalvas e os resultados R2 permanecem nos relatórios selecionados; as provas brutas e snapshots completos ficam no histórico privado.

As fontes REF, TRD e NN são bibliografia externa identificada por hash e página. A omissão dos recortes e dos 83 campos de extratos não constitui releitura ou revisão técnica da pesquisa. Os registros anteriores continuam com seus estados originais; a nova identidade autentica somente o conteúdo desta edição.

A C1 selada e seus recibos permanecem externos. Sua primeira tentativa de inclusão Git encontrou 13 marcadores de formatação herdados em nove Markdown. A C2 é uma revisão separada: remove sete espaços finais e seis linhas vazias de EOF, conserva o restante desses textos e atualiza somente guias/identidade/rastreabilidade necessários. A derivação, os hashes pais e os deltas estão em `curadoria/TRANSFORMACOES.json`, seção `revision_c2`; a falha anterior não foi apagada nem convertida em PASS.

A montagem C2 é externa ao repositório. Nenhum original, arquivo de produto ou kit foi alterado. Não houve instalação, commit, push ou publicação nesta montagem; essas ações exigem recibos próprios posteriores. O kit permanece NOT_ADOPTED, MT5 NOT_RUN e novo piloto NOT_RUN. O resultado anterior T1/T2-R2 vale somente para seus hashes; a C2 possui identidade e revisão próprias.
