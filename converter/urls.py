"""converter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.conf import settings

urlpatterns = [
    url(r'^$', TemplateView.as_view(
        template_name="index.html",
        extra_context={
            'CURRENCIES': settings.CURRENCIES,
            'CURRENCY_FROM': settings.DEFAULT_CURRENCY_FROM,
            'CURRENCY_TO': settings.DEFAULT_CURRENCY_TO,
        })),

    url(r'^api/exchange/', include('exchange.urls')),

    # url(r'^admin/', admin.site.urls),
]
