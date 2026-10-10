#!/usr/bin/env python3
"""Real synthetic PF field journeys: quota, concurrent tabs and recovery.

Quota and conflicts use the browser's actual localStorage. Only UNKNOWN uses a
one-shot read-back fault after an actual write; the production writer is intact.
This test is separate from the repository's existing validators and gates.
"""
import argparse
import functools
import hashlib
import json
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap
from dashboard_macro_test import launch_browser

ROOT = Path(__file__).resolve().parents[1]
MONTH = '2026-11'


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Server(ThreadingHTTPServer):
    request_queue_size = 128
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--label', default='candidate')
    args = parser.parse_args()
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    results, events = [], []
    server = Server(('127.0.0.1', 0), functools.partial(Quiet, directory=str(args.root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/index.html'

    def check(name, condition, observed, expected):
        results.append({'check': name, 'status': 'PASS' if condition else 'PRODUCT_FAIL',
                        'expected': expected, 'observed': observed})

    def screenshot(page, name):
        page.screenshot(path=str(args.artifact.parent / (args.label + '-' + name + '.png')),
                        full_page=True)

    with sync_playwright() as pw:
        browser = launch_browser(pw)

        def open_page(context):
            page = context.new_page()
            page.on('dialog', lambda dialog: (events.append({'type': 'dialog', 'text': dialog.message}), dialog.accept()))
            page.on('pageerror', lambda error: events.append({'type': 'pageerror', 'text': str(error)}))
            page.on('console', lambda message: events.append({'type': 'console', 'level': message.type, 'text': message.text}))
            page.on('requestfailed', lambda request: events.append({'type': 'requestfailed', 'url': request.url, 'failure': request.failure}))
            page.goto(url)
            wait_bootstrap(page)
            page.evaluate("closeModal(); window.__onbShown=true;")
            return page

        def context():
            ctx = browser.new_context(service_workers='block', viewport={'width': 1440, 'height': 1000})
            install_bootstrap(ctx)
            ctx.add_init_script('window.__onbShown=true;')
            return ctx

        def seed(page, kind='income'):
            return page.evaluate("""kind=>{
                S.onboarding.done=true;if(save()!==true)throw Error('fixture save refused');
                const month='2026-11';let r;
                if(kind==='income')r=pfActAddIncome(month,{name:'Confirmed synthetic income',projectedAmount:12500});
                if(kind==='expense')r=pfActAddExpense(month,{name:'Confirmed synthetic expense'});
                if(kind==='allocation')r=pfActAddAllocation(month,{label:'Confirmed synthetic allocation',amount:500});
                if(!r.ok)throw Error(JSON.stringify(r));
                JPWNavigation.navigate('finpes');JPWFin.ui.selectView('mensal');fbMonth=month;finpesBudgetRender();
                window.__pfObservedWrites=0;window.__pfActualSetItem=Storage.prototype.setItem;
                Storage.prototype.setItem=function(k,v){if(k===LSKEY)window.__pfObservedWrites++;return window.__pfActualSetItem.call(this,k,v);};
                return r.recordId;
            }""", kind)

        def snapshot(page):
            return page.evaluate("""()=>({raw:localStorage.getItem(LSKEY),pf:structuredClone(S.personalFinance),
                drafts:jpwWorkspaceDrafts().filter(d=>d.provider==='personal-finance-field'),
                writes:window.__pfObservedWrites,outcome:jpWealthPersistenceLastResult(),
                unknown:jpWealthPersistenceOutcomeIsUnknown()})""")

        # Correctly checksummed imported metadata can still contain forged
        # originalText/unconfirmedReference. Only the canonical rendered field
        # can supply the cancellation value; recovery must not submit it.
        for field, forged, pending, final_value in [
                ('name', 'FORGED ORIGINAL FROM IMPORT', 'Imported pending name', 'Confirmed after cancellation'),
                ('projectedAmount', '9999999,99', '333,33', '150,75')]:
            ctx = context()
            page = open_page(ctx)
            ident = seed(page)
            selector = f'[data-fi-id="{ident}"][data-fi-campo="{field}"]'
            original = page.locator(selector).input_value()
            before = snapshot(page)
            recovered = page.evaluate("""({selector,forged,pending})=>{
                const input=document.querySelector(selector),context=fbFieldIdentity(input,fbCurrentKey());
                const imported=jpwWorkspaceValidate({schemaVersion:2,preferences:{},drafts:[{
                    label:'Synthetic imported field',provider:'personal-finance-field',version:1,context,
                    baseReference:fbFieldBase(context),text:pending,originalText:forged,
                    unconfirmedReference:'forged noncanonical reference'}]}).drafts[0];
                window.__pfRecoveryEvents={input:0,change:0};
                for(const type of ['input','change'])document.querySelector('#finpesBudgetRoot').addEventListener(type,()=>__pfRecoveryEvents[type]++);
                return {item:imported,inspection:JPWWorkspaceDrafts.inspect(imported),result:JPWWorkspaceDrafts.reopen(imported)};
            }""", {'selector': selector, 'forged': forged, 'pending': pending})
            reopened = snapshot(page)
            displayed = page.locator(selector).input_value()
            recovery_events = page.evaluate('window.__pfRecoveryEvents')
            check(field + ': imported metadata cannot define cancellation or UNKNOWN reference',
                  recovered['inspection']['compatible'] and recovered['result']['ok']
                  and displayed == pending and len(reopened['drafts']) == 1
                  and reopened['drafts'][0]['originalText'] == original
                  and 'unconfirmedReference' not in reopened['drafts'][0]
                  and recovery_events == {'input': 0, 'change': 0}
                  and reopened['writes'] == before['writes'] and reopened['pf'] == before['pf']
                  and reopened['raw'] == before['raw'],
                  {'original': original, 'displayed': displayed, 'drafts': reopened['drafts'],
                   'events': recovery_events, 'inspection': recovered['inspection'], 'result': recovered['result']},
                  'Canonical rendered original, formatted 125,00 for money; discard imported UNKNOWN reference; no event or writer')
            page.locator(selector).press('Escape')
            page.locator(selector).press('Tab')
            cancelled = snapshot(page)
            check(field + ': Escape after imported recovery restores canonical display without writing',
                  page.locator(selector).input_value() == original and not cancelled['drafts']
                  and cancelled['writes'] == before['writes'] and cancelled['pf'] == before['pf']
                  and cancelled['raw'] == before['raw']
                  and (field != 'projectedAmount' or original == '125,00'),
                  {'value': page.locator(selector).input_value(), 'drafts': cancelled['drafts'], 'writes': cancelled['writes']},
                  'Escape/Tab preserve confirmed state and disk; money remains rendered in decimal units')
            screenshot(page, 'imported-cancel-' + field)
            page.locator(selector).fill('Another pending edit' if field == 'name' else '222,22')
            typing = snapshot(page)
            page.locator(selector).press('Escape')
            page.locator(selector).press('Tab')
            twice_cancelled = snapshot(page)
            check(field + ': typing after cancellation retains the canonical original',
                  len(typing['drafts']) == 1 and typing['drafts'][0]['originalText'] == original
                  and page.locator(selector).input_value() == original and not twice_cancelled['drafts']
                  and twice_cancelled['writes'] == before['writes'] and twice_cancelled['raw'] == before['raw']
                  and twice_cancelled['pf'] == before['pf'],
                  {'pending': typing['drafts'], 'value': page.locator(selector).input_value(), 'writes': twice_cancelled['writes']},
                  'Fresh local typing and Escape use canonical original; no imported metadata resurrected')
            page.locator(selector).fill(final_value)
            page.locator(selector).press('Tab')
            confirmed = snapshot(page)
            obsolete = page.evaluate('item=>({inspection:JPWWorkspaceDrafts.inspect(item),result:JPWWorkspaceDrafts.reopen(item)})', recovered['item'])
            after_obsolete = snapshot(page)
            check(field + ': newly confirmed context makes old imported draft incompatible',
                  confirmed['outcome']['status'] == 'CONFIRMED' and confirmed['writes'] == before['writes'] + 1
                  and not obsolete['inspection']['compatible'] and not obsolete['result']['ok']
                  and page.locator(selector).input_value() == final_value
                  and after_obsolete['writes'] == confirmed['writes'] and after_obsolete['raw'] == confirmed['raw']
                  and after_obsolete['pf'] == confirmed['pf'] and not after_obsolete['drafts'],
                  {'recovery': obsolete, 'value': page.locator(selector).input_value(), 'outcome': confirmed['outcome'], 'writes': after_obsolete['writes']},
                  'Real deliberate confirmation changes base; old recovery refuses without extra writes')
            ctx.close()

        # Fill a disposable origin to the actual browser quota; no refusal stub.
        for kind, prefix, field in [('income', 'fi', 'name'), ('expense', 'fe', 'name'), ('allocation', 'fa', 'label')]:
            ctx = context()
            page = open_page(ctx)
            ident = seed(page, kind)
            selector = f'[data-{prefix}-id="{ident}"][data-{prefix}-campo="{field}"]'
            typed = 'Pending synthetic ' + kind + ' ' + ('Q' * 512)
            page.locator(selector).fill(typed)
            before = snapshot(page)
            quota = page.evaluate("""()=>{
                const key='__jpw_synthetic_quota__';let low=0,high=6*1024*1024,failures=0,error='';
                while(high-low>1){const n=Math.floor((low+high)/2);
                    try{localStorage.setItem(key,'q'.repeat(n));low=n;}
                    catch(e){high=n;failures++;error=e.name;}}
                return {characters:low,failures,error};
            }""")
            page.locator(selector).press('Tab')
            page.wait_for_timeout(80)
            after = snapshot(page)
            value = page.locator(selector).input_value()
            focus = page.evaluate("()=>({tag:document.activeElement.tagName,data:{...document.activeElement.dataset}})")
            check(kind + ': actual quota refusal preserves field and draft',
                  quota['error'] == 'QuotaExceededError' and after['outcome']['status'] == 'REFUSED'
                  and after['outcome']['reason'] == 'WRITE_REFUSED' and value == typed
                  and any(d['text'] == typed for d in after['drafts'])
                  and before['raw'] == after['raw'] and before['pf'] == after['pf']
                  and focus['tag'] == 'INPUT',
                  {'quota': quota, 'value': value, 'drafts': after['drafts'], 'focus': focus,
                   'confirmedUnchanged': before['pf'] == after['pf'], 'durableUnchanged': before['raw'] == after['raw'], 'outcome': after['outcome']},
                  'REFUSED from real quota; typed text and draft retained; confirmed RAM/disk intact; Tab focus retained')
            screenshot(page, kind + '-quota')
            page.evaluate("fbGoTo('2027-01');fbGoTo('2026-11');finpesBudgetRender();")
            mounted = snapshot(page)
            check(kind + ': remount and month navigation preserve refusal without writes',
                  page.locator(selector).input_value() == typed and mounted['writes'] == after['writes']
                  and mounted['raw'] == after['raw'] and mounted['pf'] == after['pf'],
                  {'value': page.locator(selector).input_value(), 'writesBefore': after['writes'], 'writesAfter': mounted['writes']},
                  'Same text after navigation/remount; no attempted writes or materialized virtual month')
            if kind == 'income':
                captured = before['drafts'][0]
                page.locator(selector).focus()
                page.evaluate("window.__pfOuterEscapes=0;document.addEventListener('keydown',e=>{if(e.key==='Escape')window.__pfOuterEscapes++;});")
                page.locator(selector).press('Escape')
                page.locator(selector).press('Tab')
                cancelled = snapshot(page)
                check('explicit Escape cancellation discards only the field draft',
                      not cancelled['drafts'] and page.locator(selector).input_value() == 'Confirmed synthetic income'
                      and cancelled['writes'] == mounted['writes'] and cancelled['raw'] == mounted['raw']
                      and page.evaluate('window.__pfOuterEscapes') == 0,
                      {'value': page.locator(selector).input_value(), 'drafts': cancelled['drafts'], 'writes': cancelled['writes'],
                       'outerEscapeHandlersCalled': page.evaluate('window.__pfOuterEscapes')},
                      'Original field value restored; clear only pending draft; no save after Tab and no outer Escape activation')
                # Resetting the RAM provider models the adapter being reopened in a
                # fresh workspace. It does not touch the confirmed document.
                page.evaluate('fbPendingFields.clear();finpesBudgetRender();')
                recovered = page.evaluate("item=>({inspection:JPWWorkspaceDrafts.inspect(item),result:JPWWorkspaceDrafts.reopen(item)})", captured)
                reopened = snapshot(page)
                check('explicit compatible recovery reopens without submission',
                      recovered['inspection']['compatible'] and recovered['result']['ok']
                      and page.locator(selector).input_value() == typed and reopened['writes'] == cancelled['writes']
                      and reopened['raw'] == cancelled['raw'], recovered,
                      'Original reference matches; reopens field and focus without input/change/save')
                incompatible = page.evaluate("""item=>{
                    const wrong=structuredClone(item);wrong.context.month='2027-01';
                    return {context:JPWWorkspaceDrafts.inspect(wrong),base:JPWWorkspaceDrafts.inspect({...item,baseReference:'"different confirmed value"'})};
                }""", captured)
                check('incompatible recovery remains available only for review',
                      not incompatible['context']['compatible'] and not incompatible['base']['compatible'], incompatible,
                      'Wrong month or original value cannot overwrite an editor')
                page.evaluate("localStorage.removeItem('__jpw_synthetic_quota__');")
                confirmed_text = 'Confirmed deliberate revision'
                page.locator(selector).fill(confirmed_text)
                page.locator(selector).press('Tab')
                page.wait_for_timeout(80)
                confirmed = snapshot(page)
                check('CONFIRMED clears pending draft once',
                      confirmed['outcome']['status'] == 'CONFIRMED' and not confirmed['drafts']
                      and confirmed['pf']['months'][MONTH]['incomes'][0]['name'] == confirmed_text
                      and json.loads(confirmed['raw'])['personalFinance']['months'][MONTH]['incomes'][0]['name'] == confirmed_text
                      and confirmed['writes'] == reopened['writes'] + 1,
                      {'drafts': confirmed['drafts'], 'outcome': confirmed['outcome'], 'writes': confirmed['writes'], 'value': page.locator(selector).input_value()},
                      'One field command; confirmed RAM and disk agree; only this draft removed')
            ctx.close()

        # Two real tabs share storage. Tab B confirms a newer revision; tab A's
        # production stale-write guard must refuse without losing A's draft.
        ctx = context()
        page = open_page(ctx)
        ident = seed(page)
        selector = f'[data-fi-id="{ident}"][data-fi-campo="name"]'
        rival = open_page(ctx)
        rival.evaluate("JPWNavigation.navigate('finpes');JPWFin.ui.selectView('mensal');fbMonth='2026-11';finpesBudgetRender();")
        page.locator(selector).fill('Pending in first real tab')
        before = snapshot(page)
        rival.locator(selector).fill('Confirmed in second real tab')
        rival.locator(selector).press('Tab')
        rival.wait_for_timeout(80)
        rival_raw = rival.evaluate('localStorage.getItem(LSKEY)')
        page.locator(selector).press('Tab')
        page.wait_for_timeout(80)
        conflict = snapshot(page)
        check('two actual tabs refuse stale write and preserve pending text',
              conflict['outcome']['status'] == 'REFUSED' and conflict['outcome']['reason'] == 'CONFLICT'
              and page.locator(selector).input_value() == 'Pending in first real tab'
              and any(d['text'] == 'Pending in first real tab' for d in conflict['drafts'])
              and conflict['pf'] == before['pf'] and conflict['raw'] == rival_raw
              and conflict['writes'] == before['writes'],
              {'value': page.locator(selector).input_value(), 'drafts': conflict['drafts'], 'outcome': conflict['outcome'],
               'firstTabConfirmedRAMUnchanged': conflict['pf'] == before['pf'], 'secondTabDiskPreserved': conflict['raw'] == rival_raw,
               'firstTabSetItemCalls': conflict['writes']},
              'Actual second tab confirms; first tab CONFLICT refuses before setItem, retaining draft')
        screenshot(page, 'two-tabs-conflict')
        ctx.close()

        # An actual write followed by a single unavailable read-back reaches the
        # production UNKNOWN barrier. No replacement save()/pfMutate is used.
        ctx = context()
        page = open_page(ctx)
        ident = seed(page)
        selector = f'[data-fi-id="{ident}"][data-fi-campo="name"]'
        page.evaluate("""()=>{
            window.__pfActualGetItem=Storage.prototype.getItem;window.__pfFaultAfterWrite=false;
            const delegated=Storage.prototype.setItem;
            Storage.prototype.setItem=function(k,v){const r=delegated.call(this,k,v);if(k===LSKEY)window.__pfFaultAfterWrite=true;return r;};
            Storage.prototype.getItem=function(k){if(k===LSKEY&&window.__pfFaultAfterWrite){window.__pfFaultAfterWrite=false;throw Error('Synthetic one-shot read-back unavailable after actual write');}return window.__pfActualGetItem.call(this,k);};
        }""")
        page.locator(selector).fill('Attempted unknown synthetic revision')
        page.locator(selector).press('Tab')
        page.wait_for_timeout(80)
        unknown = snapshot(page)
        page.locator(selector).fill('Another edit awaiting verification')
        page.locator(selector).press('Tab')
        page.wait_for_timeout(80)
        blocked = snapshot(page)
        check('UNKNOWN preserves draft and blocks repeat writes',
              unknown['unknown'] and unknown['outcome']['status'] == 'UNKNOWN'
              and any(d['text'] == 'Attempted unknown synthetic revision' for d in unknown['drafts'])
              and page.locator(selector).input_value() == 'Another edit awaiting verification'
              and any(d['text'] == 'Another edit awaiting verification' for d in blocked['drafts'])
              and blocked['writes'] == unknown['writes'] and blocked['raw'] == unknown['raw'],
              {'first': unknown, 'blocked': blocked, 'value': page.locator(selector).input_value()},
              'UNKNOWN after actual write, no rollback claim; subsequent field change cannot retry; draft retained')
        page.evaluate("fbGoTo('2027-01');fbGoTo('2026-11');finpesBudgetRender();")
        remounted_unknown = snapshot(page)
        check('UNKNOWN remount preserves pending text without interpreting RAM as confirmed',
              page.locator(selector).input_value() == 'Another edit awaiting verification'
              and remounted_unknown['unknown'] and remounted_unknown['writes'] == blocked['writes']
              and remounted_unknown['raw'] == blocked['raw'] and remounted_unknown['pf'] == blocked['pf'],
              {'value': page.locator(selector).input_value(), 'drafts': remounted_unknown['drafts'],
               'writes': remounted_unknown['writes'], 'unknown': remounted_unknown['unknown']},
              'Own attempted RAM reference can remount draft; financial state and UNKNOWN barrier unchanged')
        screenshot(page, 'unknown-blocked')
        page.locator(selector).focus()
        page.locator(selector).press('Escape')
        page.locator(selector).press('Tab')
        cancelled_unknown = snapshot(page)
        check('Cancel under UNKNOWN affects only draft, preserving attempted facts and barrier',
              not cancelled_unknown['drafts'] and page.locator(selector).input_value() == 'Confirmed synthetic income'
              and cancelled_unknown['unknown'] and cancelled_unknown['writes'] == remounted_unknown['writes']
              and cancelled_unknown['raw'] == remounted_unknown['raw'] and cancelled_unknown['pf'] == remounted_unknown['pf'],
              {'value': page.locator(selector).input_value(), 'drafts': cancelled_unknown['drafts'],
               'writes': cancelled_unknown['writes'], 'unknown': cancelled_unknown['unknown']},
              'Original displayed value restored only in editor; no rollback of possible write or blind retry')
        imported_unknown = page.evaluate("""selector=>{
            const context=fbFieldIdentity(document.querySelector(selector),fbCurrentKey());
            const item=jpwWorkspaceValidate({schemaVersion:2,preferences:{},drafts:[{
                label:'Imported UNKNOWN journal',provider:'personal-finance-field',version:1,context,
                baseReference:fbFieldBase(context),text:'Unknown journal available to copy',
                originalText:'Forged journal original',unconfirmedReference:fbFieldBase(context)}]}).drafts[0];
            return {item,inspection:JPWWorkspaceDrafts.inspect(item),result:JPWWorkspaceDrafts.reopen(item)};
        }""", selector)
        after_imported_unknown = snapshot(page)
        check('imported UNKNOWN journal remains for consultation/copy even if attempted RAM matches',
              not imported_unknown['inspection']['compatible'] and not imported_unknown['result']['ok']
              and imported_unknown['item']['text'] == 'Unknown journal available to copy'
              and not after_imported_unknown['drafts'] and after_imported_unknown['unknown']
              and after_imported_unknown['writes'] == cancelled_unknown['writes']
              and after_imported_unknown['raw'] == cancelled_unknown['raw']
              and after_imported_unknown['pf'] == cancelled_unknown['pf'],
              {'recovery': imported_unknown, 'unknown': after_imported_unknown['unknown'],
               'drafts': after_imported_unknown['drafts'], 'writes': after_imported_unknown['writes']},
              'Actual read-back UNKNOWN is not a confirmed base; imported text remains inspectable, no reopen or writer')
        ctx.close()

        # Copy correction is checked in the visible native Settings card, both
        # themes and desktop/mobile. Opening, preview and Cancel must not persist.
        for width, height in [(1440, 1000), (390, 844)]:
            for theme in ['light', 'dark']:
                ctx = context()
                page = open_page(ctx)
                page.set_viewport_size({'width': width, 'height': height})
                page.evaluate("theme=>{S.theme=theme;applyTheme();openSettingsModal('interface');}", theme)
                page.locator('#mvpNotesAppearanceHelp').scroll_into_view_if_needed()
                help_text = page.locator('#mvpNotesAppearanceHelp').inner_text()
                geometry = page.locator('#mvpNotesAppearanceHelp').evaluate("""el=>{
                    const r=el.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,
                    clientWidth:el.clientWidth,scrollWidth:el.scrollWidth,viewport:innerWidth};
                }""")
                check(f'Notes help {width}px {theme}: coverage and layout',
                      'Backup Completo inclui a aparência confirmada' in help_text
                      and 'Finalizar sessão a preserva' in help_text and 'Markdown' in help_text
                      and 'Cancelar ou sair de Configurações descarta a prévia' in help_text
                      and geometry['left'] >= -1 and geometry['right'] <= width + 1
                      and geometry['scrollWidth'] <= geometry['clientWidth'] + 1,
                      {'text': help_text, 'geometry': geometry},
                      'Complete Backup/Finalizar preserve saved preference; Markdown is partial; preview Cancel; text contained')
                screenshot(page, f'notes-help-{width}-{theme}')
                before_preview = page.evaluate('({raw:localStorage.getItem(LSKEY),appearance:localStorage.getItem(MVP_NOTES_APPEARANCE_KEY)})')
                page.locator('#mvpNotesAppearanceTheme').select_option('dark' if theme == 'light' else 'light')
                page.locator('#mvpNotesAppearanceCancel').click()
                after_preview = page.evaluate('({raw:localStorage.getItem(LSKEY),appearance:localStorage.getItem(MVP_NOTES_APPEARANCE_KEY)})')
                check(f'Notes preview Cancel {width}px {theme}: no persistence', before_preview == after_preview,
                      {'before': before_preview, 'after': after_preview}, 'Preview and Cancel leave saved data/preferences unchanged')
                ctx.close()
        browser.close()

    server.shutdown()
    server.server_close()
    errors = [event for event in events if event['type'] in ('pageerror', 'requestfailed')]
    check('browser has no script errors or failed bootstrap requests', not errors, errors,
          'No script errors or unexpected/failed requests')
    summary = {name: sum(row['status'] == name for row in results) for name in ('PASS', 'PRODUCT_FAIL')}
    rc = 1 if summary['PRODUCT_FAIL'] else 0
    receipt = {'argv': sys.argv, 'exitCode': rc, 'durationSeconds': round(time.monotonic() - started, 3),
               'root': str(args.root.resolve()), 'label': args.label, 'viewport': {'width': 1440, 'height': 1000},
               'hashes': {name: hashlib.sha256((args.root / name).read_bytes()).hexdigest() for name in
                          ('src/js/20-ui/18-finpes-budget.js', 'src/js/10-domain/12-personal-finance.js',
                           'src/js/00-core/04-persistence.js', 'index.html')},
               'scope': 'Synthetic real Chromium UI. Real localStorage quota and two actual tabs; one-shot read-back fault only for UNKNOWN. Modular candidate; portable handled by final full gate.',
               'results': results, 'summary': summary, 'events': events}
    args.artifact.write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    print(json.dumps({'summary': summary, 'artifact': str(args.artifact), 'exitCode': rc}, ensure_ascii=False))
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
