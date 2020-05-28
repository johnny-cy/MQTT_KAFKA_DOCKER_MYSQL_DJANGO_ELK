# -*- coding: utf-8 -*-
"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse
from django.views.generic import RedirectView

from main.views import dashboard
from main.views import documentation

from main.settings import CAMEO_SUB_PATH

admin.sites.AdminSite.site_title = "EPA Admin"

sub_urlpatterns = [
    path('events/', include(("events.urls", "events"))),
    path('iot/', include(("iot.urls", "iot"))),
    path('circle/', include(("circle.urls", "circle"))),
    path('station_anomaly/', include(("station_anomaly.urls", "station_anomaly"))),
    path('configs/', include("feature_configs.urls")),
    path('dashboard/', dashboard, name="dashboard"),
    path('documentation/', documentation, name="documentation"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url="events/table/")),
]

urlpatterns = [
    path(f'{CAMEO_SUB_PATH}/', include((sub_urlpatterns, ""))),
]

if CAMEO_SUB_PATH:
    urlpatterns = [
        path('', RedirectView.as_view(url=f"/{CAMEO_SUB_PATH}/events/table")),
    ] + urlpatterns
