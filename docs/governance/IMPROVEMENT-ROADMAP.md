# Roadmap de melhoria controlada

## Onda A - Governanca multiagente

Status: implementada e verificada; aguardando revisao humana do diff.

- contexto M0-M5;
- autoridade A0-A4 e risco N0-D a N3;
- oito skills locais;
- preflight e quality gate;
- templates de tarefa, auditoria e ADR;
- auditoria de qualidade e handoff atual.

Saida: agentes deixam de depender da conversa anterior e falhas recebem classificacao reproduzivel.

## Onda B - Baseline funcional nao normativo

Status: implementada nesta branch porque os bloqueios foram revelados pelos gates da Onda A.

- `hidden`, alvos de toque, inspetor e menu contextual das Notas corrigidos;
- precache do PWA completado e portatil impedido de registrar SW inexistente;
- orientacao em falha de persistencia corrigida sem alterar schema;
- tier `standard` verde 5/5 e Notas verificadas em desktop/mobile.

## Onda C - Integridade de dados e credenciais

Status: planejada N2.

- manter gate de recuperacao ate validacao atomica do import;
- canonizar `reserveMasterCapital` entre estado vazio, migracao, checkpoint e reload;
- caracterizar estados antigos e round-trip de backup;
- decidir politica para senha de investidor;
- validar interrupcao, quota, arquivo invalido e reload.

## Onda D - Reconciliacao normativa

Status: bloqueada por decisoes N3.

Uma ADR e um conjunto de exemplos por tema:

1. perfis V10;
2. fonte oficial de equity e DD;
3. teto duplo da Genese;
4. stop ATR/Raiz-N;
5. histerese e downgrade;
6. poda LIFO;
7. rito da Fase 4;
8. guilhotina/quarentena;
9. drift e linguagem do MEI.

## Onda E - Arquitetura e manutencao

Status: somente apos B-D e gates verdes.

- extrair etapas do onboarding em funcoes puras e pequenos controladores;
- criar testes unitarios do dominio sem DOM;
- reduzir duplicacao de constantes e formatacao;
- revisar landmarks e acessibilidade;
- avaliar modularizacao do JavaScript em projeto separado, sem conversao incidental.

## Metricas de acompanhamento

- zero conflito normativo sem ADR;
- zero N2/N3 sem teste focado e autorizacao;
- tier standard verde em toda integracao;
- full sem `PRODUCT_FAIL` antes de release;
- nenhuma credencial real rastreada;
- funcao nova critica coberta por casos normal, limite, adverso e estado antigo;
- `CURRENT-STATE.md` e handoff atualizados a cada entrega material.
