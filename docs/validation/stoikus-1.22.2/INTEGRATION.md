# Stoikus 1.22.2 — candidato de continuidade

Base `0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874`, branch `codex/stoikus-continuity-20261014`, worktree `/private/tmp/jpw-stoikus-continuity-20261014`. Produto **1.22.2**, MQL **1.222**, cálculo **1.9.0** preservado. O checkout principal permanece na base e não foi alterado; esta entrega não foi publicada.

## Resultado local e limites

O NoCuda só limpa recursos admitidos pela sua instância, inclusive após falha de inicialização. O Histórico Pessoal audita até o fim em etapas, conserva snapshots e cancela consultas obsoletas sem truncar o diário. O Monitor informa espera, causa, ação, degradação e recuperação, sem alterar a autoridade dos dados financeiros.

As revisões independentes individuais aprovaram os fontes/host. O congelamento integrado **R2** passou em `leverage_suite.py --scope all`: **47/47**, e `quality_gate.py --tier full`: **57/57**, sem falhas nas demais categorias. Seus **1.023 inputs** foram conferidos após os testes, sem mudanças. A revisão integral e a identidade final do kit têm recibos separados; não implicam execução Windows.

| Prova | Estado e alcance |
| --- | --- |
| Lifecycle NoCuda | PASS host; revisão Task1 aprovada |
| Monitor | 23/23 casos host PASS; revisão R3 aprovada |
| Histórico Pessoal | CONT01–14 PASS; 20 HIS-AC PASS nas facetas host cobertas; freeze02/revisão R2 aprovada |
| Host/distribuição integrados | 47/47 PASS, R2 |
| Site completo integrado | 57/57 PASS, R2 |
| SDK/uso e reprodução | 136/83 entradas; hashes, identidade, reprodução e idempotência PASS nos verificadores oficiais |
| Seis ZIPs históricos | Byte-idênticos à base |
| PowerShell/fixtures do kit no Windows | NOT_RUN; 51 casos preparados, sem resultado inventado |
| MetaEditor/quatro programas ARM/Parallels | NOT_RUN |
| Instalação e execução MT5 ARM/Parallels | NOT_RUN |
| Windows x64 independente | NOT_RUN; plataforma indisponível |
| Iniciante/dois gráficos/padrões | NOT_RUN; proprietário participará |
| Commit/push/merge/publicação | NOT_RUN; ações separadas |

A auditoria host cobre diários de 0, 1, 100.000, 100.001 e 200.003 linhas, corrupção tardia, tipos SQLite, mudanças de geração, reservas/commit concorrente, cancelamento e exportação/restauração. Exportação CSV é conferida até EOF. O limite JSON conserva **32 × 1024 × 1024 caracteres do corpo canônico**, não uma garantia de tamanho final do arquivo em bytes. O orçamento de trabalho em etapas não garante que uma operação SQL/hash/IO indivisível termine em 25 ms no MT5.

Tentativas RED, falhas de harness e pareceres anteriores permanecem no ledger. A fixture inicial inválida tem errata e uma nova RED com fixture válida contra a base. A limitação do VFS SQLite macOS em handles simultâneos tem reprodução externa e disposição ENVIRONMENT_ERROR, com o recibo original preservado; ensaios IPC posteriores usam o VFS padrão em processos distintos. Nada disso demonstra comportamento nativo do MT5.

## Identidade e recibos

| Identidade | SHA-256 / valor |
| --- | --- |
| MQL source fingerprint | `a27bb5ccfe778cc83fc0cb37309d7bf9a1bcbfc3c50f69142c2788934b067d4e` |
| Runtime build ID | `5a207fbd41e59c2d2544f94264105d45c69911518433d0d66176eb9c0c427a1b` |
| SDK fontes | `f4f99a5ea010b8cf9ec0bda1909bbecaacbbb0b6bfa46f53470a91d8a5313006` — 780.550 bytes |
| Uso diário fontes | `d1c36843909dc20730d9dfa935294d22f10fe69bdeba6a586a50a99c942d295d` — 447.740 bytes |
| Freeze R2 | `2a5b924b11b52fa8c730751b2ec3ec890c6b82254df3886ad7c16c679d1bed4b` |
| Attestation pós-gates | `f0740d0606b35c928303df32202285a76d9dba0469470b9f365ae28cce21b349` |
| Full R2 | `fdb68347342429d0ecef880c3806f092ebe33c39d88c457335264ba0160838c0` |

Ledger: `.superpowers/sdd/stoikus-continuity-20261014/`. Recibos principais: `integrated-freeze-R2.json`, `integrated-after-gates-R2.json`, `mt5-all-R2.json`, `web-full-R2.json`, `task-1-review.md`, `task-2-implementation-review-R2.md`, `task-3-review.md`. Artefatos integrados R1 foram arquivados antes do último delta; seus hashes não são os da entrega R2.

O fechamento documental posterior altera somente os documentos focais identificados em `documentation-final-delta.json`; fontes, testes, geradores, ZIPs e builds permanecem nos bytes validados. A documentação histórica após o separador em CURRENT-STATE, ACTIVE-TASK, CONTEXT-MAP e SESSION_HANDOFF é preservada integralmente.

## Próxima prova: Windows do proprietário

Windows 11 ARM está disponível no Parallels, e o proprietário confirmou MT5 instalado. `prlctl exec` exige outra edição licenciada e não foi contornado. As tentativas legítimas de GUI não estabeleceram execução PowerShell no guest. Nenhum caminho/build de MT5 foi inferido; nenhum programa foi instalado ou armado.

O kit `native-kit/` compila apenas os quatro programas em staging temporário local, usando o MetaEditor escolhido e Includes padrão transitivos. O ZIP, cada entrada, os fontes e o Core têm pins/hashes; o recibo registra executáveis, versões e resultados. Logs desconhecidos, falhas, timeout ou EX5 não comprovado impedem COMPILADO. Os diagnósticos disponíveis são conservados. O kit não inicia o terminal nem copia arquivos para a instalação existente.

Receber quatro EX5 novos e logs completos comprova apenas a compilação desses programas. Depois da análise do recibo, o ensaio será em outra instalação/pasta de dados e conta demo. O roteiro do proprietário está em `HUMAN-ACCEPTANCE-PENDING.md`; bancos, MQL5/Files, preferências, estudos e locks da instalação de uso permanecem preservados. Compilação, instalação e abertura são estados distintos. O instalador beta anterior conserva payload 1.22.1 e não representa estas correções.

## Grafo focal separado

O grafo atualizado inclui **104 arquivos MQL + 2 documentos**, além do inventário de 9 imagens: **3.068 nós, 8.884 arestas e 106 comunidades**. Fonte, cópias congeladas e hashes constam em SOURCE_MANIFEST; os intermediários são conservados. O adapter C++ tem erros de parsing em 17/104 arquivos; o diagnóstico registra 176 referências sem endpoint e 802 pares colapsados. Portanto, o grafo é uma representação parcial, com relações inferidas identificadas, e não prova de qualidade ou compilação MQL5.

O relatório declara consumo de tokens indisponível: os zeros do schema são placeholders. O HTML oficial depende do vis-network via CDN e requer internet; JSON e relatório podem ser consultados localmente. O grafo geral histórico permanece separado. Não se declara reconciliação de toda a documentação interna nem superioridade de mercado ou clareza equivalente ao Position Sizer antes do teste com iniciante.
