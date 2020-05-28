# -*- coding: utf-8 -*-

from django.urls import path

from . import views

urlpatterns = [
    path("history/", views.index, name="iot_history"),
    path("history/animation", views.animation, name="iot_history_animation"),
    path("history/animation/v2", views.animation_v2, name="iot_history_animation_v2"),
]
