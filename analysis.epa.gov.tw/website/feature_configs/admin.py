from django.contrib import admin

from .models import *
from .forms import *

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
	list_display = ('name', 'show_text', 'circle_active', 'event_active')

@admin.register(Notification)    
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationForm
    list_display = ('email', 'risks', 'area')
