from rest_framework import serializers
from .models import Currency, Bank, ExchangeRate


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['code', 'name', 'name_cz']


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['code', 'name', 'url']


class RateEntrySerializer(serializers.Serializer):
    bank = BankSerializer()
    amount = serializers.IntegerField()
    rate_buy = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True)
    rate_sell = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True)
    rate_mid = serializers.DecimalField(max_digits=12, decimal_places=4, allow_null=True)
    valid_from = serializers.DateField()
    fetched_at = serializers.DateTimeField()
    next_update = serializers.DateTimeField(allow_null=True)
