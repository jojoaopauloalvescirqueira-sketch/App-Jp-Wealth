#!/usr/bin/env python3
"""Approved upcoming-session contract against the real calendar and stable consultation DOM.
Synthetic calendars only; the view is mounted directly to isolate it from renderer/camera timers.
"""
import argparse
import hashlib
import json
import os
import traceback
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
START = 1792065600000
MINUTE = 60000
HOUR = 60 * MINUTE
SOURCES = ['src/js/40-app/31-market-hours/01-sessions.js', 'src/js/40-app/31-market-hours/03-view.js', 'src/styles/app.css']


def catalog():
    venues = []

    def add(ident, name, spans, second=None):
        def group(parts, gid='cash'):
            periods = []
            for start, end, phase, *window in parts:
                period = dict(startUtc=START+start, endUtc=START+end, phase=phase, reason=phase)
                if window:
                    period['transitionWindow'] = dict(earliestUtc=START+window[0], latestUtc=START+end, nextPhase='continuous')
                periods.append(period)
            return dict(id=gid, label='Ações sintéticas', coverage=dict(fromUtc=START+parts[0][0], untilUtc=START+parts[-1][1], verifiedAt='2026-10-15', sourceIds=['s']), periods=periods)
        groups = [group(spans)]
        if second:
            groups.append(group(second, 'secondary'))
        venues.append(dict(id=ident, name=name, city='Cidade '+ident, country='Teste', region='Teste', timeZone='UTC', lat=0, lng=0, groups=groups))
    end = 3 * 24 * HOUR
    add('b3', 'B3', [(-HOUR, end, 'continuous')])
    add('later', 'Later', [(-HOUR, 2*HOUR+15*MINUTE, 'closed'), (2*HOUR+15*MINUTE, end, 'continuous')])
    add('resume', 'Resume', [(-HOUR, 0, 'continuous'), (0, 25*MINUTE, 'break'), (25*MINUTE, end, 'continuous')])
    add('boundary', 'Boundary', [(-HOUR, 24*HOUR, 'closed'), (24*HOUR, end, 'continuous')])
    add('outside', 'Outside', [(-HOUR, 24*HOUR+1, 'closed'), (24*HOUR+1, end, 'continuous')])
    add('straddling', 'Straddling', [(-HOUR, 24*HOUR+1000, 'auction', 24*HOUR-1000), (24*HOUR+1000, end, 'continuous')])
    add('uncertain', 'Uncertain', [(-HOUR, MINUTE+30000, 'auction', 30000), (MINUTE+30000, end, 'continuous')])
    add('active-window', 'Active window', [(-HOUR, 5000, 'auction', -5000), (5000, end, 'continuous')])
    add('active-resume', 'Active resume', [(-HOUR, -MINUTE, 'continuous'), (-MINUTE, 6000, 'auction', 0), (6000, end, 'continuous')])
    add('tie-b', 'Tie B', [(-HOUR, 25*MINUTE, 'closed'), (25*MINUTE, end, 'continuous')])
    add('tie-a', 'Tie A', [(-HOUR, 25*MINUTE, 'closed'), (25*MINUTE, end, 'continuous')])
    add('blocked', 'Blocked', [(-HOUR, MINUTE, 'closed'), (MINUTE, 2*MINUTE, 'unknown'), (2*MINUTE, 3*MINUTE, 'closed'), (3*MINUTE, end, 'continuous')])
    add('unknown', 'Unknown', [(-HOUR, end, 'unknown')])
    add('partial', 'Partial unknown', [(-HOUR, end, 'continuous')], [(-HOUR, end, 'unknown')])
    add('soon', 'Soon', [(-HOUR, 2000, 'closed'), (2000, end, 'continuous')])
    for i in range(35):
        add('open'+str(i), 'Open '+str(i), [(-HOUR, end, 'continuous')])
    return dict(schemaVersion=1, tzdbVersion='synthetic-UTC', sources=[dict(id='s', title='Fonte sintética', url='https://example.org/synthetic', publishedAt=None, verifiedAt='2026-10-15')], venues=venues)


def run(args):
    out = (ROOT / args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    fixture = out / 'fixture.html'
    fixture.write_text('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="'+(ROOT/SOURCES[-1]).as_uri()+'"></head><body><main style="grid-area:main;min-width:0;padding:16px"><div id="host"></div></main>'+''.join('<script src="'+(ROOT/p).as_uri()+'"></script>' for p in SOURCES[:-1])+'<script>window.__now='+str(START)+';window.__catalog=JPWMarketSessions.prepare('+json.dumps(catalog())+');window.__selected="b3";window.__selections=[];window.__view=JPWMarketHoursView.create(document.querySelector("#host"),__catalog,(id,origin)=>{__selected=id;__selections.push({id,origin});__render(__now)});window.__render=now=>{__now=now;__view.render(JPWMarketSessions.at(__catalog,now),__selected)};__render(__now);</script></body></html>')
    result = dict(status='PRODUCT_FAIL', checks=[], failures=[], errors=[], screenshots=[], sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES})
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('JP_WEALTH_CHROMIUM'))
        ctx = browser.new_context(viewport=dict(width=1280, height=900), reduced_motion='reduce', service_workers='block')
        ctx.set_offline(True)
        page = ctx.new_page()
        page.on('pageerror', lambda e:result['errors'].append(str(e)))

        def check(name, fn):
            if args.only and args.only not in name:
                return
            page.set_viewport_size(dict(width=1280, height=900))
            page.goto(fixture.as_uri())
            try:
                fn()
                result['checks'].append(name)
            except Exception:
                result['failures'].append(dict(name=name, detail=traceback.format_exc()))

        def ids(group):
            return page.locator('[data-mh-group='+group+'] [data-venue-id]:not([hidden])').evaluate_all('es=>es.map(e=>e.dataset.venueId)')

        def initial():
            assert page.locator('[data-mh-quick]').evaluate_all('es=>es.map(e=>e.dataset.mhQuick)') == ['open', 'all', 'unknown']
            assert page.locator('[data-mh-quick=open]').get_attribute('aria-pressed') == 'true'
            assert page.locator('[data-mh=detail-title]').inner_text() == 'B3'
            assert page.locator('[data-mh-quick=open]').inner_text() == 'Abertas 36'
            assert page.locator('[data-mh=summary]').inner_text() == '36 bolsas abertas agora'
            assert ids('upcoming') == ['active-window', 'active-resume', 'soon', 'uncertain', 'resume', 'tie-b', 'tie-a', 'later', 'boundary']
            for ident in ['outside', 'straddling', 'blocked', 'unknown', 'partial']:
                assert page.locator('[data-venue-id='+ident+']').is_hidden(), ident
            page.locator('[data-mh-quick=all]').click()
            assert page.locator('[data-mh-group=upcoming]').is_hidden()
            assert page.locator('[data-venue-id]').count() == len(catalog()['venues'])
            assert page.locator('[data-venue-id=outside]').is_visible()
            page.locator('[data-mh-quick=unknown]').click()
            assert page.locator('[data-mh-group=upcoming]').is_hidden()
            assert ids('unknown') == ['unknown', 'partial']
        check('open default, pane order, current-only counts, 24h inclusive limit and stable upcoming ordering', initial)

        def labels():
            assert page.locator('[data-venue-id=later] .mh-next').inner_text() == 'Abre em 2h15min'
            assert page.locator('[data-venue-id=resume] .mh-next').inner_text() == 'Retoma em 25min'
            assert page.locator('[data-venue-id=uncertain] .mh-next').inner_text() == 'Abre entre 30s e 1min30s'
            for ident in ['active-window', 'active-resume']:
                assert page.locator('[data-venue-id='+ident+'] .mh-next').inner_text() == 'Janela de abertura em andamento'
            assert page.locator('[data-venue-id=later] .mh-next').is_visible()
            assert page.locator('[data-venue-id=b3] .mh-next').is_hidden()
            page.evaluate('__render(__now+30000)')
            assert page.locator('[data-venue-id=uncertain] .mh-next').inner_text() == 'Janela de abertura em andamento'
            assert not page.locator('[data-mh-group=upcoming]').inner_text().find('em -') >= 0
        check('duration labels preserve exact resume, both uncertain bounds and literal in-progress text', labels)

        def filters():
            page.locator('[data-mh=search]').fill('resume')
            assert ids('open') == [] and ids('upcoming') == ['active-resume', 'resume']
            page.locator('[data-mh=phase-options] summary').click()
            page.locator('[data-mh=filter]').select_option('break')
            assert ids('upcoming') == ['resume']
            page.locator('[data-mh=search]').fill('b3')
            assert page.locator('[data-mh=empty]').is_visible()
            assert page.locator('[data-mh=upcoming-empty]').is_hidden(), 'Unmatched additional filters have one search state, not a second calendar-empty message'
            assert page.locator('[data-mh=upcoming-empty]').inner_text() == 'Nenhuma abertura confirmada nas próximas 24 horas'
            assert page.locator('[data-mh=detail-title]').inner_text() == 'B3'
            page.locator('[data-mh=show-selected]').click()
            assert page.locator('[data-mh-quick=all]').get_attribute('aria-pressed') == 'true'
            assert page.locator('[data-mh=search]').input_value() == ''
            assert page.locator('[data-mh=filter]').input_value() == 'all'
            assert page.locator('[data-venue-id=b3] button').evaluate('e=>e===document.activeElement')
        check('search and phase affect both open sections, exact upcoming empty and explicit reveal preserve selection', filters)

        def migration():
            page.locator('[data-venue-id=soon] button').click()
            page.evaluate('window.__row=document.querySelector("[data-venue-id=soon]");window.__button=__row.querySelector("button");document.querySelector(".mh-table-wrap").scrollTop=180;window.__scroll=document.querySelector(".mh-table-wrap").scrollTop')
            page.evaluate('__render(__now+3000)')
            assert page.evaluate('__row===document.querySelector("[data-venue-id=soon]") && __button===document.activeElement')
            assert page.evaluate('__row.parentElement.dataset.mhGroup') == 'open'
            assert page.evaluate('document.querySelector(".mh-table-wrap").scrollTop') == page.evaluate('__scroll')
            assert page.locator('[data-venue-id=soon]').get_attribute('data-selected') == 'true'
            assert page.locator('[data-mh=detail-title]').inner_text() == 'Soon'
            assert page.locator('[data-venue-id=soon]').count() == 1
            page.set_viewport_size(dict(width=390, height=844))
            page.wait_for_function('document.querySelector(".market-hours").dataset.compact==="true"')
            page.locator('[data-venue-id=resume] button').click()
            page.locator('[data-mh=search]').fill('Resume')
            page.evaluate('document.querySelector("[data-mh=search]").setSelectionRange(2,4);__render('+str(START+24*MINUTE)+')')
            assert page.locator('[data-mh=search]').evaluate('e=>e===document.activeElement && e.selectionStart===2 && e.selectionEnd===4')
            page.locator('[data-venue-id=resume] button').focus()
            page.evaluate('window.__resume=document.querySelector("[data-venue-id=resume]");window.__resumeButton=__resume.querySelector("button");__render('+str(START+25*MINUTE)+')')
            assert page.evaluate('__resume===document.querySelector("[data-venue-id=resume]") && __resumeButton===document.activeElement')
            assert page.evaluate('document.querySelector(".mh-inline-detail").previousElementSibling===__resume')
            assert page.locator('[data-mh=detail-title]').inner_text() == 'Resume'
            assert page.locator('[data-venue-id=resume]').count() == 1
            page.screenshot(path=str(out/'upcoming-mobile.png'))
            result['screenshots'].append(str(out/'upcoming-mobile.png'))
        check('upcoming entry migrates once preserving row, focused button, selection, scroll and compact inline detail', migration)

        def empty_and_layout():
            page.evaluate('__render('+str(START+3*24*HOUR)+')')
            assert page.locator('[data-mh=upcoming-empty]').is_visible()
            # Approved minimalism distinguishes no confirmed opening from an
            # unmatched additional search; expiry remains explicitly unknown.
            assert page.locator('[data-mh=empty]').is_hidden()
            assert page.locator('[data-mh=detail-title]').inner_text() == 'B3'
            for width in [320,390,800,1280]:
                page.set_viewport_size(dict(width=width,height=900))
                page.wait_for_timeout(40)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), str(width)
            page.screenshot(path=str(out/'upcoming-empty.png'))
            result['screenshots'].append(str(out/'upcoming-empty.png'))
        check('expired calendar has honest empty sections and no responsive horizontal overflow', empty_and_layout)
        assert result['checks'] or result['failures'], 'empty test selection'
        if not result['failures'] and not result['errors']:
            result['status'] = 'PASS'
        (out/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        browser.close()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status']=='PASS' else 1


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out-dir', default='tools/.artifacts/market-hours/noon-openings-20261016/view')
    parser.add_argument('--only', default='')
    raise SystemExit(run(parser.parse_args()))
