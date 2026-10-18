#!/usr/bin/env python3
"""Compile reviewed public local-date rules into complete, immutable UTC data.
No clock, network, third-party calendar, or financial state is consulted.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZROOT = ROOT / 'src/data/market-hours/zoneinfo'
PHASES = {'continuous', 'preopen', 'auction', 'break', 'extended', 'closed', 'unknown'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)


def local_date(value):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), 'Expected ISO local date')
    return date.fromisoformat(value)


def nonempty(value, label):
    require(isinstance(value, str) and value.strip(), label + ' is required')
    return value


def clock_seconds(value):
    require(isinstance(value, str) and re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d)?|24:00(?::00)?', value), 'Invalid wall time: ' + str(value))
    parts = list(map(int, value.split(':')))
    return parts[0] * 3600 + parts[1] * 60 + (parts[2] if len(parts) == 3 else 0)


def epoch(day, seconds, zone):
    wall = datetime.combine(day, time()) + timedelta(seconds=seconds)
    candidates = set()
    for fold in (0, 1):
        candidate = wall.replace(tzinfo=zone, fold=fold)
        utc = candidate.astimezone(timezone.utc)
        if utc.astimezone(zone).replace(tzinfo=None) == wall:
            candidates.add(int(utc.timestamp()) * 1000)
    require(len(candidates) == 1, 'Ambiguous or nonexistent local time: ' + wall.isoformat())
    return candidates.pop()


def refs(value, source_ids):
    require(isinstance(value, list) and value and len(set(value)) == len(value) and all(s in source_ids for s in value), 'Missing/unknown/duplicate source references')
    return sorted(value)


def validate_sessions(sessions, inherited_sources, source_ids):
    require(isinstance(sessions, list) and sessions, 'Sessions must be nonempty')
    spans = []
    for session in sessions:
        a, b = clock_seconds(session['start']), clock_seconds(session['end'])
        require(a < b <= 86400 and a < 86400, 'Invalid/overnight session boundaries')
        require(session['phase'] in PHASES, 'Invalid phase')
        nonempty(session.get('reason'), 'Session reason')
        refs(session.get('sourceIds', inherited_sources), source_ids)
        if 'transitionWindow' in session:
            window = session['transitionWindow']
            earliest, latest = clock_seconds(window['earliest']), clock_seconds(window['latest'])
            require(a <= earliest <= latest == b and window['nextPhase'] in PHASES, 'Invalid random transition window')
        spans.append((a, b, session))
    spans.sort(key=lambda item: item[0])
    for previous, current in zip(spans, spans[1:]):
        require(previous[1] <= current[0], 'Overlapping sessions, including inactive rules')
    for index, (_, end, session) in enumerate(spans):
        if 'transitionWindow' in session:
            following = spans[index + 1] if index + 1 < len(spans) else None
            next_phase = following[2]['phase'] if following and following[0] == end else 'closed'
            require(session['transitionWindow']['nextPhase'] == next_phase, 'Invalid random target phase')
    return spans


def compile_calendar(sources_document, rules):
    require(rules.get('schemaVersion') == 1 and sources_document.get('schemaVersion') == 1, 'Unsupported schemaVersion')
    sources = sources_document['sources']
    require(isinstance(sources, list) and sources, 'Sources required')
    source_ids = set()
    for source in sources:
        require(isinstance(source, dict), 'Invalid source')
        identifier = nonempty(source.get('id'), 'Source id')
        require(identifier not in source_ids, 'Duplicate source')
        source_ids.add(identifier)
        nonempty(source.get('title'), 'Source title')
        require(isinstance(source.get('url'), str) and re.match(r'https://[^\s/]+/', source['url']), 'Expected HTTPS source URL')
        local_date(source.get('verifiedAt'))
        require('publishedAt' in source, 'publishedAt must be explicit; null when unavailable')
        if source['publishedAt'] is not None:
            local_date(source['publishedAt'])
        if 'sha256' in source:
            require(re.fullmatch('[a-f0-9]{64}', source['sha256']), 'Invalid source hash')
    refs(rules['sources'], source_ids)
    first, last = local_date(rules['fromDate']), local_date(rules['untilDate'])
    require(first <= last, 'Invalid date coverage')
    require((last - first).days <= 5 * 366, 'Calendar coverage exceeds five years')
    manifest = read_json(TZROOT / 'manifest.json')
    require(rules.get('tzdbVersion') == manifest['version'], 'Pinned timezone version mismatch')
    venues = []
    seen_venues = set()
    require(isinstance(rules.get('venues'), list) and rules['venues'], 'Venues required')
    for venue in rules['venues']:
        vid = nonempty(venue.get('id'), 'Venue id')
        require(vid not in seen_venues, 'Duplicate venue')
        seen_venues.add(vid)
        zone_name = venue['timeZone']
        require(zone_name in manifest['files'], 'Timezone is not pinned: ' + str(zone_name))
        zone_path = TZROOT / zone_name
        data = zone_path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == manifest['files'][zone_name], 'Timezone hash mismatch: ' + zone_name)
        with zone_path.open('rb') as stream:
            zone = ZoneInfo.from_file(stream, key=zone_name)
        result_venue = {key: venue[key] for key in ('id', 'name', 'city', 'country', 'region', 'timeZone', 'lat', 'lng')}
        require(type(venue.get('lat')) in (float, int) and abs(venue['lat']) <= 90 and type(venue.get('lng')) in (float, int) and abs(venue['lng']) <= 180, 'Invalid coordinates')
        for key in ('name', 'city', 'country', 'region'):
            nonempty(venue[key], key)
        result_venue['groups'] = []
        require(isinstance(venue.get('groups'), list) and venue['groups'], 'Groups required')
        seen_groups = set()
        for group in venue['groups']:
            gid = nonempty(group.get('id'), 'Group id')
            require(gid not in seen_groups, 'Duplicate group')
            seen_groups.add(gid)
            nonempty(group.get('label'), 'Group label')
            verified = group['verifiedAt']
            local_date(verified)
            group_sources = refs(group.get('sourceIds'), source_ids)
            weekdays = group.get('weekdays', [1, 2, 3, 4, 5])
            require(isinstance(weekdays, list) and weekdays and all(type(n) is int and 1 <= n <= 7 for n in weekdays) and len(set(weekdays)) == len(weekdays), 'Invalid ISO weekdays')
            schedules = group.get('schedule', [])
            for schedule in schedules:
                start, end = local_date(schedule.get('validFrom')), local_date(schedule.get('validUntil'))
                require(start <= end, 'Invalid schedule vigency')
                refs(schedule.get('sourceIds'), source_ids)
                validate_sessions(schedule['sessions'], schedule['sourceIds'], source_ids)
            schedules = sorted(schedules, key=lambda s: s['validFrom'])
            for previous, current in zip(schedules, schedules[1:]):
                require(previous['validUntil'] < current['validFrom'], 'Overlapping schedule vigency')
            exceptions = {}
            for exception in group.get('exceptions', []):
                day_key = local_date(exception['date'])
                require(day_key not in exceptions, 'Duplicate exception date')
                require(sum(k in exception for k in ('closedReason', 'unknownReason', 'sessions')) == 1, 'Exception must have exactly one outcome')
                refs(exception.get('sourceIds'), source_ids)
                if 'sessions' in exception:
                    validate_sessions(exception['sessions'], exception['sourceIds'], source_ids)
                else:
                    nonempty(exception.get('closedReason', exception.get('unknownReason')), 'Exception reason')
                exceptions[day_key] = exception
            periods = []
            day = first
            while day <= last:
                start_day, end_day = epoch(day, 0, zone), epoch(day, 86400, zone)
                selected = next((s for s in schedules if s['validFrom'] <= day.isoformat() <= s['validUntil']), None)
                override = exceptions.get(day)
                day_sources = group_sources
                sessions = None
                if group.get('unknownReason'):
                    phase, reason = 'unknown', nonempty(group['unknownReason'], 'Unknown reason')
                elif override:
                    day_sources = refs(override['sourceIds'], source_ids)
                    if 'unknownReason' in override:
                        phase, reason = 'unknown', nonempty(override['unknownReason'], 'Unknown reason')
                    elif 'closedReason' in override:
                        phase, reason = 'closed', nonempty(override['closedReason'], 'Closed reason')
                    else:
                        sessions = override['sessions']
                elif selected is None:
                    phase, reason = 'unknown', 'Regra sem vigência confirmada para esta data'
                elif day.isoweekday() not in weekdays:
                    day_sources = refs(selected['sourceIds'], source_ids)
                    phase, reason = 'closed', 'Dia sem pregão na semana oficial'
                else:
                    day_sources = refs(selected['sourceIds'], source_ids)
                    sessions = selected['sessions']
                daily = []
                if sessions is None:
                    daily.append(dict(startUtc=start_day, endUtc=end_day, phase=phase, reason=reason, sourceIds=day_sources))
                else:
                    require(isinstance(sessions, list) and sessions, 'Session list must be nonempty; use closedReason for closure')
                    spans = []
                    for session in sessions:
                        a, b = clock_seconds(session['start']), clock_seconds(session['end'])
                        require(a < b <= 86400 and a < 86400, 'Invalid/overnight session boundaries')
                        require(session['phase'] in PHASES, 'Invalid phase')
                        nonempty(session.get('reason'), 'Session reason')
                        item = dict(startUtc=epoch(day, a, zone), endUtc=epoch(day, b, zone), phase=session['phase'], reason=session['reason'], sourceIds=refs(session.get('sourceIds', day_sources), source_ids))
                        if 'transitionWindow' in session:
                            window = session['transitionWindow']
                            earliest, latest = clock_seconds(window['earliest']), clock_seconds(window['latest'])
                            require(a <= earliest <= latest == b and window['nextPhase'] in PHASES, 'Invalid random transition window')
                            item['transitionWindow'] = dict(earliestUtc=epoch(day, earliest, zone), latestUtc=epoch(day, latest, zone), nextPhase=window['nextPhase'])
                        spans.append(item)
                    cursor = start_day
                    for item in sorted(spans, key=lambda p: p['startUtc']):
                        require(item['startUtc'] >= cursor and item['endUtc'] > item['startUtc'], 'Overlapping/invalid sessions')
                        if item['startUtc'] > cursor:
                            daily.append(dict(startUtc=cursor, endUtc=item['startUtc'], phase='closed', reason='Fora das sessões confirmadas para este grupo', sourceIds=day_sources))
                        daily.append(item)
                        cursor = item['endUtc']
                    if cursor < end_day:
                        daily.append(dict(startUtc=cursor, endUtc=end_day, phase='closed', reason='Fora das sessões confirmadas para este grupo', sourceIds=day_sources))
                for item in daily:
                    if periods and 'transitionWindow' not in periods[-1] and 'transitionWindow' not in item and periods[-1]['endUtc'] == item['startUtc'] and all(periods[-1][key] == item[key] for key in ('phase', 'reason', 'sourceIds')):
                        periods[-1]['endUtc'] = item['endUtc']
                    else:
                        periods.append(item)
                day += timedelta(days=1)
            for i, item in enumerate(periods):
                if 'transitionWindow' in item:
                    require(i + 1 < len(periods) and periods[i + 1]['phase'] == item['transitionWindow']['nextPhase'], 'Transition next phase does not match materialized period')
            result_venue['groups'].append(dict(id=gid, label=group['label'], coverage=dict(fromUtc=epoch(first, 0, zone), untilUtc=epoch(last + timedelta(days=1), 0, zone), verifiedAt=verified, sourceIds=group_sources), periods=periods))
        venues.append(result_venue)
    return dict(schemaVersion=1, tzdbVersion=manifest['version'], sources=sorted(sources, key=lambda s: s['id']), venues=venues)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', required=True)
    parser.add_argument('--rules', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        catalog = compile_calendar(read_json(args.sources), read_json(args.rules))
        payload = json.dumps(catalog, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(output.name + '.tmp')
        temporary.write_text(payload)
        temporary.replace(output)
        print('Compiled {} venues; tzdb {}; sha256 {}'.format(len(catalog['venues']), catalog['tzdbVersion'], hashlib.sha256(payload.encode()).hexdigest()))
    except (ValueError, KeyError, TypeError, OSError) as error:
        print('Calendar compilation refused: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
