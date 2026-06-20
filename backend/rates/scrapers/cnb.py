"""
Scraper pro Českou národní banku (ČNB).

ČNB zveřejňuje referenční kurzy ve formátu plain-text:
  https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/
  kurzy-devizoveho-trhu/denni_kurz.txt

Formát:
  28.05.2024 #103
  Země|Měna|Množství|Kód|Kurz
  Austrálie|dolar|1|AUD|15,195
  EMU|euro|1|EUR|25,350
  Maďarsko|forint|100|HUF|6,185
  ...

Poznámky:
  - Pouze středový kurz (bez nákupu/prodeje)
  - Aktualizace v ~14:30 v pracovní dny
  - Množství může být 1, 100 nebo 1000 (vždy zkontroluj pole 'amount')
"""
import requests
from decimal import Decimal, InvalidOperation
from datetime import datetime
from .base import BaseScraper

CNB_URL = (
    'https://www.cnb.cz/cs/financni-trhy/devizovy-trh/'
    'kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt'
)

# České názvy měn → anglické (pro uložení do DB)
CURRENCY_NAMES_CZ = {
    'AUD': 'Australský dolar',
    'BRL': 'Brazilský real',
    'BGN': 'Bulharský lev',
    'CNY': 'Čínský jüan',
    'DKK': 'Dánská koruna',
    'EUR': 'Euro',
    'PHP': 'Filipínské peso',
    'HKD': 'Hongkongský dolar',
    'INR': 'Indická rupie',
    'IDR': 'Indonéská rupie',
    'ISK': 'Islandská koruna',
    'ILS': 'Izraelský šekel',
    'JPY': 'Japonský jen',
    'ZAR': 'Jihoafrický rand',
    'KRW': 'Jihokorejský won',
    'CAD': 'Kanadský dolar',
    'HUF': 'Maďarský forint',
    'MYR': 'Malajský ringgit',
    'MXN': 'Mexické peso',
    'XDR': 'MMF SDR',
    'NOK': 'Norská koruna',
    'NZD': 'Novozélandský dolar',
    'PLN': 'Polský zlotý',
    'RON': 'Rumunský leu',
    'SGD': 'Singapurský dolar',
    'SEK': 'Švédská koruna',
    'CHF': 'Švýcarský frank',
    'THB': 'Thajský baht',
    'TRY': 'Turecká lira',
    'USD': 'Americký dolar',
    'GBP': 'Britská libra',
}


class CNBScraper(BaseScraper):
    bank_code = 'cnb'

    def fetch(self) -> list[dict]:
        response = requests.get(CNB_URL, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return self._parse(response.text)

    def _parse(self, text: str) -> list[dict]:
        lines = text.strip().split('\n')
        if len(lines) < 3:
            raise ValueError('Neočekávaný formát dat z ČNB')

        # První řádek: "28.05.2024 #103"
        date_str = lines[0].split(' ')[0]
        valid_from = datetime.strptime(date_str, '%d.%m.%Y').date()

        rates = []
        for line in lines[2:]:  # Přeskoč hlavičku "Země|Měna|Množství|Kód|Kurz"
            parts = line.strip().split('|')
            if len(parts) != 5:
                continue
            _country, currency_name, amount_str, code, rate_str = parts
            try:
                rate = Decimal(rate_str.replace(',', '.'))
                amount = int(amount_str)
            except (InvalidOperation, ValueError):
                continue

            rates.append({
                'currency_code': code,
                'currency_name': currency_name,
                'currency_name_cz': CURRENCY_NAMES_CZ.get(code, ''),
                'amount': amount,
                'rate_buy': None,
                'rate_sell': None,
                'rate_mid': rate,
                'valid_from': valid_from,
            })

        return rates
