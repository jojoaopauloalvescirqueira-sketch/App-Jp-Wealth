"""Fixtures nominais do bootstrap econômico para os sete checks noturnos.

Não substitui app, storage, documentos ou SW. Context routes cobrem também as
requisições do worker no Playwright instalado; o teste documental prova isso.
Rede desconhecida não recebe sucesso sintético. O firewall processual é separado.
"""
import json
import math
import os
import time
from pathlib import Path
from urllib.parse import urlsplit

FEED_URL = 'https://raw.githubusercontent.com/jojoaopauloalvescirqueira-sketch/jp-wealth-news-feed/main/ff-high-impact.json'
FX_PAIRS = ('EUR/USD', 'GBP/USD', 'AUD/USD', 'NZD/USD', 'USD/JPY', 'USD/CHF', 'USD/CAD', 'AUD/CAD', 'USD/BRL')
FX_URLS = {'https://api.frankfurter.dev/v2/rate/' + pair: pair for pair in FX_PAIRS}


def _record(context, event, **data):
    target = os.environ.get('JPW_REQUEST_TRACE')
    if target:
        with Path(target).open('a') as output:
            output.write(json.dumps({'pid': os.getpid(), 'context': id(context),
                'time_ns': time.time_ns(), 'event': event, **data}, ensure_ascii=False) + '\n')


def _request(request):
    worker = request.service_worker
    return {'request_id': id(request._impl_obj), 'url': request.url,
            'method': request.method, 'type': request.resource_type,
            'worker': worker.url if worker else None}


def install_bootstrap(context, fx_rates=None):
    """Instalar uma vez, antes da carga; fx_rates conserva taxas da suíte chamadora."""
    if hasattr(context, '_jpw_bootstrap_unexpected'):
        return
    rates = dict(fx_rates or {})
    assert set(rates) <= {pair.replace('/', '') for pair in FX_PAIRS}
    assert all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0 for v in rates.values())
    context._jpw_bootstrap_unexpected = []
    context.on('request', lambda r: _record(context, 'request', **_request(r)))
    context.on('requestfailed', lambda r: _record(context, 'requestfailed', **_request(r), failure=r.failure))
    context.on('response', lambda r: _record(context, 'response', **_request(r.request), status=r.status, from_service_worker=r.from_service_worker))
    context.on('console', lambda m: _record(context, 'console', type=m.type, text=m.text, location=m.location))
    context.on('weberror', lambda e: _record(context, 'weberror', error=str(e.error)))

    def respond(route):
        request = route.request
        url = request.url
        parsed = urlsplit(url)
        if parsed.scheme in ('http', 'https') and parsed.hostname in ('127.0.0.1', 'localhost', '::1') or parsed.scheme in ('file', 'data', 'blob'):
            route.continue_()
            return
        if request.method == 'GET' and url == FEED_URL:
            payload = {'version': 1, 'generated_at': '2026-09-10T00:00:00Z', 'events': []}
        elif request.method == 'GET' and url in FX_URLS:
            base, quote = FX_URLS[url].split('/')
            payload = {'date': '2026-09-10', 'base': base, 'quote': quote,
                       'rate': rates.get(base + quote, 1.0)}
        else:
            context._jpw_bootstrap_unexpected.append({'url': url, 'method': request.method})
            _record(context, 'unexpected-resource', **_request(request))
            route.abort('blockedbyclient')
            return
        _record(context, 'fixture', **_request(request), payload=payload)
        route.fulfill(status=200, content_type='application/json', body=json.dumps(payload))

    context.route('**/*', respond)
    _record(context, 'fixtures-installed', existing_pages=len(context.pages))


def wait_bootstrap(page):
    """Aguardar operações reais antes de semear/checkpoint, sem ocultar writes."""
    page.wait_for_function("() => typeof ffNewsInFlight !== 'undefined' && !ffNewsInFlight && !document.getElementById('fxUpdateBtn')?.disabled")
    assert_fixture_requests(page.context)


def assert_fixture_requests(context):
    assert not context._jpw_bootstrap_unexpected, context._jpw_bootstrap_unexpected
