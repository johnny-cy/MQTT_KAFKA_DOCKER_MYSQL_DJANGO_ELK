# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def average(request):
	return render(request, "circle/average.html")
