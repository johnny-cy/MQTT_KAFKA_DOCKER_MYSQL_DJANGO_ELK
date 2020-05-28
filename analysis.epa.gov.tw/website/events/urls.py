# -*- coding: utf-8 -*-

from django.urls import path

from . import views

urlpatterns = [
    path('table/', views.table, name="event_table"),
    path('ranking/', views.ranking, name="event_ranking"),
    path('table_v2/', views.table_v2, name="event_table_v2"),
]
