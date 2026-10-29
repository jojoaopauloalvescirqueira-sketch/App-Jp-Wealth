#!/usr/bin/env python3
"""Stored XSS via importação de backup adulterado.

Contrato: um backup é arquivo EXTERNO. Nenhuma string vinda dele pode ser
interpretada como HTML, nem no momento da importação nem depois de persistida e
recarregada. Metadata de apresentação de fase/ticker é canonicalizada. Grade sem
versão atual recebe identificação LEGACY e preserva seus índices e ordens. A
matriz importada permanece evidência; não governa o registry atual imutável.
Dados do operador continuam intactos.

Fixtures são sintéticas. O payload é inofensivo: apenas marca `window.__JPW_XSS__`.
"""
from http.server import SimpleHTTPRequestHandler
from browser_fixture_server import BrowserFixtureServer as ThreadingHTTPServer
from pathlib import Path
import json, os, socket, threading
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

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
    ctx = browser.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block')
    # Nominal economic replies are local fixtures; all other external traffic is
    # refused. In particular an injected image must never contact a third party.
    install_bootstrap(ctx)
    ctx.add_init_script('window.__onbShown = true;')
    if seed is not None:
        ctx.add_init_script(
            "if(localStorage.getItem('jpwealth_v9_state')===null){localStorage.setItem('jpwealth_v9_state',%s);}" % json.dumps(json.dumps(seed)))
    page = ctx.new_page()
    page.goto(url, wait_until='load')
    page.wait_for_timeout(600)
    wait_bootstrap(page)
    return ctx, page


def importar_arquivo(page, payload):
    """Exercita Blob/FileReader, consentimento e escritor real; nenhum S direto."""
    return page.evaluate("""async data => {
      window.__xssAlerts=[];window.__xssConfirmations=[];
      window.alert=message=>__xssAlerts.push(String(message));
      window.confirm=message=>{__xssConfirmations.push(String(message));return true;};
      const memory=JSON.stringify(S),disk=JSON.stringify(Object.fromEntries(
        Object.keys(localStorage).sort().map(key=>[key,localStorage.getItem(key)])));
      importFullBackupFile(new File([JSON.stringify(data)],'synthetic-xss.json',
        {type:'application/json'}));
      for(let i=0;i<300&&!__xssAlerts.length;i++)await new Promise(resolve=>setTimeout(resolve,10));
      return {alerts:__xssAlerts,confirmations:__xssConfirmations,
        unchanged:memory===JSON.stringify(S)&&disk===JSON.stringify(Object.fromEntries(
          Object.keys(localStorage).sort().map(key=>[key,localStorage.getItem(key)]))),
        executed:window.__JPW_XSS__===1,images:document.querySelectorAll('img[src="x"]').length};
    }""", payload)


def norma_runtime(page):
    """Referência limpa da fonte ativa; não duplicar a tabela financeira no teste."""
    return page.evaluate("""() => ({
      registry: JPWForex.policy.snapshot(),
      activeMatrix: activeRiskMatrix(),
      immutable: Object.isFrozen(JPWForex.policy) && Object.isFrozen(JPWForex.policy.phases)
        && JPWForex.policy.phases.every(Object.isFrozen),
      projections: [0,2.5,7,11,15,19,22].map(dd => JPWForex.engine.resolveAccountPhase({ddPercent:dd}))
    })""")


def sondar(page):
    """Renderiza todas as superfícies afetadas e mede execução, DOM e estado.

    Os erros de render são DEVOLVIDOS, nunca engolidos: um render que estoura
    antes de escrever innerHTML não desenha o payload e produziria um PASS vazio.
    """
    sonda = page.evaluate("""() => {
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
                              faseNome:S.phases[0].faseNome, alavtxt:S.phases[0].alavtxt,
                              ddtxt:S.phases[0].ddtxt, policyVersion:S.phases[0].policyVersion??null} : null,
        faseCount: S.phases.length,
        nomesInstrumentos: S.instruments.map(i => i.name),
        // Matriz legada é evidência preservada, distinta do registry ativo.
        matrizAtual: S.matrix,
        tamResumoOnb: (document.getElementById('cfgOnbSummary')||{}).innerHTML ?
                      (document.getElementById('cfgOnbSummary').innerHTML||'').length : -1,
        ordensFase0: S.phases[0] ? S.phases[0].orders.length : -1,
        errosRender: erros,
        tamFases: conteudo.fases.length,
        tamMotor: conteudo.motor.length,
      }; }""")
    sonda['normaRuntime'] = norma_runtime(page)
    return sonda


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


def afirmar_canonico(sonda, rotulo, norma_limpa):
    f0 = sonda['fase0']
    assert f0 is not None, f'[{rotulo}] fase 0 desapareceu'
    assert f0['title'] == 'GRADE LEGADA 1', f'[{rotulo}] title LEGACY não foi canonicalizado: {f0["title"]!r}'
    assert f0['faseNome'] == 'LEGACY 1', f'[{rotulo}] faseNome não foi canonicalizado'
    assert f0['cls'] == 'p1', f'[{rotulo}] cls não foi canonicalizado'
    assert f0['alavtxt'] == 'Histórico', f'[{rotulo}] alavtxt não foi canonicalizado'
    assert f0['ddtxt'] == 'LEGACY_UNRESOLVED', f'[{rotulo}] DD histórico foi presumido'
    assert f0['policyVersion'] is None and sonda['faseCount'] == 4, f'[{rotulo}] legado reinterpretado como seis fases atuais'
    for nome in sonda['nomesInstrumentos']:
        assert nome == '' or nome.isalnum() and nome.isupper() or nome.isdigit(), \
            f'[{rotulo}] nome de instrumento fora do formato de ticker: {nome!r}'
    assert '<' not in ''.join(sonda['nomesInstrumentos']), f'[{rotulo}] marcação sobreviveu em instruments[].name'
    assert sonda['matrizAtual'] == estado_malicioso()['matrix'], f'[{rotulo}] evidência da matriz legada foi alterada'
    assert sonda['normaRuntime']['immutable'], f'[{rotulo}] registry ativo deixou de ser imutável'
    assert sonda['normaRuntime'] == norma_limpa, f'[{rotulo}] arquivo importado alterou a norma ou suas projeções ativas'


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
    ctx_limpo, page_limpa = abrir(browser, url)
    norma_limpa = norma_runtime(page_limpa)
    ctx_limpo.close()
    # --- 1) Estado adulterado JÁ PERSISTIDO (o caminho do stored XSS) ---------
    ctx, page = abrir(browser, url, seed=estado_malicioso())
    sonda = sondar(page)
    afirmar_seguro(sonda, f'{rotulo}/load')
    afirmar_canonico(sonda, f'{rotulo}/load', norma_limpa)
    assert sonda['ordensFase0'] == 1, f'[{rotulo}] ordem legítima da fase 0 foi perdida na canonicalização'

    # --- 2) Persistência: grava e RECARREGA (contrato central do stored XSS) --
    page.evaluate('save()')
    page.reload(wait_until='load')
    page.wait_for_timeout(600)
    sonda = sondar(page)
    afirmar_seguro(sonda, f'{rotulo}/reload')
    afirmar_canonico(sonda, f'{rotulo}/reload', norma_limpa)
    ctx.close()

    # --- 3) Arquivo parcial continua recusado, sem execução ou troca da base ---
    ctx, page = abrir(browser, url)
    assert page.evaluate("() => {closeModal();window.__onbShown=true;S.onboarding.done=true;S.xssImportProbe='destination';return save();}") is True
    partial = importar_arquivo(page, estado_malicioso())
    assert partial['alerts'] and 'Arquivo parcial' in partial['alerts'][0], (rotulo, partial)
    assert partial['unchanged'] and not partial['executed'] and partial['images'] == 0, (rotulo, partial)
    assert not partial['confirmations'], 'parcial deve falhar antes do consentimento'

    # --- 4) Backup FULL v2 completo malicioso: assinatura válida, todos os roots
    # e FileReader real. Rejeitar o parcial acima não substitui testar o saneamento.
    payload = page.evaluate("""async malicious => {
      const full=JSON.parse(await dgBuildBackupBlob(2,'synthetic-xss-complete.json',
        '2026-10-06T12:00:00Z').text());
      const onboarding=full.state.onboarding;Object.assign(full.state,malicious);
      full.state.onboarding={...onboarding,...malicious.onboarding,done:true};
      full.state.xssImportProbe='signed malicious complete source';delete full.integrity;
      full.integrity={algorithm:'SHA-256',canonicalization:'JPW_SORTED_JSON_V1',
        checksum:dgBackupSha256(dgBackupCanonical(full))};
      if(dgBackupInspect(full).kind!=='FULL_V2')throw new Error('Fixture não completa');
      return full;
    }""", estado_malicioso())
    tampered = json.loads(json.dumps(payload))
    tampered['state']['params']['saldoIni'] = 77777
    rejected = importar_arquivo(page, tampered)
    assert rejected['alerts'] and 'checksum' in rejected['alerts'][0].lower(), (rotulo, rejected)
    assert rejected['unchanged'] and not rejected['executed'] and not rejected['confirmations'], rejected
    applied = importar_arquivo(page, payload)
    assert any('com sucesso' in message for message in applied['alerts']), (rotulo, applied)
    assert len(applied['confirmations']) == 1, (rotulo, applied)
    assert page.evaluate("S.xssImportProbe") == 'signed malicious complete source'
    assert page.evaluate("JSON.parse(localStorage.getItem(LSKEY)).xssImportProbe") == 'signed malicious complete source'
    assert page.evaluate("localStorage.getItem(LSKEY).includes('__JPW_XSS__')"), 'payload não pode sumir e produzir PASS vazio'
    sonda = sondar(page)
    afirmar_seguro(sonda, f'{rotulo}/import')
    afirmar_canonico(sonda, f'{rotulo}/import', norma_limpa)
    assert sonda['ordensFase0'] == 1, 'ordem legítima perdida no import real'
    page.reload(wait_until='load')
    page.wait_for_timeout(600)
    assert page.evaluate('S.xssImportProbe') == 'signed malicious complete source'
    sonda = sondar(page)
    afirmar_seguro(sonda, f'{rotulo}/import/reload')
    afirmar_canonico(sonda, f'{rotulo}/import/reload', norma_limpa)
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
    assert r['title'] == 'GRADE LEGADA 1' and r['faseNome'] == 'LEGACY 1', \
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


def f01_backup_contextual(browser, url):
    """F01 fixture: public commands create the period and its active ledger row.

    Only the disposable synthetic account registration is seeded. Financial
    facts, period, ledger identity and audit trail use their production writers.
    No financial policy or oracle is replaced.
    """
    ctx, page = abrir(browser, url)
    try:
        return page.evaluate("""async () => {
          closeModal();window.__onbShown=true;S.onboarding.done=true;
          S.accounts.push({forexAccountId:'F01-ACCOUNT',nome:'Conta sintética F01',
            tipo:'MESTRE',platformCurrency:'USD',platform:'MT5',platformLogin:'TEST-F01'});
          if(save()!==true)throw Error('F01 fixture: account save refused');
          const api=JPWForex.state,require=r=>{if(!r?.ok)throw Error(JSON.stringify(r));return r;};
          require(api.recordAccountPeriod({accountId:'F01-ACCOUNT',startedAt:'2026-09-01',
            currency:'USD',si:10000,openingBook:10000,source:'Synthetic F01 opening',
            activateCurrentPeriod:true},{reason:'Synthetic F01 period'}));
          require(api.selectOperationalAccount('F01-ACCOUNT'));
          const scope=api.operationalSelection();
          require(api.recordAccountLedger({...scope,action:'RECORDED',data:'2026-09-02',
            resultado:400,saldo:10400,nota:'Fechamento sintético F01'},
            {reason:'Synthetic F01 ledger'}));
          const full=JSON.parse(await dgBuildBackupBlob(2,'synthetic-f01.json',
            '2026-10-16T12:00:00Z').text());
          const period=full.state.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId];
          if(period.ledger.length!==1||period.ledgerEvents.length!==1)
            throw Error('F01 fixture: production commands did not create row/audit');
          return {full,scope,rowId:period.ledger[0].id,audit:period.ledgerEvents};
        }""")
    finally:
        ctx.close()


def f01_assinar(page, fixture, version, absent=False):
    """Recompute the real complete-backup checksum after changing ONE active row.

    The inert extension deliberately contains a nonnumeric `version`: validation
    is contextual, not a recursive rejection of every key named version. Audit
    snapshots retain exactly the bytes generated by the ledger command.
    """
    return page.evaluate("""({fixture,version,absent}) => {
      const full=structuredClone(fixture.full),scope=fixture.scope;
      const row=full.state.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId].ledger[0];
      if(absent)delete row.version;else row.version=version;
      row.f01CompatibleExtension={version:'<texto inerte>',retained:'F01-compatible-extension'};
      delete full.integrity;
      full.integrity={algorithm:'SHA-256',canonicalization:'JPW_SORTED_JSON_V1',
        checksum:dgBackupSha256(dgBackupCanonical(full))};
      return full;
    }""", {'fixture': fixture, 'version': version, 'absent': absent})


def f01_importar(page, payload):
    """Real FileReader/import; instrument attempted writes as well as final state.

    Returning to the same values is insufficient: a refused malicious backup
    must never ask for consent or call a local/session storage mutation.
    Instrumentation is restored in finally and cannot suppress a real write.
    """
    return page.evaluate("""async payload => {
      const state=JSON.stringify(S),snapshot=storage=>JSON.stringify(Object.fromEntries(
        Object.keys(storage).sort().map(key=>[key,storage.getItem(key)]))),
        local=snapshot(localStorage),session=snapshot(sessionStorage);
      const alerts=[],confirmations=[],writes=[],originalAlert=window.alert,
        originalConfirm=window.confirm,originals={};
      window.__JPW_XSS__=0;
      try{
        for(const method of ['setItem','removeItem','clear']){
          originals[method]=Storage.prototype[method];
          Storage.prototype[method]=function(...args){
            writes.push({method,area:this===localStorage?'local':'session',key:args[0]??null});
            return originals[method].apply(this,args);
          };
        }
        window.alert=message=>alerts.push(String(message));
        window.confirm=message=>{confirmations.push(String(message));return true;};
        importFullBackupFile(new File([JSON.stringify(payload)],'synthetic-f01.json',
          {type:'application/json'}));
        for(let i=0;i<400&&!alerts.length;i++)await new Promise(resolve=>setTimeout(resolve,10));
        await new Promise(resolve=>setTimeout(resolve,30));
        return {alerts,confirmations,writes,stateUnchanged:state===JSON.stringify(S),
          localUnchanged:local===snapshot(localStorage),sessionUnchanged:session===snapshot(sessionStorage),
          executed:window.__JPW_XSS__===1,
          images:document.querySelectorAll('img[src="x"]').length};
      }finally{
        window.alert=originalAlert;window.confirm=originalConfirm;
        for(const method of Object.keys(originals))Storage.prototype[method]=originals[method];
      }
    }""", payload)


def f01_ler_linha(page, fixture):
    return page.evaluate("""fixture => {
      const scope=fixture.scope,
        period=S.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId],
        row=period.ledger.find(r=>r.id===fixture.rowId);
      if(!row)throw Error('F01 fixture row disappeared');
      return {hasVersion:Object.prototype.hasOwnProperty.call(row,'version'),
        version:row.version??null,extension:row.f01CompatibleExtension,
        data:row.data,resultado:row.resultado,saldo:row.saldo,nota:row.nota,
        audit:period.ledgerEvents};
    }""", fixture)


def f01_sink_dom(page, unsafe_escape=False):
    """Unit DOM boundary, NOT the complete-backup integration proof above.

    The still-distributed JPWLedger.render compatibility API runs in a literal,
    test-only host because its former public Contabilidade host was removed.
    This characterizes that renderer, NOT the new Management UI. The complete
    import cases and the separate real-Management sink below cover live flows.
    Exact row/cell/financial/version checks and reader restoration stay intact.
    """
    return page.evaluate("""async ({payload,unsafeEscape}) => {
      const original=ledgerScopedRead,originalRenderer=window.JPWLedger.render,selected=ledgerUI.selected,
        month=ledgerUI.month,filter=ledgerUI.filter,
        stateBefore=JSON.stringify(S),diskBefore=localStorage.getItem(LSKEY);
      if(document.getElementById('ledgerBody'))throw Error('Compatibility fixture would duplicate an existing ledger host');
      const host=document.createElement('section');host.dataset.f01LedgerFixture='';
      host.innerHTML='<table><tbody id="ledgerBody"></tbody></table>';
      document.body.append(host);
      window.__JPW_XSS__=0;
      const row={id:'F01-SINK',accountId:'F01-ACCOUNT',periodId:'F01-SINK-PERIOD',currency:'USD',
        data:'2026-09-02',resultado:400,saldo:10400,referenceBalance:10000,
        nota:'Fechamento sintético F01',version:payload};
      let result;
      try{
        ledgerScopedRead=()=>({status:'OK',value:[structuredClone(row)]});
        ledgerUI.month='';ledgerUI.filter='';ledgerUI.selected=null;
        if(unsafeEscape){
          const source=originalRenderer.toString(),needle='esc(r.version)';
          if(source.split(needle).length!==2)throw Error('Expected exactly one real version escape to mutate');
          window.JPWLedger.render=eval('('+source.replace(needle,'String(r.version)')+')');
        }
        window.JPWLedger.render();
        await new Promise(resolve=>setTimeout(resolve,50));
        const body=document.getElementById('ledgerBody'),rows=body.querySelectorAll('tr'),
          cells=rows[0]?.querySelectorAll('td'),small=rows[0]?.querySelector('small'),
          live=[...body.querySelectorAll('*')].filter(el=>[...el.attributes].some(
            at=>/^on/i.test(at.name)&&at.value.includes('__JPW_XSS__')));
        result={rows:rows.length,cells:cells?.length||0,date:cells?.[0]?.textContent,
          resultText:cells?.[1]?.textContent,balanceText:cells?.[2]?.textContent,
          expectedResult:fmtForexMoney(400,{currency:'USD'}),
          expectedBalance:fmtForexMoney(10400,{currency:'USD'}),
          note:cells?.[4]?.textContent,versionText:small?.textContent,
          executed:window.__JPW_XSS__===1,images:body.querySelectorAll('img[src="x"]').length,
          handlers:live.length};
      }finally{
        ledgerScopedRead=original;window.JPWLedger.render=originalRenderer;ledgerUI.selected=selected;
        ledgerUI.month=month;ledgerUI.filter=filter;host.remove();
      }
      result.readerRestored=ledgerScopedRead===original&&window.JPWLedger.render===originalRenderer;
      result.fixtureRemoved=!document.querySelector('[data-f01-ledger-fixture]');
      result.stateUnchanged=stateBefore===JSON.stringify(S);
      result.diskUnchanged=diskBefore===localStorage.getItem(LSKEY);
      return result;
    }""", {'payload':PAYLOAD,'unsafeEscape':unsafe_escape})


def assert_f01_compat_sink(result):
    assert result['rows']==1 and result['cells']==6 and result['date']=='2026-09-02',result
    assert result['resultText']==result['expectedResult'] and result['balanceText']==result['expectedBalance'],result
    assert result['note']=='Fechamento sintético F01' and result['readerRestored'],result
    assert result['fixtureRemoved'] and result['stateUnchanged'] and result['diskUnchanged'],result
    assert not result['executed'] and result['images']==0 and result['handlers']==0,result
    assert result['versionText']=='v'+PAYLOAD,result


def f01_management_dom(page, fixture):
    """Real imported names/notes reach current Management controls as text.

    Version remains numeric in this integration case; Management deliberately
    does not show the compatibility renderer's version field. No reader,
    renderer, policy or financial writer is replaced here.
    """
    payload=f01_assinar(page,fixture,1)
    payload=page.evaluate("""({full,scope,name,note})=>{
      full.state.accounts.find(a=>a.forexAccountId===scope.accountId).nome=name;
      full.state.forex.accountContexts.accounts[scope.accountId].periods[scope.periodId].ledger[0].nota=note;
      delete full.integrity;full.integrity={algorithm:'SHA-256',canonicalization:'JPW_SORTED_JSON_V1',checksum:dgBackupSha256(dgBackupCanonical(full))};
      return full;
    }""",{'full':payload,'scope':fixture['scope'],'name':PAYLOAD,'note':PAYLOAD_ATTR})
    imported=f01_importar(page,payload)
    assert any('com sucesso' in m for m in imported['alerts']),imported
    assert not imported['executed'] and imported['images']==0,imported
    setup=page.evaluate("""scope=>{
      const target={accountId:scope.accountId,periodId:scope.periodId,year:2026},api=JPWManagementAnnual;
      return api.commands.savePlan({...target,startDate:'2026-09-01',annualTarget:0.25,daysPerWeek:5,monthsPerYear:12,excludedDates:[]},
        {token:api.queries.token(target),confirmOpening:true,reason:'Synthetic current Management XSS consumer fixture'});
    }""",fixture['scope'])
    assert setup['ok'] and setup['status']=='CONFIRMED',setup
    before=page.evaluate('({state:JSON.stringify(S),disk:localStorage.getItem(LSKEY),operational:JSON.stringify(JPWForex.state.operationalSelection())})')
    assert page.evaluate("JPWNavigation.navigate('management-accounting')")
    page.locator('#management [data-mg-account]').select_option(fixture['scope']['accountId'])
    page.locator('#management [data-mg-period]').select_option(fixture['scope']['periodId'])
    page.locator('#management [data-mg-year]').fill('2026')
    page.locator('#management [data-mg-year]').dispatch_event('change')
    row=page.locator('#management .mg-day[data-mg-date="2026-09-02"]')
    row.scroll_into_view_if_needed()
    assert row.is_visible() and row.locator('td,th').count()==11
    expected=page.evaluate("({result:new Intl.NumberFormat('pt-BR',{style:'currency',currency:'USD'}).format(400),balance:new Intl.NumberFormat('pt-BR',{style:'currency',currency:'USD'}).format(10400)})")
    assert expected['result'] in row.inner_text() and expected['balance'] in row.inner_text()
    assert page.locator('#management [data-mg-account] option:checked').inner_text()==PAYLOAD
    row.locator('[data-mg-detail]').click()
    page.locator('#mg-details-2026-09-02 [data-mg-action=edit-day]').click()
    assert page.locator('#management [data-mg-editor=day] input[name=note]').input_value()==PAYLOAD_ATTR
    result=page.evaluate("""()=>({
      executed:window.__JPW_XSS__===1,images:document.querySelectorAll('img[src="x"]').length,
      handlers:[...document.querySelectorAll('*')].filter(el=>[...el.attributes].some(at=>/^on/i.test(at.name)&&at.value.includes('__JPW_XSS__'))).length
    })""")
    assert not result['executed'] and result['images']==0 and result['handlers']==0,result
    page.locator('#management [data-mg-action=cancel-edit]').click()
    assert page.evaluate('({state:JSON.stringify(S),disk:localStorage.getItem(LSKEY),operational:JSON.stringify(JPWForex.state.operationalSelection())})')==before
    return {**result,'rows':1,'cells':11,'nameAsText':True,'noteAsValue':True,'cancelPreservesState':True}


def suite_f01(browser, url, rotulo):
    """F01 fixed IDs: integration import compatibility/refusal + DOM sink unit.

    Every case reports independently, so the unpatched baseline demonstrates
    both the missing structural guard and the live renderer sink in one RED run.
    No assertion is derived from the implementation's acceptance decision.
    """
    fixture=f01_backup_contextual(browser,url)
    failures=[]
    positive=[('F01-P01-ABSENT',None,True),('F01-P02-NULL',None,False),
              ('F01-P03-ZERO',0,False),('F01-P04-ONE',1,False),
              ('F01-P05-THREE',3,False),('F01-P06-MAX-SAFE',9007199254740991,False)]
    negative=[('F01-N01-HTML',PAYLOAD),('F01-N02-NUMERIC-STRING','1'),
              ('F01-N03-OBJECT',{'payload':PAYLOAD}),('F01-N04-ARRAY',[1]),
              ('F01-N05-TRUE',True),('F01-N06-FALSE',False),
              ('F01-N07-NEGATIVE',-1),('F01-N08-FRACTION',1.5),
              ('F01-N09-UNSAFE',9007199254740992),('F01-N10-EMPTY-STRING',''),
              ('F01-N11-UNSAFE-LARGE',1e100)]
    for case,version,absent in positive:
        ctx,page=abrir(browser,url)
        try:
            payload=f01_assinar(page,fixture,version,absent)
            result=f01_importar(page,payload)
            assert any('com sucesso' in m for m in result['alerts']),result
            assert len(result['confirmations'])==1 and result['writes'],result
            assert not result['executed'] and result['images']==0,result
            expected={'hasVersion':not absent,'version':version,
                      'extension':{'version':'<texto inerte>','retained':'F01-compatible-extension'},
                      'data':'2026-09-02','resultado':400,'saldo':10400,
                      'nota':'Fechamento sintético F01','audit':fixture['audit']}
            assert f01_ler_linha(page,fixture)==expected, f01_ler_linha(page,fixture)
            page.reload(wait_until='load');page.wait_for_timeout(600);wait_bootstrap(page)
            assert f01_ler_linha(page,fixture)==expected, f01_ler_linha(page,fixture)
            assert_fixture_requests(ctx)
            print(f'PASS {rotulo}/{case}: complete import and reload preserve row, extension and audit',flush=True)
        except AssertionError as error:
            failures.append(f'{rotulo}/{case}: {error}')
            print(f'FAIL {rotulo}/{case}: {error}',flush=True)
        finally:
            ctx.close()
    for case,version in negative:
        ctx,page=abrir(browser,url)
        try:
            payload=f01_assinar(page,fixture,version)
            result=f01_importar(page,payload)
            assert result['alerts'] and 'Backup inválido' in result['alerts'][0],result
            assert not result['confirmations'] and not result['writes'],result
            assert result['stateUnchanged'] and result['localUnchanged'] and result['sessionUnchanged'],result
            assert not result['executed'] and result['images']==0,result
            assert_fixture_requests(ctx)
            print(f'PASS {rotulo}/{case}: refused before consent and all storage mutations',flush=True)
        except AssertionError as error:
            failures.append(f'{rotulo}/{case}: {error}')
            print(f'FAIL {rotulo}/{case}: {error}',flush=True)
        finally:
            ctx.close()
    ctx,page=abrir(browser,url)
    try:
        result=f01_sink_dom(page)
        assert_f01_compat_sink(result)
        unsafe=f01_sink_dom(page,unsafe_escape=True)
        assert unsafe['images']>=1 and unsafe['handlers']>=1, 'Unsafe mutation did not reach the actual renderer sink'
        try:assert_f01_compat_sink(unsafe)
        except AssertionError:pass
        else:raise AssertionError('The exact same sink oracle accepted a renderer with version escaping disabled')
        assert_f01_compat_sink(f01_sink_dom(page))
        assert_fixture_requests(ctx)
        print(f'PASS {rotulo}/F01-D01-SINK: compatibility API keeps version as text in isolated literal host; not Management UI coverage',flush=True)
    except AssertionError as error:
        failures.append(f'{rotulo}/F01-D01-SINK: {error}')
        print(f'FAIL {rotulo}/F01-D01-SINK: {error}',flush=True)
    finally:
        ctx.close()
    ctx,page=abrir(browser,url)
    try:
        result=f01_management_dom(page,fixture)
        assert_fixture_requests(ctx)
        print(f'PASS {rotulo}/F01-D02-MANAGEMENT: real imported name/note remain text; financial values and cancel preserved',flush=True)
    except AssertionError as error:
        failures.append(f'{rotulo}/F01-D02-MANAGEMENT: {error}')
        print(f'FAIL {rotulo}/F01-D02-MANAGEMENT: {error}',flush=True)
    finally:
        ctx.close()
    return failures


def main():
    server, base = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            f01_failures=[]
            for rotulo, alvo in (('modular', 'index.html'),
                                 ('portatil', 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html')):
                suite_maliciosa(browser, base + alvo, rotulo)
                afirmar_mapa_de_liquidez_seguro(browser, base + alvo, rotulo)
                suite_legitima(browser, base + alvo, rotulo)
                f01_failures.extend(suite_f01(browser,base + alvo,rotulo))
            browser.close()
            assert not f01_failures, 'F01 regressions: '+ '\n'.join(f01_failures)
    finally:
        server.shutdown()
    print('IMPORT XSS OK — backup adulterado não executa nem injeta DOM ativo; '
          'metadata LEGACY é inerte, matriz histórica não altera registry/projeções e a base legítima '
          'atravessa intacta (modular e portátil).')


if __name__ == '__main__':
    main()
