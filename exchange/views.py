import decimal

from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rates.utils import get_rates


@api_view()
def exchange_from_to(request, amount, from_currency, to_currency):
    """
    API endpoint for currency conversion.

    Example

    Request:
    `$ curl http://127.0.0.1:8000/api/exchange/1000/CZK/USD/`

    Response:
    `{"from_currency":"CZK","to_currency":"USD","from_amount":1000.0,"to_amount":46.3401049}`

    """
    rates = get_rates()
    if not rates:
        return Response(
            {'error': 'Service does not have actual data.'},
            status=500
        )

    if from_currency not in rates:
        return Response(
            {'error': 'Currency [{}] not found.'.format(from_currency)},
            status=404
        )
    if to_currency not in rates:
        return Response(
            {'error': 'Currency [{}] not found.'.format(to_currency)},
            status=404
        )

    decimal.getcontext().prec = settings.DECIMAL_PREC
    from_amount = decimal.Decimal(amount)
    to_amount = from_amount * rates[from_currency][to_currency]

    return Response({
        'from_currency': from_currency,
        'to_currency': to_currency,
        'from_amount': from_amount,
        'to_amount': to_amount,
    })