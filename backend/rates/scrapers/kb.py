"""
Scraper pro Komerční banku (KB).

TODO: Implementovat.

KB publikuje kurzovní lístek na:
  https://www.kb.cz/cs/kurzy-a-urokove-sazby/kurzovni-listky

Doporučený postup implementace:
1. Otevři URL ve vývojářských nástrojích (F12 → Network → XHR/Fetch)
2. Najdi API volání vracející JSON s kurzy
3. Implementuj metodu fetch() analogicky jako CNBScraper
"""
from .base import BaseScraper


class KBScraper(BaseScraper):
    bank_code = 'kb'

    def fetch(self) -> list[dict]:
        raise NotImplementedError('Scraper pro Komerční banku zatím není implementován.')
