from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Bank, Currency, ExchangeRate
from .serializers import CurrencySerializer, RateEntrySerializer


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok'})


class CurrencyListView(APIView):
    def get(self, request):
        # Jen měny, pro které máme alespoň jeden kurz
        currencies = (
            Currency.objects
            .filter(rates__isnull=False)
            .distinct()
            .order_by('code')
        )
        return Response(CurrencySerializer(currencies, many=True).data)


class LatestRatesView(APIView):
    def get(self, request):
        currency_code = request.query_params.get('currency', 'EUR').upper()

        if not Currency.objects.filter(code=currency_code).exists():
            return Response(
                {'error': f'Měna {currency_code} nenalezena.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = []
        for bank in Bank.objects.filter(active=True):
            rate = (
                ExchangeRate.objects
                .filter(bank=bank, currency__code=currency_code)
                .order_by('-fetched_at')
                .first()
            )
            if rate:
                result.append({
                    'bank': {'code': bank.code, 'name': bank.name, 'url': bank.url},
                    'amount': rate.amount,
                    'rate_buy': rate.rate_buy,
                    'rate_sell': rate.rate_sell,
                    'rate_mid': rate.rate_mid,
                    'valid_from': rate.valid_from,
                    'fetched_at': rate.fetched_at,
                    'next_update': bank.next_update_time(),
                })

        serializer = RateEntrySerializer(result, many=True)
        return Response(serializer.data)
