# Revisão independente A0 da proposta A1 de leitura visual agrupada

**Veredito:** proposta concreta e tecnicamente plausível para apresentação/contratação N3; **não aprovada para aplicação nem declarada equivalente em browser**. Não encontrei defeito demonstrado no delta, dentro do escopo atual de botões no documento principal. O ganho temporal continua NOT_RUN e pode ser insuficiente para fechar 900 s. Não ampliar limite nem reduzir 413 casos.

## Gargalos demonstrados e limite da localização atual

Conferi o recibo focal: 852,829788s internos/853,471s de processo,685,272s em ações e 167,557s fora dos casos. Matriz original 80=251,142s e compacta 80=159,141s; detalhes completos=66,854s para 120 meses × 2 modos, preservados. Gaps 14,021s e 22,558s incluem cleanup/launch/setup; não permitem nomear uma chamada culpada. Não encontrei sleeps fixos removíveis; a sincronização relevante usa dois RAF.

Na rodada atual, o diretório UI nasceu 18:34:36.526836 UTC e o perfil residual visual-native200 nasceu 18:49:00.932416 UTC (+864,406s), antes do timeout 900,026 s. Os dois blocos legacy/compact usam o mesmo prefixo: esse artefato **não identifica sozinho qual deles executava**, nem a chamada final. Screenshots calendar/notification são capturas normais previstas. O caminho físico scratch também atingiu o teto; isso não prova nem exclui causalidade do filesystem de entrada. Sem inferir causa CloudDocs/I/O, interferência humana, travamento ou falha de produto.

## Equivalência examinada

Fonte `f7a176ab58c048801326d84c626d9c2d4524cd38f01c69971e70d2b5977d8b03`; candidato `8efe7a09583a044d4d15d84c8e6d321365f84e3f3e9f288f732aebd74945d963`. Parse independente confirmou somente `centered` e `controls_geometry` alterados, com todas as assertivas Python AST-idênticas e `CONTENT_GEOMETRY` textual idêntica. As demais funções, incluindo IDs/matrizes/counterproofs/main/gate, permanecem AST-idênticas. Os 679 inputs atuais seguem sem drift.

A contagem SVG vem do mesmo `querySelectorAll('svg')` já presente na geometria; isClose mantém o mesmo matches; clipping mantém o laço/limiares dos mesmos ancestrais. Scroll, ordem, dois RAF e cardinalidade do locator permanecem. O agrupamento fornece um snapshot coerente por controle, em lugar de várias observações separadas. A troca bounding_box→outer conserva as dimensões no documento principal atual; a equivalência **não deve ser estendida a iframe transformado ou superfície futura sem prova**.

`measurement` é uma entrada confiada pelo helper: quem fornece um dicionário antigo/falso poderia evitar nova leitura dentro de `centered`. O chamador novo inspecionado sempre obtém `inspection` do controle real na mesma iteração, sem cache. Essa fronteira precisa continuar delimitada e ser coberta por uma contraprova de snapshot stale/controle errado, não presumida a partir da igualdade de asserts.

## Controles independentes executados sem browser

**18/18 controles em memória concordaram entre funções originais e candidatas**, incluindo texto/SVG deslocados 5 px, conteúdo ausente, Fechar 20 px/sem nome/múltiplos SVG, alvo pequeno, corte por ancestral, zero/múltiplos locators, tabindex positivo e ordem incorreta no footer. Medição fornecida não contornou cardinalidade. O caminho válido manteve scroll+dois RAF e caiu de 8 para 4 chamadas do adaptador por botão; evidência devolvida foi igual.

Esses controles executam as funções Python reais sobre adaptadores sintéticos. **Não executam JS/DOM do navegador e não provam que ambos os métodos obtêm a mesma geometria real.** Os 8.000 roundtrips a menos são contagem estática das 2.000 inspeções, não economia temporal medida. Recibo: `independent-static-and-decision.json` (`fa596f66e8d72a987dba5c9e95330de3ca64238d811c7b8b65667df0d22321c6`). Nenhum gate, browser, sinal real ou fonte do projeto foi alterado pelo revisor.

## Condições A4 antes da aplicação e aceite

[AGENTS.md:81](</Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/AGENTS.md:81>) determina: “preserva A4 para N3” e “Requer CHG dedicado, comparação antes/depois, auditoria independente e aceite humano.” O patch muda como o juiz lê medições; não é a configuração efêmera dos outputs já autorizada. Exige autorização específica e CHG de control plane antes de aplicar.

A aceitação deverá comparar original/candidato em DOM real estável após os mesmos scroll/dois RAF: text/ink/outer/label/svg/isClose/cuts e decisão. Exercitar pelo caminho agrupado positivos, deslocamentos texto/SVG, Fechar 20 px, clipping, ausência de conteúdo e leitura fresca após mutação; detectar mutante que reutiliza snapshot de outro controle/caso. Preservar todas as contraprovas existentes. Depois, focal all próprio com 413 IDs/critérios/ordem/zoom/foco/touch/zero writers e cap 900; novo freeze e FULL 102 próprio. A igualdade de asserts, os 18 controles em memória ou qualquer PASS anterior não dispensam essas etapas.

Se a equivalência passar e o tempo ainda exceder 900 s, preservar a falha. Uma próxima investigação delimitada deve instrumentar fases (close/rmtree/launch/setup/seed) e custo de RPC, mantendo os critérios. A acumulação de 32 contas em compact native (seed 4 contas × 8 casos) é outra redundância concreta, mas não pertence a este patch e não autoriza alterá-la.

Identidades: patch `7b59fff1bfd49d318bf3273976fb95691bfa95dd0c69a49d85c6ed8a5bed71a2`; script independente `7a2ad9c17e7adf84712e4c453f676df0a050efc679a9ad61b62e2cf38c8f798e`. Histórico e FULL atual mantêm classificações próprias; nenhuma aprovação global é concedida nesta revisão.
