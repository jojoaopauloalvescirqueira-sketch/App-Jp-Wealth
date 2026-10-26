#!/usr/bin/env python3
"""Permanent presentation regressions for the approved compact Planning plan.

Source: docs/superpowers/plans/2026-10-21-planning-consolidated-monthly-compact.md.
The visual verifier owns execution/reporting/bootstrap. This module adds only
the delta; its financial oracle is the existing read-model, never new maths.
Run this file for the small RED selection; --case all runs the new matrix.
"""
import argparse
from pathlib import Path
import re

import planning_proportions_test as planning
from planning_parity_layout_test import financial

PLAN = 'docs/superpowers/plans/2026-10-21-planning-consolidated-monthly-compact.md'
REGRESSIONS = ['compact-summary-groups', 'compact-current-calendar-year',
               'compact-wide-seven-columns', 'compact-narrow-three-columns',
               'compact-month-details-complete', 'compact-calendar-vs-finalization',
               'compact-controls-draft-focus', 'compact-scenario-values']
COUNTERPROOFS = ['compact-counterproof-overflow', 'compact-counterproof-duplicate-control',
                 'compact-counterproof-wrong-year', 'compact-counterproof-false-finalization',
                 'compact-counterproof-future-input-value', 'compact-counterproof-cost-values',
                 'compact-counterproof-phase-subtotal', 'compact-counterproof-missing-current-row']
PRIMARY_LABELS = ['Saldo inicial', 'Resultado', 'Saque', 'Aporte', 'Finalizado']
DETAIL_LABELS = ['Pago no mês', 'Câmbio utilizado', 'Preço médio dos aportes',
                 'Última cotação disponível', 'Variação cambial', 'Cobertura', 'situação']


def required_ids(selection='all'):
    ids = list(REGRESSIONS)
    if selection == 'all':
        ids += [f'compact-matrix-{layout}-{theme}-{w}x{h}' for w, h in planning.SIZES
                for layout in planning.LAYOUTS for theme in planning.THEMES]
        ids += [f'compact-boundary-{width}' for width in [899, 900, 901]]
        ids += [f'compact-native200-{layout}-{theme}' for layout in planning.LAYOUTS for theme in planning.THEMES]
        ids += ['compact-touch-keyboard'] + COUNTERPROOFS
    return ids


def seed(page):
    """Only setup uses commands; tested interactions always use actual controls."""
    return page.evaluate('''() => {
      const api=JPWPlanning,d=new Date(),today=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');
      const run=(type,data,id)=>{const r=api.commands.execute(type,data,api.queries.token(id));
        if(!r.ok)throw Error('compact fixture '+type+': '+JSON.stringify(r));return r;};
      const create=(name,startMonth,initialUsd=1000,monthlyContributionUsd=100,profileId='base')=>run('createAccount',
        {name,startMonth,initialUsd,monthlyContributionUsd,profileId,
         goals:{adequate:{value:150,currency:'USD'},ideal:{value:300,currency:'USD'}}}).accountId;
      const start=api.engine.addMonths(today,-2),id=create('Compacta sintética',start);
      run('recordResult',{accountId:id,month:start,usd:-25},id);
      run('recordContribution',{accountId:id,month:start,usd:100,brl:500},id);
      run('recordWithdrawal',{accountId:id,month:start,usd:10,brl:50},id);
      run('finalizeMonth',{accountId:id,month:start,confirmFlows:true},id);
      const pending=api.engine.addMonths(start,1);
      run('recordResult',{accountId:id,month:pending,usd:0},id);
      const blank=api.engine.addMonths(today,1),zero=api.engine.addMonths(today,2),negative=api.engine.addMonths(today,3);
      for(const [month,rate,contributionUsd] of [[blank,null,''],[zero,0,0],[negative,-.01,12.34]])
        run('setProjection',{accountId:id,month,rate,contributionUsd},id);
      const closed=create('Atual finalizada sintética',today);
      run('recordResult',{accountId:closed,month:today,usd:0},closed);
      run('finalizeMonth',{accountId:closed,month:today,confirmFlows:true},closed);
      const large=create('Valores grandes sintéticos',today,1000000,100000,'high-risk');
      const future=create('Horizonte futuro sintético',api.engine.addMonths(today,24));
      api.ui.render(true);return {id,closed,large,future,start,pending,today,blank,zero,negative};
    }''')


def select(page, fixture, view='monthly', account=None):
    page.locator('#planning [data-pl-view=' + view + ']').click()
    page.locator('#planning [data-pl-account]').select_option(account or fixture['id'])
    planning.settle(page)


def guard(page, harness, action):
    before = financial(page)
    harness.start_write_probe(page)
    try:
        result = action()
    finally:
        observed = harness.no_writes(page)
        assert financial(page) == before, 'compact presentation interaction changed a financial family'
    return {'observed': result, 'real_delegate_calls': observed, 'financial_unchanged': True}


def monthly_geometry(page):
    """The wrapper width, not the viewport/layout name, selects the contract."""
    grid = page.locator('#planning [data-pl-monthly-grid]')
    assert grid.count() == 1, 'one monthly table must remain available'
    data = grid.evaluate('''table=>{
      const viewport=table.closest('[data-pl-monthly-viewport]')||table.parentElement,
        shell=table.closest('.pl-shell'),root=table.closest('[data-pl-monthly-layout]'),
        visible=el=>!!el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden',
        rect=el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width};},
        headers=[...table.querySelectorAll('thead th')].filter(visible),
        rows=[...table.querySelectorAll('[data-pl-grid-month]')];
      return {width:viewport.clientWidth,viewport:innerWidth,mode:root?.dataset.plMonthlyLayout,
        wrapper:rect(viewport),table:rect(table),client:viewport.clientWidth,scroll:viewport.scrollWidth,
        shell:{client:shell.clientWidth,scroll:shell.scrollWidth},
        headers:headers.map(el=>el.textContent.trim()),
        rows:rows.map(el=>({month:el.dataset.plGridMonth,cells:[...el.children].filter(visible).length})),
        truncated:[...table.querySelectorAll('td,th,button,input,select,[data-pl-month-details] *')]
          .filter(visible).filter(el=>getComputedStyle(el).textOverflow==='ellipsis'||
            el.scrollWidth>el.clientWidth+1&&['hidden','clip'].includes(getComputedStyle(el).overflowX))
          .map(el=>({text:el.textContent.trim().slice(0,90),tag:el.tagName})),
        details:[...table.querySelectorAll('[data-pl-month-details]')].filter(visible)
          .map(el=>({box:rect(el),client:el.clientWidth,scroll:el.scrollWidth}))};
    }''')
    expected = 7 if data['width'] >= 900 else 3
    assert len(data['headers']) == expected, ('monthly visible columns', expected, data)
    assert data['mode'] == ('wide' if expected == 7 else 'compact'), ('monthly mode follows useful width', data)
    expected_names = ['Mês', 'Saldo inicial', 'Resultado', 'Saque', 'Aporte', 'Patrimônio', 'Finalizado'] if expected == 7 else ['Mês', 'Resultado', 'Patrimônio']
    assert all(name in actual for name, actual in zip(expected_names, data['headers'])), ('approved header order', data)
    assert len(data['rows']) == 120 and len({r['month'] for r in data['rows']}) == 120, ('exactly120distinctmonths', data)
    assert all(r['cells'] == expected for r in data['rows']), ('row/header alignment', data)
    assert data['scroll'] <= data['client'] + 1, ('monthly horizontal overflow', data)
    assert data['table']['width'] <= data['wrapper']['width'] + 1, ('wide table hidden by overflow CSS', data)
    assert data['shell']['scroll'] <= data['shell']['client'] + 1, ('monthly shell horizontal overflow', data)
    assert data['wrapper']['left'] >= -.25 and data['wrapper']['right'] <= data['viewport'] + .25, ('monthly wrapper escapes viewport', data)
    assert not data['truncated'], ('financial content ellipsized/clipped', data['truncated'])
    assert len(data['details']) <= 1, ('multiple month details visible', data['details'])
    for detail in data['details']:
        assert detail['scroll'] <= detail['client'] + 1, ('detail horizontal overflow', detail)
    return data


def summary_groups(page):
    groups = page.locator('#planning [data-pl-summary-group]')
    assert groups.count() == 3, ('Consolidado requires three semantic groups', groups.count())
    expected = [('confirmed', 'Posição confirmada', ['Patrimônio confirmado', 'Aportes confirmados', 'Resultado confirmado']),
                ('projection', 'Projeção e objetivos', ['Projeção', 'Renda']),
                ('fx', 'Referências de câmbio', ['Preço médio dos aportes', 'Dólar'])]
    result = []
    for index, (key, title, labels) in enumerate(expected):
        group = groups.nth(index)
        assert group.get_attribute('data-pl-summary-group') == key, ('group reading order', key)
        assert group.locator('h2,h3,h4').filter(has_text=title).count() == 1, ('group heading', title)
        text = group.inner_text()
        assert all(label in text for label in labels), ('financial values in their semantic group', key, text)
        if key == 'projection':
            assert group.locator('[data-pl-projection-year]').count() == 1, 'projection selector belongs with projection and goals'
        result.append({'group': key, 'text': text})
    return result


def current_year(page):
    year = page.evaluate('String(new Date().getFullYear())')
    expected_years = page.evaluate('''()=>{
      const root=document.querySelector('#planning'),d=new Date(),today=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0');
      const sheet=JPWPlanning.queries.sheetView({accountId:root.querySelector('[data-pl-account]').value||undefined,
        month:today,quote:JPWMarket.usdBrl.get(),projectionYear:root.querySelector('[data-pl-projection-year]').value,
        tableMode:'Anual · Resumo completo'}).sheet;
      return sheet.table.annual.map(row=>String(row.year));
    }''')
    assert expected_years, 'current-year oracle requires a nonempty read-model annual table'
    rows = page.locator('#planning [data-pl-consolidated-table] tbody tr')
    shown = rows.evaluate_all('els=>els.map(el=>el.querySelector("th")?.textContent.trim())')
    markers = page.locator('#planning [data-pl-consolidated-table] [data-pl-current-year=true]')
    if year not in expected_years:
        assert markers.count() == 0, ('no artificial current-year row', year, shown)
        assert year not in shown, ('current year outside read-model horizon must not be fabricated', year, shown, expected_years)
        return {'calendar_year': year, 'expected_years': expected_years, 'not_in_horizon': True}
    assert year in shown, ('read-model current year missing from rendered annual table', year, shown, expected_years)
    assert markers.count() == 1, ('current calendar year has one marker independent of projection', year, shown)
    marker = markers.first
    assert marker.get_attribute('data-pl-annual-year') == year, ('wrong highlighted calendar year', year)
    visible_year = marker.locator('th').first.inner_text().strip()
    assert re.search(r'\b' + re.escape(year) + r'\b', visible_year), ('highlighted visible year differs from local calendar', year, visible_year)
    assert 'Em andamento' in marker.inner_text(), 'current annual row explicitly says Em andamento'
    colors = marker.evaluate('''el=>{const first=el.querySelector('td,th'),other=[...el.parentElement.children].find(n=>n!==el);
      return {row:getComputedStyle(el).backgroundColor,cell:first&&getComputedStyle(first).backgroundColor,
        other:other&&getComputedStyle(other).backgroundColor};}''')
    candidates = [list(map(float, re.findall(r'[\d.]+', colors[key] or ''))) for key in ['row', 'cell']]
    assert any(len(c) >= 3 and c[1] > c[0] and c[1] > c[2] and (len(c) < 4 or c[3] > 0) for c in candidates), ('current-year visible green background', colors)
    return {'calendar_year': year, 'expected_years': expected_years, 'visible_year': visible_year, 'shown_years': shown, 'colors': colors}


def year_independence(page, fixture):
    select(page, fixture, 'consolidated')
    selector = page.locator('#planning [data-pl-projection-year]')
    values = selector.locator('option').evaluate_all('els=>els.map(e=>e.value)')
    today = fixture['today'][:4]
    other = next(value for value in reversed(values) if value != today)
    selector.select_option(other)
    first = current_year(page)
    assert selector.input_value() == other, 'projection selector stimulus did not happen'
    page.locator('#planning [data-pl-chart-period]').select_option('current-year')
    second = current_year(page)
    assert selector.input_value() == other, 'current-year chart silently changed projection year'
    select(page, fixture, 'consolidated', fixture['future'])
    outside = current_year(page)
    assert outside.get('not_in_horizon'), 'current calendar year is outside the future-only account horizon'
    select(page, fixture, 'consolidated')
    return {'projection_year': other, 'after_projection_change': first, 'after_chart_change': second, 'outside_horizon': outside}


def model(page, fixture, account=None):
    return page.evaluate('''({id,today})=>JPWPlanning.queries.sheetView({accountId:id,month:today,
      quote:JPWMarket.usdBrl.get()}).sheet''', {'id': account or fixture['id'], 'today': fixture['today']})


def open_details(page, month, keyboard=False, touch=False):
    trigger = page.locator('#planning [data-pl-select-month="' + month + '"]')
    assert trigger.count() == 1, ('one month details trigger', month)
    if trigger.get_attribute('aria-expanded') != 'true':
        if keyboard:
            trigger.focus()
            page.keyboard.press('Enter')
        elif touch:
            trigger.tap()
        else:
            trigger.click()
    details = page.locator('#planning [data-pl-month-details="' + month + '"]')
    assert details.count() == 1 and details.is_visible(), ('month inline details available', month)
    assert trigger.get_attribute('aria-expanded') == 'true', ('trigger exposes expansion', month)
    assert details.get_attribute('id') and trigger.get_attribute('aria-controls') == details.get_attribute('id'), ('accessible details relationship', month)
    visible = page.locator('#planning [data-pl-month-details]:visible')
    assert visible.count() == 1, ('one expanded month', month, visible.count())
    return details


def unique_controls(page, fixture):
    sheet = model(page, fixture)
    for row in sheet['monthlyRows']:
        month = row['month']
        assert page.locator('[data-pl-finalized-month="' + month + '"]').count() == 1, ('unique finalized control', month)
        if month > fixture['today']:
            for field in ['rate', 'contributionUsd']:
                assert page.locator('[data-pl-inline-month="' + month + '"][data-pl-inline-open=' + field + ']').count() == 1, ('unique future cell activation', month, field)
    assert page.locator('[data-pl-inline-editor]').count() <= 1, 'one active inline editor'
    assert page.locator('[data-pl-future-field]').count() <= 1, 'one unique active future field'
    return {'months': len(sheet['monthlyRows']), 'one_control_per_month_and_field': True}


def future_input_values(page, row):
    today = page.evaluate("new Date().getFullYear()+'-'+String(new Date().getMonth()+1).padStart(2,'0')")
    if row['month'] <= today:
        return None
    # Formatting only: preserve the read-model distinction between blank and0.
    expected = page.evaluate('''r=>({
      rate:r.provisional?'':Number.isFinite(r.rate)?String(r.rate*100):'',
      contributionUsd:r.contributionBlank?'':Number.isFinite(r.contributionUsd)?String(r.contributionUsd):''
    })''', row)
    observed = {}
    for field, value in expected.items():
        control = page.locator('[data-pl-inline-month="' + row['month'] + '"][data-pl-inline-open=' + field + ']')
        assert control.count() == 1 and control.is_visible(), ('accessible unique future cell', row['month'], field)
        actual = control.get_attribute('data-pl-premise-value')
        assert actual == value, ('future cell preserves read-model value including blank/zero', row['month'], field, value, actual)
        displayed = control.locator('[data-pl-month-value=rate]').inner_text() if field == 'rate' else control.inner_text()
        expected_display = page.evaluate("([r,f])=>f==='rate'?(r.provisional?'—':(r.rate*100).toLocaleString('pt-BR',{maximumFractionDigits:2})+'%'):(r.contributionBlank?'—':new Intl.NumberFormat('pt-BR',{style:'currency',currency:'USD'}).format(r.contributionUsd))", [row, field])
        assert normalized(displayed) == normalized(expected_display), ('readonly future cell displays the correct model value', row['month'], field, displayed, expected_display)
        observed[field] = {'expected': value, 'actual': actual, 'displayed': displayed}
    return observed


def normalized(text):
    return ' '.join(str(text).replace('\u00a0', ' ').split())


def bound_value(locator, field, expected, identity, strip_rate_label=False):
    """Check a value in its own actual container; equal values elsewhere cannot pass."""
    observed = locator.evaluate_all('''(els,stripRateLabel)=>els.map(el=>{
      if(!stripRateLabel)return el.innerText;
      const copy=el.cloneNode(true);copy.querySelectorAll('.pl-rate-label').forEach(n=>n.remove());return copy.textContent;
    })''', strip_rate_label)
    assert len(observed) == 1 and locator.is_visible(), ('one accessible value container', identity, field, len(observed))
    actual = observed[0]
    candidates = expected if isinstance(expected, list) else [expected]
    assert normalized(actual) in [normalized(value) for value in candidates], ('value in its named container', identity, field, candidates, actual)
    return {'expected': candidates, 'actual': actual}


def detail_field(details, label):
    term = details.locator('.pl-month-extra-details dt').filter(has_text=re.compile(r'^\s*' + re.escape(label) + r'\s*$'))
    assert term.count() == 1, ('one named detail field', label, term.count())
    return term.locator('..').locator(':scope > dd')


def month_field_values(page, row, principal, details, mode, expected, future_values):
    identity = row['month']
    values = {}
    scopes = '[data-pl-grid-month="' + identity + '"] [data-pl-month-value="{key}"],[data-pl-month-details="' + identity + '"] [data-pl-month-value="{key}"]'
    for key, model_key in [('open', 'openUsd'), ('withdrawal', 'withdrawalUsd')]:
        values[model_key] = bound_value(page.locator(scopes.format(key=key)), model_key, expected[model_key], identity)
    if future_values is None:
        values['rate'] = bound_value(page.locator(scopes.format(key='rate')), 'rate', expected['rate'], identity, strip_rate_label=True)
        values['contributionUsd'] = bound_value(page.locator(scopes.format(key='contribution')), 'contributionUsd', expected['contributionUsd'], identity)
    finalized = page.locator('[data-pl-finalized-month="' + identity + '"]')
    assert finalized.count() == 1 and finalized.is_visible(), ('one accessible finalization control', identity)
    assert finalized.input_value() == ('Sim' if row['finalized'] else 'Não'), ('finalization control value', identity)
    cells = principal.locator(':scope > th,:scope > td')
    result_index, balance_index = (2, 5) if mode == 'wide' else (1, 2)
    for index, usd_key, brl_key in [(result_index, 'resultUsd', 'resultBrl'), (balance_index, 'closeUsd', 'closeBrl')]:
        values[usd_key] = bound_value(cells.nth(index).locator('.pl-money-primary'), usd_key, expected[usd_key], identity)
        values[brl_key] = bound_value(cells.nth(index).locator('.pl-money-secondary'), brl_key, expected[brl_key], identity)
    labels = {'paidBrl': 'Pago no mês', 'fxVariation': 'Variação cambial',
              'costCoverage': 'Cobertura', 'costStatus': 'Situação do custo'}
    for key, label in labels.items():
        wanted = expected[key]
        if wanted == '—':
            wanted = ['—', '— · Indisponível']
        values[key] = bound_value(detail_field(details, label), key, wanted, identity)
    for key, label in [('fxRate', 'Câmbio utilizado · R$/US$'),
                       ('averageRate', 'Preço médio dos aportes · R$/US$'),
                       ('quoteRate', 'Última cotação disponível · R$/US$')]:
        wanted = page.evaluate('''value=>Number.isFinite(value)?[
          value.toLocaleString('pt-BR',{minimumFractionDigits:4,maximumFractionDigits:4}),
          value.toLocaleString('pt-BR',{maximumFractionDigits:4}),
          new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(value)]:['—','— · Indisponível']''', row[key])
        values[key] = bound_value(detail_field(details, label), key, wanted, identity)
    return values


def detail_values(page, row):
    details = open_details(page, row['month'])
    principal = page.locator('[data-pl-grid-month="' + row['month'] + '"]')
    mode = principal.evaluate('el=>el.closest("[data-pl-monthly-layout]")?.dataset.plMonthlyLayout')
    assert mode in ['wide', 'compact'], ('month detail has an explicit layout mode', row['month'], mode)
    labels = details.inner_text()
    # FX/cost references belong in details in both modes. Wide primary labels
    # may stay in the table; compact details must expose the removed fields.
    primary_labels = labels if mode == 'compact' else ' '.join([
        page.locator('[data-pl-monthly-grid] thead').inner_text(), principal.inner_text(), labels])
    for label in PRIMARY_LABELS:
        assert label.casefold() in primary_labels.casefold(), ('accessible primary month label', row['month'], mode, label, primary_labels)
    for label in DETAIL_LABELS:
        assert label.casefold() in labels.casefold(), ('complete accessible month detail label', row['month'], label, labels)
    future_values = future_input_values(page, row)
    # Currency/percentage formatting only. All values are taken from the read-model.
    expected = page.evaluate('''r=>{
      const money=(v,c='USD')=>Number.isFinite(v)?new Intl.NumberFormat('pt-BR',{style:'currency',currency:c}).format(v):'—',
        percent=v=>Number.isFinite(v)?(v*100).toLocaleString('pt-BR',{maximumFractionDigits:2})+'%':'—';
      return {openUsd:money(r.openUsd),resultUsd:money(r.resultUsd),resultBrl:money(r.resultBrl,'BRL'),
        withdrawalUsd:money(r.withdrawalUsd),contributionUsd:money(r.contributionUsd),closeUsd:money(r.closeUsd),
        closeBrl:money(r.closeBrl,'BRL'),paidBrl:money(r.paidBrl,'BRL'),fxVariation:percent(r.fxVariation),
        rate:percent(r.rate),costCoverage:percent(r.costCoverage),costStatus:r.costStatus};
    }''', row)
    normalize = lambda s: ' '.join(str(s).replace('\u00a0', ' ').split())
    # The union includes principal values; compact details supply removed fields.
    text = normalize(principal.inner_text() + ' ' + labels)
    for key, value in expected.items():
        if key in ['rate', 'contributionUsd'] and future_values is not None:
            continue  # Every future row was checked against its actual inputs.
        assert normalize(value) in text, ('read-model value preserved in principal/detail', row['month'], key, value, text)
    for key in ['fxRate', 'averageRate', 'quoteRate']:
        candidates = page.evaluate('''value=>Number.isFinite(value)?[
          value.toLocaleString('pt-BR',{minimumFractionDigits:4,maximumFractionDigits:4}),
          value.toLocaleString('pt-BR',{maximumFractionDigits:4}),
          new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(value)]:['—']''', row[key])
        assert any(normalize(value) in text for value in candidates), ('exchange reference value preserved', row['month'], key, candidates, text)
    control = details.locator('[data-pl-finalized-month="' + row['month'] + '"]')
    if control.count():
        assert control.input_value() == ('Sim' if row['finalized'] else 'Não'), ('finalization value', row['month'])
    bound = month_field_values(page, row, principal, details, mode, expected, future_values)
    return {'month': row['month'], 'mode': mode, 'labels': PRIMARY_LABELS + DETAIL_LABELS,
            'read_model_values': expected, 'future_input_values': future_values, 'bound_fields': bound}


def subtotal_values(page, phase_totals):
    mode = page.locator('[data-pl-monthly-layout]').get_attribute('data-pl-monthly-layout')
    assert mode in ['wide', 'compact'], ('subtotal mode', mode)
    result = []
    for total in phase_totals:
        identity = total['cyclePhase']
        row = page.locator('[data-pl-phase-total="' + str(identity) + '"]')
        assert row.count() == 1, ('one phase subtotal', identity)
        assert total['label'] in row.inner_text() and total['monthLabel'] in row.inner_text(), ('phase label preserves source period', total)
        assert total['situation'] in row.locator('th').inner_text(), ('phase situation preserves read-model state', total)
        expected = page.evaluate('''r=>{
          const money=(v,c='USD')=>Number.isFinite(v)?new Intl.NumberFormat('pt-BR',{style:'currency',currency:c}).format(v):'—';
          return {openUsd:money(r.openUsd),resultUsd:money(r.resultUsd),resultBrl:money(r.resultBrl,'BRL'),
            withdrawalUsd:money(r.withdrawalUsd),contributionUsd:money(r.contributionUsd),
            closeUsd:money(r.closeUsd),closeBrl:money(r.closeBrl,'BRL'),
            fxRate:Number.isFinite(r.fxRate)?r.fxRate.toLocaleString('pt-BR',{minimumFractionDigits:4,maximumFractionDigits:4}):'—'};
        }''', total)
        values = {}
        for key, model_key in [('open', 'openUsd'), ('withdrawal', 'withdrawalUsd'), ('contribution', 'contributionUsd')]:
            values[model_key] = bound_value(row.locator('[data-pl-month-value="' + key + '"]'), model_key, expected[model_key], identity)
        cells = row.locator(':scope > th,:scope > td')
        result_index, balance_index = (2, 5) if mode == 'wide' else (1, 2)
        for index, usd_key, brl_key in [(result_index, 'resultUsd', 'resultBrl'), (balance_index, 'closeUsd', 'closeBrl')]:
            values[usd_key] = bound_value(cells.nth(index).locator('.pl-money-primary'), usd_key, expected[usd_key], identity)
            values[brl_key] = bound_value(cells.nth(index).locator('.pl-money-secondary'), brl_key, expected[brl_key], identity)
        fx = row.locator(':scope > th > small').filter(has_text=re.compile(r'^Câmbio utilizado'))
        values['fxRate'] = bound_value(fx, 'fxRate', 'Câmbio utilizado · R$/US$: ' + expected['fxRate'], identity)
        result.append({'cyclePhase': identity, 'mode': mode, 'values': values})
    return result


def currency_groups(page, fixture):
    geometry = monthly_geometry(page)
    result_index, balance_index = (2, 5) if geometry['mode'] == 'wide' else (1, 2)
    result = []
    for row in model(page, fixture)['monthlyRows']:
        cells = page.locator('[data-pl-grid-month="' + row['month'] + '"]').locator(':scope > th,:scope > td')
        for index, usd_key, brl_key in [(result_index, 'resultUsd', 'resultBrl'), (balance_index, 'closeUsd', 'closeBrl')]:
            expected = page.evaluate('''({usd,brl})=>({usd:Number.isFinite(usd)?new Intl.NumberFormat('pt-BR',{style:'currency',currency:'USD'}).format(usd):null,
              brl:Number.isFinite(brl)?new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(brl):null})''', {'usd': row[usd_key], 'brl': row[brl_key]})
            text = ' '.join(cells.nth(index).inner_text().split())
            for currency, value in expected.items():
                if value is not None:
                    assert ' '.join(value.split()) in text, ('USD/BRL grouped in the same principal cell', row['month'], usd_key, currency, value, text)
            if expected['usd'] and expected['brl']:
                assert text.index('US$') < text.index('R$'), ('USD primary and BRL secondary order', row['month'], text)
        result.append(row['month'])
    return {'grouped_currency_months': result, 'mode': geometry['mode']}


def complete_details(page, fixture):
    select(page, fixture)
    sheet = model(page, fixture)
    # Every month is reachable and every removed field is checked, not only the
    # first month. This runs once; the matrix reuses geometry-only checks.
    results = [detail_values(page, row) for row in sheet['monthlyRows']]
    initial_viewport = page.viewport_size
    initial_mode = page.locator('[data-pl-monthly-layout]').get_attribute('data-pl-monthly-layout')
    try:
        page.set_viewport_size({'width': 1440, 'height': 1000} if initial_mode == 'compact' else {'width': 390, 'height': 844})
        planning.settle(page)
        other_mode = page.locator('[data-pl-monthly-layout]').get_attribute('data-pl-monthly-layout')
        assert other_mode != initial_mode, ('all-month field checks exercise both modes', initial_mode, other_mode)
        other_results = [detail_values(page, row) for row in sheet['monthlyRows']]
        other_subtotals = subtotal_values(page, sheet['phaseTotals'])
    finally:
        page.set_viewport_size(initial_viewport)
        planning.settle(page)
    totals = page.locator('#planning [data-pl-phase-total]')
    assert totals.count() == 10, ('ten twelve-month phase subtotals', totals.count())
    order = page.locator('[data-pl-monthly-grid] tbody').evaluate('''el=>[...el.children].filter(n=>n.matches('[data-pl-grid-month],[data-pl-phase-total]')).map(n=>n.dataset.plGridMonth||'subtotal:'+n.dataset.plPhaseTotal)''')
    expected = []
    for index, row in enumerate(sheet['monthlyRows']):
        expected.append(row['month'])
        if (index + 1) % 12 == 0:
            expected.append('subtotal:' + str((index + 1) // 12))
    assert order == expected, 'phase subtotals follow twelve plan months, distinct from calendar years'
    for subtotal in sheet['phaseTotals']:
        text = page.locator('[data-pl-phase-total="' + str(subtotal['cyclePhase']) + '"]')
        assert subtotal['label'] in text.inner_text() and subtotal['monthLabel'] in text.inner_text(), ('phase label preserves source period', subtotal)
    return {'details': results, 'other_mode_details': other_results, 'other_mode_subtotals': other_subtotals,
            'phase_subtotals': sheet['phaseTotals'], 'subtotal_values': subtotal_values(page, sheet['phaseTotals']), 'controls': unique_controls(page, fixture),
            'currencies': currency_groups(page, fixture)}


def calendar_labels(page, fixture):
    """Pure DOM oracle, also used after deliberate false-finalization mutation."""
    result = []
    for month, expected in [(fixture['start'], 'Finalizado'), (fixture['pending'], 'Pendente'),
                            (fixture['today'], 'Em andamento'), (fixture['blank'], 'Projetado')]:
        row = page.locator('[data-pl-grid-month="' + month + '"]')
        label = row.locator('th').inner_text()
        assert expected in label, ('calendar/closure label beside month', month, expected, label)
        if month == fixture['pending']:
            assert 'Finalizado' not in label, ('elapsed time is not confirmation', month, label)
        if month == fixture['blank']:
            assert 'Pendente' in row.inner_text() or 'provisóri' in row.inner_text().lower(), ('future blank remains provisional', month)
        if month == fixture['today']:
            assert row.evaluate("el=>el.classList.contains('pl-month-current')"), 'current open month keeps current calendar styling'
        result.append({'month': month, 'label': label})
    return result


def calendar_states(page, fixture):
    select(page, fixture)
    result = calendar_labels(page, fixture)
    select(page, fixture, account=fixture['closed'])
    row = page.locator('[data-pl-grid-month="' + fixture['today'] + '"]')
    label = row.locator('th').inner_text()
    assert 'Em andamento' in label and 'Finalizado' in label, ('current finalized month exposes both independent states', label)
    assert row.evaluate("el=>el.classList.contains('pl-month-current')"), 'finalized current month retains current calendar styling'
    select(page, fixture)
    return {'states': result, 'current_finalized': label}


def draft_focus(page, fixture):
    page.set_viewport_size({'width': 1440, 'height': 1000})
    select(page, fixture)
    assert monthly_geometry(page)['mode'] == 'wide', 'draft stimulus starts wide'
    page.locator('[data-pl-inline-month="' + fixture['negative'] + '"][data-pl-inline-open=contributionUsd]').click()
    field = page.locator('[data-pl-future-month="' + fixture['negative'] + '"][data-pl-future-field=contributionUsd]')
    field.focus()
    page.keyboard.press('ControlOrMeta+A')
    page.keyboard.insert_text('12,')  # input event only; deliberately no blur/change.
    field.evaluate('''el=>{window.__compactDraftNode=el;el.setSelectionRange(1,2);window.__compactDraftSelection=[el.selectionStart,el.selectionEnd];}''')
    before_scroll = field.evaluate('el=>{el.scrollIntoView({block:"center"});return {page:scrollY,owner:el.closest("[data-pl-monthly-viewport]").scrollTop}}')
    page.set_viewport_size({'width': 390, 'height': 844})
    planning.settle(page)
    observed = page.evaluate('''()=>{const el=window.__compactDraftNode;return {connected:el.isConnected,
      active:el===document.activeElement,value:el.value,selection:[el.selectionStart,el.selectionEnd],
      expectedSelection:window.__compactDraftSelection,visible:!!el.getClientRects().length,
      box:el.getBoundingClientRect().toJSON(),height:innerHeight};}''')
    assert observed['connected'] and observed['active'] and observed['visible'], ('resize moves same focused visible node', observed)
    assert observed['value'] == '12,' and observed['selection'] == observed['expectedSelection'], ('partial draft/selection preserved', observed)
    assert observed['box']['bottom'] > 0 and observed['box']['top'] < observed['height'], ('focused migrated draft remains reachable after resize', observed)
    assert open_details(page, fixture['negative']).locator('[data-pl-future-field=contributionUsd]').evaluate('el=>el===window.__compactDraftNode'), 'focused node moved into its expanded month detail'
    compact = monthly_geometry(page)
    page.set_viewport_size({'width': 1440, 'height': 480})
    planning.settle(page)
    restored = page.evaluate('''()=>({same:window.__compactDraftNode===document.activeElement,
      value:window.__compactDraftNode.value,connected:window.__compactDraftNode.isConnected})''')
    assert restored['same'] and restored['connected'] and restored['value'] == '12,', ('reverse resize preserves same focused draft', restored)
    return {'before_scroll': before_scroll, 'compact': compact, 'draft': observed, 'restored': restored,
            'controls': unique_controls(page, fixture)}


def scenario_values(page, fixture):
    select(page, fixture)
    sheet = model(page, fixture)
    rows = {row['month']: row for row in sheet['monthlyRows']}
    assert rows[fixture['start']]['resultUsd'] == -25 and rows[fixture['pending']]['resultUsd'] == 0, 'synthetic negative/zero facts reached the existing engine'
    assert rows[fixture['blank']]['provisional'] and rows[fixture['blank']]['contributionBlank'], 'blank fixture remains different from zero'
    assert rows[fixture['zero']]['rate'] == 0 and not rows[fixture['zero']]['provisional'], 'explicit zero is not provisional'
    for month in [fixture['blank'], fixture['zero'], fixture['negative']]:
        row = rows[month]
        open_details(page, month)
        for field, expected in [('rate', '' if row['provisional'] else str(row['rate'] * 100).removesuffix('.0')),
                                ('contributionUsd', '' if row['contributionBlank'] else str(row['contributionUsd']).removesuffix('.0'))]:
            page.locator('[data-pl-inline-month="' + month + '"][data-pl-inline-open=' + field + ']').click()
            control = page.locator('[data-pl-future-month="' + month + '"][data-pl-future-field=' + field + ']')
            assert control.input_value() == expected, ('activated future input preserves exact blank/zero/value', month, field, expected, control.input_value())
            page.locator('[data-pl-action=inline-cancel]').click()
    # Past unconfirmed month has no historical quote: BRL remains unavailable.
    assert rows[fixture['pending']]['fxRate'] is None and rows[fixture['pending']]['closeBrl'] is None, 'missing historical exchange stays unavailable'
    detail_values(page, rows[fixture['pending']])
    select(page, fixture, account=fixture['large'])
    page.set_viewport_size({'width': 320, 'height': 700})
    planning.settle(page)
    large = monthly_geometry(page)
    large_sheet = model(page, fixture, fixture['large'])
    detail_values(page, large_sheet['monthlyRows'][-1])
    return {'blank_zero_negative': [rows[fixture[k]] for k in ['blank', 'zero', 'negative']], 'large': large}


def regressions(browser, url, report, harness):
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block', reduced_motion='reduce')
    try:
        page = harness.setup(context, url)
        fixture = seed(page)
        report['compact_fixture'] = fixture
        select(page, fixture, 'consolidated')
        harness.record(report, REGRESSIONS[0], lambda: guard(page, harness, lambda: summary_groups(page)), page, criteria=PLAN)
        harness.record(report, REGRESSIONS[1], lambda: guard(page, harness, lambda: year_independence(page, fixture)), page, criteria=PLAN)
        select(page, fixture)
        harness.record(report, REGRESSIONS[2], lambda: guard(page, harness, lambda: monthly_geometry(page)), page, criteria=PLAN)
        page.set_viewport_size({'width': 390, 'height': 844});planning.settle(page)
        harness.record(report, REGRESSIONS[3], lambda: guard(page, harness, lambda: monthly_geometry(page)), page, criteria=PLAN)
        harness.record(report, REGRESSIONS[4], lambda: guard(page, harness, lambda: complete_details(page, fixture)), page, criteria=PLAN)
        harness.record(report, REGRESSIONS[5], lambda: guard(page, harness, lambda: calendar_states(page, fixture)), page, criteria=PLAN)
        harness.record(report, REGRESSIONS[6], lambda: guard(page, harness, lambda: draft_focus(page, fixture)), page, criteria=PLAN)
        # Close the disposable context without blurring/committing the partial
        # draft. Scenario assertions get a separate synthetic document.
        harness.assert_fixture_requests(context)
        context.close()
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block', reduced_motion='reduce')
        page = harness.setup(context, url)
        fixture = seed(page)
        select(page, fixture)
        harness.record(report, REGRESSIONS[7], lambda: guard(page, harness, lambda: scenario_values(page, fixture)), page, criteria=PLAN)
        harness.assert_fixture_requests(context)
    finally:
        context.close()


def presentation(page, fixture):
    select(page, fixture, 'consolidated')
    groups, year = summary_groups(page), current_year(page)
    select(page, fixture)
    grid = monthly_geometry(page)
    from planning_monthly_inline_test import read_oracles
    inline_values = read_oracles(page, fixture)
    open_details(page, fixture['today'], keyboard=True)
    detailed = monthly_geometry(page)
    return {'groups': groups, 'current_year': year, 'grid': grid, 'expanded': detailed,
            'subtotal_values': subtotal_values(page, model(page, fixture)['phaseTotals']), 'inline_read_contract':inline_values}


def matrix(browser, url, report, harness):
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block', reduced_motion='reduce')
    try:
        page = harness.setup(context, url)
        fixture = seed(page)
        for width, height in planning.SIZES:
            page.set_viewport_size({'width': width, 'height': height})
            for layout in planning.LAYOUTS:
                for theme in planning.THEMES:
                    page.evaluate('layout=>mountNavigationLayout(layout)', layout)
                    page.evaluate('theme=>{document.documentElement.dataset.theme=theme;document.body.dataset.theme=theme}', theme)
                    harness.record(report, f'compact-matrix-{layout}-{theme}-{width}x{height}',
                                   lambda: guard(page, harness, lambda: presentation(page, fixture)), page, criteria=PLAN,
                                   layout=layout, theme=theme, viewport=[width, height], reduced_motion=True)
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.evaluate("mountNavigationLayout('topbar')")
        select(page, fixture)
        viewport = page.locator('[data-pl-monthly-viewport]')
        for width in [899, 900, 901]:
            def boundary(width=width):
                assert viewport.count() == 1, 'useful-width wrapper exists for boundary stimulus'
                old = viewport.get_attribute('style')
                try:
                    viewport.evaluate('(el,w)=>{el.style.width=w+"px";el.style.maxWidth="none";el.style.boxSizing="content-box";el.style.padding="0";el.style.border="0"}', width)
                    planning.settle(page)
                    result = monthly_geometry(page)
                    assert result['width'] == width, ('actual useful width stimulus', width, result['width'])
                    return result
                finally:
                    viewport.evaluate('(el,s)=>s===null?el.removeAttribute("style"):el.setAttribute("style",s)', old)
                    planning.settle(page)
            harness.record(report, f'compact-boundary-{width}', lambda: guard(page, harness, boundary), page, criteria=PLAN)
        harness.assert_fixture_requests(context)
    finally:
        context.close()


def native_case(page, report, harness, layout, theme):
    fixture = seed(page)
    harness.record(report, f'compact-native200-{layout}-{theme}',
                   lambda: guard(page, harness, lambda: presentation(page, fixture)), page, criteria=PLAN,
                   layout=layout, theme=theme, native_zoom=200)


def touch(browser, url, report, harness):
    context = browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True,
                                  is_mobile=True, service_workers='block', reduced_motion='reduce')
    try:
        page = harness.setup(context, url)
        fixture = seed(page)
        select(page, fixture)
        def journey():
            open_details(page, fixture['pending'], touch=True)
            first = monthly_geometry(page)
            open_details(page, fixture['today'], keyboard=True)
            trigger = page.locator('[data-pl-select-month="' + fixture['today'] + '"]')
            assert trigger.evaluate('el=>el===document.activeElement'), 'keyboard expansion retains triggering focus'
            assert page.locator('[data-pl-month-details="' + fixture['pending'] + '"]').is_hidden(), 'second expansion closes previous detail'
            page.keyboard.press('Tab')
            assert page.evaluate('document.activeElement.closest("#planning")!==null'), 'details keyboard focus stays reachable in Planning'
            return {'touch': first, 'keyboard': monthly_geometry(page), 'synthetic_touch': True}
        harness.record(report, 'compact-touch-keyboard', lambda: guard(page, harness, journey), page, criteria=PLAN)
        harness.assert_fixture_requests(context)
    finally:
        context.close()


def counterproofs(browser, url, report, harness):
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, service_workers='block')
    try:
        page = harness.setup(context, url)
        fixture = seed(page)
        select(page, fixture)
        def overflow():
            valid = monthly_geometry(page)
            table = page.locator('[data-pl-monthly-grid]')
            original = table.get_attribute('style')
            try:
                table.evaluate('el=>el.style.setProperty("min-width","2400px","important")')
                invalid = harness.rejected(lambda: monthly_geometry(page))
            finally:
                table.evaluate('(el,s)=>s===null?el.removeAttribute("style"):el.setAttribute("style",s)', original)
            return {'positive': valid, 'violation': invalid, 'restored': monthly_geometry(page)}
        harness.record(report, COUNTERPROOFS[0], lambda: guard(page, harness, overflow), page, criteria='same monthly geometry oracle rejects provoked horizontal overflow')
        def duplicate():
            valid = unique_controls(page, fixture)
            target = page.locator('[data-pl-inline-month="' + fixture['zero'] + '"][data-pl-inline-open=rate]')
            target.evaluate('el=>{const clone=el.cloneNode(true);clone.dataset.compactCounterproof="duplicate";el.after(clone)}')
            try:
                invalid = harness.rejected(lambda: unique_controls(page, fixture))
            finally:
                page.locator('[data-compact-counterproof=duplicate]').evaluate('el=>el.remove()')
            return {'positive': valid, 'violation': invalid, 'restored': unique_controls(page, fixture)}
        harness.record(report, COUNTERPROOFS[1], lambda: guard(page, harness, duplicate), page, criteria='same uniqueness oracle rejects duplicate financial control')
        select(page, fixture, 'consolidated')
        def wrong_year():
            valid = current_year(page)
            marker = page.locator('[data-pl-consolidated-table] [data-pl-current-year=true]')
            label = marker.locator('th').first
            original = label.inner_html()
            wrong = str(int(fixture['today'][:4]) + 1)
            try:
                label.evaluate('(el,wrong)=>el.textContent=wrong', wrong)
                invalid = harness.rejected(lambda: current_year(page))
            finally:
                label.evaluate('(el,html)=>el.innerHTML=html', original)
            return {'positive': valid, 'wrong_visible_year': wrong, 'violation': invalid, 'restored': current_year(page)}
        harness.record(report, COUNTERPROOFS[2], lambda: guard(page, harness, wrong_year), page, criteria='same annual calendar oracle rejects wrong year marker')
        select(page, fixture)
        def false_finalization():
            valid = calendar_labels(page, fixture)
            cell = page.locator('[data-pl-grid-month="' + fixture['pending'] + '"] th')
            extra = cell.evaluate('el=>{const s=document.createElement("span");s.dataset.compactCounterproof="false-final";s.textContent=" Finalizado";el.append(s);return true}')
            try:
                invalid = harness.rejected(lambda: calendar_labels(page, fixture))
            finally:
                page.locator('[data-compact-counterproof=false-final]').evaluate_all('els=>els.forEach(el=>el.remove())')
            return {'positive': valid, 'mutation_applied': extra, 'violation': invalid, 'restored': calendar_labels(page, fixture)}
        harness.record(report, COUNTERPROOFS[3], lambda: guard(page, harness, false_finalization), page, criteria='same month state oracle rejects elapsed month falsely marked finalized')
        def future_value():
            special = {fixture[key] for key in ['blank', 'zero', 'negative']}
            row = next(row for row in model(page, fixture)['monthlyRows'] if row['month'] > fixture['today'] and row['month'] not in special)
            assert row['month'] not in special, ('counterproof uses an otherwise unchecked future month', row['month'])
            valid = detail_values(page, row)
            violations = {}
            restored = {}
            for field in ['rate', 'contributionUsd']:
                target = page.locator('[data-pl-inline-month="' + row['month'] + '"][data-pl-inline-open=' + field + ']')
                original = target.get_attribute('data-pl-premise-value')
                try:
                    # DOM corruption only: no input/change event or financial command.
                    target.evaluate('el=>el.dataset.plPremiseValue="987.654321"')
                    violations[field] = harness.rejected(lambda: detail_values(page, row))
                finally:
                    target.evaluate('(el,value)=>el.dataset.plPremiseValue=value', original)
                restored[field] = detail_values(page, row)
                visible_target = target.locator('[data-pl-month-value=rate]') if field == 'rate' else target
                original_html = visible_target.inner_html()
                try:
                    # Metadata remains correct; the visible amount alone is wrong.
                    visible_target.evaluate('el=>el.textContent="987.654321"')
                    violations[field + '_visible_text'] = harness.rejected(lambda: detail_values(page, row))
                finally:
                    visible_target.evaluate('(el,html)=>el.innerHTML=html', original_html)
                restored[field + '_visible_text'] = detail_values(page, row)

            return {'positive': valid, 'violations': violations, 'restored': restored}
        harness.record(report, COUNTERPROOFS[4], lambda: guard(page, harness, future_value), page, criteria='same per-month detail/input oracle rejects corrupted future rate and contribution values')
        def wrong_cost():
            row = next(row for row in model(page, fixture)['monthlyRows'] if row['month'] == fixture['start'])
            valid = detail_values(page, row)
            details = page.locator('[data-pl-month-details="' + row['month'] + '"]')
            violations = {}
            restored = {}
            for field, label, wrong in [('paidBrl', 'Pago no mês', '—'), ('costCoverage', 'Cobertura', '0%')]:
                target = detail_field(details, label)
                original = target.inner_html()
                try:
                    target.evaluate('(el,value)=>el.textContent=value', wrong)
                    violations[field] = harness.rejected(lambda: detail_values(page, row))
                finally:
                    target.evaluate('(el,html)=>el.innerHTML=html', original)
                restored[field] = detail_values(page, row)
            return {'positive': valid, 'violations': violations, 'restored': restored}
        harness.record(report, COUNTERPROOFS[5], lambda: guard(page, harness, wrong_cost), page, criteria='same bound month-field oracle rejects removed BRL cost and wrong coverage')
        def wrong_subtotal():
            totals = model(page, fixture)['phaseTotals']
            valid = subtotal_values(page, totals)
            mode = page.locator('[data-pl-monthly-layout]').get_attribute('data-pl-monthly-layout')
            target = page.locator('[data-pl-phase-total="' + str(totals[0]['cyclePhase']) + '"]').locator(':scope > th,:scope > td').nth(5 if mode == 'wide' else 2).locator('.pl-money-primary')
            original = target.inner_html()
            try:
                target.evaluate('el=>el.textContent=new Intl.NumberFormat("pt-BR",{style:"currency",currency:"USD"}).format(0)')
                invalid = harness.rejected(lambda: subtotal_values(page, totals))
            finally:
                target.evaluate('(el,html)=>el.innerHTML=html', original)
            return {'positive': valid, 'violation': invalid, 'restored': subtotal_values(page, totals)}
        harness.record(report, COUNTERPROOFS[6], lambda: guard(page, harness, wrong_subtotal), page, criteria='same phase-value oracle rejects a wrong subtotal amount despite preserved period label')
        select(page, fixture, 'consolidated')
        def missing_current_row():
            valid = current_year(page)
            marker = page.locator('[data-pl-consolidated-table] [data-pl-current-year=true]')
            marker.evaluate('''el=>{window.__compactRemovedAnnual={row:el,parent:el.parentNode,next:el.nextSibling};el.remove();}''')
            try:
                invalid = harness.rejected(lambda: current_year(page))
            finally:
                page.evaluate('''()=>{const saved=window.__compactRemovedAnnual;saved.parent.insertBefore(saved.row,saved.next);delete window.__compactRemovedAnnual;}''')
            return {'positive': valid, 'violation': invalid, 'restored': current_year(page)}
        harness.record(report, COUNTERPROOFS[7], lambda: guard(page, harness, missing_current_row), page, criteria='same read-model annual-membership oracle rejects missing current row and marker')
        harness.assert_fixture_requests(context)
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=['regressions', 'all'], default='regressions')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    import sys
    import ui_visual_quality_test as visual
    sys.argv = [sys.argv[0], '--case', 'compact-regressions' if args.case == 'regressions' else 'compact', '--out', str(args.out)]
    return visual.main()


if __name__ == '__main__':
    raise SystemExit(main())
