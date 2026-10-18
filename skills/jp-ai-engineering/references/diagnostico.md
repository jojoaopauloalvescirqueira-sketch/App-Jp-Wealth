# Diagnóstico causal

Observe o defeito, reproduza a propriedade relevante e teste uma hipótese que diferencie causas possíveis. Registre apenas entrada, estado, esperado/observado, ambiente e frequência necessários para alguém conferir. Reduza o caso sem remover a condição que causa o problema.

Consulte produtores, consumidores, relógios/estado e dependências pertinentes. Mapa ou busca localiza fontes; ausência de resultado ou aresta não prova ausência de dependência. Leia a fonte aplicável e preserve regras atuais.

Na intermitência, examine ordem, relógio, seed, latência, awaits, cleanup e estado compartilhado conforme a superfície afetada. Aumentar timeout, retries ou agentes não confirma a causa. Distinga contenção, mitigação, correção, prevenção e recuperação. Sem reprodução, mantenha a hipótese como hipótese.

Corrija quando autorizado, deixando caso de regressão permanente na menor camada suficiente. Congele estímulo e expectativa: RED deve mostrar o defeito esperado e GREEN a correção; preserve a saída bruta e os consumidores afetados. Reproduza versões anteriores em cópia descartável, nunca apagando trabalho atual. Três tentativas sem aprendizado exigem rediagnóstico; não há obrigação de realizar três tentativas. Falha anterior ao delta não identifica seu responsável. Preserve falhas brutas e declare a parte inconclusiva.
