# REF — leitura semântica batch 13b

Escopo exclusivo: páginas físicas PDF 4259–4490 (232 páginas), lidas integralmente no texto extraído em oito lotes de até 29.000 caracteres. Não houve inspeção visual; não se inferem imagens, paginação impressa ou aparência. MQL_NOT_RUN. Aplicações abaixo são propostas para Stoikus, não descrição de produto implementado. Nenhuma alteração de produto, manual, harness ou Git. O registro reference-batch-13 parcial de 155 páginas foi preservado.

## Síntese aplicada

O risco dominante deste intervalo é propriedade de objetos. CArrayObj e CList podem liberar objetos automaticamente; cópia de ponteiros pode criar múltiplos proprietários, referências pendentes ou vazamentos. CTree não oferece a mesma escolha de FreeMode. Separar Detach de Delete é essencial em qualquer proposta de fila e índice simultâneos.

Coleções genéricas oferecem contratos tipados distintos: lista permite índices e duplicação; hash map exige chaves únicas e não ordena; hash set exige valores únicos e perde multiplicidade. Igualdade de pares usa a chave; não comprova conteúdo igual. O hash inteiro do contêiner não substitui SHA-256.

Pontos que exigem verificação nativa futura: descrições inconsistentes de Shutdown/AssignArray; exemplos Save/Load com teste de criação invertido; CList Add retorna índice zero válido; assinatura Clone extraída incompleta; BinarySearch documenta retorno de vizinho na ausência; SetEquals tem descrição que não explicita exclusão de extras. Esses pontos impedem copiar exemplos como provas de execução.

## Notas por ID

### REF-0001 — MQL5 Reference — [REF, MQL5 Reference, p.PDF 4259–4490]

Contêiner hierárquico: este registro cobre somente o cruzamento p.4259–4490 por meio dos filhos abaixo; não afirma leitura integral da seção maior. Proposta Stoikus: escolher estrutura pelo contrato de propriedade, ordem e identidade, sem inferir uso atual no produto.

### REF-1136 — Standard Library — [REF, Standard Library, p.PDF 4259–4490]

Contêiner hierárquico: este registro cobre somente o cruzamento p.4259–4490 por meio dos filhos abaixo; não afirma leitura integral da seção maior. Proposta Stoikus: escolher estrutura pelo contrato de propriedade, ordem e identidade, sem inferir uso atual no produto.

### REF-1508 — Data Collections — [REF, Data Collections, p.PDF 4259–4368]

Contêiner hierárquico: este registro cobre somente o cruzamento p.4259–4368 por meio dos filhos abaixo; não afirma leitura integral da seção maior. Proposta Stoikus: escolher estrutura pelo contrato de propriedade, ordem e identidade, sem inferir uso atual no produto.

### REF-1742 — CArrayObj — [REF, CArrayObj, p.PDF 4259–4302]

Array dinâmico de ponteiros CObject, com propriedade ativa por padrão e operações ordenadas/persistência. O exemplo de arrays bidimensionais mostra composição; copiar contêineres copia referências. Proposta Stoikus: escolher dono único de registros e contratos de transferência.

### REF-1743 — FreeMode — [REF, CArrayObj, p.PDF 4264–4264]

Consulta ou define quem libera objetos dinâmicos; padrão ativo. Em Stoikus, uma coleção proprietária deve ser a única responsável por delete; referências emprestadas não podem sobreviver à remoção.

### REF-1744 — FreeMode — [REF, CArrayObj, p.PDF 4265–4266]

Consulta ou define quem libera objetos dinâmicos; padrão ativo. Em Stoikus, uma coleção proprietária deve ser a única responsável por delete; referências emprestadas não podem sobreviver à remoção.

### REF-1745 — Reserve — [REF, CArrayObj, p.PDF 4267–4267]

Reserva elementos adicionais, não cria objetos; tamanho não positivo ou falha retorna false; crescimento usa Step, padrão 16. Proposta: reservar antes de capturar lotes de eventos e tratar falha sem perder o estado anterior.

### REF-1746 — Resize — [REF, CArrayObj, p.PDF 4268–4268]

Reduz tamanho; itens excedentes são perdidos e sua liberação depende de FreeMode. Proposta: retenção de evidências só após persistência, nunca cortar silenciosamente eventos ainda necessários.

### REF-1747 — Clear — [REF, CArrayObj, p.PDF 4269–4269]

Esvazia a coleção; nas coleções de CObject a liberação depende de FreeMode e CArrayObj preserva a memória do array. Proposta: separar reinício da captura de encerramento final.

### REF-1748 — Shutdown — [REF, CArrayObj, p.PDF 4270–4270]

Libera armazenamento do array; a nota condiciona a liberação dos elementos a FreeMode, apesar da descrição resumida dizer “but not its elements”. Proposta: verificar a implementação nativa antes de usar como contrato de descarte.

### REF-1749 — CreateElement — [REF, CArrayObj, p.PDF 4271–4272]

É ponto de extensão de fábrica: CArrayObj base sempre retorna false e CList base NULL; carregamento precisa de derivação que crie o tipo concreto. Proposta: reconstruir eventos tipados com fábrica explícita, sem presumir que a base funciona.

### REF-1750 — Add — [REF, CArrayObj, p.PDF 4273–4273]

Adiciona item; CArrayObj retorna bool e rejeita ponteiro inválido; CList retorna índice ou -1; genéricas retornam bool. Proposta: comparar o retorno correto, pois índice zero válido não é false de falha.

### REF-1751 — AddArray — [REF, CArrayObj, p.PDF 4274–4276]

Copia ponteiros, não objetos; FreeMode em duas coleções pode causar ponteiros inválidos ou vazamento. Proposta: transferência com proprietário único ou cópia real deliberada de registros de evidência.

### REF-1752 — Insert — [REF, CArrayObj, p.PDF 4277–4278]

Insere na posição indicada (ou nó na árvore). CObject inválido é rejeitado; CList retorna índice/-1, CArrayObj bool, CTree ponteiro do proprietário/NULL. Proposta: adaptar tratamento por contrato, sem reutilizar um teste booleano genérico.

### REF-1753 — InsertArray — [REF, CArrayObj, p.PDF 4279–4280]

Insere referências de outra coleção e remete aos riscos de AddArray. Proposta: não compartilhar propriedade de eventos dinâmicos entre fila e histórico.

### REF-1754 — AssignArray — [REF, CArrayObj, p.PDF 4281–4282]

Remove elementos anteriores e copia referências da origem; a frase inicial “Compares” conflita com assinatura e nota de atribuição. Proposta: tratar como substituição destrutiva e garantir propriedade antes de restaurar snapshots.

### REF-1755 — Update — [REF, CArrayObj, p.PDF 4283–4283]

Substitui referência no índice; rejeita ponteiro inválido e libera o antigo se FreeMode ativo. Proposta: invalidar qualquer referência emprestada ao registro anterior.

### REF-1756 — Shift — [REF, CArrayObj, p.PDF 4284–4284]

Move item por deslocamento positivo ou negativo, retornando bool. Proposta: reordenar apresentação sem confundir posição atual com identidade persistente do evento.

### REF-1757 — Detach — [REF, CArrayObj, p.PDF 4285–4285]

Desvincula sem liberar o objeto; no CTree também rebalanceia. Proposta: transferência explícita entre coleções, com liberação posterior garantida pelo novo proprietário.

### REF-1758 — Delete — [REF, CArrayObj, p.PDF 4286–4286]

Remove e, nos contêineres com FreeMode ativo, libera; na árvore sempre libera e rebalanceia. Proposta: distinguir remoção definitiva de transferência de evidências.

### REF-1759 — DeleteRange — [REF, CArrayObj, p.PDF 4287–4287]

Remove do primeiro ao último índice informado, com liberação condicionada a FreeMode. Proposta: registrar faixa e validar extremos antes de aplicar política de retenção.

### REF-1760 — At — [REF, CArrayObj, p.PDF 4288–4288]

Retorna ponteiro ou NULL para posição inexistente. Proposta: testar acesso antes de desreferenciar evento no monitor.

### REF-1761 — CompareArray — [REF, CArrayObj, p.PDF 4289–4289]

Compara coleções; texto do retorno omite false, mas assinatura bool. Proposta: comparação auxilia auditoria de conteúdo, sem substituir hash de artefato nem provar persistência completa.

### REF-1762 — InsertSort — [REF, CArrayObj, p.PDF 4290–4290]

Insere em array já ordenado; ponteiro inválido não entra. Proposta: manter comparador e ordenação consistentes ao organizar eventos por tempo/chave.

### REF-1763 — Search — [REF, CArrayObj, p.PDF 4291–4291]

Busca igualdade em coleção ordenada; CArrayObj devolve índice/-1 e CList ponteiro/NULL. Proposta: ordenar no mesmo modo e não interpretar ausência como evento com valor zero.

### REF-1764 — SearchGreat — [REF, CArrayObj, p.PDF 4292–4292]

Busca valor estritamente maior em array ordenado, retornando índice ou -1. Proposta: localizar primeiro candidato após limiar sem relaxar a desigualdade.

### REF-1765 — SearchLess — [REF, CArrayObj, p.PDF 4293–4293]

Busca valor estritamente menor em array ordenado, índice/-1. Proposta: definir claramente limites exclusivos de janelas de eventos.

### REF-1766 — SearchGreatOrEqual — [REF, CArrayObj, p.PDF 4294–4295]

Busca maior ou igual em array ordenado, índice/-1. Proposta: usar inclusão explícita da fronteira temporal ou numérica.

### REF-1767 — SearchLessOrEqual — [REF, CArrayObj, p.PDF 4296–4296]

Busca menor ou igual em array ordenado, índice/-1. Proposta: separar janela inclusiva da busca estrita.

### REF-1768 — SearchFirst — [REF, CArrayObj, p.PDF 4297–4297]

Busca primeira ocorrência igual no array ordenado, índice/-1. Proposta: identificar início de grupo de eventos com chave repetida.

### REF-1769 — SearchLast — [REF, CArrayObj, p.PDF 4298–4298]

Busca última ocorrência igual no array ordenado, índice/-1. Proposta: identificar fim do grupo e conferir duplicatas sem perder ordem.

### REF-1770 — Save — [REF, CArrayObj, p.PDF 4299–4299]

Serializa para handle binário aberto e retorna bool. Proposta: exigir fechamento e confirmação da escrita; exemplos CArrayObj/CList usam teste !=NULL na criação, aparente inversão que não deve ser copiada.

### REF-1771 — Load — [REF, CArrayObj, p.PDF 4300–4301]

Lê de handle binário aberto e usa fábrica de elementos; a base de CArrayObj/CList não cria objetos concretos. Proposta: validar formato/versão e só promover snapshot após sucesso completo; exemplos contêm teste de criação invertido.

### REF-1772 — Type — [REF, CArrayObj, p.PDF 4302–4302]

Identifica tipo da biblioteca (CArrayObj 7778, CList 7779); não representa versão de dados. Proposta: manter versão do esquema de evidências separada deste identificador.

### REF-1773 — CList — [REF, CList, p.PDF 4303–4335]

Lista dinâmica de CObject, navegação por cursor, ordenação e persistência; compartilha riscos de FreeMode. Proposta Stoikus: fila/histórico com limites explícitos e sem ponteiros emprestados após descarte.

### REF-1774 — FreeMode — [REF, CList, p.PDF 4305–4305]

Consulta ou define quem libera objetos dinâmicos; padrão ativo. Em Stoikus, uma coleção proprietária deve ser a única responsável por delete; referências emprestadas não podem sobreviver à remoção.

### REF-1775 — FreeMode — [REF, CList, p.PDF 4306–4307]

Consulta ou define quem libera objetos dinâmicos; padrão ativo. Em Stoikus, uma coleção proprietária deve ser a única responsável por delete; referências emprestadas não podem sobreviver à remoção.

### REF-1776 — Total — [REF, CList, p.PDF 4308–4308]

Retorna quantidade de nós da lista. Proposta: usar para limites de iteração e telemetria, sem confundir com capacidade reservada.

### REF-1777 — IsSorted — [REF, CList, p.PDF 4309–4309]

Verifica ordenação no modo informado; Sort define flag e add/insert a reinicializam. Proposta: conferir precondição antes da busca ordenada em eventos.

### REF-1778 — SortMode — [REF, CList, p.PDF 4310–4310]

Retorna modo de ordenação ou -1 se não ordenada. Proposta: preservar modo junto de qualquer algoritmo de busca dependente de ordem.

### REF-1779 — CreateElement — [REF, CList, p.PDF 4311–4311]

É ponto de extensão de fábrica: CArrayObj base sempre retorna false e CList base NULL; carregamento precisa de derivação que crie o tipo concreto. Proposta: reconstruir eventos tipados com fábrica explícita, sem presumir que a base funciona.

### REF-1780 — Add — [REF, CList, p.PDF 4312–4312]

Adiciona item; CArrayObj retorna bool e rejeita ponteiro inválido; CList retorna índice ou -1; genéricas retornam bool. Proposta: comparar o retorno correto, pois índice zero válido não é false de falha.

### REF-1781 — Insert — [REF, CList, p.PDF 4313–4314]

Insere na posição indicada (ou nó na árvore). CObject inválido é rejeitado; CList retorna índice/-1, CArrayObj bool, CTree ponteiro do proprietário/NULL. Proposta: adaptar tratamento por contrato, sem reutilizar um teste booleano genérico.

### REF-1782 — DetachCurrent — [REF, CList, p.PDF 4315–4315]

Extrai nó corrente sem delete, independentemente de FreeMode. Proposta: transferir o item e definir seu novo responsável por liberação.

### REF-1783 — DeleteCurrent — [REF, CList, p.PDF 4316–4316]

Remove nó corrente e libera se FreeMode ativo. Proposta: salvar avanço/estado do iterador antes de invalidar o nó usado no processamento.

### REF-1784 — Delete — [REF, CList, p.PDF 4317–4317]

Remove e, nos contêineres com FreeMode ativo, libera; na árvore sempre libera e rebalanceia. Proposta: distinguir remoção definitiva de transferência de evidências.

### REF-1785 — Clear — [REF, CList, p.PDF 4318–4318]

Esvazia a coleção; nas coleções de CObject a liberação depende de FreeMode e CArrayObj preserva a memória do array. Proposta: separar reinício da captura de encerramento final.

### REF-1786 — IndexOf — [REF, CList, p.PDF 4319–4319]

Localiza primeira ocorrência ou índice do nó, retornando -1 se ausente. Proposta: testar >=0; exemplo CList testa Add como booleano e pode ignorar o primeiro índice válido.

### REF-1787 — GetNodeAtIndex — [REF, CList, p.PDF 4320–4320]

Obtém ponteiro no índice ou NULL; ponteiro continua pertencendo à lista. Proposta: não deletar referência emprestada.

### REF-1788 — GetFirstNode — [REF, CList, p.PDF 4321–4321]

Obtém primeiro nó ou NULL. Proposta: iniciar varredura sem presumir lista não vazia e sem tomar propriedade do resultado.

### REF-1789 — GetPrevNode — [REF, CList, p.PDF 4322–4322]

Obtém nó anterior ou NULL. Proposta: parar na fronteira e preservar consistência do cursor ao remover itens.

### REF-1790 — GetCurrentNode — [REF, CList, p.PDF 4323–4323]

Obtém nó corrente ou NULL. Proposta: não assumir que há corrente após mutações da lista.

### REF-1791 — GetNextNode — [REF, CList, p.PDF 4324–4324]

Obtém próximo nó ou NULL. Proposta: avançar de forma explícita e evitar referências após descarte.

### REF-1792 — GetLastNode — [REF, CList, p.PDF 4325–4325]

Obtém último nó ou NULL. Proposta: distinguir ordem da lista de tempo real do último evento.

### REF-1793 — Sort — [REF, CList, p.PDF 4326–4326]

CList ordena ascendente pelo modo; CArrayList oferece lista inteira, comparador ou faixa start/count. Proposta: definir desempate determinístico de eventos e repetir o mesmo comparador na busca.

### REF-1794 — MoveToIndex — [REF, CList, p.PDF 4327–4327]

Move o nó corrente para índice e retorna bool. Proposta: não usar posição como chave estável após reorganização.

### REF-1795 — Exchange — [REF, CList, p.PDF 4328–4328]

Troca dois nós e retorna bool. Proposta: validar ambos os ponteiros e atualizar qualquer mapa de posição derivado.

### REF-1796 — CompareList — [REF, CList, p.PDF 4329–4329]

Retorna igualdade entre listas como bool. Proposta: usar como checagem auxiliar; não prova identidade de arquivos nem valida estado de terminal.

### REF-1797 — Search — [REF, CList, p.PDF 4330–4330]

Busca igualdade em coleção ordenada; CArrayObj devolve índice/-1 e CList ponteiro/NULL. Proposta: ordenar no mesmo modo e não interpretar ausência como evento com valor zero.

### REF-1798 — Save — [REF, CList, p.PDF 4331–4332]

Serializa para handle binário aberto e retorna bool. Proposta: exigir fechamento e confirmação da escrita; exemplos CArrayObj/CList usam teste !=NULL na criação, aparente inversão que não deve ser copiada.

### REF-1799 — Load — [REF, CList, p.PDF 4333–4334]

Lê de handle binário aberto e usa fábrica de elementos; a base de CArrayObj/CList não cria objetos concretos. Proposta: validar formato/versão e só promover snapshot após sucesso completo; exemplos contêm teste de criação invertido.

### REF-1800 — Type — [REF, CList, p.PDF 4335–4335]

Identifica tipo da biblioteca (CArrayObj 7778, CList 7779); não representa versão de dados. Proposta: manter versão do esquema de evidências separada deste identificador.

### REF-1801 — CTreeNode — [REF, CTreeNode, p.PDF 4336–4352]

Nó de árvore binária exige derivação de fábrica e Compare; persistência customizada escreve campos e comprimento de string. Exemplo subtrai longs e converte a int, merecendo comparação sem estreitamento. Proposta: ordenar identidade com comparação relacional segura.

### REF-1802 — Owner — [REF, CTreeNode, p.PDF 4341–4341]

Getter/setter do ponteiro proprietário do nó. Proposta: manter relações estruturais sob controle da árvore, evitando ciclos por alteração direta.

### REF-1803 — Left — [REF, CTreeNode, p.PDF 4342–4342]

Getter/setter do filho esquerdo. Proposta: mutação manual exige preservar invariantes e vida dos nós; preferir operações do contêiner.

### REF-1804 — Right — [REF, CTreeNode, p.PDF 4343–4343]

Getter/setter do filho direito. Proposta: não alterar links durante busca sem reconstrução consistente da árvore.

### REF-1805 — Balance — [REF, CTreeNode, p.PDF 4344–4344]

Lê balanço do nó. Proposta: observação estrutural para diagnóstico, sem inferir desempenho medido.

### REF-1806 — BalanceL — [REF, CTreeNode, p.PDF 4345–4345]

Lê balanço da subárvore esquerda. Proposta: diagnóstico da estrutura, sem substituir rebalanceamento do contêiner.

### REF-1807 — BalanceR — [REF, CTreeNode, p.PDF 4346–4346]

Lê balanço da subárvore direita. Proposta: diagnóstico simétrico e preservação da ordenação de chaves.

### REF-1808 — CreateSample — [REF, CTreeNode, p.PDF 4347–4347]

Fábrica virtual de novo nó ou NULL. Proposta: criar o subtipo correto para busca/persistência, tratando falha de alocação.

### REF-1809 — RefreshBalance — [REF, CTreeNode, p.PDF 4348–4348]

Recalcula e retorna balanço. Proposta: não presumir que recalcular metadado substitui operação de rebalanceamento.

### REF-1810 — GetNext — [REF, CTreeNode, p.PDF 4349–4349]

Retorna próximo nó a partir de um nó informado. Proposta: checar término e não manter ponteiro após Delete/Clear.

### REF-1811 — SaveNode — [REF, CTreeNode, p.PDF 4350–4350]

Grava nó em handle binário aberto, bool de sucesso. Proposta: registrar falha de escrita do nó e não publicar arquivo parcial como snapshot válido.

### REF-1812 — LoadNode — [REF, CTreeNode, p.PDF 4351–4351]

Lê nó em handle aberto para nó principal informado, bool de sucesso. Proposta: validar reconstrução antes de substituir árvore ativa.

### REF-1813 — Type — [REF, CTreeNode, p.PDF 4352–4352]

Identifica tipo da biblioteca (CArrayObj 7778, CList 7779); não representa versão de dados. Proposta: manter versão do esquema de evidências separada deste identificador.

### REF-1814 — CTree — [REF, CTree, p.PDF 4353–4368]

Árvore binária de CTreeNode: ao contrário da lista/array não oferece FreeMode; Delete/Clear liberam nós, Detach preserva e rebalanceia. Proposta: usar transferência explícita para índices de evidência e não copiar exemplos sem validar retornos.

### REF-1815 — Root — [REF, CTree, p.PDF 4359–4359]

Retorna raiz da árvore. Proposta: raiz é ponto estrutural, não registro cronologicamente primeiro.

### REF-1816 — CreateElement — [REF, CTree, p.PDF 4360–4360]

É ponto de extensão de fábrica: CArrayObj base sempre retorna false e CList base NULL; carregamento precisa de derivação que crie o tipo concreto. Proposta: reconstruir eventos tipados com fábrica explícita, sem presumir que a base funciona.

### REF-1817 — Insert — [REF, CTree, p.PDF 4361–4361]

Insere na posição indicada (ou nó na árvore). CObject inválido é rejeitado; CList retorna índice/-1, CArrayObj bool, CTree ponteiro do proprietário/NULL. Proposta: adaptar tratamento por contrato, sem reutilizar um teste booleano genérico.

### REF-1818 — Detach — [REF, CTree, p.PDF 4362–4362]

Desvincula sem liberar o objeto; no CTree também rebalanceia. Proposta: transferência explícita entre coleções, com liberação posterior garantida pelo novo proprietário.

### REF-1819 — Delete — [REF, CTree, p.PDF 4363–4363]

Remove e, nos contêineres com FreeMode ativo, libera; na árvore sempre libera e rebalanceia. Proposta: distinguir remoção definitiva de transferência de evidências.

### REF-1820 — Clear — [REF, CTree, p.PDF 4364–4364]

Esvazia a coleção; nas coleções de CObject a liberação depende de FreeMode e CArrayObj preserva a memória do array. Proposta: separar reinício da captura de encerramento final.

### REF-1821 — Find — [REF, CTree, p.PDF 4365–4365]

Busca nó por amostra e retorna ponteiro/NULL. Proposta: comparador da chave deve ser consistente; liberar amostra temporária após a busca.

### REF-1822 — Save — [REF, CTree, p.PDF 4366–4366]

Serializa para handle binário aberto e retorna bool. Proposta: exigir fechamento e confirmação da escrita; exemplos CArrayObj/CList usam teste !=NULL na criação, aparente inversão que não deve ser copiada.

### REF-1823 — Load — [REF, CTree, p.PDF 4367–4367]

Lê de handle binário aberto e usa fábrica de elementos; a base de CArrayObj/CList não cria objetos concretos. Proposta: validar formato/versão e só promover snapshot após sucesso completo; exemplos contêm teste de criação invertido.

### REF-1824 — Type — [REF, CTree, p.PDF 4368–4368]

Identifica tipo da biblioteca (CArrayObj 7778, CList 7779); não representa versão de dados. Proposta: manter versão do esquema de evidências separada deste identificador.

### REF-1825 — Generic Data Collections — [REF, CTree, p.PDF 4369–4490]

Contêiner hierárquico: este registro cobre somente o cruzamento p.4369–4490 por meio dos filhos abaixo; não afirma leitura integral da seção maior. Proposta Stoikus: escolher estrutura pelo contrato de propriedade, ordem e identidade, sem inferir uso atual no produto.

### REF-1826 — ICollection<T> — [REF, ICollection<T>, p.PDF 4371–4377]

Interface tipada de Add, Count, Contains, CopyTo, Clear e Remove. Proposta Stoikus: contrato comum de armazenamento sem supor ordem, unicidade ou política de memória de uma implementação específica.

### REF-1827 — Add — [REF, ICollection<T>, p.PDF 4372–4372]

Adiciona item; CArrayObj retorna bool e rejeita ponteiro inválido; CList retorna índice ou -1; genéricas retornam bool. Proposta: comparar o retorno correto, pois índice zero válido não é false de falha.

### REF-1828 — Count — [REF, ICollection<T>, p.PDF 4373–4373]

Retorna número de elementos, distinto de capacidade. Proposta: conferir contagem exportada contra número copiado no snapshot.

### REF-1829 — Contains — [REF, ICollection<T>, p.PDF 4374–4374]

Consulta presença por valor; em mapas a sobrecarga documentada verifica chave e valor. Proposta: separar presença da chave de igualdade do conteúdo ao reconciliar snapshots.

### REF-1830 — CopyTo — [REF, ICollection<T>, p.PDF 4375–4375]

Copia para array a partir de dst_start e retorna quantidade copiada; mapas permitem pares ou arrays paralelos chave/valor. Proposta: verificar quantidade e associação antes de serializar evidências.

### REF-1831 — Clear — [REF, ICollection<T>, p.PDF 4376–4376]

Esvazia a coleção; nas coleções de CObject a liberação depende de FreeMode e CArrayObj preserva a memória do array. Proposta: separar reinício da captura de encerramento final.

### REF-1832 — Remove — [REF, ICollection<T>, p.PDF 4377–4377]

Remove ocorrência/valor ou par pela chave conforme contêiner, bool de sucesso. Proposta: ausência não deve ser confundida com remoção confirmada.

### REF-1833 — IEqualityComparable<T> — [REF, IEqualityComparable<T>, p.PDF 4378–4380]

Objeto define igualdade e hash próprio. Proposta: identidade de evento coerente entre Equals e HashCode, separada de conteúdo e hash criptográfico.

### REF-1834 — Equals — [REF, IEqualityComparable<T>, p.PDF 4379–4379]

Compara igualdade; nos pares CKeyValuePair usa somente chaves. Proposta: validar conteúdo do valor separadamente ao comparar duas evidências com mesma identidade.

### REF-1835 — HashCode — [REF, IEqualityComparable<T>, p.PDF 4380–4380]

Calcula hash inteiro para organização de coleções; CKeyValuePair usa hash da chave. Proposta: não confundir com SHA-256 do arquivo ou prova criptográfica.

### REF-1836 — IComparable<T> — [REF, IComparable<T>, p.PDF 4381–4382]

Acrescenta ordem a igualdade/hash; Compare negativo, zero ou positivo. Proposta: ordem determinística de registros com desempate explícito.

### REF-1837 — Compare — [REF, IComparable<T>, p.PDF 4382–4382]

Retorna negativo/zero/positivo; em CKeyValuePair compara chaves. Proposta: comparador determinístico com campos e desempates explícitos; igualdade de chave não prova igualdade de conteúdo.

### REF-1838 — IComparer<T> — [REF, IComparer<T>, p.PDF 4383–4384]

Comparador externo de dois valores T. Proposta: separar ordenação por horário de identidade por ticket, usando o mesmo comparador na busca.

### REF-1839 — Compare — [REF, IComparer<T>, p.PDF 4384–4384]

Retorna negativo/zero/positivo; em CKeyValuePair compara chaves. Proposta: comparador determinístico com campos e desempates explícitos; igualdade de chave não prova igualdade de conteúdo.

### REF-1840 — IEqualityComparer<T> — [REF, IEqualityComparer<T>, p.PDF 4385–4387]

Comparador externo de igualdade/hash. Proposta: deduplicação por chave estável, sem tolerância numérica improvisada em identidade.

### REF-1841 — Equals — [REF, IEqualityComparer<T>, p.PDF 4386–4386]

Compara igualdade; nos pares CKeyValuePair usa somente chaves. Proposta: validar conteúdo do valor separadamente ao comparar duas evidências com mesma identidade.

### REF-1842 — HashCode — [REF, IEqualityComparer<T>, p.PDF 4387–4387]

Calcula hash inteiro para organização de coleções; CKeyValuePair usa hash da chave. Proposta: não confundir com SHA-256 do arquivo ou prova criptográfica.

### REF-1843 — IList<T> — [REF, IList<T>, p.PDF 4388–4394]

Interface de lista com acesso bool por índice e busca first/last retornando -1. Proposta: distinguir ausência de valor padrão e não persistir índice como identificador.

### REF-1844 — TryGetValue — [REF, IList<T>, p.PDF 4389–4389]

Obtém valor por índice nas listas ou chave nos mapas e escreve por referência apenas sob contrato de sucesso bool. Proposta: testar retorno antes de usar saída e não converter ausência em zero.

### REF-1845 — TrySetValue — [REF, IList<T>, p.PDF 4390–4390]

Altera valor em índice/chave e retorna bool. Proposta: não presumir inserção automática nem aceitar falha silenciosa de atualização.

### REF-1846 — Insert — [REF, IList<T>, p.PDF 4391–4391]

Insere na posição indicada (ou nó na árvore). CObject inválido é rejeitado; CList retorna índice/-1, CArrayObj bool, CTree ponteiro do proprietário/NULL. Proposta: adaptar tratamento por contrato, sem reutilizar um teste booleano genérico.

### REF-1847 — IndexOf — [REF, IList<T>, p.PDF 4392–4392]

Localiza primeira ocorrência ou índice do nó, retornando -1 se ausente. Proposta: testar >=0; exemplo CList testa Add como booleano e pode ignorar o primeiro índice válido.

### REF-1848 — LastIndexOf — [REF, IList<T>, p.PDF 4393–4393]

Busca última ocorrência, admite faixa na CArrayList e retorna -1 se ausente. Proposta: delimitar duplicatas e validar start/count.

### REF-1849 — RemoveAt — [REF, IList<T>, p.PDF 4394–4394]

Remove pelo índice e retorna bool. Proposta: índices posteriores podem mudar; não são identidade permanente.

### REF-1850 — IMap<TKey,TValue> — [REF, IMap<TKey,TValue>, p.PDF 4395–4401]

Contrato tipado chave/valor com acesso bool e cópia para arrays paralelos. Proposta: índice de eventos por identidade; não confundir Contains(key,value) com ContainsKey.

### REF-1851 — Add — [REF, IMap<TKey,TValue>, p.PDF 4396–4396]

Adiciona item; CArrayObj retorna bool e rejeita ponteiro inválido; CList retorna índice ou -1; genéricas retornam bool. Proposta: comparar o retorno correto, pois índice zero válido não é false de falha.

### REF-1852 — Contains — [REF, IMap<TKey,TValue>, p.PDF 4397–4397]

Consulta presença por valor; em mapas a sobrecarga documentada verifica chave e valor. Proposta: separar presença da chave de igualdade do conteúdo ao reconciliar snapshots.

### REF-1853 — Remove — [REF, IMap<TKey,TValue>, p.PDF 4398–4398]

Remove ocorrência/valor ou par pela chave conforme contêiner, bool de sucesso. Proposta: ausência não deve ser confundida com remoção confirmada.

### REF-1854 — TryGetValue — [REF, IMap<TKey,TValue>, p.PDF 4399–4399]

Obtém valor por índice nas listas ou chave nos mapas e escreve por referência apenas sob contrato de sucesso bool. Proposta: testar retorno antes de usar saída e não converter ausência em zero.

### REF-1855 — TrySetValue — [REF, IMap<TKey,TValue>, p.PDF 4400–4400]

Altera valor em índice/chave e retorna bool. Proposta: não presumir inserção automática nem aceitar falha silenciosa de atualização.

### REF-1856 — CopyTo — [REF, IMap<TKey,TValue>, p.PDF 4401–4401]

Copia para array a partir de dst_start e retorna quantidade copiada; mapas permitem pares ou arrays paralelos chave/valor. Proposta: verificar quantidade e associação antes de serializar evidências.

### REF-1857 — ISet<T> — [REF, ISet<T>, p.PDF 4402–4413]

Interface de conjuntos com operações que modificam o conjunto atual e predicados de inclusão. Proposta: reconciliar universos de eventos sobre cópias para preservar capturas originais.

### REF-1858 — ExceptWith — [REF, ISet<T>, p.PDF 4404–4404]

Diferença A menos B, modifica coleção atual e aceita coleção ou array. Proposta: calcular eventos retirados sobre cópia quando o snapshot original precisar permanecer auditável.

### REF-1859 — IntersectWith — [REF, ISet<T>, p.PDF 4405–4405]

Interseção, conserva no conjunto atual apenas elementos também presentes no outro. Proposta: reconciliar identidades comuns sobre cópia.

### REF-1860 — SymmetricExceptWith — [REF, ISet<T>, p.PDF 4406–4406]

Diferença simétrica, mantém itens presentes em apenas um dos conjuntos e modifica atual. Proposta: detectar divergências entre capturas sem determinar sozinho a causa.

### REF-1861 — UnionWith — [REF, ISet<T>, p.PDF 4407–4407]

União adiciona elementos ausentes ao conjunto atual. Proposta: consolidar identidades sem duplicatas, mantendo metadados de origem fora do conjunto.

### REF-1862 — IsProperSubsetOf — [REF, ISet<T>, p.PDF 4408–4408]

Testa subconjunto próprio, excluindo igualdade. Proposta: distinguir cobertura estritamente menor de conjunto equivalente.

### REF-1863 — IsProperSupersetOf — [REF, ISet<T>, p.PDF 4409–4409]

Testa superconjunto próprio, excluindo igualdade. Proposta: detectar expansão real das identidades observadas.

### REF-1864 — IsSubsetOf — [REF, ISet<T>, p.PDF 4410–4410]

Testa inclusão não estrita e aceita igualdade. Proposta: conferir se eventos observados pertencem ao universo esperado, sem provar completude.

### REF-1865 — IsSupersetOf — [REF, ISet<T>, p.PDF 4411–4411]

Testa superconjunto não estrito. Proposta: verificar cobertura das identidades esperadas sem inferir ordem ou multiplicidade.

### REF-1866 — Overlaps — [REF, ISet<T>, p.PDF 4412–4412]

Testa existência de interseção. Proposta: detectar identidades compartilhadas sem concluir igualdade de conjuntos.

### REF-1867 — SetEquals — [REF, ISet<T>, p.PDF 4413–4413]

Descrição diz conter todos os itens; nome sugere igualdade de conjunto. Proposta: testar conjuntos com extras, repetidos e vazios antes de confiar como prova de igualdade; a formulação textual é insuficiente.

### REF-1868 — CDefaultComparer<T> — [REF, CDefaultComparer<T>, p.PDF 4414–4415]

Implementa comparação usando overload global Compare conforme T. Proposta: conferir se ordem padrão corresponde à chave requerida antes de ordenar evidências.

### REF-1869 — Compare — [REF, CDefaultComparer<T>, p.PDF 4415–4415]

Retorna negativo/zero/positivo; em CKeyValuePair compara chaves. Proposta: comparador determinístico com campos e desempates explícitos; igualdade de chave não prova igualdade de conteúdo.

### REF-1870 — CDefaultEqualityComparer<T> — [REF, CDefaultEqualityComparer<T>, p.PDF 4416–4418]

Usa Equals e GetHashCode globais. Proposta: customizar quando a identidade de negócio não coincide com igualdade padrão do tipo.

### REF-1871 — Equals — [REF, CDefaultEqualityComparer<T>, p.PDF 4417–4417]

Compara igualdade; nos pares CKeyValuePair usa somente chaves. Proposta: validar conteúdo do valor separadamente ao comparar duas evidências com mesma identidade.

### REF-1872 — HashCode — [REF, CDefaultEqualityComparer<T>, p.PDF 4418–4418]

Calcula hash inteiro para organização de coleções; CKeyValuePair usa hash da chave. Proposta: não confundir com SHA-256 do arquivo ou prova criptográfica.

### REF-1873 — CRedBlackTreeNode<T> — [REF, CRedBlackTreeNode<T>, p.PDF 4419–4426]

Nó genérico com valor, pai, filhos e cor; fábrica vazia cria nó preto. Proposta: detalhe interno de coleção, sem necessidade de expor no fluxo do monitor.

### REF-1874 — Value — [REF, CRedBlackTreeNode<T>, p.PDF 4420–4420]

Getter/setter do valor de nó ou par. Proposta: separar identidade estável de conteúdo mutável e registrar atualizações.

### REF-1875 — Parent — [REF, CRedBlackTreeNode<T>, p.PDF 4421–4421]

Getter/setter do pai na árvore rubro-negra. Proposta: não relincar nós de evidência manualmente sem preservar invariantes.

### REF-1876 — Left — [REF, CRedBlackTreeNode<T>, p.PDF 4422–4422]

Getter/setter do filho esquerdo. Proposta: mutação manual exige preservar invariantes e vida dos nós; preferir operações do contêiner.

### REF-1877 — Right — [REF, CRedBlackTreeNode<T>, p.PDF 4423–4423]

Getter/setter do filho direito. Proposta: não alterar links durante busca sem reconstrução consistente da árvore.

### REF-1878 — Color — [REF, CRedBlackTreeNode<T>, p.PDF 4424–4424]

Getter/setter da cor RED_BLACK_TREE_NODE_RED/BLACK. Proposta: detalhe estrutural da árvore, sem significado financeiro.

### REF-1879 — IsLeaf — [REF, CRedBlackTreeNode<T>, p.PDF 4425–4425]

Testa se nó é folha. Proposta: tratar como propriedade de navegação, não como ausência de eventos futuros.

### REF-1880 — CreateEmptyNode — [REF, CRedBlackTreeNode<T>, p.PDF 4426–4426]

Fábrica estática de nó preto sem pai nem filhos. Proposta: conferir alocação e não presumir que nó vazio seja evidência válida.

### REF-1881 — CLinkedListNode<T> — [REF, CLinkedListNode<T>, p.PDF 4427–4431]

Nó duplamente ligado com dono, próximo, anterior e valor; descrição repete nome do nó no lugar da lista. Proposta: tratar links como internos e verificar header para implementação futura.

### REF-1882 — List — [REF, CLinkedListNode<T>, p.PDF 4428–4428]

Getter/setter do ponteiro à lista dona de nó duplamente ligado. Proposta: manter dono e links consistentes em qualquer transferência.

### REF-1883 — Next — [REF, CLinkedListNode<T>, p.PDF 4429–4429]

Getter/setter do próximo nó. Proposta: evitar links pendentes e ciclos em navegação de eventos.

### REF-1884 — Previous — [REF, CLinkedListNode<T>, p.PDF 4430–4430]

Getter/setter do nó anterior. Proposta: manter simetria com Next e não desreferenciar nó removido.

### REF-1885 — Value — [REF, CLinkedListNode<T>, p.PDF 4431–4431]

Getter/setter do valor de nó ou par. Proposta: separar identidade estável de conteúdo mutável e registrar atualizações.

### REF-1886 — CKeyValuePair<TKey,TValue> — [REF, CKeyValuePair<TKey,TValue>, p.PDF 4432–4438]

Par tipado implementa IComparable; Compare e Equals usam chave, HashCode é hash da chave. Proposta: comparação de conteúdo exige valor adicional e Clone não comprova cópia profunda.

### REF-1887 — Key — [REF, CKeyValuePair<TKey,TValue>, p.PDF 4433–4433]

Getter/setter da chave do par. Proposta: não mudar chave de objeto já indexado sem remoção/reinserção, para preservar busca por identidade.

### REF-1888 — Value — [REF, CKeyValuePair<TKey,TValue>, p.PDF 4434–4434]

Getter/setter do valor de nó ou par. Proposta: separar identidade estável de conteúdo mutável e registrar atualizações.

### REF-1889 — Clone — [REF, CKeyValuePair<TKey,TValue>, p.PDF 4435–4435]

Cria novo par com chave e valor iguais; assinatura extraída está incompleta (TValue>*). Proposta: conferir header nativo antes de escrever exemplo; não inferir cópia profunda de objetos referenciados.

### REF-1890 — Compare — [REF, CKeyValuePair<TKey,TValue>, p.PDF 4436–4436]

Retorna negativo/zero/positivo; em CKeyValuePair compara chaves. Proposta: comparador determinístico com campos e desempates explícitos; igualdade de chave não prova igualdade de conteúdo.

### REF-1891 — Equals — [REF, CKeyValuePair<TKey,TValue>, p.PDF 4437–4437]

Compara igualdade; nos pares CKeyValuePair usa somente chaves. Proposta: validar conteúdo do valor separadamente ao comparar duas evidências com mesma identidade.

### REF-1892 — HashCode — [REF, CKeyValuePair<TKey,TValue>, p.PDF 4438–4438]

Calcula hash inteiro para organização de coleções; CKeyValuePair usa hash da chave. Proposta: não confundir com SHA-256 do arquivo ou prova criptográfica.

### REF-1893 — CArrayList<T> — [REF, CArrayList<T>, p.PDF 4439–4460]

Lista dinâmica tipada, capacidade separada de contagem, operações por faixa e comparador. Proposta: snapshot ordenável de eventos sem migrar produto nesta pesquisa.

### REF-1894 — Capacity — [REF, CArrayList<T>, p.PDF 4441–4441]

Consulta/define capacidade, distinta da contagem. Proposta: dimensionar lote previsto sem interpretar memória reservada como registros existentes.

### REF-1895 — Count — [REF, CArrayList<T>, p.PDF 4442–4442]

Retorna número de elementos, distinto de capacidade. Proposta: conferir contagem exportada contra número copiado no snapshot.

### REF-1896 — Contains — [REF, CArrayList<T>, p.PDF 4443–4443]

Consulta presença por valor; em mapas a sobrecarga documentada verifica chave e valor. Proposta: separar presença da chave de igualdade do conteúdo ao reconciliar snapshots.

### REF-1897 — TrimExcess — [REF, CArrayList<T>, p.PDF 4444–4444]

Ajusta capacidade à contagem e libera memória não usada. Proposta: executar fora de caminho frequente de eventos e medir custo antes de otimizar.

### REF-1898 — TryGetValue — [REF, CArrayList<T>, p.PDF 4445–4445]

Obtém valor por índice nas listas ou chave nos mapas e escreve por referência apenas sob contrato de sucesso bool. Proposta: testar retorno antes de usar saída e não converter ausência em zero.

### REF-1899 — TrySetValue — [REF, CArrayList<T>, p.PDF 4446–4446]

Altera valor em índice/chave e retorna bool. Proposta: não presumir inserção automática nem aceitar falha silenciosa de atualização.

### REF-1900 — Add — [REF, CArrayList<T>, p.PDF 4447–4447]

Adiciona item; CArrayObj retorna bool e rejeita ponteiro inválido; CList retorna índice ou -1; genéricas retornam bool. Proposta: comparar o retorno correto, pois índice zero válido não é false de falha.

### REF-1901 — AddRange — [REF, CArrayList<T>, p.PDF 4448–4448]

Adiciona array ou ICollection tipada e retorna bool. Proposta: importar lote com validação prévia e conferir sucesso.

### REF-1902 — Insert — [REF, CArrayList<T>, p.PDF 4449–4449]

Insere na posição indicada (ou nó na árvore). CObject inválido é rejeitado; CList retorna índice/-1, CArrayObj bool, CTree ponteiro do proprietário/NULL. Proposta: adaptar tratamento por contrato, sem reutilizar um teste booleano genérico.

### REF-1903 — InsertRange — [REF, CArrayList<T>, p.PDF 4450–4450]

Insere array ou coleção em índice e retorna bool. Proposta: validar posição e manter sequência de captura explícita.

### REF-1904 — CopyTo — [REF, CArrayList<T>, p.PDF 4451–4451]

Copia para array a partir de dst_start e retorna quantidade copiada; mapas permitem pares ou arrays paralelos chave/valor. Proposta: verificar quantidade e associação antes de serializar evidências.

### REF-1905 — BinarySearch — [REF, CArrayList<T>, p.PDF 4452–4452]

Exige lista ascendente; aceita faixa/comparador. Se ausente, texto diz retornar índice do menor elemento mais próximo, não -1. Proposta: conferir igualdade do item encontrado e testar fronteiras antes de usar como existência exata.

### REF-1906 — IndexOf — [REF, CArrayList<T>, p.PDF 4453–4453]

Localiza primeira ocorrência ou índice do nó, retornando -1 se ausente. Proposta: testar >=0; exemplo CList testa Add como booleano e pode ignorar o primeiro índice válido.

### REF-1907 — LastIndexOf — [REF, CArrayList<T>, p.PDF 4454–4454]

Busca última ocorrência, admite faixa na CArrayList e retorna -1 se ausente. Proposta: delimitar duplicatas e validar start/count.

### REF-1908 — Clear — [REF, CArrayList<T>, p.PDF 4455–4455]

Esvazia a coleção; nas coleções de CObject a liberação depende de FreeMode e CArrayObj preserva a memória do array. Proposta: separar reinício da captura de encerramento final.

### REF-1909 — Remove — [REF, CArrayList<T>, p.PDF 4456–4456]

Remove ocorrência/valor ou par pela chave conforme contêiner, bool de sucesso. Proposta: ausência não deve ser confundida com remoção confirmada.

### REF-1910 — RemoveAt — [REF, CArrayList<T>, p.PDF 4457–4457]

Remove pelo índice e retorna bool. Proposta: índices posteriores podem mudar; não são identidade permanente.

### REF-1911 — RemoveRange — [REF, CArrayList<T>, p.PDF 4458–4458]

Remove faixa start_index/count, diferentemente de DeleteRange(from,to). Proposta: não reutilizar limites inclusivos no lugar de contagem.

### REF-1912 — Reverse — [REF, CArrayList<T>, p.PDF 4459–4459]

Inverte lista inteira ou faixa start/count, bool de sucesso. Proposta: inversão de apresentação não pode redefinir ordem original de captura.

### REF-1913 — Sort — [REF, CArrayList<T>, p.PDF 4460–4460]

CList ordena ascendente pelo modo; CArrayList oferece lista inteira, comparador ou faixa start/count. Proposta: definir desempate determinístico de eventos e repetir o mesmo comparador na busca.

### REF-1914 — CHashMap<TKey,TValue> — [REF, CHashMap<TKey,TValue>, p.PDF 4461–4473]

Tabela hash dinâmica de pares não ordenados com chaves únicas. Proposta: índice por identidade; ordenar exportação separadamente para reprodutibilidade.

### REF-1915 — Add — [REF, CHashMap<TKey,TValue>, p.PDF 4463–4463]

Adiciona item; CArrayObj retorna bool e rejeita ponteiro inválido; CList retorna índice ou -1; genéricas retornam bool. Proposta: comparar o retorno correto, pois índice zero válido não é false de falha.

### REF-1916 — Count — [REF, CHashMap<TKey,TValue>, p.PDF 4464–4464]

Retorna número de elementos, distinto de capacidade. Proposta: conferir contagem exportada contra número copiado no snapshot.

### REF-1917 — Comparer — [REF, CHashMap<TKey,TValue>, p.PDF 4465–4465]

Retorna ponteiro ao comparador de igualdade usado no hash. Proposta: manter igualdade/hash coerentes com a identidade do evento.

### REF-1918 — Contains — [REF, CHashMap<TKey,TValue>, p.PDF 4466–4466]

Consulta presença por valor; em mapas a sobrecarga documentada verifica chave e valor. Proposta: separar presença da chave de igualdade do conteúdo ao reconciliar snapshots.

### REF-1919 — ContainsKey — [REF, CHashMap<TKey,TValue>, p.PDF 4467–4467]

Testa somente presença da chave. Proposta: útil na deduplicação; valor precisa de verificação separada.

### REF-1920 — ContainsValue — [REF, CHashMap<TKey,TValue>, p.PDF 4468–4468]

Testa presença do valor em algum par. Proposta: não usar para identificar unicamente um evento sem conhecer sua chave.

### REF-1921 — CopyTo — [REF, CHashMap<TKey,TValue>, p.PDF 4469–4469]

Copia para array a partir de dst_start e retorna quantidade copiada; mapas permitem pares ou arrays paralelos chave/valor. Proposta: verificar quantidade e associação antes de serializar evidências.

### REF-1922 — Clear — [REF, CHashMap<TKey,TValue>, p.PDF 4470–4470]

Esvazia a coleção; nas coleções de CObject a liberação depende de FreeMode e CArrayObj preserva a memória do array. Proposta: separar reinício da captura de encerramento final.

### REF-1923 — Remove — [REF, CHashMap<TKey,TValue>, p.PDF 4471–4471]

Remove ocorrência/valor ou par pela chave conforme contêiner, bool de sucesso. Proposta: ausência não deve ser confundida com remoção confirmada.

### REF-1924 — TryGetValue — [REF, CHashMap<TKey,TValue>, p.PDF 4472–4472]

Obtém valor por índice nas listas ou chave nos mapas e escreve por referência apenas sob contrato de sucesso bool. Proposta: testar retorno antes de usar saída e não converter ausência em zero.

### REF-1925 — TrySetValue — [REF, CHashMap<TKey,TValue>, p.PDF 4473–4473]

Altera valor em índice/chave e retorna bool. Proposta: não presumir inserção automática nem aceitar falha silenciosa de atualização.

### REF-1926 — CHashSet<T> — [REF, CHashSet<T>, p.PDF 4474–4490]

Conjunto hash dinâmico não ordenado com valores únicos; leitura deste registro só até p.4490, não até fim4493. Proposta: deduplicar identidades, não usar para contar multiplicidade nem reconstruir cronologia.

### REF-1927 — Add — [REF, CHashSet<T>, p.PDF 4476–4476]

Adiciona item; CArrayObj retorna bool e rejeita ponteiro inválido; CList retorna índice ou -1; genéricas retornam bool. Proposta: comparar o retorno correto, pois índice zero válido não é false de falha.

### REF-1928 — Count — [REF, CHashSet<T>, p.PDF 4477–4477]

Retorna número de elementos, distinto de capacidade. Proposta: conferir contagem exportada contra número copiado no snapshot.

### REF-1929 — Contains — [REF, CHashSet<T>, p.PDF 4478–4478]

Consulta presença por valor; em mapas a sobrecarga documentada verifica chave e valor. Proposta: separar presença da chave de igualdade do conteúdo ao reconciliar snapshots.

### REF-1930 — Comparer — [REF, CHashSet<T>, p.PDF 4479–4479]

Retorna ponteiro ao comparador de igualdade usado no hash. Proposta: manter igualdade/hash coerentes com a identidade do evento.

### REF-1931 — TrimExcess — [REF, CHashSet<T>, p.PDF 4480–4480]

Ajusta capacidade à contagem e libera memória não usada. Proposta: executar fora de caminho frequente de eventos e medir custo antes de otimizar.

### REF-1932 — CopyTo — [REF, CHashSet<T>, p.PDF 4481–4481]

Copia para array a partir de dst_start e retorna quantidade copiada; mapas permitem pares ou arrays paralelos chave/valor. Proposta: verificar quantidade e associação antes de serializar evidências.

### REF-1933 — Clear — [REF, CHashSet<T>, p.PDF 4482–4482]

Esvazia a coleção; nas coleções de CObject a liberação depende de FreeMode e CArrayObj preserva a memória do array. Proposta: separar reinício da captura de encerramento final.

### REF-1934 — Remove — [REF, CHashSet<T>, p.PDF 4483–4483]

Remove ocorrência/valor ou par pela chave conforme contêiner, bool de sucesso. Proposta: ausência não deve ser confundida com remoção confirmada.

### REF-1935 — ExceptWith — [REF, CHashSet<T>, p.PDF 4484–4484]

Diferença A menos B, modifica coleção atual e aceita coleção ou array. Proposta: calcular eventos retirados sobre cópia quando o snapshot original precisar permanecer auditável.

### REF-1936 — IntersectWith — [REF, CHashSet<T>, p.PDF 4485–4485]

Interseção, conserva no conjunto atual apenas elementos também presentes no outro. Proposta: reconciliar identidades comuns sobre cópia.

### REF-1937 — SymmetricExceptWith — [REF, CHashSet<T>, p.PDF 4486–4486]

Diferença simétrica, mantém itens presentes em apenas um dos conjuntos e modifica atual. Proposta: detectar divergências entre capturas sem determinar sozinho a causa.

### REF-1938 — UnionWith — [REF, CHashSet<T>, p.PDF 4487–4487]

União adiciona elementos ausentes ao conjunto atual. Proposta: consolidar identidades sem duplicatas, mantendo metadados de origem fora do conjunto.

### REF-1939 — IsProperSubsetOf — [REF, CHashSet<T>, p.PDF 4488–4488]

Testa subconjunto próprio, excluindo igualdade. Proposta: distinguir cobertura estritamente menor de conjunto equivalente.

### REF-1940 — IsProperSupersetOf — [REF, CHashSet<T>, p.PDF 4489–4489]

Testa superconjunto próprio, excluindo igualdade. Proposta: detectar expansão real das identidades observadas.

### REF-1941 — IsSubsetOf — [REF, CHashSet<T>, p.PDF 4490–4490]

Testa inclusão não estrita e aceita igualdade. Proposta: conferir se eventos observados pertencem ao universo esperado, sem provar completude.
