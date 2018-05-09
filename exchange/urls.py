from django.conf import urls

from .views import exchange_from_to

urlpatterns = [
    urls.url(r'^(?P<amount>\d+(\.\d+)?)/(?P<from_currency>[A-Z]+)/(?P<to_currency>[A-Z]+)/$',
             exchange_from_to, name='api_exchange_from_to'),
]
