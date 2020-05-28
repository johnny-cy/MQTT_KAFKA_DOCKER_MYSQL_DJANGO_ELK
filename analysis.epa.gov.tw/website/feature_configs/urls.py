# -*- coding: utf-8 -*-

from django.urls import path

from . import views

urlpatterns = [
    path("js/area-meta-map.js", views.area_map_js, name="configs_area_map_js"),
]
