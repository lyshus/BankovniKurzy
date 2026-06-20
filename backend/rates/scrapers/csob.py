"""
Scraper pro ČSOB.

ČSOB zveřejňuje kurzovní lístek ve strojově čitelném textovém formátu:
  https://www.csob.cz/webcsob/kurzy/kurzynewcz.txt

Formát (středníkový):
  2026-06-19 00:00:00
  (prázdný řádek)
  ;;;;Devizy;;;Valuty
  Země;Množství;Měna;Změna;Nákup;Prodej;Střed;Nákup;Prodej;Střed
  Austrálie;1;AUD;0.5;14,428;15,209;14,819;0,000;0,000;0,000
  EUR;1;EUR;0.3;23,584;24,855;24,220;23,584;24,855;24,220
  ...

Sloupce (0-based):
  0 = Země (název země/měny), 1 = Množství, 2 = Kód měny, 3 = Změna,
  4 = Deviza nákup, 5 = Deviza prodej, 6 = Deviza střed,
  7-9 = Valuty (přeskočíme)
"""
from datetime import datetime, date
from decimal import Decimal
import requests
from .base import BaseScraper

CSOB_URL = 'https://www.csob.cz/webcsob/kurzy/kurzynewcz.txt'


class CSOBScraper(BaseScraper):
    bank_code = 'csob'

    def fetch(self) -> list[dict]:
        session = self._make_session()
        r = session.get(CSOB_URL, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or 'utf-8'
        return self._parse(r.text)

    def _parse(self, text: str) -> list[dict]:
        lines = [l.strip() for l in text.strip().splitlines()]
        if not lines:
            raise ValueError('ČSOB: prázdná odpověď')

        # Řádek 0: datum "2026-06-19 00:00:00"
        try:
            valid_from = datetime.strptime(lines[0][:10], '%Y-%m-%d').date()
        except (ValueError, IndexError):
            valid_from = date.today()

        # Najdi hlavičkový řádek s "Množství"
        data_start = None
        for i, line in enumerate(lines):
            if 'množství' in line.lower() or 'mnozstv' in line.lower():
                data_start = i + 1
                break

        if data_start is None:
            raise ValueError('ČSOB: nenalezen hlavičkový řádek s "Množství"')

        results = []
        for line in lines[data_start:]:
            parts = line.split(';')
            if len(parts) < 7:
                continue
            code = parts[2].strip().upper()
            if len(code) != 3 or not code.isalpha():
                continue

            country_name = parts[0].strip()
            try:
                amount = int(parts[1].strip())
            except ValueError:
                amount = 1

            buy = self._decimal(parts[4])
            sell = self._decimal(parts[5])
            mid = self._decimal(parts[6])

            # ČSOB uvádí 0,000 pro nedostupné kurzy
            if buy is not None and buy == Decimal('0'):
                buy = None
            if sell is not None and sell == Decimal('0'):
                sell = None
            if mid is not None and mid == Decimal('0'):
                mid = None

            if buy is None and sell is None and mid is None:
                continue

            results.append({
                'currency_code': code,
                'currency_name': country_name,
                'currency_name_cz': country_name,
                'amount': amount,
                'rate_buy': buy,
                'rate_sell': sell,
                'rate_mid': mid,
                'valid_from': valid_from,
            })

        return results
