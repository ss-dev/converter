import decimal
import simplejson as json
import logging
import requests

from django.conf import settings
from django.core.cache import cache

from .exceptions import OXRException

logger = logging.getLogger(__name__)


def load_latest_rates():
    """
    Get latest rates from OXR service
    and return JSON data or raise an exception if something is wrong.
    """
    res = requests.get(settings.OXR_URL)

    if res.status_code != 200:
        raise OXRException('Bad status code from OXR: {}'.format(res))

    data = res.json()
    if data.get('error', False) or not data.get('rates'):
        raise OXRException('Bad response from OXR: {}'.format(res))

    return data


def generate_all_rates(data):
    """
    Generate table of rates for each currency.
    Example:
        data: {
            ...
            "base": "USD",
            "rates": {
                "CZK": 21.35455
            }
        }
        result: {
            "USD": {
                "CZK": 21.35455
            },
            "CZK": {
                "USD": 0.046828
            }
        }
    """
    res = {}

    decimal.getcontext().prec = settings.DECIMAL_PREC

    for from_c, from_v in data['rates'].items():
        res[from_c] = {}
        for to_c, to_v in data['rates'].items():
            res[from_c][to_c] = decimal.Decimal(to_v) / decimal.Decimal(from_v)

    return res


def _update_cache(data):
    """
    Update rates cache.
    """
    cache.set(settings.STORAGE_CACHE_KEY, json.dumps(data),
              settings.STORAGE_CACHE_TIME)


def save_rates(data):
    """
    Save rates structure and update cache.
    """
    with open(settings.STORAGE_PATH, 'w') as f:
        json.dump(data, f, use_decimal=True)
    _update_cache(data)


def get_rates():
    """
    Return latest stored rates or None.
    Try to get data from cache, then from storage and update cache.
    """
    res = cache.get(settings.STORAGE_CACHE_KEY)
    if res is not None:
        return json.loads(res, use_decimal=True)

    try:
        with open(settings.STORAGE_PATH, 'r') as f:
            res = json.load(f, use_decimal=True)
    except Exception as e:
        logger.error('Error for reading rates from storage: {}'.format(e))
        return

    _update_cache(res)
    return res
