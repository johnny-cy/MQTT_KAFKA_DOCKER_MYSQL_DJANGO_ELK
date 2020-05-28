# -*- coding: utf-8 -*-
from django.db import models

class Area(models.Model):
	name = models.CharField(verbose_name="區域名稱", help_text="在程式中當作 Key 來對應。(Unique)", max_length=32, unique=True)
	show_text = models.CharField(verbose_name="顯示名稱", help_text="用於 排放潛勢 及 IoT 數據回朔", max_length=128)
	min_lat = models.FloatField(verbose_name="經緯度邊界 - 最低緯度", help_text="")
	max_lat = models.FloatField(verbose_name="經緯度邊界 - 最高緯度", help_text="")
	min_lon = models.FloatField(verbose_name="經緯度邊界 - 最小經度", help_text="")
	max_lon = models.FloatField(verbose_name="經緯度邊界 - 最大經度", help_text="")
	circle_active = models.BooleanField(verbose_name="是否顯示在排放潛勢選單", default=False)
	event_active = models.BooleanField(verbose_name="是否顯示在 事件表 及 IoT數據回朔", default=True)


class Notification(models.Model):
	email = models.EmailField(verbose_name="收件者 Email", help_text="(Unique)", unique=True)
	risks = models.CharField(max_length=32)
	area = models.TextField(blank=True)
