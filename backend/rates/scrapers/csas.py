"""
Scraper pro Českou spořitelnu (ČSAS).

TODO: Implementovat.

Česká spořitelna publikuje kurzovní lístek na:
  https://www.csas.cz/cs/osobni-finance/meny-a-kurzy/kurzovni-listek

Doporučený postup implementace:
1. Otevři URL ve vývojářských nástrojích (F12 → Network → XHR/Fetch)
2. Najdi API volání vracející JSON s kurzy
3. Implementuj metodu fetch() analogicky jako CNBScraper
4. Přidej bank_code = 'csas' a zaregistruj v SCRAPERS v fetch_rates.py
"""
from .base import BaseScraper


class CSASScraper(BaseScraper):
    bank_code = 'csas'

    def fetch(self) -> list[dict]:
        raise NotImplementedError('Scraper pro Českou spořitelnu zatím není implementován.')
