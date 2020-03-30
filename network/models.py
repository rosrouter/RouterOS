from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class L2TP(models.Model):
    username = models.CharField(verbose_name='L2TP用户名', max_length=60, null=False, default='')
    password = models.CharField(verbose_name='L2TP密码', max_length=60, null=False, default='')
    status = models.CharField(verbose_name='VPN状态', max_length=60, null=False, default='')

    class Meta:
        verbose_name = "VPN信息"
        verbose_name_plural = verbose_name
        db_table = "l2tp"


class NetworkManage(models.Model):
    ip = models.GenericIPAddressField(verbose_name='ip地址', max_length=30, null=False, default='')
    vpns = models.ManyToManyField(L2TP, verbose_name='下属VPN', blank=True)

    class Meta:
        verbose_name = "网络设备关联VPN"
        verbose_name_plural = verbose_name
        db_table = "network"


class UserManage(models.Model):
    user = models.ForeignKey(User, verbose_name='系统用户', blank=True, on_delete=False)
    device = models.ManyToManyField(NetworkManage, verbose_name='下属设备', blank=True)

    class Meta:
        verbose_name = "用户管理设备"
        verbose_name_plural = verbose_name
        db_table = "user_manage"
