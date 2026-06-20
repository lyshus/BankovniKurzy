"""
Scraper pro Českou spořitelnu (ČS / ČSAS).

Česká spořitelna poskytuje kurzy přes interní JSON API (zjištěno z widget JS):
  https://www.csas.cz/webapi/api/v2/rates/exchangerates

Autentizace: hlavička Web-Api-Key (klíč je veřejný, nalezený v kódu widgetu
na stránce https://www.csas.cz/en/exchange-rates).

Klíčová pole v odpovědi:
  shortName   – kód měny (AUD, EUR, ...)
  amount      – množství (1, 100, ...)
  validFrom   – datum platnosti (ISO 8601)
  currBuy     – deviza nákup (nonCash)
  currSell    – deviza prodej (nonCash)
  currMid     – deviza střed
  name        – název měny v češtině (Dolar, Euro, ...)
  country     – název země v češtině
"""
from datetime import datetime, date
from decimal import Decimal
import requests
from .base import BaseScraper

CSAS_API_URL = 'https://www.csas.cz/webapi/api/v2/rates/exchangerates'
CSAS_API_KEY = '08aef2f7-8b72-4ae1-831e-2155d81f46dd'


class CSASScraper(BaseScraper):
    bank_code = 'csas'

    def fetch(self) -> list[dict]:
        session = self._make_session()
        session.headers.update({
            'Accept': 'application/json',
            'Web-Api-Key': CSAS_API_KEY,
            'Referer': 'https://www.csas.cz/en/exchange-rates',
        })
        r = session.get(CSAS_API_URL, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not data:
            raise ValueError('ČS API vrátilo prázdný seznam.')
        return self._parse(data)

    def _parse(self, data: list) -> list[dict]:
        results = []
        for item in data:
            code = item.get('shortName', '').upper()
            if len(code) != 3:
                continue

            valid_raw = item.get('validFrom', '')
            try:
                valid_from = datetime.fromisoformat(valid_raw).date()
            except (ValueError, TypeError):
                valid_from = date.today()

            buy_raw = item.get('currBuy')
            sell_raw = item.get('currSell')
            mid_raw = item.get('currMid')

            results.append({
                'currency_code': code,
                'currency_name': item.get('name', code),
                'currency_name_cz': item.get('name', ''),
                'amount': int(item.get('amount', 1) or 1),
                'rate_buy': Decimal(str(buy_raw)) if buy_raw else None,
                'rate_sell': Decimal(str(sell_raw)) if sell_raw else None,
                'rate_mid': Decimal(str(mid_raw)) if mid_raw else None,
                'valid_from': valid_from,
            })

        return results
