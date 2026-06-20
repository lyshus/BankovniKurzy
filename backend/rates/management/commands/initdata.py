"""
Inicializuje databázi s výchozími daty bank.

Spuštění (po migrate):
  python manage.py initdata
"""
from django.core.management.base import BaseCommand
from rates.models import Bank

BANKS = [
    {
        'code': 'cnb',
        'name': 'Česká národní banka',
        'url': 'https://www.cnb.cz',
        'update_times': ['14:30'],
    },
    {
        'code': 'kb',
        'name': 'Komerční banka',
        'url': 'https://www.kb.cz',
        'update_times': ['07:00', '15:00'],
    },
    {
        'code': 'csas',
        'name': 'Česká spořitelna',
        'url': 'https://www.csas.cz',
        'update_times': ['08:00'],
    },
    {
        'code': 'csob',
        'name': 'ČSOB',
        'url': 'https://www.csob.cz',
        'update_times': ['08:00'],
    },
    {
        'code': 'rb',
        'name': 'Raiffeisenbank',
        'url': 'https://www.rb.cz',
        'update_times': ['08:00'],
    },
]


class Command(BaseCommand):
    help = 'Inicializuje DB s výchozími daty bank'

    def handle(self, *args, **options):
        for data in BANKS:
            bank, created = Bank.objects.update_or_create(
                code=data['code'],
                defaults=data,
            )
            verb = 'Vytvořena' if created else 'Aktualizována'
            self.stdout.write(f'{verb}: {bank.name}')
        self.stdout.write(self.style.SUCCESS('Hotovo.'))
