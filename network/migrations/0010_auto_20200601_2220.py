# Generated by Django 2.2 on 2020-06-01 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0009_auto_20200420_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rosrouter',
            name='ip',
            field=models.GenericIPAddressField(blank=True, null=True, unique=True, verbose_name='ip地址'),
        ),
        migrations.AlterField(
            model_name='vpninfo',
            name='remark',
            field=models.CharField(blank=True, default='', max_length=60, verbose_name='备注'),
        ),
    ]