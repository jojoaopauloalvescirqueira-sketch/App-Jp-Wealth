#!/usr/bin/env python3
"""Rebuild the reviewed public packet and its embedded JS block, entirely offline.

Input evidence and explicit curation live beside this script. No network,
publication, keys, dependencies or app persistence are involved.
"""
from datetime import datetime, timedelta, timezone
import argparse
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path):
    return json.loads(path.read_text())


def build_package(check=False):
    bea = load(HERE / 'data/bea-2026-10.json')
    captures = load(HERE / 'evidence/source-captures.json')
    curation = load(HERE / 'data/curation-2026-10.json')
    for capture in captures:
        if capture.get('evidenceFile'):
            actual = hashlib.sha256((HERE / 'evidence' / capture['evidenceFile']).read_bytes()).hexdigest()
            if actual != capture['evidenceSha256']:
                raise ValueError('Evidence changed without documentary review: ' + capture['id'])
    raw_bea = (HERE / 'evidence/bea-schedule.ics').read_bytes()
    if hashlib.sha256(raw_bea).hexdigest() != bea['provenance']['sha256']:
        raise ValueError('BEA source hash mismatch')
    captured = {row['id']: row for row in captures}
    stamp = max([bea['updatedAt']] + [row['capturedAt'] for row in captures if row.get('capturedAt')])
    valid_until = (datetime.fromisoformat(stamp.replace('Z', '+00:00')) + timedelta(hours=48)).isoformat().replace('+00:00', 'Z')
    sources = [
        dict(id='bea', name='U.S. Bureau of Economic Analysis', currency='USD', timeZone='UTC',
             url='https://www.bea.gov/news/schedule/icalendar', license='U.S. public domain',
             licenseUrl='https://www.bea.gov/help/faq/147', attribution='Source: U.S. Bureau of Economic Analysis',
             scope='BEA release schedule; excludes BLS/Federal Reserve'),
        dict(id='bls', name='U.S. Bureau of Labor Statistics — pendente', currency='USD', timeZone='America/New_York',
             url='https://www.bls.gov/schedule/', scope='No reviewed package in this delivery'),
        dict(id='fed', name='Federal Reserve — pendente', currency='USD', timeZone='America/New_York',
             url='https://www.federalreserve.gov/newsevents/calendar.htm', scope='No reviewed package in this delivery'),
        dict(id='ons', name='Office for National Statistics', currency='GBP', timeZone='Europe/London',
             url='https://www.ons.gov.uk/releasecalendar', license='Open Government Licence v3.0',
             licenseUrl='https://www.ons.gov.uk/help/terms-conditions', attribution='Source: Office for National Statistics, © Crown copyright 2026; adapted by JP Wealth',
             scope='Explicit economic release catalogue in curation-2026-10.json; not all ONS releases'),
        dict(id='boe', name='Bank of England — pendente', currency='GBP', timeZone='Europe/London',
             url='https://www.bankofengland.co.uk/news', scope='No reviewed package in this delivery'),
        dict(id='sbj', name='Statistics Bureau of Japan', currency='JPY', timeZone='Asia/Tokyo',
             url='https://www.stat.go.jp/english/', license='Public Data License 1.0 / CC BY 4.0 compatible',
             licenseUrl='https://www.stat.go.jp/english/info/riyou.html', attribution='Created by JP Wealth by editing Statistics Bureau of Japan release schedules, accessed 2026-10-23; not a Government of Japan product',
             scope='CPI, labour force, household expenditure, savings, business structure and population schedules; date only'),
        dict(id='boj', name='Bank of Japan — pendente', currency='JPY', timeZone='Asia/Tokyo',
             url='https://www.boj.or.jp/en/', scope='No reviewed package in this delivery'),
        dict(id='statsnz', name='Stats NZ — publicações selecionadas', currency='NZD', timeZone='Pacific/Auckland',
             url='https://www.stats.govt.nz/release-calendar/', license='CC BY 4.0 (Crown copyright; exceptions apply)',
             licenseUrl='https://www.stats.govt.nz/about-us/copyright/',
             attribution='This work is based on/includes Stats NZ’s data which are licensed by Stats NZ for reuse under the Creative Commons Attribution 4.0 International licence. Adapted by JP Wealth.',
             scope='CPI September quarter and selected price indexes September only; export not validated'),
        dict(id='statsnz-calendar', name='Stats NZ — calendário completo pendente', currency='NZD', timeZone='Pacific/Auckland',
             url='https://www.stats.govt.nz/release-calendar/', scope='Calendar export not validated; no complete month claim'),
        dict(id='rbnz', name='Reserve Bank of New Zealand — pendente', currency='NZD', timeZone='Pacific/Auckland',
             url='https://www.rbnz.govt.nz/', scope='Automated access prohibited without permission; no automated collection or claimed human curation'),
        dict(id='chf-pending', name='CHF — licença de agenda pendente', currency='CHF', timeZone='Europe/Zurich',
             url='https://opendata.swiss/', scope='No official calendar commercial redistribution licence verified; no events shipped')
    ]
    events = list(bea['events'])
    catalogue = set(curation['ons']['selectedUris'])
    seen, query_counts = set(), {}
    for capture_id in ('ons-published', 'ons-upcoming', 'ons-cancelled'):
        response = load(HERE / 'evidence' / (capture_id + '.json'))
        releases = response['releases']
        expected = response['breakdown']['total']
        if len(releases) != expected:
            raise ValueError('ONS pagination incomplete')
        query_counts[capture_id] = len(releases)
        for row in releases:
            if row['uri'] not in catalogue:
                continue
            description = row['description']
            title = description['title'].strip()
            at = description['release_date']
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z', at):
                raise ValueError('ONS release lacks explicit UTC instant')
            dt = datetime.fromisoformat(at.replace('Z', '+00:00'))
            source_date = dt.astimezone(ZoneInfo('Europe/London')).date().isoformat()
            prefix = title.lower()
            impact = 'low'
            if prefix.startswith(('gdp monthly estimate', 'consumer price inflation', 'uk labour market', 'retail sales')):
                impact = 'high'
            elif prefix.startswith(('index of production', 'index of services', 'uk trade', 'producer price inflation',
                                    'public sector finances', 'earnings and employment', 'employee earnings', 'construction output')):
                impact = 'medium'
            events.append(dict(id='ons:' + row['uri'].split('/')[-1], title=title,
                currency='GBP', impact=impact, date=source_date, at=at, precision='instant',
                sourceId='ons', sourceUrl='https://www.ons.gov.uk' + row['uri'], timeZone='Europe/London',
                status='cancelled' if description['cancelled'] else ('published' if description['published'] else 'scheduled'),
                reviewedAt=captured[capture_id]['capturedAt'], sourceUid=row['uri'],
                documentaryEvidence=capture_id, dateChanges=row.get('date_changes'), editorialPolicy='jpw-macro-impact-v1'))
            seen.add(row['uri'])
    if seen != catalogue:
        raise ValueError('Curated ONS identity missing from full-month evidence')
    for row in curation['sbj']:
        evidence = captured[row['documentaryEvidence']]
        events.append(dict(row, currency='JPY', sourceId='sbj', timeZone='Asia/Tokyo',
                           reviewedAt=evidence['capturedAt'], status='scheduled', at=None,
                           precision='date', editorialPolicy='jpw-macro-impact-v1'))
    for row in curation['statsnz']:
        events.append(dict(row, currency='NZD', sourceId='statsnz', timeZone='Pacific/Auckland',
                           editorialPolicy='jpw-macro-impact-v1'))
    if len({event['id'] for event in events}) != len(events):
        raise ValueError('Duplicate canonical event identity')
    coverage = []
    reasons = {
        'bea':('confirmed','Mês completo do calendário BEA somente; USD continua parcial sem BLS e Fed.'),
        'bls':('pending','Calendário BLS ainda não coletado/revisado neste pacote.'),
        'fed':('pending','Calendário Federal Reserve ainda não coletado/revisado neste pacote.'),
        'ons':('confirmed','Catálogo econômico ONS explicitamente selecionado: mês inteiro, publicadas/futuras/canceladas consultadas; exclui séries duplicadas e publicações fora do catálogo.'),
        'boe':('pending','Bank of England sem pacote de eventos revisado.'),
        'sbj':('partial','Seis famílias de calendários oficiais SBJ; horários não comprovados, datas preservadas no Japão. Não cobre todas as estatísticas japonesas.'),
        'boj':('pending','Bank of Japan sem pacote de eventos revisado.'),
        'statsnz':('partial','Somente CPI trimestral e selected price indexes comprovados; não representa o mês econômico NZD completo.'),
        'statsnz-calendar':('pending','Exportação mensal Stats NZ ainda não validada; ausência de outros eventos não significa agenda vazia.'),
        'rbnz':('pending','Sem acesso automatizado autorizado e sem curadoria humana fornecida; nenhum evento presumido.'),
        'chf-pending':('pending','Redistribuição comercial gratuita da agenda oficial CHF não comprovada; nenhum evento presumido.')
    }
    for source in sources:
        status, reason = reasons[source['id']]
        row = dict(currency=source['currency'], sourceId=source['id'], month='2026-10',
            **{'from':'2026-10-01','to':'2026-10-31'}, status=status, reviewedAt=stamp, reason=reason)
        if status in ('confirmed', 'partial'):
            row['validUntil'] = valid_until
        coverage.append(row)
    if any(event['date'].startswith('2026-11') for event in events):
        coverage.append(dict(currency='NZD', sourceId='statsnz', month='2026-11',
            **{'from':'2026-11-01','to':'2026-11-30'}, status='partial', reviewedAt=stamp, validUntil=valid_until,
            reason='Somente próxima divulgação SPI citada na publicação de setembro; demais eventos não revisados, horário não informado.'))
    packet = dict(schemaVersion=1, generatedAt=stamp, updatedAt=stamp,
        currencies=['USD','GBP','JPY','NZD','CHF'], months=['2026-10'], sources=sources,
        editorialPolicy=dict(id='jpw-macro-impact-v1', publisher='JP Wealth', kind='editorial',
            disclaimer='Impacto editorial JP Wealth; não informado pelas fontes e não é autorização operacional.',
            dateOnly='Dia do calendário da fonte; horário não informado. A data não muda com o fuso do usuário.'),
        events=sorted(events, key=lambda row:(row['date'], row.get('at') or '', row['id'])), coverage=coverage,
        provenance=[bea['provenance']] + captures + [dict(sourceId='ons',method='explicit-catalogue-selection',queryCounts=query_counts,
            catalogueFile='data/curation-2026-10.json', selectedCount=len(catalogue))] + curation.get('externalDocumentaryEvidence',[]),
        limitations=['Entrega parcial por fontes/famílias; não comprova mês completo de todas as cinco moedas.',
            'Não contém valores anteriores, consenso, resultado, surpresa ou impacto nativo de provedor.',
            'Status scheduled em calendário passado não comprova publicação; não inferir published pela passagem do tempo.',
            'Sem atualização automática no app; pacote estático revisado, validade de cobertura de 48 horas.',
            'Curadoria documental assistida por IA não é aceite ou revisão humana.',
            'Identidades SBJ por família/período; ONS por URI; BEA por UID. Nunca usar a data de divulgação como identidade.'])
    encoded = json.dumps(packet,ensure_ascii=False,indent=2) + '\n'
    output = HERE / 'data/monthly-economic-2026-10.json'
    model = ROOT / 'src/js/40-app/16-monthly-economic-data.js'
    text = model.read_text()
    # The same JS is inlined into the portable HTML: source text must not end
    # its script element. Escape only the JS representation, keeping JSON exact.
    inline_encoded = encoded.replace('<', '\\u003c')
    replacement = '/* JPW_MONTHLY_DATA_BEGIN */\n' + inline_encoded.rstrip() + '\n  /* JPW_MONTHLY_DATA_END */'
    text, count = re.subn(r'/\* JPW_MONTHLY_DATA_BEGIN \*/[\s\S]*?/\* JPW_MONTHLY_DATA_END \*/',lambda match:replacement,text)
    if count != 1:
        raise ValueError('Expected exactly one embedded package block')
    if check:
        if output.read_text() != encoded or model.read_text() != text:
            raise ValueError('Offline reproduction differs from canonical JSON or embedded block')
        print('Offline package verified: %d events; no files written.' % len(events))
    else:
        output.write_text(encoded)
        model.write_text(text)
        print('Embedded %d real events; source coverage stays explicit and partial.' % len(events))
    return packet


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Verify offline reproduction without writing files')
    build_package(check=parser.parse_args().check)
