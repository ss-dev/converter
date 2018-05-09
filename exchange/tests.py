import decimal
from unittest.mock import Mock

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

ALL_RATES = {
    "USD": {
        "CZK": decimal.Decimal('21.35455')
    },
    "CZK": {
        "USD": decimal.Decimal('0.0468284277')
    }
}

# Mock rates for each test
from rates import utils
utils.get_rates = Mock(return_value=ALL_RATES)


class ApiExchangeTests(APITestCase):

    def test_exchange_ok(self):
        url = reverse('api_exchange_from_to', args=(100, 'CZK', 'USD'))
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['from_currency'], 'CZK')
        self.assertEqual(res.data['to_currency'], 'USD')
        self.assertEqual(res.data['from_amount'], 100)
        self.assertEqual(res.data['to_amount'], decimal.Decimal('4.68284277'))

    def test_exchange_unknown_currency(self):
        url = reverse('api_exchange_from_to', args=(100, 'CZK', 'BADCURRENCY'))
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', res.data)

        url = reverse('api_exchange_from_to', args=(100, 'BADCURRENCY', 'USD'))
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', res.data)
