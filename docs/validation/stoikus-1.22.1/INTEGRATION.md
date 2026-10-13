# Stoikus 1.22.1 — correções de usabilidade, candidato local

Implementação autorizada pelo proprietário nesta conversa; referência escolhida: [Position Sizer da EarnForex](https://www.earnforex.com/metatrader-expert-advisors/Position-Sizer/). Base Git `0f247215cc20829fdba40c3b33458ee976c17ea1`, branch `codex/stoikus-renaming-20261012`, checkout `/private/tmp/jpw-stoikus-renaming-20261012`. Sem commit, push, merge, publicação ou instalação no MT5 do proprietário.

## Comportamento entregue

O percurso de uso possui três componentes permanentes e um abridor pontual: Monitor em gráfico de apoio; Conta e NoCuda no gráfico de trabalho; `JPW_Stoikus_Abrir_Paineis` acrescenta os indicadores ausentes. O SDK conserva testes, laboratório e ferramentas de engenharia separados desse percurso. O site mantém suas cinco abas e prioriza o download de uso.

Os 20 parâmetros preservam nomes, tipos, ordem e padrões. Grupos, rótulos e erros de inicialização explicam unidade, intervalo e zero/vazio. O abridor consulta todas as sub-janelas antes de criar handles, usa caminhos enraizados e informa instâncias legadas, falhas parciais e falhas de liberação. Presença não é comprovação de saúde, versão ou compatibilidade. A repetição não atualiza um indicador antigo.

Fórmulas e cálculo 1.9.0, schemas, bibliotecas financeiras/NoCuda, dados, locks, preferências e estudos não receberam mudanças. A preservação de estados nos testes é sintética; persistência e ciclo de vida nativos precisam do ensaio MT5. Supervisor não armado; Fibonacci importado permanece UNVERIFIED_NATIVE.

## Identidade dos artefatos

| Artefato | Membros / programas MQ5 | Bytes | SHA-256 |
| --- | --- | --- | --- |
| JPW_Stoikus_Uso_Fontes_v1.22.1.zip | 82 / 4 | 441516 | `5b2c7ca40736dda976fe97a91a2677d190eb1ccfdf9527703fd471ee702a11e5` |
| JPW_Stoikus_Fontes_v1.22.1.zip | 135 / 34 | 773801 | `03ccb37824175511108b36e9abb5c9fa0dc28d89a338caea1dc7bf02508b9cae` |

Produto/MQL/cálculo: 1.22.1 / 1.221 / 1.9.0. Build MQL `b4031d96f5d180aa35c6285ad8baec97f017d162e7ea0499d38df339571d81db`; fingerprint MQL `8c35c3c02e9049b7727d8d0595c12ca424df04f8052d64c0aced92b587438894`. Build web `20af9dfa48bb7648`. Freeze R4 de 394 inputs: `4abcb1e1b47c6f25b524ed67ecf2f9f83a3c47059e26879caa6e8dec86ef675d`.

Geradores oficiais: `tools/build_leverage_package.py` e `tools/rebuild_monolith.py`. O hash declarado do script de navegação/download foi atualizado; os ZIPs históricos são preservados. O pacote de uso inclui quatro programas, 69 includes, oito imagens e LEIA_PRIMEIRO. Nenhum EX5 é distribuído neste candidato.

## Verificação e crítica

- Host/distribuição: **PASS 44/44** em `leverage_suite.py --scope all`, com inputs invariantes durante a suíte. Inclui os 29 cenários do abridor, fechamento de dependências, reprodução, idempotência, downloads íntegros/corruptos, HTTP, arquivo local, HTML portátil e PWA offline.
- Site JP Wealth: **PASS 57/57**, `quality_gate.py --tier full`, nos mesmos inputs congelados R4; comparação antes/depois sem alteração.
- Revisão independente do código/pacotes: **REVIEW_PASS**. Oráculo independente comparou os 20 inputs com o ZIP imutável 1.22.0 e rejeitou quatro mutantes próprios. Os casos negativos anteriores de distribuição foram conservados.
- Gauntlet de clareza documental/web: **PASS**. Crítico independente escolheu o candidato diante da referência, examinou as cinco abas em 1440/390/320, teclado, rótulos, downloads reais e hashes. Autoria reconhecível nos materiais: cegamento parcial. A comparação externa é documental; não existe screenshot externa que sustente comparação visual.
- Correções provenientes da crítica: cadência solicitada e limites 30 s/5 s; caminhos absolutos; listagem distinta de saúde; avisos visíveis de release; shortnames corretos em Ctrl+I; isolamento definido antes do percurso; legados recolhidos; rótulos PT primários; alvo de toque de 44 px no link de ajuda.
- Melhorias editoriais P3 restantes: concisão das tabelas em 320 px e alguns atalhos de engenharia/USC. Não houve P1/P2 aberto no percurso web examinado. Os pareceres completos conservam essas ressalvas.

As tentativas anteriores e seus resultados foram preservados: R2 encontrou o adaptador Print não variádico e bloqueio de loopback pelo sandbox; R3 encontrou um alvo de toque de 18 px. O adaptador foi corrigido sem remover os 12 casos/contraprovas; o markup recebeu a classe acessível existente sem relaxar o critério. R4 é o recibo da revisão final, e não uma combinação de resultados intermediários.

## Limite operacional

Compilação MetaEditor, OnInit/OnDeinit, desenho, cliques, timers e permanência dos indicadores após o script terminar: **NOT_RUN**. O comando de execução dentro do Windows foi indisponível na edição instalada do Parallels; essa função exige Pro ou Business. É uma limitação do ambiente, não uma rejeição de aprovação automática. O teste host substitui APIs do MT5 por seams e não encerra essa lacuna.

Instalação operacional e aceite humano permanecem pendentes. Não há migração de dados, limpeza da instalação existente, negociação ou autorização financeira nova. O [roteiro nativo](NATIVE-CHECKLIST.md) liga o futuro ensaio aos hashes exatos e descreve preservação, falhas parciais, instâncias reconhecidas porém inativas e ciclo de vida real.

Rollback: reverter somente o delta 1.22.1, restaurando os bytes da baseline 1.22.0 e seus derivados verificados; não tocar dados ou a renomeação anterior. As fotografias de contexto anteriores foram preservadas byte a byte. Os recibos locais completos estão em `/private/tmp/jpw-stoikus-usability-evidence-20261013`; cópias finais estão nesta validação e na entrega durável.


Recibos: [host/all](host-all-R4.json) · [site full](full-R4.json) · [freeze R4](FREEZE-R4.json) · [vínculo de inputs do full](full-input-binding.json) · [revisão de código](CODE-REVIEW.md) · [revisão de clareza web](SITE-REVIEW.md). O recibo full é independente do campo web_full_gate da suíte host; a invariância dos inputs foi conferida separadamente contra FREEZE-R4.json. O campo da suíte host descreve somente o que aquela suíte executa.
