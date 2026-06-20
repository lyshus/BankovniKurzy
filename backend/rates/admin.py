from django.contrib import admin
from .models import Bank, Currency, ExchangeRate


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'active', 'update_times']
    list_filter = ['active']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'name_cz']
    search_fields = ['code', 'name']


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['bank', 'currency', 'amount', 'rate_buy', 'rate_sell', 'rate_mid', 'valid_from', 'fetched_at']
    list_filter = ['bank', 'currency']
    ordering = ['-fetched_at']
