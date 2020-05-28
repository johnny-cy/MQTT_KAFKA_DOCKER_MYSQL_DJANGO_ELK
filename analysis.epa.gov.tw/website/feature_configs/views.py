from django.shortcuts import render
from django.http import HttpResponse

import json
from .models import Area

def area_map_js(request):
	
	raw_list = Area.objects.all()
	res_dict = {}

	for area in raw_list:
		inner_obj = {}
		inner_obj["bounds"] = list([ area.min_lon, area.max_lon, area.min_lat, area.max_lat ])
		inner_obj["showText"] = area.show_text
		inner_obj["circleActive"] = area.circle_active
		inner_obj["eventActive"] = area.event_active
		res_dict[ area.name ] = inner_obj

	return HttpResponse("var areaMetaMap = " + json.dumps(res_dict), content_type="application/x-javascript")
