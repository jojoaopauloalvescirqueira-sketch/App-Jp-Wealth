#!/usr/bin/env python3
"""X1-01..04: real keyboard journeys, field names/errors, contrast and reflow.

Synthetic profiles and existing nominal bootstrap/server; --root permits the
same oracle against a preserved baseline. No live resources or real user data.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

from playwright.sync_api import sync_playwright


def load(root, name):
    spec = importlib.util.spec_from_file_location(name, root / "tools" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contrast(fg, bg):
    def luminance(color):
        rgb = [float(n) / 255 for n in re.findall(r"[\d.]+", color)[:3]]
        linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
        return sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
    a, b = sorted((luminance(fg), luminance(bg)))
    return (b + 0.05) / (a + 0.05)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--artifact", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    budget = load(root, "finpes_budget_test")
    bootstrap = load(root, "browser_bootstrap_fixture")
    sources = ("src/js/20-ui/18-finpes-budget.js", "src/styles/app.css")
    result = {"root": str(root), "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "sources": {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sources}, "checks": []}

    def record(name, passed, detail=None):
        result["checks"].append({"name": name, "status": "PASS" if passed else "PRODUCT_FAIL", "detail": detail})

    def snapshot(page):
        return page.evaluate("() => ({pf:JSON.stringify(S.personalFinance),disk:localStorage.getItem('jpwealth_v9_state'),writes:window.__x1Writes})")

    def focus_id(page):
        return page.evaluate("() => document.activeElement.id")

    def open_recurrence(page):
        page.locator('[data-fi-cfg]').first.focus()
        page.keyboard.press("Enter")
        page.locator("#fbRecOn").wait_for()

    def capture(page, suffix):
        path = args.artifact.with_name(args.artifact.stem + "-" + suffix + ".png")
        page.screenshot(path=str(path), full_page=True)
        return str(path)

    server, url = budget.serve()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context(viewport={"width": 1440, "height": 950}, service_workers="block")
            bootstrap.install_bootstrap(context)
            context.add_init_script("window.__onbShown=true;")
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.on("dialog", lambda dialog: dialog.accept())
            page.goto(url, wait_until="load")
            bootstrap.wait_bootstrap(page)
            page.evaluate("""() => {
                closeModal(); const r=pfActAddIncome(pfCurrentMonthKey(),{name:'Receita sintética X1',projectedAmount:123400});
                if(!r.ok) throw new Error('seed PF recusado');
                navigateToScreen('finpes'); JPWFin.ui.selectView('mensal');
                window.__x1OriginalSave=save; window.__x1Writes=0;
                save=function(){window.__x1Writes++;return window.__x1OriginalSave.apply(this,arguments);};
            }""")
            before = snapshot(page)
            open_recurrence(page)
            record("X1-01 named modal", page.get_by_role("dialog", name=re.compile("Recorrência.*Receita sintética X1")).count() == 1)
            record("X1-01 initial focus", focus_id(page) == "fbRecOn", focus_id(page))
            for field, label in (("fbRecAmount", "Valor mensal da regra (R$)"), ("fbRecStart", "Início (YYYY-MM)"), ("fbRecEnd", "Fim (opcional)")):
                record("X1-02 label " + field, page.get_by_label(label, exact=True).count() == 1)
            page.locator("#modalConfirm").focus()
            page.keyboard.press("Tab")
            record("X1-01 Tab wraps", focus_id(page) == "fbRecOn", focus_id(page))
            page.locator("#fbRecOn").focus()
            page.keyboard.press("Shift+Tab")
            record("X1-01 Shift+Tab wraps", focus_id(page) == "modalConfirm", focus_id(page))
            page.locator("#fbRecOn").focus()
            page.keyboard.press("Escape")
            record("X1-01 Escape closes and restores", not page.locator("#modalOverlay").is_visible() and page.locator('[data-fi-cfg]').first.evaluate("el=>el===document.activeElement"))
            record("X1-01 open/cancel zero writes", before == snapshot(page))

            open_recurrence(page)
            page.locator("#fbRecOn").check()
            for field, value in (("fbRecAmount", ""), ("fbRecStart", ""), ("fbRecEnd", "2026-01")):
                page.locator("#fbRecAmount").fill("1234,56")
                page.locator("#fbRecStart").fill("2026-09")
                page.locator("#fbRecEnd").fill("")
                page.locator("#" + field).fill(value)
                page.locator("#modalConfirm").focus()
                page.keyboard.press("Enter")
                detail = page.locator("#" + field).evaluate("""el=>({invalid:el.getAttribute('aria-invalid'),
                    description:(el.getAttribute('aria-describedby')||'').split(/\\s+/).some(id=>{
                      const error=document.getElementById(id);return error&&error.classList.contains('modal-err')&&error.getClientRects().length;
                    }),focused:document.activeElement===el,value:el.value})""")
                record("X1-02 error " + field, detail["invalid"] == "true" and detail["description"] and detail["focused"] and detail["value"] == value, detail)
                record("X1-02 invalid zero writes " + field, before == snapshot(page))
            capture(page, "recurrence-invalid")
            page.locator("#modalCancel").focus()
            page.keyboard.press("Enter")
            record("X1-01 Cancel restores", page.locator('[data-fi-cfg]').first.evaluate("el=>el===document.activeElement"))
            record("X1-01 invalid then cancel preserves", before == snapshot(page))

            open_recurrence(page)
            page.locator("#fbRecOn").check()
            page.locator("#fbRecAmount").fill("1234,56")
            page.locator("#fbRecStart").fill("2026-09")
            page.evaluate("() => {window.__x1CountingSave=save;save=()=>false;}")
            page.locator("#modalConfirm").focus()
            page.keyboard.press("Enter")
            record("X1-01 refusal keeps draft/modal", page.locator("#modalOverlay").is_visible() and page.locator("#fbRecAmount").input_value() == "1234,56")
            record("X1-01 refusal preserves PF/disk", before == snapshot(page))
            page.evaluate("() => {save=window.__x1CountingSave;}")
            page.locator("#modalConfirm").focus()
            page.keyboard.press("Enter")
            detail = page.evaluate("""() => ({rules:S.personalFinance.recurringIncome.length,
              amount:S.personalFinance.recurringIncome[0]?.amount,start:S.personalFinance.recurringIncome[0]?.startMonth,
              diskRules:JSON.parse(localStorage.getItem('jpwealth_v9_state')).personalFinance.recurringIncome.length,writes:window.__x1Writes})""")
            record("X1-01 success single act", detail == {"rules": 1, "amount": 123456, "start": "2026-09", "diskRules": 1, "writes": 1}, detail)
            record("X1-01 success rerender restores", not page.locator("#modalOverlay").is_visible() and page.locator('[data-fi-cfg]').first.evaluate("el=>el===document.activeElement"))
            open_recurrence(page)
            page.locator("#modalOverlay").click(position={"x": 2, "y": 2})
            record("X1-01 backdrop restores", not page.locator("#modalOverlay").is_visible() and page.locator('[data-fi-cfg]').first.evaluate("el=>el===document.activeElement"))
            before_visual = snapshot(page)
            open_recurrence(page)
            page.locator('[data-fi-cfg]').first.focus()
            record("X1-01 background focus stays in dialog", focus_id(page) == "fbRecOn", focus_id(page))
            page.evaluate("() => closeModal()")
            page.locator('[data-fi-cfg]').first.focus()
            record("X1-01 external close releases focus", page.locator('[data-fi-cfg]').first.evaluate("el=>el===document.activeElement"))
            page.evaluate("() => openTransitionModal(2)")
            page.locator("#modalCancel").focus()
            page.keyboard.press("Escape")
            record("X1-01 shared modal Escape preserved", not page.locator("#modalOverlay").is_visible())

            for width in (1440, 390, 320):
                page.set_viewport_size({"width": width, "height": 950 if width == 1440 else 844})
                for theme in ("light", "dark"):
                    name = f"{width}-{theme}"
                    page.evaluate("theme=>{document.documentElement.dataset.theme=theme;navigateToScreen('dashboard');}", theme)
                    eyebrow = page.locator('#dashMacro [data-dm-card="forex"] .dm-eyebrow')
                    colors = eyebrow.evaluate("""el=>{const fg=getComputedStyle(el).color;let n=el;
                      while(n&&getComputedStyle(n).backgroundColor==='rgba(0, 0, 0, 0)')n=n.parentElement;
                      return {fg,bg:n?getComputedStyle(n).backgroundColor:'rgb(255, 255, 255)'};}""")
                    ratio = contrast(colors["fg"], colors["bg"])
                    record("X1-03 contrast " + name, ratio >= 4.5, {**colors, "ratio": ratio})
                    capture(page, "dashboard-" + name)
                    page.evaluate("() => {navigateToScreen('research-forex');}")
                    page.locator('#research [data-ecal-role="filters"]').wait_for(state="visible")
                    for surface in ("workspace", "modal"):
                        if surface == "modal":
                            page.evaluate("() => openEconomicCalendar(document.activeElement)")
                        selector = '#ecalFilters' if surface == "modal" else '#research [data-ecal-role="filters"]'
                        group = page.locator(selector)
                        rects = group.locator("button").evaluate_all("""els=>els.map(el=>{const r=el.getBoundingClientRect();return {text:el.textContent,x:r.x,right:r.right,y:r.y,width:r.width,height:r.height};})""")
                        record("X1-04 controls visible " + surface + " " + name, len(rects) == 5 and all(r["x"] >= 0 and r["right"] <= width + 1 and r["height"] >= 24 for r in rects), rects)
                        overflow = page.evaluate("() => ({scroll:document.documentElement.scrollWidth,viewport:innerWidth})")
                        record("X1-04 no overflow " + surface + " " + name, overflow["scroll"] <= overflow["viewport"] + 1, overflow)
                        for currency in ("all", "USD", "EUR", "GBP", "JPY"):
                            button = group.locator('[data-ecal-cur="' + currency + '"]')
                            button.focus()
                            page.keyboard.press("Enter")
                            record("X1-04 select " + currency + " " + surface + " " + name, button.get_attribute("aria-pressed") == "true" and group.locator('[aria-pressed="true"]').count() == 1)
                        capture(page, "calendar-" + surface + "-" + name)
                        if surface == "modal":
                            page.keyboard.press("Escape")
                    page.evaluate("() => {navigateToScreen('finpes');JPWFin.ui.selectView('mensal');}")
                    open_recurrence(page)
                    page.locator("#modalConfirm").focus()
                    box = page.locator("#modalConfirm").bounding_box()
                    record("X1-01 reachable confirm " + name, box is not None and box["x"] >= 0 and box["x"] + box["width"] <= width + 1 and box["y"] >= 0 and box["y"] + box["height"] <= page.viewport_size["height"] + 1, box)
                    capture(page, "recurrence-" + name)
                    page.keyboard.press("Escape")
                    record("X1-01 matrix cancel restores " + name, page.locator('[data-fi-cfg]').first.evaluate("el=>el===document.activeElement"))
            record("X1-01 visual/navigation zero writes", before_visual == snapshot(page))
            bootstrap.assert_fixture_requests(context)
            record("no page errors", not errors, errors)
            context.close()
            browser.close()
    except Exception as exc:
        result["checks"].append({"name": "test execution", "status": "TEST_HARNESS_FAIL", "error": str(exc)})
    finally:
        server.shutdown()
    result["passed"] = sum(x["status"] == "PASS" for x in result["checks"])
    result["total"] = len(result["checks"])
    args.artifact.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"passed": result["passed"], "total": result["total"], "failures": [x for x in result["checks"] if x["status"] != "PASS"]}, ensure_ascii=False))
    return 0 if result["passed"] == result["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
