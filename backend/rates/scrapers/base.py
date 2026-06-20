from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """
    Základní třída pro všechny scrapery bank.
    Každá banka má vlastní soubor scrapers/<kod_banky>.py
    s třídou dědící od BaseScraper.
    """
    bank_code: str  # Musí být definováno v podtřídě (např. 'cnb', 'csas')

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
