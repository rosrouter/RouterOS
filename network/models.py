from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class RosRouter(models.Model):
    ip = models.GenericIPAddressField(verbose_name='ip地址', null=True, blank=True)
    ros_user = models.CharField(verbose_name='ros用户', max_length=100, null=False, default='')
    ros_pwd = models.CharField(verbose_name='ros密码', max_length=100, null=False, default='')

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = "ros设备"
        verbose_name_plural = verbose_name
        db_table = "ros_router"


class VPNInfo(models.Model):
    ros = models.ForeignKey(RosRouter, verbose_name='归属ros路由器', blank=True, on_delete=False)
    vpn_user = models.CharField(verbose_name='VPN用户名', max_length=60, null=False, default='')
    vpn_pwd = models.CharField(verbose_name='VPN密码', max_length=60, null=False, default='')
    status = models.BooleanField(verbose_name='VPN状态', null=False, default=False)
    up_time = models.CharField(verbose_name='在线时间', max_length=60, null=False, blank=True, default='')

    class Meta:
        verbose_name = "VPN信息"
        verbose_name_plural = verbose_name
        db_table = "vpn_info"


class UserManage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 绑定user的唯一性
    device = models.ForeignKey(RosRouter, verbose_name='下属ros路由器', blank=True, on_delete=False)

    class Meta:
        verbose_name = "用户管理设备"
        verbose_name_plural = verbose_name
        db_table = "user_manage"
        unique_together = ('user', 'device',)  # 绑定user和device组合的唯一性（其实没必要了）
