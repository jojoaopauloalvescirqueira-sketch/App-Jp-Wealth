#!/usr/bin/env python3
"""Real-browser batching counterproofs, nested under the existing visual gate ID.

Oracle: CHG-JPW-VISUAL-MEASUREMENT-CONTROLS-20261025. Main-document controls
only. Proxies delegate every DOM call; no geometry is synthesized or cached for
positive checks. The reference retains the original eight-call reading path.
"""
import argparse
from contextlib import contextmanager
from functools import partial
from hashlib import sha256
import json
from pathlib import Path
import threading
import traceback

from playwright.sync_api import sync_playwright
from notes_launcher_test import launch_options


FIXTURE = '''<!doctype html><style>
body{margin:0;font:14px Arial}#fixture{margin:30px;width:400px}
button{display:flex;align-items:center;justify-content:center;box-sizing:border-box;
 width:180px;height:44px;padding:0;border:0;margin:8px;background:#ddd;font:14px Arial}
svg{width:20px;height:20px}.pl-close{width:44px}
</style><div id="fixture"><button id="text"><span>Measured text</span></button>
<button id="icon" aria-label="Icon"><svg viewBox="0 0 20 20"><path d="M4 4L16 16M16 4L4 16"/></svg></button>
<button id="close" class="pl-close" aria-label="Close"><svg viewBox="0 0 20 20"><path d="M4 4L16 16M16 4L4 16"/></svg></button></div>'''


class LocatorProbe:
    def __init__(self, real, page, button=None, controls=False):
        self.real, self.page, self.button, self.controls = real, page, button, controls

    def nth(self, index):
        return LocatorProbe(self.real.nth(index), self.page,
                            index if self.controls else self.button)

    def locator(self, selector):
        return LocatorProbe(self.real.locator(selector), self.page, self.button)

    def call(self, method, *args):
        if self.button is not None:
            self.page.active = self.button
            self.page.calls.setdefault(self.button, []).append(method)
        value = getattr(self.real, method)(*args)
        if method == 'evaluate' and isinstance(value, dict) and 'geometry' in value:
            self.page.latest = (self, value['geometry'])
            self.page.inspections.append(value)
            if self.page.substitute is not None:
                return self.page.substitute
        return value

    def count(self):
        return self.call('count')

    def evaluate(self, *args):
        return self.call('evaluate', *args)

    def evaluate_all(self, *args):
        return self.call('evaluate_all', *args)

    def bounding_box(self):
        return self.call('bounding_box')


class PageProbe:
    def __init__(self, real, substitute=None):
        self.real, self.substitute = real, substitute
        self.calls, self.inspections = {}, []
        self.active, self.latest = None, None

    def locator(self, selector):
        self.active = None
        return LocatorProbe(self.real.locator(selector), self,
                            controls=selector.endswith(' button:visible'))

    def evaluate(self, *args):
        if self.active is not None:
            self.calls[self.active].append('double-RAF')
        return self.real.evaluate(*args)


@contextmanager
def immediate_snapshot_protocol(harness, probe):
    """Observe the private caller protocol, without adding an API to the oracle."""
    original = harness.centered

    def checked(locator, kind='text', close=False, *, measurement=None):
        assert probe.latest is not None, 'missing immediate real DOM snapshot'
        owner, fresh = probe.latest
        assert owner is locator and fresh is measurement, 'wrong/stale immediate real DOM snapshot'
        probe.latest = None  # Only the immediate caller may consume this snapshot.
        return original(locator, kind, close, measurement=measurement)

    harness.centered = checked
    try:
        yield
    finally:
        harness.centered = original


def reference_controls(page, harness, scope):
    """Pre-batching browser reads and decisions; intentionally no snapshot input."""
    controls = page.locator(scope + ' button:visible')
    assert controls.count() > 0
    results, observations = [], []
    for index in range(controls.count()):
        control = controls.nth(index)
        control.evaluate("el=>el.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'})")
        harness.planning.settle(page)
        kind = 'ink' if control.locator('svg').count() else 'text'
        is_close = control.evaluate("el=>el.matches('.pl-close,.risk-close')")
        data = harness.centered(control, kind, is_close)
        box = control.bounding_box()
        assert box and box['width'] >= 24 and box['height'] >= 24, ('nonzero accessible target', data)
        cuts = control.evaluate(r'''el=>{
          const b=el.getBoundingClientRect(),bad=[];
          for(let p=el.parentElement;p&&p!==document.body;p=p.parentElement){
            const r=p.getBoundingClientRect(),s=getComputedStyle(p);
            if(['auto','scroll','hidden','clip'].includes(s.overflowX)&&(b.left<r.left-.25||b.right>r.right+.25))bad.push('horizontal:'+p.className);
            if(['auto','scroll','hidden','clip'].includes(s.overflowY)&&(b.top<r.top-.25||b.bottom>r.bottom+.25))bad.push('vertical:'+p.className);
          }return bad;
        }''')
        assert not cuts, ('control cut by its owner', data, cuts)
        results.append(data)
        observations.append({'geometry': data, 'isClose': is_close, 'cuts': cuts})
    return results, observations


def refusal(action, expected):
    try:
        action()
    except AssertionError as error:
        assert expected in str(error), ('unexpected rejection', expected, str(error))
        return str(error)
    raise AssertionError('deliberate violation accepted: ' + expected)


def compare(page, harness, scope):
    original_probe = PageProbe(page)
    original, observations = reference_controls(original_probe, harness, scope)
    probe = PageProbe(page)
    with immediate_snapshot_protocol(harness, probe):
        batched = harness.controls_geometry(probe, scope)
    assert original == batched['controls'], 'original/batched real geometry differs'
    assert observations == probe.inspections, 'original/batched labels/svg/isClose/cuts differ'
    assert len(probe.calls) == len(original) > 0
    for calls in probe.calls.values():
        assert calls == ['evaluate', 'double-RAF', 'evaluate', 'count'], calls
    for calls in original_probe.calls.values():
        assert len(calls) == 8, calls
    return {'controls': len(original), 'original_calls': original_probe.calls,
            'batched_calls': probe.calls, 'geometry_and_decisions_equal': True}


def budget(page, harness):
    page.set_content(FIXTURE)
    probe = PageProbe(page)
    measured = harness.controls_geometry(probe, '#fixture')
    counts = {str(index): len(calls) for index, calls in probe.calls.items()}
    evidence = {'rpc_per_control': counts, 'calls': probe.calls,
                'measured_controls': len(measured['controls']),
                'excluded': 'scope/setup counts, reading order, selectors and inputs'}
    print(json.dumps({'budget_evidence': evidence}), flush=True)
    assert len(counts) == 3 and all(value <= 4 for value in counts.values()), (
        'at most4 real browser RPCs per button required', evidence)
    return evidence


def run(browser, harness, *, budget_only=False, planning_page=None):
    """Permanent synthetic mainframe negatives through the actual batched path."""
    context = browser.new_context(viewport={'width': 900, 'height': 700}, service_workers='block')
    try:
        page = context.new_page()
        page.set_default_timeout(5000)
        result = {'budget': budget(page, harness)}
        if budget_only:
            return result
        result['equivalence'] = compare(page, harness, '#fixture')
        if planning_page is not None:
            result['planning_mainframe_equivalence'] = compare(
                planning_page, harness, '#planning dialog[open]')
        changes = [
            ('text5px', "document.querySelector('#text span').style.transform='translateX(5px)'", 'inner content center exceeds2CSSpx'),
            ('svg5px', "document.querySelector('#icon path').setAttribute('transform','translate(5 0)')", 'inner content center exceeds2CSSpx'),
            ('close20px', "document.querySelector('#close').style.cssText='width:20px;height:20px'", '44px close'),
            ('ancestor_clipping', "document.querySelector('#fixture').style.cssText='width:40px;overflow:hidden'", 'control cut by its owner'),
            ('missing_content', "document.querySelector('#text').replaceChildren()", 'missing measurable text'),
        ]
        result['counterproofs'] = {}
        for name, mutation, message in changes:
            page.set_content(FIXTURE)
            page.evaluate(mutation)
            old = refusal(lambda: reference_controls(page, harness, '#fixture'), message)
            probe = PageProbe(page)
            with immediate_snapshot_protocol(harness, probe):
                new = refusal(lambda: harness.controls_geometry(probe, '#fixture'), message)
            result['counterproofs'][name] = {'original_rejection': old, 'batched_rejection': new}
        page.set_content(FIXTURE)
        for name, selector in [('zero_locator', '#absent'), ('multiple_locators', '#fixture button')]:
            result['counterproofs'][name] = refusal(lambda: harness.centered(page.locator(selector)), 'exactly one control required')
            snapshot = page.locator('#text').evaluate(harness.CONTENT_GEOMETRY)
            result['counterproofs'][name + '_with_snapshot'] = refusal(
                lambda: harness.centered(page.locator(selector), measurement=snapshot),
                'exactly one control required')
        result['counterproofs']['missing_scope'] = refusal(lambda: harness.controls_geometry(page, '#absent'), 'required open dialog missing')
        page.set_content('<div id="fixture"></div>')
        result['counterproofs']['missing_buttons'] = refusal(lambda: harness.controls_geometry(page, '#fixture'), 'dialog has no measured controls')
        page.set_content(FIXTURE)
        first = PageProbe(page)
        with immediate_snapshot_protocol(harness, first):
            valid = harness.controls_geometry(first, '#fixture')
        page.evaluate("document.querySelector('#text span').style.transform='translateX(5px)'")
        second = PageProbe(page)
        with immediate_snapshot_protocol(harness, second):
            result['counterproofs']['fresh_dom'] = refusal(lambda: harness.controls_geometry(second, '#fixture'), 'inner content center exceeds2CSSpx')
        before = valid['controls'][0]['text']['left']
        after = second.inspections[0]['geometry']['text']['left']
        assert abs(after - before - 5) < .01, ('DOM mutation must be remeasured', before, after)
        result['fresh_dom_text_shift_css_px'] = after - before
        # Deliberately substitute previously observed REAL snapshots. This proves
        # the instrumentation catches a broken private-caller protocol; it does
        # not claim centered authenticates arbitrary externally supplied dicts.
        for name, snapshot in [('stale_snapshot', first.inspections[0]),
                               ('wrong_control_snapshot', first.inspections[1])]:
            bad = PageProbe(page, substitute=snapshot)
            with immediate_snapshot_protocol(harness, bad):
                result['counterproofs'][name] = refusal(lambda: harness.controls_geometry(bad, '#fixture'), 'wrong/stale immediate real DOM snapshot')
        return result
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--budget-only', action='store_true')
    args = parser.parse_args()
    import ui_visual_quality_test as harness
    report = {'classification': 'NOT_RUN', 'source_sha256': {
        str(path.name): sha256(path.read_bytes()).hexdigest()
        for path in [Path(__file__), Path(harness.__file__)]}}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch_options())
            try:
                report['browser'] = browser.version
                if args.budget_only:
                    report['measurements'] = run(browser, harness, budget_only=True)
                else:
                    server = harness.BrowserFixtureServer(('127.0.0.1', 0),
                        partial(harness.planning.Quiet, directory=str(harness.ROOT)))
                    threading.Thread(target=server.serve_forever, daemon=True).start()
                    app_context = browser.new_context(viewport={'width': 700, 'height': 900}, service_workers='block')
                    try:
                        planning_page = harness.setup(app_context, f'http://127.0.0.1:{server.server_port}/index.html')
                        before = harness.financial(planning_page)
                        harness.start_write_probe(planning_page)
                        harness.planning.open_form(planning_page)
                        report['measurements'] = run(browser, harness, planning_page=planning_page)
                        assert harness.financial(planning_page) == before, 'measurement changed financial state'
                        report['writes'] = harness.no_writes(planning_page)
                        harness.assert_fixture_requests(app_context)
                    finally:
                        app_context.close()
                        server.shutdown()
                        server.server_close()
                report['classification'] = 'PASS'
            finally:
                browser.close()
    except AssertionError as error:
        report.update(classification='TEST_HARNESS_FAIL', error=str(error), trace=traceback.format_exc())
    except Exception as error:
        report.update(classification='ENVIRONMENT_ERROR', error=str(error), trace=traceback.format_exc())
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)
    return 0 if report['classification'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
