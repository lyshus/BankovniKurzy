"""
Scraper pro Komerční banku (KB).

KB server-side renderuje data kurzů přímo do stránky jako JSON v proměnné
WIDGETS_CONFIG. Scraper tato data extrahuje z HTML bez volání interního API.

URL stránky: https://www.kb.cz/cs/kurzovni-listek

Klíčové JSON pole v každém záznamu:
  curencyIso   – kód měny (USD, EUR, ...)
  currencyUnit – množství (1, 100, ...)
  nonCashBuy   – deviza nákup (float)
  nonCashSell  – deviza prodej (float)
  middleKB     – střední kurz KB (0 = není, KB ho nepublikuje)
  validDate    – datum platnosti (ISO 8601)
  title        – název země/měny v češtině
"""
import re
import json
from decimal import Decimal
from datetime import datetime, date
import requests
from .base import BaseScraper

KB_URL = 'https://www.kb.cz/cs/kurzovni-listek'


class KBScraper(BaseScraper):
    bank_code = 'kb'

    def fetch(self) -> list[dict]:
        session = self._make_session()
        session.headers['Referer'] = 'https://www.kb.cz/'
        r = session.get(KB_URL, timeout=30)
        r.raise_for_status()
        return self._parse(r.text)

    def _parse(self, html: str) -> list[dict]:
        m = re.search(r'WIDGETS_CONFIG\s*=\s*(\{.+)', html, re.DOTALL)
        if not m:
            raise ValueError('KB: WIDGETS_CONFIG nenalezen v HTML stránce.')

        raw = m.group(1)
        depth = end = 0
        for i, c in enumerate(raw):
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if not end:
            raise ValueError('KB: Nelze určit konec WIDGETS_CONFIG JSON.')

        data = json.loads(raw[:end])
        widget = next(iter(data.values()))
        items = widget.get('items', [])
        if not items:
            raise ValueError('KB: Prázdný seznam kurzů v WIDGETS_CONFIG.')

        query_date_str = widget.get('queryDate', '')
        try:
            valid_from = datetime.fromisoformat(query_date_str).date()
        except (ValueError, TypeError):
            valid_from = date.today()

        results = []
        for item in items:
            code = item.get('curencyIso', '').upper()
            if len(code) != 3:
                continue

            amount = int(item.get('currencyUnit', 1) or 1)
            buy = Decimal(str(item['nonCashBuy'])) if item.get('nonCashBuy') else None
            sell = Decimal(str(item['nonCashSell'])) if item.get('nonCashSell') else None
            mid_raw = item.get('middleKB', 0)
            mid = Decimal(str(mid_raw)) if mid_raw and mid_raw != 0 else None

            results.append({
                'currency_code': code,
                'currency_name': item.get('title', code),
                'currency_name_cz': item.get('title', ''),
                'amount': amount,
                'rate_buy': buy,
                'rate_sell': sell,
                'rate_mid': mid,
                'valid_from': valid_from,
            })

        return results
