#!/usr/bin/env python3
"""Compile the approved indicative FOREX.com convention using frozen TZif bytes.
No broker operating schedule, equity opening, market tradability or holiday is inferred.
"""
import hashlib,json
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from compile_market_hours import ROOT,TZROOT,compile_calendar,read_json,epoch


def compile_sessions():
    source=read_json(ROOT/'src/data/market-hours/forex-sources.json')
    rules=read_json(ROOT/'src/data/market-hours/forex-rules.json')
    catalog=compile_calendar(source,rules)
    catalog['convention']={'id':'forex-com-local-v1','kind':'indicative-fx-session','reviewedAt':'2026-10-31','holidays':'not-modelled','brokerAvailability':'not-modelled'}
    catalog['displayDays']={}
    first=date.fromisoformat(rules['fromDate']);last=date.fromisoformat(rules['untilDate'])
    for name in ('UTC','Australia/Sydney','Asia/Tokyo','Europe/London','America/New_York','America/Sao_Paulo'):
        with (TZROOT/name).open('rb') as stream: zone=ZoneInfo.from_file(stream,key=name)
        days=[];day=first
        while day<=last:
            start,end=epoch(day,0,zone),epoch(day+timedelta(days=1),0,zone)
            ticks=[]
            for utc in range(start,end+1,3600000):
                local=datetime.fromtimestamp(utc/1000,timezone.utc).astimezone(zone)
                ticks.append({'utc':utc,'label':local.strftime('%H:%M'),'offset':local.strftime('%z')})
            days.append({'date':day.isoformat(),'fromUtc':start,'untilUtc':end,'ticks':ticks})
            day+=timedelta(days=1)
        catalog['displayDays'][name]=days
    return catalog

if __name__=='__main__':
    payload=json.dumps(compile_sessions(),ensure_ascii=False,separators=(',',':'))+'\n'
    target=ROOT/'src/data/market-hours/forex-sessions-v1.json';target.write_text(payload)
    print('Compiled 4 indicative FX centres; TZif2026b; sha256 '+hashlib.sha256(payload.encode()).hexdigest())
