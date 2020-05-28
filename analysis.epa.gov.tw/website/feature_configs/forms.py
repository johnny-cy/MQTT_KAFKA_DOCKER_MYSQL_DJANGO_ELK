# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ValidationError
from .models import *

RISK_CHOICES = ( ('高', '高'), ('中', '中'), ('低', '低') )

# refers to: 
#   https://stackoverflow.com/a/27158781
#   https://djangosnippets.org/snippets/1200/
class MultipleCharChoiceField(forms.MultipleChoiceField):
	def to_python(self, value):
		if not value:
			return ''
		elif not isinstance(value, (list, tuple)):
			raise ValidationError(
				self.error_messages['invalid_list'], code='invalid_list'
			)
		return ','.join([str(val) for val in value])

	def validate(self, value):
		if self.required:
			if not value:
				raise ValidationError(
					self.error_messages['required'], code='required'
				)
			else:
				# Validate that each value in the value list is in self.choices.
				for val in value.split(','):
					if not self.valid_value(val):
						raise ValidationError(
							self.error_messages['invalid_choice'],
							code='invalid_choice',
							params={'value': val},
						)


	def prepare_value(self, value):
		if value is not None:
			return value if isinstance(value, list) else value.split(',')
		return ''


def get_area_list():
	return list(Area.objects.filter(event_active=True).values_list("name","name"))

class NotificationForm(forms.ModelForm):
	risks = MultipleCharChoiceField(choices=RISK_CHOICES, widget=forms.CheckboxSelectMultiple(), required=True, label="風險等級", help_text="多選。必填", initial="高,中")
	area = MultipleCharChoiceField(choices=get_area_list, widget=forms.CheckboxSelectMultiple(), required=False, label="區域", help_text="多選。不填則視為全部。關聯自 Area 之中，可以顯示在事件表的區域。")
