# Generated by Django 2.2 on 2020-04-09 13:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_auto_20200409_2142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermanage',
            name='user',
            field=models.ForeignKey(blank=True, on_delete=False, related_name='user_manage', to=settings.AUTH_USER_MODEL, verbose_name='系统用户'),
        ),
    ]
