# Preenchimento mensal — entrega e validação

Implementação local concluída no build **e08c12101146ae7b**, na branch existente `codex/planejamento-patrimonial-20261020`, HEAD `ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34`. **FULL:96/96 PASS; visual:240/240 PASS.** Os arquivos permaneceram iguais durante a execução final. Revisão independente: **AUDIT_PASS_WITH_DEBT**, com dívidas herdadas descritas abaixo; aceite visual humano separado.

[Prévia local](http://127.0.0.1:8000/index.html?v=e08c12101146ae7b) → Planejamento → Preenchimento mensal. Se aparecer uma versão anterior, feche as abas antigas da prévia e reabra o link. Não apague os dados do navegador: o service worker pode manter a versão das abas ainda abertas. A entrega não inclui commit, merge, push ou publicação.

## O que mudou

- **Leitura compacta:** resultado em US$ e percentual juntos, R$ abaixo; patrimônio em duas moedas onde o modelo já fornece ambas. Sete colunas a partir de900 px úteis e três abaixo, sem exigir rolagem horizontal. Valores grandes e zoom conservam altura automática.
- **Edição por célula:** Resultado, Aporte e Saque abrem um editor no próprio mês, com Salvar e Cancelar. Clique fora não grava nem descarta; Escape cancela. Só um mês/editor fica expandido, com campos únicos, foco e cursor preservados no redimensionamento.
- **Resultado realizado:** percentual ou US$, usando abertura atual e arredondamento aos centavos do projeto. A revisão mostra abertura, valor digitado, unidade, resultado e taxa correspondente. Sem abertura positiva, a conversão percentual fica indisponível; US$ conserva as validações anteriores.
- **Gravação explícita:** Salvar prepara a revisão dos fatos reais; Confirmar registro aciona os comandos existentes. Premissas futuras usam Salvar explícito. Aportes e saques conservam lançamentos individuais e histórico; reais pagos no aporte são obrigatórios, reais recebidos no saque opcionais. Custos não são preenchidos pela cotação.
- **Histórico e filtros:** verde suave para meses passados, inclusive pendentes, com opção de desligar; o mês atual conserva sua indicação. Todos os meses/Atual em diante combinam com AnoTodos ou ano escolhido. Grupos vazios são ocultados; subtotais identificam o ciclo completo.
- **Preferências isoladas:** somente versão e dois booleanos em `jpwealth_planning_monthly_view_v1`, fora dos dados financeiros e do Backup Completo, com limpeza pelas preferências existentes. Conteúdo incompatível é preservado e falhas permitem uso temporário com aviso.
- **Contexto e cancelamento:** célula, seletor, linha e ações superiores mantêm o mesmo mês. Finalizado mostra somente o estado confirmado, inclusive ao cancelar a janela. Os fluxos antigos de resultado/aporte/saque sincronizam a seleção e devolvem o foco ao acionador conectado ou ao seletor do mês.

## Antes e depois

Medições com os mesmos dados sintéticos, viewport1440 px e tabela977,625 px:

| Linha comum | Antes | Depois |
|---|---:|---:|
| Passado/atual |106,5 px |53 px |
| Futuro |132,5 px |53 px |

O objetivo de até64 px aplica-se à leitura desktop usual, sem editor aberto. Alvos de interação têm44 px; alinhamentos declarados usam tolerância de2 px. Telas estreitas, valores extensos e zoom podem aumentar a altura para manter os dados completos.

[Comparação atual](final-e08c/COMPARISON.json) · [Antes no computador](captures/before-monthly-1440.png) · [Depois no computador](final-e08c/captures/after-monthly-1440.png) · [Depois no celular](final-e08c/captures/after-monthly-390.png) · [Revisão na célula](final-e08c/captures/after-editor-review-1440.png)

Navegar, expandir, filtrar, redimensionar e digitar não gravaram dados financeiros nas jornadas testadas. A revisão real só adotou alterações após confirmação explícita. As capturas também registraram zero chamadas de escritor. [Medições e contadores](final-e08c/AFTER.json).

## Verificação automatizada atual

| Escopo | Resultado |
|---|---|
| TierFULL |**96/96**, saída real0; nenhuma falha ou check não executado |
| Verificador visual padrão |**240/240**, incluindo todos206 anteriores;565,415s |
| Edição mensal |**34/34**, incluindo25 comportamentos e9 contraprovas dedicadas; contraprovas adicionais no caso de identidade |
| Estado/prévia de resultado |**68/68**, com54 anteriores e14 novos |
| Focais do pacote final |**7/7**: paridade, três abas, proporções, layouts, interface/PDF, distribuição e finalização |
| Validação estrutural/reprodutibilidade |PASS |
| HTTP/PWA offline/arquivo local/portátil |PASS nas jornadas de distribuição |
| Aceite visual humano |**PENDENTE**, não inferido dos testes |

Os números se sobrepõem:240 casos e68 testes estão dentro de comandos do FULL; não são96+240 checks independentes.

[FULL vinculado às fontes](FULL-RESULT.json) · [FULL bruto](FULL-RAW.json) · [Comando e saída reais](final-e08c/FULL-COMMAND.json) · [Log completo](final-e08c/FULL.log) · [Visual240](final-e08c/UI-DEFAULT-240.json) · [Casos34](final-e08c/INLINE-34.json) · [Focais7](final-e08c/FOCALS.json)

A cobertura inclui quatro layouts, dois temas,320–1440 px, fronteiras899/900/901 px úteis, zoom nativo200%, teclado e toque simulado. A matriz conserva verificações dos120 meses, valores visíveis e subtotais. As contraprovas rejeitam altura excessiva, duplicação, data/estado incorreto, gravação por digitação, contaminação do backup, moeda errada, alvo menor, conteúdo desalinhado, seleção divergente, falsa indicação Sim e foco perdido. Nenhum limite anterior foi reduzido.

## Achados corrigidos e origem

| Achado | Correção/prova |
|---|---|
| Conta de um rascunho podia divergir da conta global e preencher premissa nula |Guarda de navegação e consulta vinculada à conta do editor; escritor real/read-back sintético preserva taxa nula e aporte17 |
| Escape de menu/Notas alcançava edição inferior |Respeito à camada proprietária; rascunho permanece até o Escape do próprio editor |
| Ações internas tinham30 px, revisão ficava fora da área visível e sucesso perdia foco |Alvos44 px/centro2 px; revisão visível e foco não interativo; retorno à célula após salvar |
| Abrir célula de outro mês não sincronizava os controles |Seleção e contexto unificados; Cancelar/Escape/Salvar mantêm a identidade |
| Herança: Finalizado ficavaSim após cancelar e o mês escolhido no fluxo antigo divergia do seletor |Restauração do valor confirmado e sincronização visual antes dos diálogos existentes |
| A sincronização introduziu perda do acionador de retorno |Remapeamento por ação/ID/tipo ou seletor; seis caminhos de Cancelar/Escape e dois fallbacks conferidos independentemente |

Os REDs, contraprovas e GREENs foram preservados. [Reabertura34GREEN](final-e08c/REOPENING-GREEN.json) · [Preservação](final-e08c/REOPENING-PRESERVATION.json) · [Foco independente](final-e08c/INDEPENDENT-FOCUS-GREEN.json) · [Construtor](final-e08c/UI-BUILDER.md).

[Parecer independente final](FINAL-INDEPENDENT-AUDIT.md) · [Veredito](FINAL-VERDICT.json) · [Conferência final dos recibos](FINAL-FULL-INDEPENDENT-VERIFICATION.json).

## Preservação e rastreabilidade

A base tinha1921 arquivos e8 links, incluindo122 pendências anteriores. A cópia recuperável foi conferida por hashes. Permanecem intactos motor, escritores, fórmulas, histórico, formato de backup, Consolidado, formulário, Stoikus e fontes dos três jogos/Bolsas Globais nos limites registrados. A consulta nova é somente leitura.

O fingerprint oficial tem327 entradas;397 arquivos de runtime,264 de testes, executor e37 controles foram congelados. O executor e a ordem dos96 checks são idênticos à base. As53 entradas anteriores do índice de regressões foram preservadas; oito registros próprios delimitam os novos estímulos/proteções. Os documentos receberam cabeçalhos factuais, preservando seus corpos históricos.

[Escopo](SCOPE.json) · [Fingerprint](FINGERPRINT-INPUTS.json) · [Runtime](RUNTIME-INPUTS.json) · [Testes](TESTS-INPUTS.json) · [Controles](CONTROL-INPUTS.json) · [Registro61/originais53](final-e08c/REGISTRY-PRESERVATION.json) · [Validador do registro](final-e08c/ENGINEERING.log).

## Histórico e limites

- As primeiras FULL6ca/004d foram interrompidas para reparos de contexto, sem resultado completo e sem aprovação presumida. A segunda tinha62 comandosPASS/0FAIL. Os recibos permanecem em [tentativa1](attempts/full1-6ca/INTERRUPTION.json) e [tentativa2](attempts/full2-004d/INTERRUPTION.json). Somente a execução final e08 aprova estes arquivos.
- O ambiente antigo em `/private/tmp` perdeu arquivos na virada do dia. As falhas de importação foram ambientais; as mesmas versões foram recuperadas do cache local, sem pip, rede ou dependência do aplicativo. Foram conferidos292 arquivos pelo RECORD dos pacotes. [Ambiente atual](final-e08c/ENVIRONMENT.json) · [Recuperação](final-e08c/RUNTIME-RECOVERY.json).
- As primeiras comparações com a UI original não comprovaram a interceptação e foram classificadas como inconclusivas. Foram repetidas com resposta original observada; os primeiros arquivos não foram apagados. A comparação isola a UI original em fixture controlada, sem alegar restauração integral do aplicativo antigo. [Origem observada](final-e08c/OBSERVED-BASELINE-FINALIZADO.json).
- **Dívidas herdadas:** confirmar pela janela antiga pode recompor a página e deixar o foco no corpo; a edição nova na célula devolve o foco à célula. O PDF está legível, mas sua segunda página mantém apenas duas linhas de rodapé. O incidente histórico Alladin caseF permanece aberto; esta execução não o encerra automaticamente. [InspeçãoPDF](final-e08c/PDF-INSPECTION.json).
- Safari, leitor de tela, toque físico, percepção do popup nativo e compreensão/aceite humano não foram estabelecidos. A cobertura visual dedicada é Planejamento, não uma certificação visual de todas as áreas do site.

Não houve migração financeira, nova dependência do aplicativo, configuração de memória, alteração de normas, plugin ou AGENTS, commit, merge, push ou publicação. Uso local e dados sintéticos de teste permanecem distintos dos dados reais do usuário.

Os verificadores foram ampliados dentro do contrato aprovado, com contraprovas, preservando critérios anteriores, executor e ordem dos96 checks.
