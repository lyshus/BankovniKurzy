from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
import requests


BROWSER_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/125.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}


class BaseScraper(ABC):
    bank_code: str

    @abstractmethod
    def fetch(self) -> list[dict]:
        """
        Stáhne a naparsuje kurzy.
        Vrátí seznam slovníků s klíči:
          currency_code: str       (např. 'EUR')
          currency_name: str       (např. 'euro')
          amount: int              (množství cizí měny, obvykle 1)
          rate_buy: Decimal|None   (kurz nákupu — banka kupuje od vás)
          rate_sell: Decimal|None  (kurz prodeje — banka prodává vám)
          rate_mid: Decimal|None   (střední kurz)
          valid_from: date         (datum platnosti)
        """
        ...

    @classmethod
    def _make_session(cls) -> requests.Session:
        session = requests.Session()
        session.headers.update(BROWSER_HEADERS)
        return session

    @staticmethod
    def _decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            cleaned = str(value).strip().replace(',', '.').replace('\xa0', '').replace(' ', '')
            if not cleaned or cleaned == '-':
                return None
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
