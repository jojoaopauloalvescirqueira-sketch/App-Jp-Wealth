#!/usr/bin/env python3
"""Alimentador de notícias de alto impacto para o widget do JP Wealth.

Busca o calendário semanal público do Forex Factory, filtra apenas eventos de
impacto Alto nas moedas que interessam ao terminal (USD, EUR, JPY, GBP — que
cobrem EURUSD, USDJPY, GBPUSD, S&P 500 e Gold) e grava ff-high-impact.json na
raiz do repositório.

Regra de ouro: NUNCA sobrescrever o JSON anterior com dado inválido. Se o feed
falhar (rede, HTTP 429 de rate-limit, HTML de erro, JSON malformado ou vazio),
o arquivo existente permanece intacto e o script sai com código 0 — o widget
continua servindo o último dado bom, com o carimbo generated_at antigo
denunciando a idade.
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

FEED_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
OUTPUT = Path(__file__).resolve().parent.parent / "ff-high-impact.json"
CURRENCIES = {"USD", "EUR", "JPY", "GBP"}
REQUIRED_KEYS = {"title", "country", "date", "impact"}
MAX_ATTEMPTS = 3
RETRY_WAIT_S = 75  # o feed limita ~1 req/min por IP; esperar mais que a janela


def fetch_feed():
    req = urllib.request.Request(
        FEED_URL, headers={"User-Agent": "jp-wealth-news-feed/1.0 (+github actions)"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def main():
    raw = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            body = fetch_feed()
            candidate = json.loads(body)  # HTML de rate-limit falha aqui
            if isinstance(candidate, list) and candidate:
                raw = candidate
                break
            print(f"tentativa {attempt}: resposta não é lista JSON com eventos")
        except Exception as exc:  # rede, timeout, JSON inválido, HTTP != 200
            print(f"tentativa {attempt}: {exc}")
        if attempt < MAX_ATTEMPTS:
            time.sleep(RETRY_WAIT_S)

    if raw is None:
        print("feed indisponível — mantendo ff-high-impact.json anterior intacto")
        return 0

    events = []
    for e in raw:
        if not isinstance(e, dict) or not REQUIRED_KEYS.issubset(e):
            continue
        if e.get("impact") != "High" or e.get("country") not in CURRENCIES:
            continue
        events.append(
            {
                "title": e.get("title"),
                "country": e.get("country"),
                "date": e.get("date"),
                "impact": e.get("impact"),
                "forecast": e.get("forecast") or "",
                "previous": e.get("previous") or "",
            }
        )

    out = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "forexfactory-ff_calendar_thisweek",
        "events": events,
    }
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"gravado {OUTPUT.name} com {len(events)} eventos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
