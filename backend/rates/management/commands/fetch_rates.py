"""
Příkaz pro stažení kurzů ze všech aktivních bank.

Spuštění:
  python manage.py fetch_rates           # všechny banky
  python manage.py fetch_rates --bank cnb  # pouze ČNB

Jak přidat novou banku:
  1. Vytvoř rates/scrapers/<kod>.py s třídou dědící BaseScraper
  2. Přidej třídu do seznamu SCRAPERS níže
  3. Spusť: python manage.py initdata  (přidá záznam banky do DB)
"""
from django.core.management.base import BaseCommand
from rates.models import Bank, Currency, ExchangeRate
from rates.scrapers.cnb import CNBScraper
# Odkomentuj až implementuješ:
# from rates.scrapers.csas import CSASScraper
# from rates.scrapers.csob import CSOBScraper
# from rates.scrapers.kb import KBScraper

SCRAPERS = [
    CNBScraper,
    # CSASScraper,
    # CSOBScraper,
    # KBScraper,
]


class Command(BaseCommand):
    help = 'Stáhne aktuální kurzy ze všech bank'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bank',
            type=str,
            help='Stáhnout pouze tuto banku (kód, např. cnb)',
        )

    def handle(self, *args, **options):
        only_bank = options.get('bank')
        scrapers = [s for s in SCRAPERS if not only_bank or s.bank_code == only_bank]

        if not scrapers:
            self.stdout.write(self.style.ERROR(f'Scraper pro banku "{only_bank}" nenalezen.'))
            return

        for ScraperClass in scrapers:
            code = ScraperClass.bank_code
            self.stdout.write(f'Stahuji kurzy: {code} …')
            try:
                bank = Bank.objects.get(code=code, active=True)
            except Bank.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'  Banka "{code}" nenalezena nebo není aktivní. '
                    f'Spusť "python manage.py initdata" pro inicializaci.'
                ))
                continue

            try:
                rates = ScraperClass().fetch()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Chyba při stahování: {e}'))
                continue

            saved = 0
            for r in rates:
                currency, _ = Currency.objects.get_or_create(
                    code=r['currency_code'],
                    defaults={
                        'name': r['currency_name'],
                        'name_cz': r.get('currency_name_cz', ''),
                    },
                )
                # Nekládej duplicity: stejná banka, měna a datum platnosti
                already_exists = ExchangeRate.objects.filter(
                    bank=bank,
                    currency=currency,
                    valid_from=r['valid_from'],
                ).exists()
                if not already_exists:
                    ExchangeRate.objects.create(
                        bank=bank,
                        currency=currency,
                        amount=r['amount'],
                        rate_buy=r['rate_buy'],
                        rate_sell=r['rate_sell'],
                        rate_mid=r['rate_mid'],
                        valid_from=r['valid_from'],
                    )
                    saved += 1

            self.stdout.write(self.style.SUCCESS(
                f'  ✓ {saved} nových kurzů uloženo ({len(rates) - saved} duplicit přeskočeno)'
            ))
