# Dante — mascote e guia do JP Wealth

Contrato editorial do candidato de 24/10/2026, conforme [brief aprovado](../work/BRIEF-DANTE-20261024.md) e [mudança de produto](../work/CHG-JPW-DANTE-PRODUCT-20261024.md). Esta referência orienta a representação e o texto do mascote; não concede permissões a agentes nem altera regras financeiras.

Dante é o mascote inspirado no cachorro do proprietário do JP Wealth. Ele acompanha a apresentação dos controles com paciência, curiosidade e cuidado. Sua identidade é distinta de **Dante Alighieri**, retrato histórico que continua no catálogo de avatares. A nova opção se identifica como `dante-mascote`.

## Imagem e origem

O proprietário forneceu a ilustração `IMG_2561.jpg` nesta conversa em 24/10/2026. O original preservado é [dante-original.jpg](../../assets/dante-original.jpg), JPEG de 853×1280 px, 110.066 bytes, SHA-256 `db7b8aa062b9b25a135b1598743d9343c2bda8a0129df320d76c68449eacd2c7`.

A arte de interface é [dante-guide.png](../../assets/dante-guide.png), PNG com canal alfa de 426×640 px, 258.896 bytes, SHA-256 `42269f1a0ad8e40c494de63c71d734d7d205b9d875386f233cf67dfca21110a2`. Foi derivada do original com `image_gen`, operação `background-extraction, identity-preserve`, e normalização técnica `sips -Z640`. O arquivo gerado antes dessa normalização chama-se `exec-646a6351-a5c3-44e8-81d9-1b3d2c2a5b32.png`.

A instrução de extração preserva pose, expressão, pelagem preta e creme, orelhas, óculos, olho castanho à esquerda da imagem e azul à direita, camiseta JP Wealth, tablet, relógio, calça, calçados e cauda. A derivação por geração pode introduzir diferenças; os hashes identificam os bytes, e o aceite visual humano permanece separado. Origem, operação, prompt e hashes estão em [dante-provenance.json](../../assets/dante-provenance.json). O original não deve ser substituído pela derivação.

## Presença no aplicativo

Dante é o avatar visual padrão quando não há foto ou avatar pessoal escolhido. Essa apresentação não cria perfil, nome, identidade ou preferência salva. A escolha pessoal prevalece; remover a foto retorna à apresentação padrão. O mascote acompanha a entrada **Conhecer com Dante** e o guia iniciado por escolha do usuário, sem iniciar navegação na carga do app.

A interface usa imagens locais registradas pelo builder oficial para distribuição e uso offline/portátil. A apresentação cabe nos espaços existentes do avatar e do guia. O runtime não oferece chatbot, síntese de voz, microfone ou mascote flutuante; os balões são texto editorial local.

## Voz editorial

Dante fala em português brasileiro, na primeira pessoa quando se apresenta ou explica sua participação, e convida a explorar com “vamos”. Cada balão tem até duas frases curtas. Ele indica um controle concreto, explica a consequência e deixa a decisão com a pessoa. Humor leve pode acolher, sem infantilizar, pressionar ou interromper uma tarefa.

Exemplos adequados:

- “Oi, eu sou o Dante! Vou mostrar os controles do JP Wealth, um passo de cada vez.”
- “Vamos separar resultado registrado de mês finalizado.”
- “Eu confiro data, fuso, filtros e cobertura antes de interpretar o calendário.”
- “Você pode apenas ler ou salvar uma nota sua necessária pelos controles originais.”

Ao explicar persistência, distingue rascunho, confirmação e resultado desconhecido. Uma lista vazia pode depender de filtros ou ausência de dados; um traço não vira zero. O mascote não anuncia gravação, download concluído ou resolução de pendência sem a evidência correspondente do fluxo original. Não promete retorno, recomenda operação, presume elegibilidade, seleciona conta ou solicita dados fictícios numa base real.

Em vez de transformar instruções extensas em um discurso por prefixo, o catálogo mantém `instruction` como referência e fornece `speech` editado por lição. Configurações e visões de patrimônio compartilham frases curtas deliberadas por família, com diferenças específicas para Checklist, conta local e estorno. Nos percursos de formulário, mês e agenda, Dante explica os campos na ordem da tarefa, a revisão e a decisão de confirmar ou cancelar. Ele distingue a solicitação de gravação da confirmação original e explica recusa, conflito e resultado indeterminado sem presumir sucesso. Âncoras por fala acompanham controles e diálogos previamente delimitados, sem dar ao mascote autoridade para usar os comandos. A [arquitetura do guia](../architecture/LEARNING-GUIDE.md) descreve a jornada, a leitura progressiva e os limites de observação.

## Fronteira desta referência

Este documento governa apenas identidade visual e conteúdo editorial de Dante dentro do escopo aprovado. Não muda norma, cálculo, governança, disponibilidade dos módulos, escritores financeiros, Backup Completo, instruções globais ou autoridade de execução. Uma alteração nesses contratos exige sua própria fonte e autorização.
