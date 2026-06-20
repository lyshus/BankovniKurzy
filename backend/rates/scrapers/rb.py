"""
Scraper pro Raiffeisenbank (RB).

RB načítá kurzy přes Angular SPA pomocí autentizovaného API na api.rb.cz (HTTP 403
bez přihlašovacích údajů). JS bundle je plně obfuskován, stránka neobsahuje
server-side renderovaná data.

Možnosti implementace do budoucna:
  a) Požádat RB o API přístup přes developer.rb.cz
  b) Použít headless browser (Playwright/Selenium) k zachycení XHR volání
  c) Využít agregátor (kurzy.cz, fio.cz) pokud zveřejňuje RB data

Stránka kurzy: https://www.rb.cz/informacni-servis/kurzovni-listek
"""
from .base import BaseScraper


class RBScraper(BaseScraper):
    bank_code = 'rb'

    def fetch(self) -> list[dict]:
        raise NotImplementedError(
            'RB scraper není implementován: API na api.rb.cz vyžaduje autentizaci '
            'a JS bundle je obfuskován. Viz komentář v scrapers/rb.py.'
        )
