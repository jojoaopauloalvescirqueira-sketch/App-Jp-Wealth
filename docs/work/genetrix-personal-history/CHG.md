# CHG GENETRIX Histórico Pessoal 1.18.0

Autoridade: pedido humano PLEASE IMPLEMENT THIS PLAN na conversa, cobrindo implementação isolada, testes sintéticos, revisão e entrega. N2 de persistência e histórico financeiro observacional; fórmulas canônicas preservadas. Não concede negociação, instalação operacional, publicação, commit/push/merge ou alteração do juiz.

Base: candidato1.17RC2, HEAD deffc5061fe2eff3d83b6f6e742fa105ac9c5b06. Todos126 inputs congelados conferidos, zero divergências.675 arquivos conhecidos copiados para worktree codex/genetrix-personal-history-20261001 em /private/tmp/jpw-genetrix-personal-history-20261001. BASELINE-INPUTS.json registra os hashes; fontes anteriores e checkout do site intocados. Dirty herdado é conhecido e preservado; --allow-dirty é a opção documentada do preflight nesta retomada coordenada, sem enfraquecer gate.

1. Finalidade: produto local de leitura de risco e rastreabilidade; registrar fatos de ausência de SL e máximos observados, sem certificar conformidade V11.
2. Responsabilidade: EA coleta/grava/avisa; Core define estados; Store financeiro novo e isolado persiste; Cockpit somente lê e exporta por solicitação.
3. Antes: StopRisk conserva duas gerações; Diagnostics é técnico; MDD não mede pico de alavancagem. Depois: episódios, avisos, cobertura, máximos Current/Estimated e fotografias permanentes.
4. Impacto: Observer, leitura de conta/inventário e UI/Actions; novo namespace pessoal. Sem alterar ledger, MDD, StopRisk, normas, supervisor7x ou site.
5. Invariantes: alertas após SL==0 observado,60s, conta inteira; chave estável conta/instalação; sem segredos, reset, exclusão automática ou trading; snapshots e máximos atomicamente ligados; sinais técnicos não viram fatos financeiros.
6. Prova: HIS-AC01…20 congelados antes do código,3 processos por caso, oráculo independente e SQLite real no host; auditor diferente do autor, nativeNOT_RUN separado.

Fontes: AGENTS raiz/local, README/CONTEXT-MAP, PROJECT-CONTEXT, FOREX-V11-ENGINE, QUALITY-GATES, skills roteadas; Master Specification canônico relocalizado no vault2/6C, SHA b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95, §§14–18 e27: incremento/freeze/validação/auditoria e backup íntegro. Não ativar exceções de falha histórica.

Fronteira: novos arquivos JPW_PersonalHistory_* em Include/JPWealth, testes sob tools/tests/fixtures e script sintético, Observer e Cockpit/Coordinator/Presentation/Actions para integração; docs específicos e empacotamento novo. Não escrever em fontes synced, acervo1.17, site paralelo, instalações reais ou bancos reais.

Rollback: retornar ao fonte1.17 congelado; deixar banco PersonalHistory preservado e não lido por versões antigas. Artefatos1.18 separados; sem migração de bases antigas. Ambiente MT5 nativo é pendência; nunca apresentar C++/SQLite host como compilação MQL/EX5 ou reprodução de popup/som.

## Adaptação dos testes de regressão existentes

Os adapters de `leverage_details_event_test.py` e `leverage_geometry_test.py` recebem somente declarações das novas dependências. A verificação estática de navegação em `leverage_panel_test.py` mantém as cinco abas originais e exige também Histórico Pessoal e suas ações estáveis. Não muda os 20 critérios congelados nem reduz expectativas anteriores. Falhas das tentativas de desenvolvimento são preservadas; a aba nova tem verificação própria independente.

`leverage_scheduler_test.py` recebe adapter no-op somente para a nova dependência de desligamento do histórico, mantendo os critérios originais de fairness. A investigação nativa encontrou MetaEditor, ausência de Wine executável e `prlctl exec` recusado com exit255 pela edição do Parallels; nenhuma sessão MT5 foi alterada.
