# Generated by Django 2.0.7 on 2018-10-24 08:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feature_configs', '0005_auto_20181002_0101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='area',
            name='square_radius',
        ),
    ]