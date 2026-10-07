# JP Wealth — correções de interface

Contrato: CHG-JPW-INTERFACE-BUGFIX-20261006 (N1/A2), autorizado por “rastreie e corrija bugs da interface”.

## Compreensão e limites

1. **Produto:** aplicativo local de gestão; esta revisão corrige interação e apresentação, não o modelo financeiro.
2. **Base:** candidate 3ea4d24e6b8c3bf7, 729 entradas conferidas; snapshot e diff anteriores preservados externamente. O localhost:54839 informado estava encerrado.
3. **Fontes:** componentes em src/js/20-ui e shell de navegação; monólito/portátil/manifesto são derivados oficiais. sources/ do projeto sincronizado é somente referência.
4. **Contexto:** conta consultada não altera conta operacional. Prévias e rascunhos não integram totais confirmados. Recusas de gravação e guardas de rascunho continuam canônicas.
5. **Escrita:** os comandos existentes permanecem responsáveis pelos atos. Finanças Pessoais confirma cada campo em change; corrigir foco não altera esse contrato. Desenho, navegação e resize não criam fatos.
6. **Verificação:** reprodução sintética, contraprova, revisão independente e gates originais; PASS focal não apaga PRODUCT_FAIL financeiro conhecido (DD 14%) nem comprova MT5 nativo.

## Execução

- Reproduzir gaveta após resposta assíncrona ao diálogo de rascunho e prioridade de Escape.
- Verificar continuidade de teclado e clique em edição de Finanças Pessoais.
- Auditar Forex, Configurações e Notas, diferenciando defeitos confirmados de hipóteses refutadas.
- Corrigir somente causas confirmadas; guardar probes e evidências fora do produto. Nenhum teste/gate existente será alterado.
- Regenerar derivados, congelar bytes, rodar focais, standard/full e auditar o delta.

## Entrega e retorno

Candidate local, inventário de achados, evidências antes/depois, limitações e relatório. Rollback pelo baseline.tar.gz e baseline.json externos. Sem commit, integração, publicação ou instalação MT5.
