# -*- coding: utf-8 -*-

from ..models import Area
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def circle_area_list(context):
	return Area.objects.filter(circle_active=True)
