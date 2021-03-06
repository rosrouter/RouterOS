# Generated by Django 2.2 on 2020-08-30 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0021_center'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='incoming',
            field=models.CharField(default='', max_length=100, verbose_name='入口流量'),
        ),
        migrations.AddField(
            model_name='center',
            name='outgoing',
            field=models.CharField(default='', max_length=100, verbose_name='出口流量'),
        ),
        migrations.AddField(
            model_name='center',
            name='username',
            field=models.CharField(default='', max_length=100, verbose_name='用户名'),
        ),
    ]
