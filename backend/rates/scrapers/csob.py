"""
Scraper pro ČSOB.

TODO: Implementovat.

ČSOB publikuje kurzovní lístek na:
  https://www.csob.cz/portal/lide/kurzovni-listky

Doporučený postup implementace:
1. Otevři URL ve vývojářských nástrojích (F12 → Network → XHR/Fetch)
2. Najdi API volání vracející JSON s kurzy
3. Implementuj metodu fetch() analogicky jako CNBScraper
"""
from .base import BaseScraper


class CSOBScraper(BaseScraper):
    bank_code = 'csob'

    def fetch(self) -> list[dict]:
        raise NotImplementedError('Scraper pro ČSOB zatím není implementován.')
