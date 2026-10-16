# Stoikus assinatura R4 — plano de distribuição

Objetivo: distribuir a identidade aprovada como produto 1.22.3/MQL1.223, interfaceR4, sem alterar cálculo1.9.0 nem substituir artefatos históricos. Escopo e autorização: `../evidence/scope.md` da cópia isolada.

Arquitetura: reutilizar `build_leverage_package.py` para stamp, dependências e arquivos determinísticos; reutilizar os nove arquivos selados do kitR3, alterando somente referências/identidades/pins e a descrição atual da marca. O kitR4 contém o mesmo ZIP diário que o manifesto distribui; o pin permanece separado. Native continua NOT_RUN.

- [ ] Preservar hashes de todos os downloads históricos e snapshots dos testes/control plane antes do delta.
- [ ] Atualizar metadados1.22.3/1.223, README e guia corrente; documentar Stoikus by JPWealth e a identidade NoCuda preservada.
- [ ] Criar geradorR4 com preparação via helpers oficiais, freeze específico de fontes/preview, identidade, scripts derivados do kitR3 e pin externo; recusar saída existente, input inconsistente e EX5.
- [ ] Esperar assets/MQL/prévia congelados do root; gerar kitR4/pin/ZIPs com novos nomes; atualizar os pins exatos do contrato oficial.
- [ ] Adaptar somente os valores deliberadamente versionados nos consumidores/testes atuais; conservar todos os negativos e oráculos. Rodar focos de pacote/distribuição/reprodutibilidade pertinentes, sem browser amplo.
- [ ] Conferir preservação histórica, idempotência e igualdade kit/daily; registrar limites e relatório `../evidence/distribution-branding.md` para crítica independente.

Não executar commit/push/merge, instalador ou instalação/compilação MT5. O root é dono de index/srcweb/prévia/assets; o builderMQL é dono da apresentação MQL. A geração final depende do congelamento explícito dessas entradas.
