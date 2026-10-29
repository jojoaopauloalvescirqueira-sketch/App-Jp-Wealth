#!/usr/bin/env python3
"""Offline collector regressions. Only temporary directories and synthetic data.

The product mutations named by these cases are: early CAD/non-High filtering;
false source-time renewal; cancellation inferred from absence; archive weeks
replaced globally; fabricated native identity/time; corrupted source accepted;
upstream failure reported as success; double fetch for compatible outputs.
"""
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get('JPW_FF_COLLECTOR', ROOT / 'infra/ff-news-feed/scripts/fetch_news.py'))
spec = importlib.util.spec_from_file_location('jpw_ff_calendar_collector', SOURCE)
feed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feed)
STAMP = '2026-10-28T20:21:55Z'
LATER = '2026-10-28T20:51:55Z'


def row(currency='CAD', title='Synthetic event', at='2026-10-28T09:45:00-04:00', impact='High'):
    return dict(title=title, country=currency, date=at, impact=impact, forecast='', previous='')


def snapshot(rows=None, stamp=STAMP, week=None):
    return feed.normalize_snapshot(json.dumps(rows or [row()]), stamp, week)


class CollectorTests(unittest.TestCase):
    def test_cad_and_all_nine_currencies_reach_packet(self):
        expected = {'USD','EUR','GBP','JPY','CHF','CAD','AUD','NZD','CNY'}
        packet = feed.build_packet([snapshot([row(c, c) for c in expected])])
        self.assertEqual({e['currency'] for e in packet['events']}, expected)
        self.assertEqual(set(packet['currencies']), expected)

    def test_high_medium_low_and_non_economic_are_preserved(self):
        snap = snapshot([row(title=i, impact=i) for i in ['High','Medium','Low','Holiday']])
        packet = feed.build_packet([snap])
        self.assertEqual({e['impact'] for e in packet['events']}, {'high','medium','low','unclassified'})
        self.assertEqual({e['providerImpact'] for e in packet['events']}, {'High','Medium','Low','Holiday'})

    def test_compatibility_view_stays_four_currencies_high_only(self):
        snap = snapshot([row(c, c) for c in ('USD','EUR','GBP','JPY','CAD')] + [row('USD','Medium',impact='Medium')])
        legacy = feed.legacy_packet(snap)
        self.assertEqual({e['country'] for e in legacy['events']}, {'USD','EUR','GBP','JPY'})
        self.assertTrue(all(e['impact']=='High' for e in legacy['events']))
        self.assertEqual(legacy['version'], 1)
        self.assertEqual(legacy['generated_at'], STAMP)

    def test_omission_remains_visible_without_cancel_or_publication(self):
        a = snapshot([row(title='A'),row(title='B')])
        b = snapshot([row(title='A')], LATER)
        events = feed.build_packet([a,b])['events']
        omitted = next(e for e in events if e['title']=='B')
        self.assertEqual(omitted['observationStatus'], 'not-in-latest')
        self.assertEqual(omitted['status'], 'scheduled')
        self.assertEqual(omitted['observedAt'], STAMP)
        self.assertEqual(omitted['missingSince'], LATER)
        self.assertEqual(next(e for e in events if e['title']=='A')['observationStatus'], 'present')

    def test_returning_observation_replaces_its_missing_copy(self):
        a = snapshot([row(title='A'),row(title='B')])
        b = snapshot([row(title='A')], LATER)
        c = snapshot([row(title='A'),row(title='B')], '2026-10-28T21:21:55Z')
        events = feed.build_packet([a,b,c])['events']
        self.assertEqual(len(events),2)
        self.assertTrue(all(e['observationStatus']=='present' for e in events))

    def test_next_week_does_not_mark_archived_week_missing(self):
        old = snapshot([row(title='Old')])
        new = snapshot([row(title='New', at='2026-11-04T08:30:00-05:00')], '2026-11-04T14:00:00Z')
        packet = feed.build_packet([old,new])
        self.assertEqual(next(e for e in packet['events'] if e['title']=='Old')['observationStatus'], 'present')
        old_cov = [c for c in packet['coverage'] if c['month']=='2026-10']
        self.assertTrue(all(c['archived'] for c in old_cov))
        self.assertTrue(all(c['collectedAt']==STAMP for c in old_cov))

    def test_feed_has_no_fabricated_provider_id_or_actual_value(self):
        event = snapshot()['events'][0]
        self.assertIsNone(event['sourceUid'])
        self.assertEqual(event['identityBasis'], 'snapshot-observation')
        self.assertIsNone(event['providerUpdatedAt'])
        self.assertIsNone(event['sourcePublishedAt'])
        self.assertNotIn('actual', event)
        self.assertFalse(event['timeConfirmed'])

    def test_offset_preserved_and_tentative_time_is_not_confirmed(self):
        event = snapshot([row(at='2026-10-28T00:30:00-04:00')])['events'][0]
        self.assertEqual(event['at'], '2026-10-28T00:30:00-04:00')
        self.assertEqual(event['precision'], 'instant')
        self.assertFalse(event['timeConfirmed'])

    def test_rebuild_reference_cannot_refresh_source_collection(self):
        packet = feed.build_packet([snapshot()], as_of='2026-11-05T00:00:00Z')
        self.assertEqual(packet['collectedAt'], STAMP)
        self.assertEqual(packet['updatedAt'], STAMP)
        self.assertEqual(packet['packagePublishedAt'], '2026-11-05T00:00:00Z')
        self.assertTrue(all(c['validUntil']=='2026-10-28T22:21:55Z' for c in packet['coverage']))

    def test_week_coverage_is_interval_not_full_month(self):
        packet = feed.build_packet([snapshot()])
        self.assertTrue(all(c['from']=='2026-10-25' and c['to']=='2026-10-31' for c in packet['coverage']))
        self.assertTrue(all(c['status']=='partial' and c['scope']=='weekly-snapshot' for c in packet['coverage']))

    def test_week_spanning_months_is_split_without_fake_gaps(self):
        snap = snapshot([row(at='2026-11-30T08:30:00-05:00')], '2026-12-01T12:00:00Z')
        usd = [c for c in feed.build_packet([snap])['coverage'] if c['currency']=='USD']
        self.assertEqual([(c['from'],c['to']) for c in usd], [('2026-11-29','2026-11-30'),('2026-12-01','2026-12-05')])

    def test_empty_html_and_non_list_source_refused(self):
        for raw in ['[]','{}','<html>upstream unavailable</html>','null']:
            with self.subTest(raw=raw), self.assertRaises((ValueError,TypeError)):
                feed.normalize_snapshot(raw, STAMP)

    def test_bad_date_and_missing_offset_refuse_whole_snapshot(self):
        for at in ['2026-02-30T09:45:00-04:00','2026-10-28T09:45:00','2026-11-04T09:45:00-05:00','2026-10-28T09:45:00+01:99']:
            with self.subTest(at=at), self.assertRaises(ValueError):
                feed.normalize_snapshot(json.dumps([row(),row(title='bad',at=at)]), STAMP)

    def test_invalid_currency_impact_and_control_text_refused(self):
        for bad in [row(currency='XXX'),row(impact='Definitely high'),row(title='Bad\nTitle')]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                feed.normalize_snapshot(json.dumps([bad]), STAMP)

    def test_zero_string_preserved_and_missing_not_coerced_numeric(self):
        source = row();source['forecast']='0';source['previous']=''
        event = snapshot([source])['events'][0]
        self.assertEqual(event['forecast'],'0')
        self.assertEqual(event['previous'],'')
        source['forecast']=0
        with self.assertRaises(ValueError):snapshot([source])

    def test_duplicate_observations_refused(self):
        with self.assertRaises(ValueError):snapshot([row(),row()])

    def test_same_title_new_time_is_not_automatically_a_reschedule(self):
        a = snapshot([row()])
        b = snapshot([row(at='2026-10-28T10:45:00-04:00')], LATER)
        events = feed.build_packet([a,b])['events']
        self.assertEqual(len(events),2)
        self.assertNotEqual(events[0]['id'],events[1]['id'])
        self.assertEqual({e['observationStatus'] for e in events}, {'present','not-in-latest'})

    def test_crosswalk_is_explicit_not_generic_title_day(self):
        known = snapshot([row('USD','Federal Funds Rate','2026-10-28T14:00:00-04:00')])['events'][0]
        changed = snapshot([row('USD','Federal Funds Rate','2026-10-28T15:00:00-04:00')])['events'][0]
        self.assertEqual(known['familyKey'],'fed-fomc-2026-10:rate-decision')
        self.assertNotIn('familyKey',changed)

    def test_builder_returns_copies_and_deterministic_output(self):
        snap = snapshot();before=deepcopy(snap)
        packet = feed.build_packet([snap]);packet['events'][0]['title']='consumer change'
        self.assertEqual(snap,before)
        self.assertEqual(feed.encoded(feed.build_packet([snap])),feed.encoded(feed.build_packet([snap])))

    def invoke(self, directory, argv, effect):
        p=Path(directory)
        arguments=argv+['--archive-dir',str(p/'archive'),'--output',str(p/'new.json'),'--legacy-output',str(p/'old.json'),'--official-input',str(p/'none.json')]
        with patch.object(feed,'utc_now',return_value=STAMP), patch.object(feed,'fetch_feed',side_effect=effect) as fetch, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code=feed.main(arguments)
        return code,fetch.call_count

    def test_one_network_capture_supplies_both_outputs_and_archive(self):
        with tempfile.TemporaryDirectory() as d:
            code,calls=self.invoke(d,['--fetch-ff'],lambda:json.dumps([row()]))
            self.assertEqual((code,calls),(0,1))
            self.assertTrue((Path(d)/'new.json').exists())
            self.assertTrue((Path(d)/'old.json').exists())
            self.assertEqual(len(list((Path(d)/'archive').glob('*/*.snapshot.json'))),1)

    def test_network_failure_returns_nonzero_and_preserves_good_views(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'new.json').write_text('prior-new');(p/'old.json').write_text('prior-old')
            code,calls=self.invoke(d,['--fetch-ff'],HTTPError(feed.FEED_URL,403,'Forbidden',{},None))
            self.assertEqual((code,calls),(1,1))
            self.assertEqual((p/'new.json').read_text(),'prior-new')
            self.assertEqual((p/'old.json').read_text(),'prior-old')
            self.assertFalse((p/'archive').exists())

    def test_invalid_fetched_source_preserves_both_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'new.json').write_text('prior-new');(p/'old.json').write_text('prior-old')
            code,_=self.invoke(d,['--fetch-ff'],lambda:'<html>error</html>')
            self.assertEqual(code,1)
            self.assertEqual((p/'new.json').read_text(),'prior-new')
            self.assertEqual((p/'old.json').read_text(),'prior-old')

    def test_offline_input_requires_original_collection_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source.json';source.write_text(json.dumps([row()]))
            code,calls=self.invoke(d,['--input-ff',str(source)],lambda:None)
            self.assertEqual((code,calls),(1,0))
            self.assertFalse((Path(d)/'new.json').exists())

    def test_offline_reproduction_has_zero_fetch_and_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source.json';source.write_text(json.dumps([row()]))
            code,_=self.invoke(d,['--input-ff',str(source),'--collected-at',STAMP],lambda:None)
            self.assertEqual(code,0)
            p=Path(d);before={f:f.read_bytes() for f in p.rglob('*') if f.is_file()}
            code,calls=self.invoke(d,['--rebuild-archives','--check'],lambda:None)
            self.assertEqual((code,calls),(0,0))
            self.assertEqual(before,{f:f.read_bytes() for f in p.rglob('*') if f.is_file()})

    def test_tampered_archive_refuses_without_replacing_good_views(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'source.json';source.write_text(json.dumps([row()]))
            self.invoke(d,['--input-ff',str(source),'--collected-at',STAMP],lambda:None)
            p=Path(d);good=(p/'new.json').read_bytes();raw=next((p/'archive').glob('*/*.source.json'));raw.write_text('[]')
            code,calls=self.invoke(d,['--rebuild-archives'],lambda:None)
            self.assertEqual((code,calls),(1,0));self.assertEqual((p/'new.json').read_bytes(),good)

    def assert_official_refused_and_views_preserved(self, mutate):
        official = dict(schemaVersion=1,
            sources=[dict(id='boc-policy', name='Synthetic BoC schedule', currency='CAD',
                url='https://www.bankofcanada.ca/press/upcoming-events/', timeZone='America/Toronto', provider='official')],
            events=[dict(id='official:synthetic-policy', familyKey='synthetic-policy:2026-10', title='Synthetic policy decision',
                currency='CAD', impact='high', date='2026-10-28', at='2026-10-28T13:45:00Z', precision='instant',
                timeConfirmed=True, timeZone='America/Toronto', sourceId='boc-policy',
                sourceUrl='https://www.bankofcanada.ca/press/upcoming-events/', sourceUid=None,
                identityBasis='curated-official-family', status='scheduled', reviewedAt=STAMP, observedAt=STAMP,
                provider='official', providerImpact=None, impactOrigin='editorial')],
            coverage=[dict(sourceId='boc-policy',currency='CAD',month='2026-10',
                **{'from':'2026-10-28','to':'2026-10-28'},status='partial',scope='selected-policy-families',
                reviewedAt=STAMP,collectedAt=STAMP,validUntil='2026-10-30T20:21:55Z')],
            provenance=[dict(id='synthetic-source',sourceUrl='https://www.bankofcanada.ca/press/upcoming-events/',
                capturedAt=STAMP,sourceSha256='0'*64,method='synthetic-test-fixture')])
        mutate(official)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'new.json').write_text('prior-new');(p/'old.json').write_text('prior-old')
            (p/'official.json').write_text(json.dumps(official))
            args=['--fetch-ff','--archive-dir',str(p/'archive'),'--output',str(p/'new.json'),
                '--legacy-output',str(p/'old.json'),'--official-input',str(p/'official.json')]
            with patch.object(feed,'utc_now',return_value=STAMP), patch.object(feed,'fetch_feed',return_value=json.dumps([row()])), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code=feed.main(args)
            self.assertEqual(code,1,'Malformed official input must be refused before replacing last good views')
            self.assertEqual((p/'new.json').read_text(),'prior-new')
            self.assertEqual((p/'old.json').read_text(),'prior-old')
            self.assertFalse((p/'archive').exists())

    def test_official_unsafe_source_url_refused_before_writes(self):
        self.assert_official_refused_and_views_preserved(lambda p:p['sources'][0].update(url='javascript:alert(1)'))

    def test_official_unknown_currency_refused_before_writes(self):
        self.assert_official_refused_and_views_preserved(lambda p:p['events'][0].update(currency='XXX'))

    def test_official_unknown_status_refused_before_writes(self):
        self.assert_official_refused_and_views_preserved(lambda p:p['events'][0].update(status='pretend-published'))

    def test_official_mismatched_coverage_month_refused_before_writes(self):
        self.assert_official_refused_and_views_preserved(lambda p:p['coverage'][0].update(month='2026-11'))

    def test_official_publisher_currency_binding_refused_before_writes(self):
        def mutate(packet):
            packet['sources'][0]['currency']='USD'
            packet['events'][0]['currency']='USD'
            packet['coverage'][0]['currency']='USD'
        self.assert_official_refused_and_views_preserved(mutate)

    def test_official_offsetless_time_refused_before_writes(self):
        self.assert_official_refused_and_views_preserved(lambda p:p['events'][0].update(at='2026-10-28T09:45:00'))

    def test_immutable_snapshot_collision_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'snapshot.json';feed.atomic_write(path,'old',immutable=True)
            with self.assertRaises(ValueError):feed.atomic_write(path,'new',immutable=True)
            self.assertEqual(path.read_text(),'old')


if __name__ == '__main__':
    unittest.main(verbosity=2)
