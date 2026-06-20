"""
Příkaz pro stažení kurzů ze všech aktivních bank.

Spuštění:
  python manage.py fetch_rates           # všechny banky
  python manage.py fetch_rates --bank cnb  # pouze ČNB

Ochrana před blacklistingem:
  - Mezi bankami je náhodná pauza 2–5 s
  - Kurzy se znovu nestahují, pokud byly staženy v posledních 90 minutách
  - Všechna volání používají User-Agent prohlížeče

Jak přidat novou banku:
  1. Vytvoř rates/scrapers/<kod>.py s třídou dědící BaseScraper
  2. Přidej třídu do seznamu SCRAPERS níže
  3. Spusť: python manage.py initdata
"""
import time
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from rates.models import Bank, Currency, ExchangeRate
from rates.scrapers.cnb import CNBScraper
from rates.scrapers.kb import KBScraper
from rates.scrapers.csas import CSASScraper
from rates.scrapers.csob import CSOBScraper
from rates.scrapers.rb import RBScraper

SCRAPERS = [
    CNBScraper,
    KBScraper,
    CSASScraper,
    CSOBScraper,
    RBScraper,
]

# Přeskočit banku, pokud byly kurzy staženy před méně než N minutami
MIN_FETCH_INTERVAL_MINUTES = 90


class Command(BaseCommand):
    help = 'Stáhne aktuální kurzy ze všech bank'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bank',
            type=str,
            help='Stáhnout pouze tuto banku (kód, např. cnb)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Ignorovat minimální interval a stáhnout vždy',
        )

    def handle(self, *args, **options):
        only_bank = options.get('bank')
        force = options.get('force', False)
        scrapers = [s for s in SCRAPERS if not only_bank or s.bank_code == only_bank]

        if not scrapers:
            self.stdout.write(self.style.ERROR(f'Scraper pro banku "{only_bank}" nenalezen.'))
            return

        for i, ScraperClass in enumerate(scrapers):
            code = ScraperClass.bank_code

            try:
                bank = Bank.objects.get(code=code, active=True)
            except Bank.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'  [{code}] Banka nenalezena nebo není aktivní. '
                    f'Spusť "python manage.py initdata".'
                ))
                continue

            if not force:
                cutoff = timezone.now() - timedelta(minutes=MIN_FETCH_INTERVAL_MINUTES)
                if ExchangeRate.objects.filter(bank=bank, fetched_at__gte=cutoff).exists():
                    self.stdout.write(
                        f'  [{code}] Přeskočeno — kurzy staženy před méně než {MIN_FETCH_INTERVAL_MINUTES} min.'
                    )
                    continue

            self.stdout.write(f'Stahuji kurzy: {code} …')
            try:
                rates = ScraperClass().fetch()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [{code}] Chyba při stahování: {e}'))
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
                f'  [{code}] ✓ {saved} nových kurzů uloženo ({len(rates) - saved} duplicit přeskočeno)'
            ))

            # Pauza mezi bankami (kromě poslední) — ochrana před blacklistingem
            if i < len(scrapers) - 1:
                delay = random.uniform(2, 5)
                self.stdout.write(f'  Pauza {delay:.1f}s před další bankou…')
                time.sleep(delay)
