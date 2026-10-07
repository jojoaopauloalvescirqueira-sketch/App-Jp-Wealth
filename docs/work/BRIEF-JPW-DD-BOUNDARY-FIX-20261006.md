# JP Wealth — precisão nas fronteiras do DD

Objetivo autorizado: “Corrija a falha financeira conhecida”. N3/A4, contrato CHG-JPW-DD-BOUNDARY-FIX-20261006. Base local571d8c2c99b56fbd, HEADac3a2faffeb398357ff105adbf1d47f70ca309bd, snapshot731entradas preservado externamente.

1. Finalidade: medir deterioração da conta conforme SI/equity/ajuste documentado, sem permitir mudança artificial de fase por arredondamento binário.
2. Responsabilidade: 10-domain/00-forex-engine calcula; state grava fase/histerese e consumidores reutilizam a projeção. Esta tarefa corrige somente a aritmética na origem.
3. Antes: SI10000/equity8600/cf0 gera14.000000000000002→F5. Depois: DD14 exato→F4, DD real acima→F5. SI0.5/equity0.39→22 bloqueante. USD/USC devem ser coerentes.
4. Afetados: fase, histerese, capacidade prudencial, readModel, Board, header e Dashboard. Contextos antigos e picos gravados permanecem fatos históricos; sem reparação automática.
5. Preservar: política, norma, parâmetros PENDING, estado/schema, salvamento, snapshots e MT5. Não corrigir outros cálculos ou fórmulas financeiras paralelas nesta tarefa.
6. Prova: oráculo racional decimal independente; caracterização antes/depois, limites/adjacentes, CF minúsculo, USD/USC, extremos, estado→UI e full. Nenhum teste/gate do repositório será alterado.

Fontes conferidas: Estatuto V11 SHA2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769, PDFp32 Art4.1 (SIfixo, caixa neutralizado, subida estrita, retorno condicionado), pp51–54 Arts6.1/6.3 (limites2/6/10/14/18; fechamento>=22). Anexo T03 SHA6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23: P01/P03/P04. Não há decisão nova de parâmetro. Harness externo7C SHA b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95, §§12–14/19/24/28–30/36–48.

Semântica: Number.toString representa o decimal canônico recebido/persistido; não recupera dígitos perdidos antes do motor. A subtração e razão são racionais exatas em RAM, com conversão final para Number; nenhum BigInt é exposto/persistido. Caso arredondamento final coincida com limiar apesar de estar realmente acima/abaixo, preservar o lado pelo Number adjacente. Sem tolerância ou redução para duas casas. Se não houver representação coerente com todos os limiares, NOT_COMPUTABLE. Ajuste de equity não representável permanece recusado.

Retorno: versão anterior preservada e baseline.tar.gz, nunca inversão de dados em uso. Testes são sintéticos; entrega local não é aceite, homologação, Git ou publicação.
