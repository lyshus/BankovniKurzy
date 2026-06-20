from django.db import models
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

PRAGUE_TZ = ZoneInfo('Europe/Prague')


class Bank(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    url = models.URLField()
    # Časy aktualizací v průběhu dne (pracovní dny), formát ["08:00", "14:30"]
    update_times = models.JSONField(default=list)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def next_update_time(self):
        """Vrátí předpokládaný čas příští aktualizace kurzů."""
        if not self.update_times:
            return None

        now = datetime.now(PRAGUE_TZ)
        check_date = now.date()

        # Dnes je pracovní den — zkus najít čas který ještě nenastal
        if check_date.weekday() < 5:
            for time_str in sorted(self.update_times):
                hour, minute = map(int, time_str.split(':'))
                scheduled = datetime.combine(check_date, time(hour, minute), tzinfo=PRAGUE_TZ)
                if scheduled > now:
                    return scheduled

        # Přejdi na další pracovní den
        check_date += timedelta(days=1)
        while check_date.weekday() >= 5:
            check_date += timedelta(days=1)

        first_time = sorted(self.update_times)[0]
        hour, minute = map(int, first_time.split(':'))
        return datetime.combine(check_date, time(hour, minute), tzinfo=PRAGUE_TZ)


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)   # EUR, USD, …
    name = models.CharField(max_length=100)               # "euro", "dolar"
    name_cz = models.CharField(max_length=100, blank=True)  # "Euro", "Americký dolar"

    class Meta:
        ordering = ['code']
        verbose_name_plural = 'currencies'

    def __str__(self):
        return f'{self.code} – {self.name_cz or self.name}'


class ExchangeRate(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='rates')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rates')
    # Množství cizí měny ke které se kurz vztahuje (ČNB: 100 HUF = X CZK → amount=100)
    amount = models.IntegerField(default=1)
    rate_buy = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    rate_sell = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    rate_mid = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    valid_from = models.DateField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['currency', '-fetched_at']),
            models.Index(fields=['bank', 'currency', '-fetched_at']),
        ]
        ordering = ['-fetched_at']

    def __str__(self):
        return f'{self.bank.code} {self.currency.code} {self.valid_from}'
