# CHG-JPW-COCKPIT-AI-GUIDE-20260929 — guia local para IAs

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-COCKPIT-AI-GUIDE-20260929
status: implemented_local_pending_independent_audit
objective: guia subordinado de manutencao e auditoria para o pacote-fonte MT5
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
derived_from: jpw-cockpit-product-r12-892ede1761848bfd51140c1a57543dc041a4311126705539eb522acdebb957df
approved_by: Proprietario, pedido PLEASE IMPLEMENT THIS PLAN para JPW Cockpit 1.8.0
```

## Objetivo e autoridade

Adicionar apenas `mt5/jpw-alavancagem-atual/AGENTS.md` como guia de leitura e manutencao para IA e inclui-lo no ZIP de fontes. Ele mapeara componentes, formulas/unidades, estados, registros separados, atualizacao, rollback, testes e coerencia de fonte/pagina/manifesto/pacote. Sera subordinado a instrucoes superiores do repositorio, Estatuto e Harness canonico externo. Nao concedera autorizacao, Human Acceptance, homologacao P-21 nem permissao de negociar. Nao sera copiado a `MQL5` na instalacao.

O guia sera escrito **depois** do congelamento do delta de produto. Assim seu efeito sobre a camada agentica e a diferenca do produto podem ser revisados separadamente. A adicao exige auditoria independente N3/A4 e teste estrutural, alem da auditoria do produto. Fonte r11 continua historica com seus bloqueios, e o guia nao corrige ou reclassifica falhas.

## Escopo, revisao e rollback

Permitidos: o guia, entrada explicita no manifesto/ZIP e referencias curtas no README/indicador; CHG/ACTIVE-TASK e evidencias externas. Proibidos: edicao de root AGENTS, skills, roteamento, Estatuto, Harness externo, formulas, registros financeiros, conta real, operacoes no MT5 operacional, Git ou publicacao. Conferir que `AGENTS.md` nao aparece dentro de `MQL5/`, que nenhum texto atua como nova autoridade, e que o pacote contem bytes/hash exatos. Reverter removendo somente o guia e suas referencias/entrada de pacote, preservando checkpoint de produto.

## Resultado

O produto foi congelado antes do guia em snapshot externo de 81 arquivos, fingerprint `892ede1761848bfd51140c1a57543dc041a4311126705539eb522acdebb957df`. Este guia foi criado na raiz do pacote-fonte, listado no manifesto e exigido pelo gerador; nao integra `MQL5`. Teste estrutural, candidate final e parecer independente ainda precisam de recibos. Aceite humano e etapas Git continuam separados.
