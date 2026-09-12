#!/usr/bin/env python3
"""A11: canonical context, unchanged metrics and no navigation side effects.

Expectations fixed before implementation. --baseline records previous behavior;
it is not a PASS of the new requirement. Synthetic profiles; nominal fixtures.
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_bootstrap_fixture import install_bootstrap, wait_bootstrap, assert_fixture_requests
from dashboard_forex_relocation_test import serve
from dashboard_macro_test import launch_browser

ROOT = Path(__file__).resolve().parents[1]


def run(root, baseline=False):
    server, url = serve(root)
    observations = []
    try:
        with sync_playwright() as p:
            browser = launch_browser(p)
            for mode, width, theme in [('sidebar',1440,'light'),('topbar',1440,'dark'),
                                       ('sidebar',390,'dark'),('topbar',390,'light')]:
                context = browser.new_context(viewport={'width':width,'height':960}, service_workers='block')
                install_bootstrap(context)
                context.add_init_script("""window.__onbShown=true;
                    window.__a11Timers=0; const interval=window.setInterval;
                    window.setInterval=function(...a){window.__a11Timers++;return interval.apply(this,a)};""")
                page = context.new_page()
                errors = []
                page.on('pageerror',lambda e: errors.append(str(e)))
                page.goto(url); wait_bootstrap(page)
                page.evaluate("([mode,theme])=>{mountNavigationLayout(mode);S.theme=theme;applyTheme();S.params.saldoAtu=10240;S.params.inicio='2026-09-01';render()}",[mode,theme])
                before = page.evaluate("() => ({state:JSON.stringify(S),storage:JSON.stringify({...localStorage}),timers:__a11Timers})")
                page.evaluate("""() => {window.__a11Computes=0;window.__a11Saves=0;
                    const c=compute,s=save;compute=function(...a){__a11Computes++;return c.apply(this,a)};
                    save=function(...a){__a11Saves++;return s.apply(this,a)};
                    window.__a11Nodes=[...document.querySelectorAll('#gdContextRow [id]')];}""")
                for route in ['forex-overview','dashboard','research-forex','personal-finance','alladin'] * 3:
                    assert page.evaluate('(r)=>JPWNavigation.navigate(r)',route)
                    row = page.locator('#gdContextRow')
                    visible = row.is_visible()
                    expected = route == 'forex-overview'
                    if not baseline:
                        assert visible == expected, (route,visible)
                        assert row.evaluate('(e)=>e.hidden===e.inert')
                        assert row.evaluate('(e)=>e.getBoundingClientRect().height') > 0 if expected else row.evaluate('(e)=>e.getBoundingClientRect().height') == 0
                    observations.append({'mode':mode,'width':width,'theme':theme,'route':route,'bar_visible':visible,'compute_calls':page.evaluate('() => __a11Computes')})
                assert page.evaluate("() => __a11Nodes.every(n=>n===document.getElementById(n.id))")
                assert page.locator('#gdContextRow').count() == 1
                after = page.evaluate("() => ({state:JSON.stringify(S),storage:JSON.stringify({...localStorage}),timers:__a11Timers})")
                assert before == after, 'navigation changed state/storage/timer count'
                assert page.evaluate('() => __a11Saves===0')
                # Existing render feeds phase and metrics even while hidden. Return
                # must show those canonical values without calculating a second set.
                page.evaluate("() => {S.params.saldoAtu=12050;render();window.__a11Expected={equity:document.getElementById('hdrEquity').textContent,phase:document.getElementById('hPhaseLbl').textContent};__a11Computes=0;__a11Saves=0;JPWNavigation.navigate('forex-overview')}")
                assert page.evaluate("() => document.getElementById('hdrEquity').textContent===__a11Expected.equity && document.getElementById('hPhaseLbl').textContent===__a11Expected.phase")
                assert page.evaluate('() => __a11Saves===0')
                assert page.evaluate("() => document.documentElement.scrollWidth<=innerWidth+1"), 'horizontal overflow'
                assert not errors, errors
                assert_fixture_requests(context)
                context.close()
            browser.close()
    finally:
        server.shutdown()
    return {'classification':'OBSERVED_BASELINE' if baseline else 'PASS','observations':observations,'count':len(observations)}


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--baseline',action='store_true');parser.add_argument('--output',type=Path);parser.add_argument('--baseline-evidence',type=Path)
    args=parser.parse_args()
    result=run(args.root,args.baseline)
    if args.baseline_evidence:
        old=json.loads(args.baseline_evidence.read_text())
        assert [r['compute_calls'] for r in old['observations']]==[r['compute_calls'] for r in result['observations']], 'new calculation calls introduced'
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
