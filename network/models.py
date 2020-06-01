from django.db import models
from django.contrib.auth.models import User
# from stdimage.models import StdImageField


# Create your models here.
class RosRouter(models.Model):
    ip = models.GenericIPAddressField(verbose_name='ip地址', null=True, blank=True, unique=True)
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
    remark = models.CharField(verbose_name='备注信息', max_length=400, null=False, default='')
    up_time = models.CharField(verbose_name='在线时间', max_length=60, null=False, blank=True, default='')
    remark = models.CharField(verbose_name='备注', max_length=60, null=False, blank=True, default='')

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


class Button(models.Model):
    name = models.CharField(verbose_name='按钮名称', blank=False, max_length=60, default='')
    port = models.CharField(verbose_name='端口号', max_length=60, default='')
    ip = models.GenericIPAddressField(verbose_name='ip', null=True, blank=True)

    class Meta:
        verbose_name = "路由与接口功能"
        verbose_name_plural = verbose_name
        db_table = "button"


# class ZabbixGraph(models.Model):
#     ros = models.OneToOneField(RosRouter, on_delete=models.CASCADE)
#     ether1 = StdImageField(upload_to='path/to/img', blank=True,
#                            variations={'large': (600, 400), 'thumbnail': (100, 100, True), 'medium': (300, 200), })
#     ether2 = StdImageField(upload_to='path/to/img', blank=True,
#                            variations={'large': (600, 400), 'thumbnail': (100, 100, True), 'medium': (300, 200), })
#     bridge1 = StdImageField(upload_to='path/to/img', blank=True,
#                             variations={'large': (600, 400), 'thumbnail': (100, 100, True), 'medium': (300, 200), })
