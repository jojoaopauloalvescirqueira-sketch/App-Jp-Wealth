# Stoikus by JP Wealth — mapa da assinatura R4

Autorização: design aprovado pelo proprietário e aplicação nos âmbitos de influência do Stoikus, conforme o escopo da tarefa de15/10/2026. Produto **1.22.3**, MQL **1.223**, interface **R4**, cálculo **1.9.0**. A revisão aplica identidade visual e cria uma distribuição própria; não representa compilação, instalação, ensaio MT5 ou aceite financeiro.

A composição aprovada usa Stoikus em Arial regular24px, by12px e a logo vermelha JP Wealth original com12px de altura, em240×28px lógicos. Os BMPs incorporados fornecem escalas100/125/150/200 e temas claro/escuro; a conferência em DPI nativo continua pendente. A marca geral do site JP Wealth e a identidade NoCuda são preservadas.

| Superfície | Fonte ou artefato atual | Vínculo e limite |
|---|---|---|
| Conta/Histórico e apresentação da suíte MT5 | `mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Stoikus_Brand.mqh` e oito `MQL5/Images/JPWealth/JPW_Stoikus_Logo_*.bmp` | Build e fingerprint vinculam os recursos aos fontes; eventos e desenho nativos não demonstrados. |
| Monitor e Supervisor | Fontes MQL Stoikus correspondentes | Atribuição/paleta; não muda persistência, IDs ou negociação. |
| NoCuda | Fonte e logo NoCuda existentes | Identidade própria preservada; assinatura Stoikus delimita a suíte. |
| Site | Bloco Stoikus e serviços de download existentes | O site orienta e distribui; não executa MT5. |
| Prévia fictícia | `downloads/jpw-alavancagem-atual/Previa_Stoikus_Interface_R4.html` | Arquivo selado próprio; não comprova execução nativa. |
| Kit Windows | `Kit_Windows_Stoikus_Assinatura_R4.zip` + `root-pin-R4.json` externo | Mesmo diário do manifesto; preparo/compilação em staging, sem instalação automática. |
| Fontes de uso e SDK | `JPW_Stoikus_Uso_Fontes_v1.22.3_interface.zip` e `JPW_Stoikus_Fontes_v1.22.3_interface.zip` | Gerados pelo `tools/build_leverage_package.py` oficial. |
| Assistente Windows em desenvolvimento | Entrega do instalador em tarefa própria | A identidade não transforma o kit em instalador nem autoriza uso de um terminal real. |

O gerador `tools/build_stoikus_interface_kit.py` reutiliza o freezerR3 e os arquivos do kit seladoR3. O núcleo `NativeKit.Core.ps1` conserva os bytes; runner, fixtures e verificador recebem referências/pinsR4. O pin registra estados no momento da selagem e não herda o PASS48/48 antigo.

Os treze downloads anteriores — ZIPs históricos, kitR3, pinR3 e préviaR3 — continuam separados e protegidos. As novas saídas R4 têm nomes próprios. Compilação MetaEditor, runtime MT5, PowerShell no Windows, Windows x64 independente e aceite humano permanecem **NOT_RUN** até recibos exatos; o serviço Parallels indisponível não permite inferir sucesso.
