#!/usr/bin/env python3
"""Explicit, offline-first BEA schedule collector. Python standard library only.

Network is used only with --fetch-bea, for one fixed official endpoint. It never
publishes, schedules a job, uses credentials, or accesses any other provider.
"""
import argparse
import calendar
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.request import Request, urlopen

BEA_URL = 'https://www.bea.gov/news/schedule/ics/online-calendar-subscription.ics'
BEA_PAGE = 'https://www.bea.gov/news/schedule/icalendar'
BEA_LICENSE = 'https://www.bea.gov/help/faq/147'


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def atomic_write(path, text):
    """Validate first, replace last; invalid source cannot overwrite good output."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                     prefix='.' + path.name + '.', delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(text)
    try:
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def ical_text(value):
    return re.sub(r'\\([nN,;\\])', lambda m: '\n' if m[1].lower() == 'n' else m[1], value).strip()


def impact_for_bea(title):
    # JP Wealth editorial policy, never a BEA classification or trade instruction.
    if title.startswith(('GDP ', 'Personal Income and Outlays')):
        return 'high'
    if title.startswith('U.S. International Trade in Goods and Services'):
        return 'medium'
    return 'low'


def parse_bea_ics(text, reviewed_at):
    """Strict official BEA UTC events; RFC5545 UID survives schedule changes."""
    lines = re.sub(r'\r?\n[ \t]', '', text).splitlines()
    if not lines or lines[0].strip() != 'BEGIN:VCALENDAR' or 'END:VCALENDAR' not in lines:
        raise ValueError('BEA response is not a complete VCALENDAR')
    rows, fields = [], None
    for line in lines:
        if line == 'BEGIN:VEVENT':
            if fields is not None:
                raise ValueError('Nested VEVENT')
            fields = {}
        elif line == 'END:VEVENT':
            if fields is None:
                raise ValueError('Unbalanced VEVENT')
            uid, title = fields.get('UID', ''), ical_text(fields.get('SUMMARY', ''))
            if not uid or not title or len(uid) > 250:
                raise ValueError('BEA event missing stable UID or title')
            raw_at = fields.get('DTSTART', '')
            if not re.fullmatch(r'\d{8}T\d{6}Z', raw_at):
                raise ValueError('BEA event requires explicit UTC DTSTART')
            instant = datetime.strptime(raw_at, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)
            at = instant.isoformat().replace('+00:00', 'Z')
            # BEA schedule declares UTC. Keep that source civil date; app can project it.
            rows.append(dict(id='bea:' + uid, title=title, currency='USD',
                impact=impact_for_bea(title), date=at[:10], at=at, precision='instant',
                sourceId='bea', sourceUrl=BEA_PAGE, timeZone='UTC',
                status='cancelled' if fields.get('STATUS') == 'CANCELLED' else 'scheduled',
                reviewedAt=reviewed_at, sequence=int(fields.get('SEQUENCE', '0')),
                sourceUpdatedAt=fields.get('LAST-MODIFIED') or fields.get('DTSTAMP'),
                sourceUid=uid, editorialPolicy='jpw-macro-impact-v1'))
            fields = None
        elif fields is not None and ':' in line:
            key, value = line.split(':', 1)
            key = key.split(';', 1)[0]
            if key in fields and key in ('UID', 'DTSTART', 'SUMMARY', 'SEQUENCE'):
                raise ValueError('Duplicate BEA identity/time field')
            fields[key] = value
    if fields is not None or not rows:
        raise ValueError('Incomplete or empty BEA schedule; preserve prior output')
    latest = {}
    for row in rows:
        before = latest.get(row['id'])
        if before is None or (row['sequence'], row.get('sourceUpdatedAt') or '') > (
                before['sequence'], before.get('sourceUpdatedAt') or ''):
            latest[row['id']] = row
    return sorted(latest.values(), key=lambda item: (item['at'], item['id']))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--month', required=True, help='YYYY-MM, inclusive full source month')
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--input-bea', type=Path, help='Previously captured official ICS (offline)')
    inputs.add_argument('--fetch-bea', action='store_true', help='Explicitly GET official BEA ICS')
    parser.add_argument('--output', required=True, type=Path, help='BEA normalized JSON, never deployed')
    parser.add_argument('--snapshot-output', type=Path, help='Optional raw ICS capture for provenance')
    args = parser.parse_args(argv)
    if not re.fullmatch(r'\d{4}-\d{2}', args.month):
        parser.error('month must be YYYY-MM')
    first = datetime.strptime(args.month, '%Y-%m')
    last_day = calendar.monthrange(first.year, first.month)[1]
    if args.fetch_bea:
        request = Request(BEA_URL, headers={'User-Agent': 'JPWealth-schedule-review/1.0 (manual collection)'})
        with urlopen(request, timeout=20) as response:
            if response.geturl() != BEA_URL:
                raise ValueError('Unexpected BEA redirect; review before collection')
            payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise ValueError('BEA source exceeds size limit')
    else:
        payload = args.input_bea.read_bytes()
    reviewed_at = utc_now()
    rows = parse_bea_ics(payload.decode('utf-8-sig'), reviewed_at)
    events = [row for row in rows if row['date'].startswith(args.month)]
    package = dict(schemaVersion=1, updatedAt=reviewed_at, events=events,
        provenance=dict(sourceId='bea', sourceUrl=BEA_URL, licenseUrl=BEA_LICENSE,
            capturedAt=reviewed_at if args.fetch_bea else None, normalizedAt=reviewed_at,
            method='explicit-official-GET' if args.fetch_bea else 'local-source-file',
            sha256=hashlib.sha256(payload).hexdigest(), fullSourceEventCount=len(rows),
            sourceRange={'from': min(r['date'] for r in rows), 'to': max(r['date'] for r in rows)}),
        coverage=[dict(currency='USD', sourceId='bea', month=args.month,
            **{'from': args.month + '-01', 'to': args.month + '-%02d' % last_day},
            status='confirmed', reviewedAt=reviewed_at,
            reason='Complete BEA source schedule for this month only; excludes BLS and Federal Reserve.')])
    encoded = json.dumps(package, ensure_ascii=False, indent=2) + '\n'
    if args.snapshot_output:
        atomic_write(args.snapshot_output, payload.decode('utf-8-sig'))
    atomic_write(args.output, encoded)
    print('BEA source month %s: %d events; local output only.' % (args.month, len(events)))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print('Collection refused: %s' % error, file=sys.stderr)
        sys.exit(1)
