# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
	return render(request, "iot/history/index.html")

def animation(request):
	return render(request, "iot/history/animation.html")

def animation_v2(request):
	return render(request, "iot/history/animation_v2.html")
