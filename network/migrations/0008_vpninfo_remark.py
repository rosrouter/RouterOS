# Generated by Django 2.2 on 2020-04-17 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0007_auto_20200409_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='vpninfo',
            name='remark',
            field=models.CharField(blank=True, default='', max_length=60, verbose_name='备注'),
        ),
    ]
