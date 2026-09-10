#!/usr/bin/env python3
"""V11 documental: aceite explícito, histórico preservado e originais offline.

Navegadores isolados e dados sintéticos. Nenhuma regra financeira é substituída.
O hash do leitor fixa a extração aprovada; não há segunda fixture normativa.
"""
from pathlib import Path
import base64
import hashlib
import json
import re
import sys

sys.dont_write_bytecode = True
from playwright.sync_api import Error, sync_playwright
from dashboard_macro_test import boot as dashboard_boot, launch_browser, serve
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests

def boot(browser, url):
    context, page, observed = dashboard_boot(browser, url, prepare_context=install_bootstrap)
    wait_bootstrap(page)
    return context, page, observed


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tools/.artifacts/statute_documentary_test.json'
VERSION = 'V11.0+JPW-ANNEX-T03'
OLD_DATE = '2026-01-02 03:04:05'
READER_SHA256 = 'f96afc12cec8da07c9f315a63700eff6f152428ede5663c43ea5b0007f32edab'
DOCUMENTS = (
    ('docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf', 'application/pdf',
     '2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769'),
    ('docs/normative/ANEXO_PARAMETRICO_CANONICO.md', 'text/markdown',
     '6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23'),
)
SEED = '''({version,accepted}) => {
  closeModal(); window.__onbShown=true;
  window.__consentAlerts=[];
  window.alert=msg=>window.__consentAlerts.push(String(msg));
  S=structuredClone(DEFAULTS);
  const pr=getActiveRiskProfile('base');
  S.params={...S.params,inicio:'2026-09-01',saldoIni:10000,saldoAtu:10000,refM:pr.mensal,refA:pr.anual};
  S.period={...S.period,profile:'base'};
  S.phases.forEach(ph=>ph.orders=[]); S.ledger=[];
  S.onboarding={...S.onboarding,done:true,operador:'Operador Sintético',supervisor:'Supervisor Sintético',
    corretora:BROKER_PARTNERS.find(b=>!isPropFirm(b)).name,plataforma:TRADING_PLATFORMS[0].name,alavCorretora:'1:100',
    moedaBase:'USD',brokerLogin:'TEST-ONLY',investorPassword:'SYNTHETIC-ONLY',brokerServer:'Demo Synthetic',
    reserveFcrCurrent:'2000',reserveMonthlyExpenses:'100',reserveFeoCurrent:'1000',
    reserveSegregationAccepted:true,reserveDeficitAccepted:false,
    centralCashStatus:'Sim.',centralCashCustody:'Outra',centralCashCustodyOther:'Custódia sintética',centralCashMainPct:'100',
    fcrLiquidity:'D+0',feoLiquidity:'D+0',cashLedgerStatus:'Livro-razão patrimonial ativo',centralCashPolicyAccepted:true,
    epStatus:'Não se aplica a esta conta.',epNotes:'Conta sintética exclusivamente para teste local.',epRestrictiveAccepted:true,
    summaryAccepted:true,consentAccepted:accepted,consentVersion:version,
    consentDocument:version==='V10.0'?'Documento histórico V10':'Documento registrado da versão',
    consentAcceptedAt:'2026-01-02 03:04:05',consentOperator:'Operador Sintético'};
  S.dataGovernance.responsibility={accepted:true,acceptedAt:'2026-01-02 03:04:05',
    version:typeof DG_RESPONSIBILITY_VERSION!=='undefined'?DG_RESPONSIBILITY_VERSION:1};
  S.transitionLog=[{fase:'consentimento estatuto',ts:'2026-01-02T06:04:05Z',resumo:{consentAccepted:true,
    consentVersion:'V10.0',consentDocument:'Documento histórico V10',
    consentAcceptedAt:'2026-01-02 03:04:05',consentOperator:'Operador Sintético'}}];
  save(); render();
  window.__documentaryWrites=[];
  for(const method of ['setItem','removeItem','clear']){
    const original=Storage.prototype[method];
    Storage.prototype[method]=function(...args){
      if(this===localStorage) window.__documentaryWrites.push(method);
      return original.apply(this,args);
    };
  }
}'''
SNAPSHOT = '''() => ({state:JSON.stringify(S),writes:(window.__documentaryWrites||[]).length,
  storage:JSON.stringify(Object.fromEntries(Object.entries(localStorage).sort())),
  onboarding:structuredClone(S.onboarding),history:structuredClone(S.transitionLog),
  finance:JSON.stringify({params:S.params,phases:S.phases,cycleRealizado:S.cycleRealizado,
    ledger:S.ledger,period:S.period,quarantine:S.quarantine})})'''


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def click(page, element_id):
    page.evaluate('(id)=>document.getElementById(id).click()', element_id)


def snapshot(page):
    return page.evaluate(SNAPSHOT)


def no_writes(before, page, action):
    after = snapshot(page)
    assert before['state'] == after['state'], f'{action}: estado alterado'
    assert before['storage'] == after['storage'], f'{action}: localStorage alterado'
    assert before['writes'] == after['writes'], f'{action}: chamada de escrita no localStorage'


def reader_check(page):
    click(page, 'obEstatutoToggle')
    assert page.locator('#obEstatutoReader').is_visible(), 'leitor não abriu'
    reader = page.locator('#obEstatutoReader').text_content()
    assert sha256(reader.encode('utf-8')) == READER_SHA256, 'leitor diverge da extração aprovada'
    assert [int(n) for n in re.findall(r'^--- PAGE (\d+) ---$', reader, re.M)] == list(range(1, 126))
    assert reader.endswith((ROOT / DOCUMENTS[1][0]).read_text(encoding='utf-8')), 'Anexo integral ausente'
    assert 'motor financeiro legado ainda não foi adaptado' in page.locator('#modalBox').inner_text().lower()


def open_edit(page):
    page.evaluate("() => openOnboardingModal('edit','consent')")


def prepare_summary(page):
    click(page, 'modalConfirm')
    assert page.locator('#obSummaryAccept').count() == 1, page.evaluate('() => window.__consentAlerts')
    click(page, 'obSummaryAccept')
    assert not page.locator('#obSummaryConfirm').is_disabled()


def consent_case(browser, url, version, accepted, mode):
    context, page, errors = boot(browser, url)
    try:
        build = page.evaluate('() => JP_WEALTH_BUILD_ID')
        page.evaluate(SEED, {'version': version, 'accepted': accepted})
        before = snapshot(page)
        open_edit(page)
        assert page.locator('#obConsent').is_checked() == (version == VERSION and accepted)
        no_writes(before, page, 'abrir edição')
        if mode == 'readonly':
            reader_check(page)
            no_writes(before, page, 'abrir leitor')
            click(page, 'modalConfirm')
            assert page.locator('#obConsentErr').evaluate("el=>el.classList.contains('show')")
            no_writes(before, page, 'confirmar sem aceite')
            page.keyboard.press('Escape')
            no_writes(before, page, 'cancelar edição')
            page.evaluate("() => openSettingsModal('statute')")
            links = page.locator('#settingsOverlay a[href^="docs/normative/"]').evaluate_all(
                '(els)=>els.map(e=>({label:e.textContent,href:e.getAttribute("href")}))')
            assert all(any(link['href'] == path for link in links) for path, _, _ in DOCUMENTS), links
            assert any('V11.0' in link['label'] for link in links), links
            page.evaluate('() => closeSettingsModal()')
            no_writes(before, page, 'consultar configurações')
            open_edit(page)
            assert not page.locator('#obConsent').is_checked()
            page.keyboard.press('Escape')
            no_writes(before, page, 'reabrir/cancelar')
            page.reload(wait_until='load')
            page.wait_for_function('() => typeof openOnboardingModal==="function" && !!S.onboarding')
            loaded = page.evaluate('() => ({ob:S.onboarding,history:S.transitionLog})')
            for field in ('consentAccepted', 'consentVersion', 'consentDocument', 'consentAcceptedAt', 'consentOperator'):
                assert loaded['ob'][field] == before['onboarding'][field], f'boot reescreveu {field}'
            assert loaded['history'] == before['history']
        elif mode in ('accept', 'reuse'):
            if mode == 'accept':
                click(page, 'obConsent')
                no_writes(before, page, 'marcar aceite sem confirmar')
            prepare_summary(page)
            started = page.evaluate('() => Date.now()')
            click(page, 'obSummaryConfirm')
            finished = page.evaluate('() => Date.now()')
            after = snapshot(page)
            ob = after['onboarding']
            assert ob['consentAccepted'] is True and ob['consentVersion'] == VERSION
            assert 'V11.0' in ob['consentDocument'] and 'JPW-ANNEX-T03' in ob['consentDocument']
            assert ob['consentAcceptedAt']
            if mode == 'reuse':
                assert ob['consentAcceptedAt'] == OLD_DATE, 'aceite existente teve data renovada'
            else:
                assert re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', ob['consentAcceptedAt'])
                stamp = page.evaluate('value => new Date(value).getTime()', ob['consentAcceptedAt'])
                assert started // 1000 * 1000 <= stamp <= finished // 1000 * 1000, 'data fora da confirmação'
            assert after['history'][:len(before['history'])] == before['history'], 'histórico reescrito'
            assert after['finance'] == before['finance'], 'edição documental alterou estado financeiro'
            # save() já remove investorPassword recursivamente na baseline.
            # Só a máscara do NOVO log de edição pode diferir da memória; todo
            # o histórico anterior e os demais campos devem persistir exatamente.
            expected_history = json.loads(json.dumps(after['history']))
            assert len(expected_history) == len(before['history']) + 1
            assert expected_history[-1]['fase'] == 'edição formulário de início'
            assert expected_history[-1]['resumo']['investorPassword'] == '•••'
            expected_history[-1]['resumo']['investorPassword'] = ''
            stored_history = page.evaluate('() => JSON.parse(localStorage.getItem(LSKEY)).transitionLog')
            assert stored_history == expected_history, 'histórico não foi gravado integralmente'
            page.reload(wait_until='load')
            page.wait_for_function('() => typeof openOnboardingModal==="function" && !!S.onboarding')
            loaded = snapshot(page)
            for field in ('consentAccepted', 'consentVersion', 'consentDocument', 'consentAcceptedAt', 'consentOperator'):
                assert loaded['onboarding'][field] == ob[field], f'aceite não persistiu: {field}'
            assert loaded['history'] == expected_history, 'histórico confirmado não persistiu'
        elif mode == 'revoke_at_commit':
            click(page, 'obConsent')
            prepare_summary(page)
            # Omitir o change testa a guarda REAL no ato de gravação, não só o listener.
            page.evaluate("() => { document.getElementById('obConsent').checked=false; document.getElementById('obSummaryConfirm').click(); }")
            no_writes(before, page, 'aceite retirado antes de gravar')
            assert page.locator('#obConsentErr').evaluate("el=>el.classList.contains('show')")
        elif mode == 'new_unchecked':
            page.keyboard.press('Escape')
            page.evaluate("() => openOnboardingModal('new','consent')")
            assert not page.locator('#obConsent').is_checked(), 'novo período herdou aceite'
            no_writes(before, page, 'abrir novo período')
            page.keyboard.press('Escape')
            no_writes(before, page, 'cancelar novo período')
        else:
            assert mode == 'cancel'
            page.keyboard.press('Escape')
            no_writes(before, page, 'cancelar aceite pendente/sem versão')
        assert not errors['pageerror'] and not errors['console'], errors
        return {'build': build, 'version': version, 'accepted': accepted, 'case': mode, 'status': 'PASS'}
    finally:
        try:
            assert_fixture_requests(context)
        finally:
            context.close()


def document_checks(browser, url, result):
    base = url.removesuffix('index.html')
    context, page, errors = boot(browser, url)
    try:
        result['build'] = page.evaluate('() => JP_WEALTH_BUILD_ID')
        page.wait_for_function('() => !!navigator.serviceWorker.controller', timeout=30000)
        cached = page.evaluate('''async()=>{const c=await caches.open('jp-wealth-'+JP_WEALTH_BUILD_ID);
          return (await c.keys()).map(r=>r.url).filter(u=>u.includes('/docs/normative/'));}''')
        assert set(cached) == {base + path for path, _, _ in DOCUMENTS}, cached
        result['consultations'] = []
        for offline in (False, True):
            context.set_offline(offline)
            for path, mime, expected in DOCUMENTS:
                fetched = page.evaluate('''async path=>{const r=await fetch(path);const b=await r.arrayBuffer();
                  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(x=>x.toString(16).padStart(2,'0')).join('');
                  return {status:r.status,mime:r.headers.get('content-type'),sha256:hash};}''', path)
                assert fetched['status'] == 200 and fetched['sha256'] == expected and fetched['mime'].split(';', 1)[0] == mime, fetched
                navpage = context.new_page()
                responses, downloads = [], []
                navpage.on('download', lambda download: downloads.append(download))
                navpage.on('response', lambda r: responses.append({
                    'url': r.url, 'status': r.status, 'mime': r.headers.get('content-type', ''),
                    'worker': r.from_service_worker, 'type': r.request.resource_type}))
                try:
                    try:
                        response = navpage.goto(base + path, wait_until='commit', timeout=15000)
                        # CDP devolve o HTML interno do viewer PDF e texto já
                        # decodificado para Markdown. Integridade é medida no
                        # fetch e no DOWNLOAD REAL do mesmo path, abaixo.
                        view = navpage.evaluate('''() => ({mime:document.contentType,
                          appShell:!!window.JPWDashMacro || !!document.getElementById('dash') || !!document.getElementById('nav')})''')
                        assert view['mime'] == mime and not view['appShell'], 'documento virou app shell'
                    except Error as error:
                        # Chromium pode baixar certos MIME em vez de abri-los. Só o
                        # objeto Download real e seus bytes justificam esse resultado.
                        if 'Download is starting' not in str(error):
                            raise
                        if not downloads:
                            navpage.wait_for_event('download', timeout=15000)
                        assert len(downloads) == 1, 'navegação não produziu download'
                        assert sha256(Path(downloads[0].path()).read_bytes()) == expected
                    delivered = [r for r in responses if r['url'] == base + path and r['type'] == 'document']
                    assert delivered and all(r['status'] == 200 and r['mime'].split(';', 1)[0] == mime and r['worker'] for r in delivered), responses
                finally:
                    navpage.close()
                page.evaluate('''path=>{const a=document.createElement('a');a.id='statuteDownloadProbe';
                  a.href=path;a.download=path.split('/').pop();document.body.append(a);}''', path)
                try:
                    with page.expect_download(timeout=15000) as download_info:
                        click(page, 'statuteDownloadProbe')
                    download = download_info.value
                    downloaded = Path(download.path()).read_bytes()
                    assert sha256(downloaded) == expected and downloaded == (ROOT / path).read_bytes()
                    result['consultations'].append({'path': path, 'offline': offline, **fetched,
                        'navigation': 'PASS', 'appShell': False, 'downloadSHA256': sha256(downloaded)})
                finally:
                    page.evaluate("() => document.getElementById('statuteDownloadProbe').remove()")
        routepage = context.new_page()
        try:
            response = routepage.goto(base + 'non-document-probe', wait_until='commit')
            assert response.headers.get('content-type', '').startswith('text/html') and response.from_service_worker
            result['otherRouteUnchanged'] = True
        finally:
            routepage.close()
        assert not errors['pageerror'] and not errors['console'], errors
    finally:
        try:
            assert_fixture_requests(context)
        finally:
            context.close()

    portable = ROOT / 'dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html'
    context = browser.new_context(service_workers='block', viewport={'width': 390, 'height': 844}, accept_downloads=True)
    install_bootstrap(context)
    try:
        context.add_init_script('window.__onbShown=true;')
        context.set_offline(True)
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        # Fixtures nominais externas; arquivo, JS/CSS e documentos permanecem reais.
        page.goto(portable.as_uri(), wait_until='load')
        wait_bootstrap(page)
        page.wait_for_function('() => typeof openOnboardingModal==="function" && !!window.JPWDashMacro')
        assert page.evaluate('() => JP_WEALTH_BUILD_ID') == result['build']
        page.evaluate("() => {closeModal();openOnboardingModal('new','consent');}")
        reader_check(page)
        assert not page.locator('#obConsent').is_checked()
        page.evaluate('() => {closeModal();openSettingsModal("statute");}')
        result['standalone'] = {'file': True, 'offline': True, 'reader': 'PASS', 'sha256': sha256(portable.read_bytes()), 'downloads': []}
        for path, mime, expected in DOCUMENTS:
            anchor = page.locator(f'#settingsOverlay a[href^="data:{mime};"][download]:visible').first
            data = anchor.get_attribute('href')
            assert data.startswith('data:' + mime + ';') and ';base64,' in data
            embedded = base64.b64decode(data.split(',', 1)[1], validate=True)
            assert sha256(embedded) == expected and embedded == (ROOT / path).read_bytes()
            with page.expect_download(timeout=15000) as download_info:
                anchor.click()
            download = download_info.value
            downloaded = Path(download.path()).read_bytes()
            assert sha256(downloaded) == expected and downloaded == embedded
            assert download.suggested_filename == anchor.get_attribute('download')
            result['standalone']['downloads'].append({'path': path, 'sha256': expected, 'filename': download.suggested_filename, 'status': 'PASS'})
        assert not errors, errors
    finally:
        try:
            assert_fixture_requests(context)
        finally:
            context.close()


def main():
    report = {'status': 'RUNNING', 'consents': []}
    server = None
    try:
        for path, _, expected in DOCUMENTS:
            assert sha256((ROOT / path).read_bytes()) == expected, f'original aprovado alterado: {path}'
        server, url = serve()
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            try:
                for case in [('V10.0', True, 'readonly'), ('V10.0', True, 'accept'),
                             (VERSION, True, 'reuse'), ('V10.0', True, 'revoke_at_commit'),
                             ('', True, 'cancel'), (VERSION, False, 'cancel'), (VERSION, True, 'new_unchecked')]:
                    report['consents'].append(consent_case(browser, url, *case))
                document_checks(browser, url, report)
                assert {item['build'] for item in report['consents']} == {report['build']}, 'build mudou durante o teste'
                report['status'] = 'PASS'
            finally:
                browser.close()
    except Exception as error:
        report.update(status='FAIL', error=f'{type(error).__name__}: {error}')
        raise
    finally:
        if server:
            server.shutdown()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"STATUTE DOCUMENTARY OK — {report['build']}: 7 aceites, leitor aprovado, "
          '4 consultas PWA online/offline e 2 downloads standalone offline.')


if __name__ == '__main__':
    main()
