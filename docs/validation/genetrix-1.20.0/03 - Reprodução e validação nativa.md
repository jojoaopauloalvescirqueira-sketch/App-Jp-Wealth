# Reprodução local e roteiro nativo

Use a pasta `Reprodução` com seu layout original. Não execute EAs do ZIP operacionalmente para reproduzir os testes host.

## Ensaios locais

Python3, compiladorC++17 e SQLite são necessários. No macOS, a implementação host usa CommonCrypto; os adapters são documentação de testes, não um terminal de negociação. Executar cada comando em processo novo, com diretório/recibo novo; conservar stdout/stderr e hashes antes/depois.

```
python3 tools/core_monitor_judge.py --receipt evidence/reproduction-monitor-01.json
python3 tools/core_replay_judge.py --receipt evidence/reproduction-replay-01.json
python3 tools/core_preparation_judge.py --receipt evidence/reproduction-preparation-01.json
python3 tools/core_package_judge.py --receipt evidence/reproduction-package-01.json
python3 tools/jpw_genetrix_ledger_test.py --receipt evidence/reproduction-ledger.json
```

Repetir os casos novos em três processos distintos. Hashes dos julgadores R2/R3 e oráculos estão nos freezes. O juiz de pacote depende do manifesto/downloads e CANDIDATE-FREEZE-R1. Probes em `evidence/author-*` são debug do autor, não aprovação independente. Resultados brutos anteriores ficam preservados e não são a expectativa da próxima tentativa.

## Compilação comprovada

Os33 logs/EX5 provêm do MetaEditor nativo em namespace Windows próprio. `NATIVE-INPUT-FREEZE-R1.json`, `NATIVE-ROOT-RECEIPT-R1.json` e `NATIVE-INDEPENDENT-REVIEW-R1-PARSER-R2.json` ligam compiler/dependências/fontes/CMD/artefatos. O auxiliar COMPILE-ONLY não instala, não inicia MT5 e não executa EAs. RAW_RETURN1 não foi interpretado como êxito ou erro; os logs completos e EX5 novos são a evidência.

Para recompilar novamente, criar outro namespace local Windows com fonte exata, biblioteca padrão e MetaEditor oficial da instalação; não usar pasta operacional ou recuperar EX5 de versões antigas. Não remover marcadores de uma tentativa anterior para reutilizar o recibo. O compilador em si não é redistribuído neste candidato; obtenha-o pela instalação MetaTrader oficial.

## Execução nativa pendente

Em terminal isolado com negociação desativada, congelar account/profile/fixtures/logs e executar os24 critérios, com três sessões novas nos percursos críticos. Dados e cobranças que não forem reproduzíveis não ganham PASS por ausência de falha. Conservar todas as tentativas. Testar os50mil deals/ordens separadamente e limite+1, sem expor uma conta operacional.

Conferir timers, eventos, locks, corrupção/busy, restart/crash, origem/custos/parciais, gráficos e texto/foco/rascunhos, minimizar/remover apoio, avisos semSL com som/popup e persistência. Registrar intenção de aviso versus entrega conhecida. A janela entre evento/captura/atualização precisa ser medida, não presumida.

Depois do aceite concreto, preservar a instalação, retirar os produtores legados normalmente e anexar o Monitor ao apoio; consumidores continuam no trabalho. Conferir resumo, Cockpit, dois módulos e motivos de dados incompletos no seu gráfico. Não armar Supervisor, trocar conta ou publicar. O manual ilustrado acompanha os passos e rollback.
