import os
import decimal
import responses
from requests.exceptions import ConnectionError

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from .utils import load_latest_rates, generate_all_rates, save_rates, get_rates
from .exceptions import OXRException

OXR_RESPONSE = {
    "base": "USD",
    "rates": {
        "CZK": '21.35455',
        "USD": '1'
    }
}

ALL_RATES = {
    "USD": {
        "CZK": decimal.Decimal('21.35455')
    },
    "CZK": {
        "USD": decimal.Decimal('0.0468284277')
    }
}

STORAGE_PATH = os.path.join(settings.BASE_DIR, 'rates', 'tests', 'rates.json')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


class LoadRatesTests(TestCase):

    @responses.activate
    def test_load_rates_ok(self):
        responses.add(responses.GET, settings.OXR_URL,
                      json=OXR_RESPONSE, status=200)
        res = load_latest_rates()
        self.assertEqual(res['base'], OXR_RESPONSE['base'])
        self.assertEqual(res['rates']['CZK'], OXR_RESPONSE['rates']['CZK'])
        self.assertEqual(res['rates']['USD'], OXR_RESPONSE['rates']['USD'])

    @responses.activate
    def test_load_rates_server_error(self):
        responses.add(responses.GET, 'foo-bar-url')
        with self.assertRaises(ConnectionError):
            res = load_latest_rates()

    @responses.activate
    def test_load_rates_bad_status(self):
        responses.add(responses.GET, settings.OXR_URL,
                      status=500)
        with self.assertRaises(OXRException):
            res = load_latest_rates()

    @responses.activate
    def test_load_rates_error_in_response(self):
        responses.add(responses.GET, settings.OXR_URL,
                      json={'error': 'foo'}, status=200)
        with self.assertRaises(OXRException):
            res = load_latest_rates()

    @responses.activate
    def test_load_rates_bad_response(self):
        responses.add(responses.GET, settings.OXR_URL,
                      json={'foo': 'bar'}, status=200)
        with self.assertRaises(OXRException):
            res = load_latest_rates()


class GenerateRatesTests(TestCase):

    def test_generate_all_rates(self):
        res = generate_all_rates(OXR_RESPONSE)
        self.assertIn('CZK', res)
        self.assertIn('USD', res['CZK'])
        self.assertIn('USD', res)
        self.assertIn('CZK', res['USD'])
        self.assertEqual(res['CZK']['USD'], ALL_RATES['CZK']['USD'])
        self.assertEqual(res['USD']['CZK'], ALL_RATES['USD']['CZK'])


class RatesStorageTests(TestCase):

    @override_settings(STORAGE_PATH=STORAGE_PATH, CACHES=CACHES)
    def test_save_rates(self):
        save_rates(ALL_RATES)
        res = get_rates()
        self.assertIn('CZK', res)
        self.assertIn('USD', res['CZK'])
        self.assertIn('USD', res)
        self.assertIn('CZK', res['USD'])
        self.assertEqual(res['CZK']['USD'], ALL_RATES['CZK']['USD'])
        self.assertEqual(res['USD']['CZK'], ALL_RATES['USD']['CZK'])
