# Dashboard macro — triagem somente leitura

- Comando focal: runtime Python isolado + `tools/dashboard_macro_test.py`.
- Resultado: `PRODUCT_FAIL`, assert linha 389, caso `390-light-sidebar-expanded-csszoom1.25-long1`.
- Falha: `documentElement.scrollWidth=393`, `clientWidth=390`; limite preservado <=1 px.
- Causa: regra nova de cabeçalho móvel cria seis tracks mínimos de44 px e gaps4 px. No caso, o contêiner tem272 pxCSS incluindo10 pxCSS de padding esquerdo herdado. O botão Finalizar termina em392,5 px renderizados.
- Não é falha de domínio do calendário semanal nem expectativa herdada de FF; as jornadas e links profundos precedentes passaram.
- Contraprova sem editar fontes: `page.add_style_tag` com a mesma regra móvel alterando somente gap para2 px. Overflow passa a0, último botão termina em380 px, e toda `assert_superficies_dashboard` passa. Áreas44 pxCSS preservadas. Sem erros JS/console.
- Proposta: ajustar a regra nova de espaçamento móvel, preservando limite de overflow, geometria dos controles e todos os testes existentes. Não enfraquecer teste nem aumentar timeout.
- Esta triagem não alterou fontes, verificadores, Git, calendários ou dados do projeto.

Evidências: `dashboard-triage.log`, `dashboard-triage-probe.json`, `dashboard-triage-red.png`, `dashboard-triage-proposed-green.png`. A injeção CSS é contraprova diagnóstica, não correção integrada. A suíte focal completa permanece RED até a alteração deliberada e nova execução.
