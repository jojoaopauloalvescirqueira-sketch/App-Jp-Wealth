# Fontes normativas — JP Wealth V11

Verificado em 2026-09-08. Índice de responsabilidade e proveniência, sem regra nova.
O proprietário determinou nesta sessão substituir as normas anteriores pela V11 e
forneceu os dois arquivos abaixo. A autorização de adoção documental não é homologação
financeira nem prova de que o software executa os novos contratos.

| Fonte | Identidade preservada | SHA256 |
|---|---|---|
| [Estatuto V11](Estatuto_JP_WEALTH_UNIFICADO.pdf) | PDF fornecido,125p; nome canônico genérico preserva links existentes | `2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769` |
| [Anexo Paramétrico Canônico](ANEXO_PARAMETRICO_CANONICO.md) | JPW-ANNEX-T03,2026-09-03; cópia byte-idêntica | `6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23` |

Os originais externos permaneceram intactos. O Anexo declara autoridade somente
sobre elementos efetivamente delegados; espelhos continuam subordinados à norma
hospedeira. `CANONICAL` não significa `HOMOLOGATED`; `PENDING` não é zero/fallback.
A classificação N0–N3 do corpus financeiro não se confunde com risco N0–N3 do Harness.

## Divergências que precisam permanecer visíveis

Os arquivos recebidos **não são totalmente equivalentes**. Não foram corrigidos ou
fundidos para ocultar isso:

- **FCR:** PDFp86 Art13.2§1 e p91/110 usam capital nominal; Anexo X-FCR/M-02/K-01
  usa DD_MAX×SI. Capital nominal e SI não podem ser presumidos iguais.
- **FEO:** PDFp87–88 Art13.3§§1/5/7/10 ainda trata percentual nominal/homologação;
  AnexoP-29/K usa percentual somente derivado de despesas reais. A redação externa
  atual dos LivrosIV/VII é posterior ao PDF, mas não foi incorporada por esta tarefa.
- **Abertura do ciclo:** PDF exige verificar fundos antes de fixar SI; redação externa
  posterior descreve ato único com ordem lógica. Não inventar sequência executável.
- **Condensação D-11:** omite risco reservado às ordens pendentes ampliadoras,
  incluído no PDFp70 Art8.4§9.
- **FluxoG:** não explicita a camada de Risco Comprometido/Orçamento da Operação
  exigida no PDFp66/71; TRA/capacidade prudencial não a substituem.
- **FEO na ParteM:** BLOCKS_OPERATION=NÃO precisa distinguir operação existente de
  novo período/Gênese, bloqueado sem fundos constituídos no PDFp88/91.

Os P-14/P-18/P-17 pendentes e a replicação suspensa são estados deliberados do
corpus. Não impedem guardar os documentos, mas impedem assumir operabilidade.
Para identificação dos atos externos e matriz norma/código, ver a
[auditoria de adoção](../audit/STATUTE-V11-ISOLATION-2026-09-08.md).

## Legado e responsabilidade

As cópias anteriores de Norma Vigente/Antigo Estatuto foram removidas do worktree e
são recuperáveis no Git em `02d3a6991fe82569c1fe232722d9b8566fc62ecd`. Auditorias,
ADRs antigos e o HTML original preservado são M5; referências V10 nesses registros
não reativam a norma anterior. O organograma existente é referência auxiliar e não
prevalece sobre o Estatuto V11.

O motor quadrifásico, cálculo de DD, fatores, reservas e quarentena continuam
legados. A troca documental não altera esses cálculos nem migra dados. Adequação
financeira requer tarefa própria com decisões explícitas e testes normativos.
