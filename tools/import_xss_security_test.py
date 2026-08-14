#!/usr/bin/env python3
"""Stored XSS via importação de backup adulterado.

Contrato: um backup é arquivo EXTERNO. Nenhuma string vinda dele pode ser
interpretada como HTML, nem no momento da importação nem depois de persistida e
recarregada. Metadata estrutural (rótulo/classe de fase, nome de instrumento) é
catálogo fechado: o app nunca a escreve, então o valor do backup é descartado e
reconstruído a partir de DEFAULTS. Dados do operador continuam intactos.

Fixtures são sintéticas. O payload é inofensivo: apenas marca `window.__JPW_XSS__`.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, os, socket, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

# Payload de detecção: se o HTML for interpretado, onerror dispara e marca a flag.
PAYLOAD = '<img src=x onerror="window.__JPW_XSS__=1">'
# Contexto de atributo: fecha o atributo antes de injetar (alvo do class="phase ...").
PAYLOAD_ATTR = '"><img src=x onerror="window.__JPW_XSS__=1">'

CAMPOS_FASE = ('title', 'faseNome', 'cls', 'alavtxt')


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass


def serve():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]
    server = ThreadingHTTPServer(('127.0.0.1', port), Quiet)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f'http://127.0.0.1:{port}/'


def estado_malicioso():
    """Backup adulterado: payload em cada campo estrutural auditado."""
    return {
        # params.inicio chegava a innerHTML sem esc() no resumo do onboarding —
        # cada campo vizinho escapava, este nao. Vetor de stored XSS.
        'params': {'saldoIni': 10000, 'saldoAtu': 10000, 'inicio': PAYLOAD},
        # Matriz Quadrifasica: catalogo normativo fechado que nenhuma tela escreve.
        # A guarda antiga validava so a FORMA, entao estes valores atravessavam e
        # passavam a definir fase vigente, teto de risco e teto de alavancagem.
        'matrix': [
            {'nome': PAYLOAD, 'ddmin': 0, 'ddmax': 0.99, 'alav': 99},
            {'nome': PAYLOAD, 'ddmin': 0.99, 'ddmax': 0.99, 'alav': 99},
            {'nome': PAYLOAD, 'ddmin': 0.99, 'ddmax': 0.99, 'alav': 99},
            {'nome': PAYLOAD, 'ddmin': 0.99, 'ddmax': 0.99, 'alav': 99},
        ],
        # Mapa de Liquidez do questionario de inicio: os dois unicos campos do
        # painel que chegavam a innerHTML sem esc(). Pela interface sao <select>
        # de opcoes fixas, mas migrate() nao normaliza campo algum de
        # S.onboarding — o valor do arquivo chega cru ao render.
        'onboarding': {'fcrLiquidity': PAYLOAD, 'feoLiquidity': PAYLOAD},
        'phaseUnlocked': [True, True, False, False],  # destrava F2: exercita grade ativa + histórico
        'quarantine': {'inicio': PAYLOAD, 'fim': PAYLOAD},
        'transitionLog': [{'fase': 2, 'ts': PAYLOAD, 'resumo': {'x': PAYLOAD}}],
        'instruments': [
            {'name': PAYLOAD, 'preco': PAYLOAD, 'cpl': 100000, 'teto': 0.05, 'updated': '2026-07-02'},
            {'name': 'EURUSD', 'preco': 1.1413, 'cpl': 100000, 'teto': 0.05, 'updated': '2026-07-02'},
        ],
        'phases': [
            {'title': PAYLOAD, 'cls': PAYLOAD_ATTR, 'faseNome': PAYLOAD, 'ddtxt': PAYLOAD, 'alavtxt': PAYLOAD,
             'orders': [{'id': 'A1', 'par': 'EURUSD', 'tipo': 'BUY', 'lote': 0.04,
                         'entry': 1.1, 'sl': 1.09, 'tp': 1.12, 'result': 0, 'status': 'Aberta'}]},
            {'title': PAYLOAD, 'cls': PAYLOAD_ATTR, 'faseNome': PAYLOAD, 'ddtxt': PAYLOAD, 'alavtxt': PAYLOAD,
             'orders': []},
            {'title': PAYLOAD, 'cls': PAYLOAD_ATTR, 'faseNome': PAYLOAD, 'ddtxt': PAYLOAD, 'alavtxt': PAYLOAD,
             'orders': []},
            {'title': PAYLOAD, 'cls': PAYLOAD_ATTR, 'faseNome': PAYLOAD, 'ddtxt': PAYLOAD, 'alavtxt': PAYLOAD,
             'orders': []},
        ],
    }


def estado_legitimo():
    """Base real mínima: sobrevivência dos dados do operador (§15)."""
    return {
        'params': {'saldoIni': 25000, 'saldoAtu': 25400},
        'accounts': [{'nome': 'Conta Sintética', 'tipo': 'MESTRE', 'broker': 'FTMO',
                      'perfil': 'Base', 'sini': 25000, 'satu': 25400, 'perfilLocked': True}],
        'ledger': [{'data': '2026-08-03', 'resultado': 400, 'saldo': 25400, 'nota': 'fechamento sintético'}],
        'phases': [{'title': 'FASE 1 — O ATAQUE', 'cls': 'p1', 'faseNome': 'FASE 1',
                    'ddtxt': '0–4%', 'alavtxt': '4,0x',
                    'orders': [{'id': 'X9', 'par': 'GBPUSD', 'tipo': 'BUY', 'lote': 0.04,
                                'entry': 1.35, 'sl': 1.33, 'tp': 1.38, 'result': 0, 'status': 'Aberta'}]}],
    }


def abrir(browser, url, seed=None):
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800})
    ctx.add_init_script('window.__onbShown = true;')
    if seed is not None:
        ctx.add_init_script(
            "try{localStorage.setItem('jpwealth_v9_state',%s);}catch(e){}" % json.dumps(json.dumps(seed)))
    page = ctx.new_page()
    page.route('**/api.frankfurter.dev/**', lambda r: r.fulfill(
        status=200, content_type='application/json', body='{"rates":{}}'))
    page.route('**/raw.githubusercontent.com/**', lambda r: r.fulfill(
        status=200, content_type='application/json', body='{"version":1,"events":[]}'))
    page.goto(url, wait_until='load')
    page.wait_for_timeout(600)
    return ctx, page


def sondar(page):
    """Renderiza todas as superfícies afetadas e mede execução, DOM e estado.

    Os erros de render são DEVOLVIDOS, nunca engolidos: um render que estoura
    antes de escrever innerHTML não desenha o payload e produziria um PASS vazio.
    """
    return page.evaluate("""() => {
      // Força o desenho das telas que consomem os campos auditados.
      const erros = {};
      const desenhar = (nome, fn) => { try{ fn(); }catch(e){ erros[nome]=String(e&&e.message||e); } };
      desenhar('renderPhases', ()=>renderPhases());
      desenhar('renderMotor', ()=>renderMotor());
      desenhar('renderAuditLog', ()=>renderAuditLog());
      desenhar('renderConfigQuarantine', ()=>renderConfigQuarantine());
      desenhar('renderConfigOnboarding', ()=>renderConfigOnboarding());
      const conteudo = {
        fases: (document.getElementById('phaseContainer')||{}).innerHTML || '',
        motor: (document.getElementById('motorBody')||{}).innerHTML || '',
      };
      // O app usa onerror LEGÍTIMO no logo de corretora (05-brokers-prop-firms.js),
      // então contar todo [onerror] daria falso positivo. Medimos só o marcador do
      // payload: '__JPW_XSS__' vivo como handler é o que caracteriza a injeção.
      const html = document.documentElement.innerHTML;
      const vivos = [...document.querySelectorAll('*')].filter(el => {
        for (const at of el.attributes || []) {
          if (/^on/i.test(at.name) && at.value.includes('__JPW_XSS__')) return true;
        }
        return false;
      });
      return {
        executou: window.__JPW_XSS__ === 1,
        imgs: document.querySelectorAll('img[src="x"]').length,
        comOnerror: vivos.length,
        // Escapado, o payload vira NÓ DE TEXTO. Não se mede isso no HTML serializado:
        // dentro de texto o serializador escapa `<` (&lt;) mas devolve as aspas
        // literais, então `onerror="..."` aparece inerte na fonte. Quem decide é o
        // DOM — elemento criado e handler vivo — não a aparência da string.
        marcacaoViva: vivos.length > 0,
        scriptsComPayload: [...document.querySelectorAll('script')]
          .filter(s => (s.textContent||'').includes('__JPW_XSS__')).length,
        htmlLen: html.length,
        fase0: S.phases[0] ? {title:S.phases[0].title, cls:S.phases[0].cls,
                              faseNome:S.phases[0].faseNome, alavtxt:S.phases[0].alavtxt} : null,
        nomesInstrumentos: S.instruments.map(i => i.name),
        // Compara com DEFAULTS na propria pagina: repetir a tabela normativa aqui
        // criaria uma segunda fonte de verdade justamente do que se quer proteger.
        matrizCanonica: JSON.stringify(S.matrix) === JSON.stringify(DEFAULTS.matrix),
        matrizAtual: S.matrix,
        tamResumoOnb: (document.getElementById('cfgOnbSummary')||{}).innerHTML ?
                      (document.getElementById('cfgOnbSummary').innerHTML||'').length : -1,
        ordensFase0: S.phases[0] ? S.phases[0].orders.length : -1,
        errosRender: erros,
        tamFases: conteudo.fases.length,
        tamMotor: conteudo.motor.length,
      }; }""")


def afirmar_seguro(sonda, rotulo):
    # Antes de qualquer conclusão de segurança: provar que as telas REALMENTE
    # desenharam. Sem isto, um render quebrado viraria um PASS sem significado.
    assert not sonda['errosRender'], \
        f'[{rotulo}] render falhou (PASS seria vazio): {sonda["errosRender"]}'
    assert sonda['tamFases'] > 200, \
        f'[{rotulo}] grade de fases não foi desenhada ({sonda["tamFases"]} chars) — teste não provaria nada'
    assert sonda['tamMotor'] > 100, \
        f'[{rotulo}] motor de lote não foi desenhado ({sonda["tamMotor"]} chars)'
    assert not sonda['executou'], f'[{rotulo}] STORED XSS: handler do payload EXECUTOU'
    assert sonda['imgs'] == 0, f'[{rotulo}] payload criou {sonda["imgs"]} elemento(s) IMG no DOM'
    assert sonda['comOnerror'] == 0, f'[{rotulo}] payload criou atributo onerror vivo no DOM'
    assert not sonda['marcacaoViva'], f'[{rotulo}] elemento com handler do payload sobreviveu no DOM'
    assert sonda['scriptsComPayload'] == 0, f'[{rotulo}] payload virou <script> no documento'


def afirmar_canonico(sonda, rotulo):
    f0 = sonda['fase0']
    assert f0 is not None, f'[{rotulo}] fase 0 desapareceu'
    assert f0['title'] == 'FASE 1 — O ATAQUE', f'[{rotulo}] title não foi canonicalizado: {f0["title"]!r}'
    assert f0['faseNome'] == 'FASE 1', f'[{rotulo}] faseNome não foi canonicalizado'
    assert f0['cls'] == 'p1', f'[{rotulo}] cls não foi canonicalizado'
    assert f0['alavtxt'] == '4,0x', f'[{rotulo}] alavtxt não foi canonicalizado'
    for nome in sonda['nomesInstrumentos']:
        assert nome == '' or nome.isalnum() and nome.isupper() or nome.isdigit(), \
            f'[{rotulo}] nome de instrumento fora do formato de ticker: {nome!r}'
    assert '<' not in ''.join(sonda['nomesInstrumentos']), f'[{rotulo}] marcação sobreviveu em instruments[].name'
    # A matriz e catalogo fechado: qualquer valor vindo de arquivo tem de ser
    # descartado em favor da fonte oficial. Sem isto, um backup define os tetos.
    assert sonda['matrizCanonica'], \
        f'[{rotulo}] Matriz Quadrifásica do arquivo sobreviveu à importação: {sonda["matrizAtual"]!r}'


def afirmar_mapa_de_liquidez_seguro(browser, url, rotulo):
    """Mapa de Liquidez do questionario de inicio nao executa payload de backup.

    centralCashPanelHTML() e local ao modulo do onboarding e o painel so existe
    depois que o modal e montado — por isso este bloco ABRE o questionario no
    passo do Caixa Central em vez de chamar um renderizador global. Sem abrir, o
    payload nunca chega ao DOM e a assercao passaria vazia.
    """
    ctx, page = abrir(browser, url, seed=estado_malicioso())
    page.on('dialog', lambda d: d.accept())
    page.evaluate("() => { window.__onbShown = true; openOnboardingModal('edit','cash'); }")
    page.wait_for_timeout(500)
    medida = page.evaluate("""() => {
      const painel = document.getElementById('obCentralCashPanel');
      // MESMO criterio de sondar(): so conta HANDLER vivo (atributo on*). O
      // marcador dentro de um value="" escapado e justamente a prova de que o
      // escape funcionou — conta-lo daria falso positivo.
      const vivos = [...document.querySelectorAll('*')].filter(el => {
        for (const at of el.attributes || []) {
          if (/^on/i.test(at.name) && String(at.value).includes('__JPW_XSS__')) return true;
        }
        return false;
      }).length;
      return {
        montou: !!painel,
        imgs: painel ? painel.querySelectorAll('img[src="x"], img[src="y"]').length : -1,
        atributosVivos: vivos,
        executou: window.__JPW_XSS__ === 1,
        // O payload precisa estar la como TEXTO: se sumisse, o teste passaria
        // por ausencia de dado em vez de por escape correto.
        comoTexto: painel ? painel.innerText.includes('__JPW_XSS__') : False_,
      };
    }""".replace('False_', 'false'))
    assert medida['montou'], f'[{rotulo}] painel do Caixa Central nao montou — assercao seria vazia'
    # Seguranca primeiro: se o payload executar, e ISSO que o relatorio precisa
    # dizer. A guarda de vacuidade fica por ultimo, porque sem esc() o payload
    # vira ELEMENTO e some do innerText — falhar ali por primeiro daria uma
    # mensagem enganosa para o defeito mais grave.
    assert not medida['executou'], f'[{rotulo}] payload do Mapa de Liquidez EXECUTOU'
    assert medida['imgs'] == 0, f"[{rotulo}] payload injetou {medida['imgs']} elemento(s) no painel"
    assert medida['atributosVivos'] == 0, f"[{rotulo}] marcador vivo em atributo de evento: {medida['atributosVivos']}"
    assert medida['comoTexto'], f'[{rotulo}] payload nao chegou ao painel como texto — escape ausente ou assercao vazia'
    ctx.close()


def suite_maliciosa(browser, url, rotulo):
    # --- 1) Estado adulterado JÁ PERSISTIDO (o caminho do stored XSS) ---------
    ctx, page = abrir(browser, url, seed=estado_malicioso())
    sonda = sondar(page)
    afirmar_seguro(sonda, f'{rotulo}/load')
    afirmar_canonico(sonda, f'{rotulo}/load')
    assert sonda['ordensFase0'] == 1, f'[{rotulo}] ordem legítima da fase 0 foi perdida na canonicalização'

    # --- 2) Persistência: grava e RECARREGA (contrato central do stored XSS) --
    page.evaluate('save()')
    page.reload(wait_until='load')
    page.wait_for_timeout(600)
    sonda = sondar(page)
    afirmar_seguro(sonda, f'{rotulo}/reload')
    afirmar_canonico(sonda, f'{rotulo}/reload')
    ctx.close()

    # --- 3) Caminho real de IMPORTAÇÃO: normalizeImportedState() -------------
    ctx, page = abrir(browser, url)
    aplicado = page.evaluate("""(bruto) => {
      const imported = normalizeImportedState(JSON.parse(bruto));
      S = imported; migrate();
      return { title:S.phases[0].title, cls:S.phases[0].cls,
               nomes:S.instruments.map(i=>i.name) }; }""", json.dumps(estado_malicioso()))
    assert aplicado['title'] == 'FASE 1 — O ATAQUE', f'[{rotulo}] import não canonicalizou title'
    assert aplicado['cls'] == 'p1', f'[{rotulo}] import não canonicalizou cls'
    assert not any('<' in n for n in aplicado['nomes']), f'[{rotulo}] import preservou marcação em name'
    sonda = sondar(page)
    afirmar_seguro(sonda, f'{rotulo}/import')
    ctx.close()


def suite_legitima(browser, url, rotulo):
    """§15: backup legítimo continua funcionando — sem regressão funcional."""
    ctx, page = abrir(browser, url, seed=estado_legitimo())
    r = page.evaluate("""() => {
      try{ renderPhases(); }catch(e){}
      return {
        saldoIni: S.params.saldoIni,
        conta: S.accounts[0] && S.accounts[0].nome,
        ledger: S.ledger.length,
        nota: S.ledger[0] && S.ledger[0].nota,
        ordemId: S.phases[0].orders[0] && S.phases[0].orders[0].id,
        ordemPar: S.phases[0].orders[0] && S.phases[0].orders[0].par,
        title: S.phases[0].title,
        faseNome: S.phases[0].faseNome,
        instrumentos: S.instruments.map(i=>i.name),
      }; }""")
    assert r['saldoIni'] == 25000, f'[{rotulo}] parâmetros do operador alterados'
    assert r['conta'] == 'Conta Sintética', f'[{rotulo}] conta do operador perdida'
    assert r['ledger'] == 1 and r['nota'] == 'fechamento sintético', f'[{rotulo}] ledger alterado'
    assert r['ordemId'] == 'X9' and r['ordemPar'] == 'GBPUSD', f'[{rotulo}] ordem do operador perdida'
    assert r['title'] == 'FASE 1 — O ATAQUE' and r['faseNome'] == 'FASE 1', \
        f'[{rotulo}] metadata legítima deixou de ser coerente'
    assert 'EURUSD' in r['instrumentos'] and 'US500' in r['instrumentos'], \
        f'[{rotulo}] catálogo de instrumentos legítimo não sobreviveu'

    # export → import → reload do fluxo legítimo
    page.evaluate('save()')
    page.reload(wait_until='load')
    page.wait_for_timeout(600)
    r2 = page.evaluate("""() => ({ saldoIni:S.params.saldoIni, ordemId:S.phases[0].orders[0].id,
                                   ledger:S.ledger.length, conta:S.accounts[0].nome })""")
    assert r2 == {'saldoIni': 25000, 'ordemId': 'X9', 'ledger': 1, 'conta': 'Conta Sintética'}, \
        f'[{rotulo}] dados legítimos não sobreviveram ao ciclo save/reload: {r2}'
    ctx.close()


def main():
    server, base = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for rotulo, alvo in (('modular', 'index.html'),
                                 ('portatil', 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')):
                suite_maliciosa(browser, base + alvo, rotulo)
                afirmar_mapa_de_liquidez_seguro(browser, base + alvo, rotulo)
                suite_legitima(browser, base + alvo, rotulo)
            browser.close()
    finally:
        server.shutdown()
    print('IMPORT XSS OK — backup adulterado não executa, não injeta DOM e não persiste '
          'marcação; metadata estrutural volta ao catálogo oficial e a base legítima '
          'atravessa intacta (modular e portátil).')


if __name__ == '__main__':
    main()
