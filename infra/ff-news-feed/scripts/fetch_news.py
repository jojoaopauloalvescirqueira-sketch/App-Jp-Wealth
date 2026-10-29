#!/usr/bin/env python3
"""Explicit public calendar collection, offline archives and two compatible views.

One FF request supplies both economic-calendar.json (v2, nine currencies/all
impacts) and legacy ff-high-impact.json (v1, four currencies/High). No personal
state, credentials, publication, scheduling or trading operation is performed.
An upstream failure returns nonzero and never replaces either good view.
"""
import argparse
import calendar
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent.parent
FEED_URL = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'
CALENDAR_URL = 'https://www.forexfactory.com/calendar'
OUTPUT = HERE / 'ff-high-impact.json'
PACKET_OUTPUT = HERE / 'economic-calendar.json'
ARCHIVE_DIR = HERE / 'data/snapshots'
OFFICIAL_INPUT = HERE / 'data/official-policy-2026.json'
CURRENCIES = ('USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'CNY')
LEGACY_CURRENCIES = {'USD', 'EUR', 'GBP', 'JPY'}
IMPACT = {'High': 'high', 'Medium': 'medium', 'Low': 'low', 'Holiday': 'unclassified', 'Non-Economic': 'unclassified'}
MAX_BYTES = 4_000_000
STALE_SECONDS = 2 * 60 * 60

# Explicitly reviewed October policy-meeting associations. These are local
# catalogue associations, not native FF identities or a rescheduling heuristic.
# Other events never inherit a family through title/date similarity.
POLICY_CROSSWALK = {
    ('USD', 'Federal Funds Rate', '2026-10-28T14:00:00-04:00'): 'fed-fomc-2026-10:rate-decision',
    ('USD', 'FOMC Statement', '2026-10-28T14:00:00-04:00'): 'fed-fomc-2026-10:policy-statement',
    ('USD', 'FOMC Press Conference', '2026-10-28T14:30:00-04:00'): 'fed-fomc-2026-10:press-conference',
    ('CAD', 'Overnight Rate', '2026-10-28T09:45:00-04:00'): 'boc-policy-2026-10:rate-decision',
    ('CAD', 'BOC Rate Statement', '2026-10-28T09:45:00-04:00'): 'boc-policy-2026-10:policy-statement',
    ('CAD', 'BOC Monetary Policy Report', '2026-10-28T09:45:00-04:00'): 'boc-policy-2026-10:monetary-policy-report',
    ('CAD', 'BOC Press Conference', '2026-10-28T10:30:00-04:00'): 'boc-policy-2026-10:press-conference',
}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def instant(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})', value):
        raise ValueError('Timestamp requires a valid date, time and explicit offset')
    if not value.endswith('Z') and (int(value[-5:-3]) > 23 or int(value[-2:]) > 59):
        raise ValueError('Timestamp offset is outside ISO-8601 bounds')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamp has no offset')
    return parsed


def civil(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Civil date must be YYYY-MM-DD')
    return date.fromisoformat(value)


def week_start(at):
    local = instant(at).astimezone(ZoneInfo('America/New_York')).date()
    return (local - timedelta(days=(local.weekday() + 1) % 7)).isoformat()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def fetch_feed():
    """One ordinary, identified GET. No retry, spoofing, cookies or bypass."""
    request = Request(FEED_URL, headers={'User-Agent': 'JPWealth-economic-calendar/2.0 (manual public-source collection)'})
    with urlopen(request, timeout=30) as response:
        if response.geturl() != FEED_URL:
            raise ValueError('Unexpected provider redirect; review it before collection')
        if response.headers.get_content_type() != 'application/json':
            raise ValueError('Provider returned a non-JSON content type')
        payload = response.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError('Provider response exceeds maximum size')
    return payload.decode('utf-8')


def normalize_snapshot(raw_text, collected_at, source_week=None, method='local-captured-source'):
    """Strict normalization; a bad row rejects the entire replacement snapshot."""
    instant(collected_at)
    if not isinstance(raw_text, str) or len(raw_text.encode('utf-8')) > MAX_BYTES:
        raise ValueError('Invalid or oversized source text')
    raw = json.loads(raw_text)
    if not isinstance(raw, list) or not raw or len(raw) > 3000:
        raise ValueError('Provider snapshot must be a nonempty event list')
    first = source_week or week_start(collected_at)
    if civil(first).weekday() != 6:
        raise ValueError('Provider week starts on Sunday')
    end = (civil(first) + timedelta(days=6)).isoformat()
    source_sha = digest(raw_text.encode('utf-8'))
    snapshot_id = 'ff-' + first + '-' + collected_at.replace(':', '').replace('+', '_') + '-' + source_sha[:16]
    events, fingerprints = [], set()
    for row in raw:
        if not isinstance(row, dict):
            raise ValueError('Provider row must be an object')
        title, currency, raw_at, raw_impact = (row.get(k) for k in ('title', 'country', 'date', 'impact'))
        if not isinstance(title, str) or not title.strip() or len(title) > 600 or any(ord(c) < 32 for c in title):
            raise ValueError('Provider title missing, too long or contains controls')
        if currency not in CURRENCIES:
            raise ValueError('Unrecognized provider currency')
        at = instant(raw_at)
        source_day = at.date().isoformat()
        if not first <= source_day <= end:
            raise ValueError('Provider event is outside declared source week')
        if raw_impact not in IMPACT:
            raise ValueError('Unrecognized provider impact; review before classification')
        for key in ('forecast', 'previous'):
            if key in row and (not isinstance(row[key], str) or len(row[key]) > 120):
                raise ValueError('Provider numeric display must remain a bounded string')
        fingerprint = digest(json.dumps([currency, title, raw_at], ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
        if fingerprint in fingerprints:
            raise ValueError('Duplicate provider observation in one snapshot')
        fingerprints.add(fingerprint)
        event = dict(id=snapshot_id + ':' + fingerprint[:24], title=title, currency=currency,
            impact=IMPACT[raw_impact], date=source_day, at=raw_at, precision='instant', timeConfirmed=False,
            timeZone='America/New_York', timeZoneBasis='Source timestamp has a numeric offset; display zone is New York.',
            sourceId='ff-' + currency, sourceUrl=CALENDAR_URL, sourceUid=None, status='scheduled',
            reviewedAt=collected_at, observedAt=collected_at, provider='forexfactory', providerImpact=raw_impact,
            impactOrigin='provider', identityBasis='snapshot-observation', snapshotId=snapshot_id,
            observationFingerprint=fingerprint, observationStatus='present', forecast=row.get('forecast', ''),
            previous=row.get('previous', ''), sourcePublishedAt=None, providerUpdatedAt=None)
        family = POLICY_CROSSWALK.get((currency, title, raw_at))
        if family:
            event['familyKey'] = family
            event['associationBasis'] = 'jpw-reviewed-policy-crosswalk-2026-10-v1'
        events.append(event)
    return dict(schemaVersion=2, snapshotId=snapshot_id, sourceUrl=FEED_URL,
        collectedAt=collected_at, sourcePublishedAt=None, providerUpdatedAt=None,
        sourceSha256=source_sha, sourceBytes=len(raw_text.encode('utf-8')),
        method=method, sourceWeek={'from': first, 'to': end}, events=events)


def verify_snapshot(snapshot):
    """Validate loaded observation records without upgrading their timestamp."""
    if not isinstance(snapshot, dict) or snapshot.get('schemaVersion') != 2:
        raise ValueError('Unsupported archive snapshot schema')
    instant(snapshot.get('collectedAt'))
    first = snapshot.get('sourceWeek', {}).get('from')
    if civil(first).weekday() != 6 or snapshot.get('sourceWeek', {}).get('to') != (civil(first) + timedelta(days=6)).isoformat():
        raise ValueError('Invalid archive source week')
    events = snapshot.get('events')
    if not isinstance(events, list) or not events:
        raise ValueError('Archive snapshot has no observations')
    ids = set()
    for row in events:
        if row.get('id') in ids or row.get('snapshotId') != snapshot.get('snapshotId'):
            raise ValueError('Archive identity mismatch')
        ids.add(row.get('id'))
        if row.get('currency') not in CURRENCIES or row.get('sourceId') != 'ff-' + row['currency']:
            raise ValueError('Archive currency/source mismatch')
        if row.get('sourceUid') is not None or row.get('identityBasis') != 'snapshot-observation':
            raise ValueError('Archive cannot invent a provider identity')
        if row.get('status') != 'scheduled' or row.get('timeConfirmed') is not False:
            raise ValueError('FF archive cannot prove publication or confirmed time')
        if row.get('observedAt') != snapshot['collectedAt'] or row.get('reviewedAt') != snapshot['collectedAt']:
            raise ValueError('Archive source timestamp mismatch')
        instant(row.get('at'))
    return snapshot


def load_archives(directory):
    directory = Path(directory)
    snapshots = []
    if not directory.exists():
        return snapshots
    for path in sorted(directory.glob('*/*.snapshot.json')):
        item = json.loads(path.read_text(encoding='utf-8'))
        raw_name = item.get('rawFile')
        if raw_name is not None and (not isinstance(raw_name, str) or Path(raw_name).name != raw_name or not raw_name.endswith('.source.json')):
            raise ValueError('Archive raw path must be a local source filename')
        raw_path = path.parent / raw_name if raw_name else path.with_name(path.name.replace('.snapshot.json', '.source.json'))
        payload = raw_path.read_bytes()
        if digest(payload) != item.get('sourceSha256'):
            raise ValueError('Archived provider source hash differs: ' + path.name)
        rebuilt = normalize_snapshot(payload.decode('utf-8'), item['collectedAt'], item['sourceWeek']['from'], item['method'])
        expected = {k: v for k, v in rebuilt.items() if k != 'events'} if raw_name else rebuilt
        recorded = {k: v for k, v in item.items() if k != 'rawFile'} if raw_name else item
        if expected != recorded:
            raise ValueError('Archive normalization differs from source: ' + path.name)
        snapshots.append(verify_snapshot(rebuilt))
    return snapshots


def weekly_views(snapshots):
    groups = {}
    for snapshot in snapshots:
        verify_snapshot(snapshot)
        groups.setdefault(snapshot['sourceWeek']['from'], {})[snapshot['snapshotId']] = snapshot
    views = []
    for first, keyed in sorted(groups.items()):
        rows = sorted(keyed.values(), key=lambda item: (instant(item['collectedAt']), item['snapshotId']))
        observations = {}
        for snapshot in rows:
            present = {row['observationFingerprint']: deepcopy(row) for row in snapshot['events']}
            for fingerprint, old in observations.items():
                if fingerprint not in present:
                    previous = deepcopy(old)
                    previous['observationStatus'] = 'not-in-latest'
                    previous['missingSince'] = previous.get('missingSince') or snapshot['collectedAt']
                    present[fingerprint] = previous
            observations = present
        views.append(dict(sourceWeek=rows[-1]['sourceWeek'], collectedAt=rows[-1]['collectedAt'],
            snapshotId=rows[-1]['snapshotId'], events=list(observations.values())))
    return views


def segments(first, last):
    cursor, end = civil(first), civil(last)
    while cursor <= end:
        month_end = date(cursor.year, cursor.month, calendar.monthrange(cursor.year, cursor.month)[1])
        stop = min(month_end, end)
        yield cursor.isoformat()[:7], cursor.isoformat(), stop.isoformat()
        cursor = stop + timedelta(days=1)


def official_url(value):
    if not isinstance(value, str) or any(c.isspace() for c in value):
        return False
    try:
        url = urlsplit(value)
        return url.scheme == 'https' and url.hostname in ('www.federalreserve.gov', 'www.bankofcanada.ca') and not url.username and not url.password and url.port in (None, 443)
    except ValueError:
        return False


def bounded_text(value, limit):
    return isinstance(value, str) and 0 < len(value.strip()) <= limit and not any(ord(c) < 32 for c in value)


def validate_official(packet):
    """Refuse malformed curation before any archive or last-good view is written."""
    if packet is None:
        return dict(sources=[], events=[], coverage=[], provenance=[])
    if not isinstance(packet, dict) or packet.get('schemaVersion') != 1:
        raise ValueError('Unsupported official policy curation')
    if any(not isinstance(packet.get(key), list) for key in ('sources', 'events', 'coverage', 'provenance')):
        raise ValueError('Official curation collections must be lists')
    source_ids = {}
    publisher_bindings = {
        'fed-policy': ('USD', 'www.federalreserve.gov', 'America/New_York'),
        'boc-policy': ('CAD', 'www.bankofcanada.ca', 'America/Toronto'),
    }
    for source in packet['sources']:
        if not isinstance(source, dict) or not bounded_text(source.get('id'), 80) or not re.fullmatch(r'[a-z][a-z0-9-]*', source['id']):
            raise ValueError('Official source ID is invalid')
        if source['id'] in source_ids or source.get('currency') not in CURRENCIES or not bounded_text(source.get('name'), 600):
            raise ValueError('Official source identity, name or currency is invalid')
        if not official_url(source.get('url')) or (source.get('licenseUrl') and not official_url(source['licenseUrl'])):
            raise ValueError('Official source URL must be a permitted HTTPS URL without credentials')
        if source['id'] not in publisher_bindings or (source['currency'], urlsplit(source['url']).hostname, source.get('timeZone')) != publisher_bindings[source['id']]:
            raise ValueError('Official publisher currency/host/time-zone binding is inconsistent')
        ZoneInfo(source.get('timeZone', ''))
        source_ids[source['id']] = source
    ids = set()
    for event in packet['events']:
        if not isinstance(event, dict) or not bounded_text(event.get('id'), 300) or event['id'] in ids or event.get('sourceId') not in source_ids:
            raise ValueError('Official identity/source mismatch')
        ids.add(event['id'])
        source = source_ids[event['sourceId']]
        if event.get('currency') != source['currency'] or not bounded_text(event.get('title'), 600):
            raise ValueError('Official event currency/title is invalid')
        if event.get('impact') not in ('high', 'medium', 'low', 'unclassified') or event.get('status') not in ('scheduled', 'published', 'cancelled'):
            raise ValueError('Official impact/status is invalid')
        if not official_url(event.get('sourceUrl')) or urlsplit(event['sourceUrl']).hostname != urlsplit(source['url']).hostname:
            raise ValueError('Official event URL is invalid or belongs to a different publisher')
        civil(event.get('date'))
        instant(event.get('reviewedAt'))
        for field in ('observedAt', 'sourcePublishedAt', 'providerUpdatedAt'):
            if event.get(field) is not None:
                instant(event[field])
        zone = ZoneInfo(event.get('timeZone', ''))
        if event.get('precision') == 'instant':
            at = instant(event.get('at'))
            if at.astimezone(zone).date().isoformat() != event['date'] or not isinstance(event.get('timeConfirmed'), bool):
                raise ValueError('Official source date/time confirmation is inconsistent')
        elif event.get('precision') != 'date' or event.get('at') is not None or event.get('timeConfirmed') is not False:
            raise ValueError('Official event has invalid precision')
        if event.get('impactOrigin') != 'editorial' or event.get('providerImpact') is not None or event.get('provider') != 'official':
            raise ValueError('Official publisher did not classify market impact')
    for row in packet['coverage']:
        if not isinstance(row, dict) or row.get('sourceId') not in source_ids or row.get('currency') != source_ids[row['sourceId']]['currency']:
            raise ValueError('Official coverage source/currency mismatch')
        first, last = civil(row.get('from')), civil(row.get('to'))
        if first > last or row.get('month') != first.isoformat()[:7] or row['month'] != last.isoformat()[:7]:
            raise ValueError('Official coverage interval/month is inconsistent')
        if row.get('status') != 'partial' or row.get('scope') != 'selected-policy-families':
            raise ValueError('Selected official families cannot claim complete currency coverage')
        reviewed = instant(row.get('reviewedAt'))
        if row.get('collectedAt') is not None:
            instant(row['collectedAt'])
        if row.get('validUntil') is not None and instant(row['validUntil']) < reviewed:
            raise ValueError('Official coverage validity precedes its review')
    for row in packet['provenance']:
        if not isinstance(row, dict) or not official_url(row.get('sourceUrl')):
            raise ValueError('Official evidence URL is invalid')
        instant(row.get('capturedAt'))
        if not isinstance(row.get('sourceSha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', row['sourceSha256']):
            raise ValueError('Official evidence requires its received source SHA-256')
    return packet


def build_packet(snapshots, official=None, as_of=None):
    official = validate_official(official)
    ff_observed = [item['collectedAt'] for item in snapshots]
    official_observed = [event['reviewedAt'] for event in official.get('events', [])]
    observed = ff_observed + official_observed
    if not observed:
        raise ValueError('No successfully observed source to build')
    latest_at = max(observed, key=instant)
    reference = as_of or latest_at
    instant(reference)
    current_week = week_start(reference)
    sources = [dict(id='ff-' + currency, name='Forex Factory · ' + currency, currency=currency,
        url=CALENDAR_URL, timeZone='America/New_York', provider='forexfactory',
        scope='Weekly snapshot observations, all exported impacts; not a complete month.',
        licenseUrl='https://www.forexfactory.com/notices',
        permissionBasis='Owner declaration of non-commercial permission; not independently verified.',
        attribution='Source: Forex Factory / Fair Economy; impact classification by provider.') for currency in CURRENCIES]
    events, coverage = [], []
    views = weekly_views(snapshots)
    for view in views:
        events.extend(deepcopy(view['events']))
        for currency in CURRENCIES:
            for month, first, last in segments(view['sourceWeek']['from'], view['sourceWeek']['to']):
                coverage.append(dict(sourceId='ff-' + currency, currency=currency, month=month,
                    **{'from': first, 'to': last}, status='partial', scope='weekly-snapshot',
                    archived=view['sourceWeek']['from'] != current_week, reviewedAt=view['collectedAt'],
                    collectedAt=view['collectedAt'], sourcePublishedAt=None, snapshotId=view['snapshotId'],
                    validUntil=(instant(view['collectedAt']) + timedelta(seconds=STALE_SECONDS)).isoformat().replace('+00:00', 'Z'),
                    reason='Observações da semana exportada; não comprova mês inteiro nem todos os eventos. Horários do export não distinguem provisórios.'))
    sources.extend(deepcopy(official.get('sources', [])))
    events.extend(deepcopy(official.get('events', [])))
    coverage.extend(deepcopy(official.get('coverage', [])))
    if len({event['id'] for event in events}) != len(events):
        raise ValueError('Duplicate output observation ID')
    provenance = [dict(sourceId='forexfactory', snapshotId=item['snapshotId'], sourceUrl=FEED_URL,
        capturedAt=item['collectedAt'], normalizedAt=latest_at, sourcePublishedAt=None,
        providerUpdatedAt=None, sha256=item['sourceSha256'], sourceWeek=item['sourceWeek'],
        method=item['method']) for item in sorted(snapshots, key=lambda item: (instant(item['collectedAt']), item['snapshotId']))]
    provenance.extend(deepcopy(official.get('provenance', [])))
    return dict(schemaVersion=2, generatedAt=reference, updatedAt=latest_at,
        collectedAt=max(ff_observed, key=instant) if ff_observed else latest_at,
        packagePublishedAt=reference, packageTimestampBasis='Local package transformation reference, not remote publication.',
        publishedAt=None, sourcePublishedAt=None, providerUpdatedAt=None,
        currentWeekFrom=current_week, currencies=list(CURRENCIES), months=sorted({row['month'] for row in coverage}),
        sources=sources, events=sorted(events, key=lambda row: (row['date'], row.get('at') or '', row['id'])),
        coverage=coverage, provenance=provenance,
        limitations=['Cobertura parcial por intervalos observados; ausência não significa calendário sem eventos.',
            'Sem histórico anterior à primeira captura, resultado realizado ou identidade nativa no export FF.',
            'Sumiço de observação não comprova cancelamento; revisões desconhecidas permanecem identificadas.',
            'A atualização local não publica nem ativa o alimentador remoto. Publicação depende de autorização separada.',
            'Permissão FF não comercial declarada pelo proprietário, sem auditoria documental ou ampliação comercial.'])


def legacy_packet(snapshot):
    return dict(version=1, generated_at=snapshot['collectedAt'], source='forexfactory-ff_calendar_thisweek',
        events=[dict(title=row['title'], country=row['currency'], date=row['at'], impact=row['providerImpact'],
            forecast=row['forecast'], previous=row['previous']) for row in snapshot['events']
            if row['currency'] in LEGACY_CURRENCIES and row['providerImpact'] == 'High'])


def atomic_write(path, text, immutable=False):
    path = Path(path)
    payload = text.encode('utf-8')
    path.parent.mkdir(parents=True, exist_ok=True)
    if immutable and path.exists():
        if path.read_bytes() != payload:
            raise ValueError('Refusing to replace immutable snapshot: ' + str(path))
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name + '.', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if immutable:
            try:
                os.link(temporary, path)
            except FileExistsError:
                if path.read_bytes() != payload:
                    raise ValueError('Immutable snapshot collision')
        else:
            temporary.replace(path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--fetch-ff', action='store_true', help='One explicit public provider GET')
    group.add_argument('--input-ff', type=Path, help='Previously captured raw JSON, no network')
    group.add_argument('--rebuild-archives', action='store_true', help='Reproduce from immutable archives only')
    parser.add_argument('--collected-at', help='Original successful capture timestamp, required for --input-ff')
    parser.add_argument('--week-start', help='Source Sunday, otherwise calculated from original capture timestamp')
    parser.add_argument('--as-of', help='Explicit package transformation reference, never a new source capture')
    parser.add_argument('--archive-dir', type=Path, default=ARCHIVE_DIR)
    parser.add_argument('--output', type=Path, default=PACKET_OUTPUT)
    parser.add_argument('--legacy-output', type=Path, default=OUTPUT)
    parser.add_argument('--official-input', type=Path, default=OFFICIAL_INPUT)
    parser.add_argument('--diagnostic-output', type=Path)
    parser.add_argument('--check', action='store_true', help='Compare deterministic output without writing')
    args = parser.parse_args(argv)
    previous_good = {'economic-calendar': args.output.exists(), 'legacy': args.legacy_output.exists()}
    diagnostic = dict(result='NOT_RUN', sourceUrl=FEED_URL, outputsWritten=[], previousGood=previous_good)
    try:
        official = json.loads(args.official_input.read_text()) if args.official_input and args.official_input.exists() else None
        snapshots = load_archives(args.archive_dir)
        current, raw = None, None
        if args.fetch_ff:
            raw, captured = fetch_feed(), utc_now()
            current = normalize_snapshot(raw, captured, args.week_start, 'explicit-public-GET')
        elif args.input_ff:
            if not args.collected_at:
                raise ValueError('--input-ff requires the original --collected-at; local rebuild cannot renew source time')
            raw = args.input_ff.read_bytes().decode('utf-8')
            current = normalize_snapshot(raw, args.collected_at, args.week_start, 'local-captured-source')
        if current and not any(s['snapshotId'] == current['snapshotId'] for s in snapshots):
            snapshots.append(current)
        package = build_packet(snapshots, official, args.as_of)
        latest = max(snapshots, key=lambda item: (instant(item['collectedAt']), item['snapshotId'])) if snapshots else None
        outputs = [(args.output, encoded(package))]
        if latest:
            outputs.append((args.legacy_output, encoded(legacy_packet(latest))))
        if args.check:
            for path, text in outputs:
                if not path.exists() or path.read_text(encoding='utf-8') != text:
                    raise ValueError('Offline reproduction differs: ' + str(path))
        else:
            if current:
                base = args.archive_dir / current['sourceWeek']['from'] / current['snapshotId']
                raw_name = current['sourceSha256'] + '.source.json'
                atomic_write(base.parent / raw_name, raw, immutable=True)
                # Same-byte recaptures reuse raw data; each immutable receipt
                # records its own collection time without repeating 97 rows.
                manifest = {key: value for key, value in current.items() if key != 'events'}
                manifest['rawFile'] = raw_name
                atomic_write(base.with_name(base.name + '.snapshot.json'), encoded(manifest), immutable=True)
            for path, text in outputs:
                atomic_write(path, text)
                diagnostic['outputsWritten'].append(str(path))
        diagnostic.update(result='PASS', snapshotId=current['snapshotId'] if current else None,
            collectedAt=package['collectedAt'], packagePublishedAt=package['packagePublishedAt'],
            events=len(package['events']), coverageRows=len(package['coverage']), networkRequests=1 if args.fetch_ff else 0,
            checkOnly=args.check, deployment='NOT_PERFORMED')
        print(encoded(diagnostic).rstrip())
        if args.diagnostic_output:
            atomic_write(args.diagnostic_output, encoded(diagnostic))
        return 0
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as error:
        diagnostic.update(result='ENVIRONMENT_ERROR' if isinstance(error, OSError) else 'PRODUCT_FAIL',
            errorType=type(error).__name__, message=str(error), networkRequests=1 if args.fetch_ff else 0,
            latestGoodPreserved=not diagnostic['outputsWritten'], deployment='NOT_PERFORMED')
        print(encoded(diagnostic).rstrip(), file=sys.stderr)
        if args.diagnostic_output:
            atomic_write(args.diagnostic_output, encoded(diagnostic))
        return 1


if __name__ == '__main__':
    sys.exit(main())
