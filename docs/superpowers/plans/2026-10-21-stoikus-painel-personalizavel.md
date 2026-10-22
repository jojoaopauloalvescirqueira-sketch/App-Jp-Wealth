# Stoikus — painel personalizável

Contrato e critérios: [CHG](../../work/CHG-STOIKUS-PAINEL-PERSONALIZAVEL-20261021.md). Plano aprovado na conversa, execução sem operações Git de integração/publicação.

- [x] Prévia navegável isolada: linhas compactas, escolha/ordem, Aplicar/Cancelar, temas e estados sintéticos.
- [x] Preferência nova estrita, independente das preferências anteriores; compatibilidade em memória, sem gravação automática.
- [x] Painel nativo, editor de personalização, paginação, controles reunidos e comunicação local Conta–NoCuda; fallback independente.
- [ ] Diagnóstico/recuperação dirigida dos controles repetidos, sem exclusão global de objetos.
- [x] Revisão da janela completa, documentação de uso e regressões permanentes.
- [ ] Revisão independente e suítes do candidato; compilação/ensaio nativo com identidades próprias e aceite separado.

Estado final local em 21/10: C5 com kit e aplicação revisados independentemente; MT5-all: 58 PASS, 3 PRODUCT_FAIL; FULL: 73 PASS, 4 PRODUCT_FAIL, 4 ENVIRONMENT_ERROR. Seis focais separados passaram após informar navegador/Node ao processo; não substituem nem reclassificam o FULL bruto, que registrou essas ocorrências de ambiente. As 55 verificações host passaram, mas não há aceite integral. O ajuste do teste Conta–NoCuda e o lote nativo foram autorizados e aplicados. O proprietário decidiu verificar manualmente sem ensaio MT5 nesta entrega. Inventário/recuperação legada, compilação/interação MT5 e aceite humano permanecem pendentes; Windows x64 indisponível. Guia em `PARA-TESTAR-MANUALMENTE.md` no arquivo privado da sessão.
