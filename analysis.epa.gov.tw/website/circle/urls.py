# -*- coding: utf-8 -*-

from django.urls import path

from . import views

urlpatterns = [
    path("average", views.average, name="circle_average"),
]