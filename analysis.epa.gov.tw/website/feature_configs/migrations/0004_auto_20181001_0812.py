# Generated by Django 2.0.7 on 2018-10-01 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feature_configs', '0003_auto_20181001_0809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='event_active',
            field=models.BooleanField(default=True, verbose_name='是否顯示在 事件表 及 IoT數據回朔'),
        ),
    ]
