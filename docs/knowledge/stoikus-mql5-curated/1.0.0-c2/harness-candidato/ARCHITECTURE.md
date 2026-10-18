# Mapa arquitetural de contexto

| Camada | Entrada / responsabilidade | Prova exigida |
|---|---|---|
| Plataforma MQL5 | eventos, séries, handles, arquivos, trade API | REF/TRD por página e teste nativo quando necessário |
| Núcleo de cálculo | política versionada e dados dimensionados | contrato normativo identificado + suíte correspondente |
| Monitor | observa e apresenta estado | testes de estado/UI + terminal para alegação nativa |
| Accountant | histórico, reconciliação, persistência | IDs e duplicações + fixtures de recuperação |
| Supervisor opcional | permissões e ações separadas | autorização expressa, nunca inferida de versão |
| Painéis/scripts | projeção de leitura e comandos delimitados | propriedade dos objetos, foco e rastreio de versões |
| Pacote | fontes, recursos, manifesto, recibos | hashes do candidato exato |

Mapa de localização, sem atestar leitura integral: mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth contém Monitor, Accountant e Supervisor; MQL5/Scripts/JPWealth contém abertura de painéis e testes de ledger/risco. tools contém verificações host. Fonte normativa financeira não é substituída pelos livros de programação.

Fluxo proposto: dados externos → adaptação validada → domínio → persistência/reconciliação → projeção UI. Eventos indicam que há trabalho; não garantem observação de cada mudança. Handlers têm orçamento e estado explícitos. Trabalho caro deve ter contrato próprio antes de ser deslocado para Timer. ML/Python/OpenCL/ONNX são pesquisa futura, não capacidade instalada demonstrada.
