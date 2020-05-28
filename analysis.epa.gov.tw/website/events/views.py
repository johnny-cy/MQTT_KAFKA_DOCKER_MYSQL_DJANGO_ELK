# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def table(request):
    return render(request, 'events/table.html')

@login_required
def table_v2(request):
    return render(request, 'events/table_v2.html')

@login_required
def ranking(request):
	return render(request, 'events/ranking.html')
