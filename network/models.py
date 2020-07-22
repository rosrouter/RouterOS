from django.db import models
from django.contrib.auth.models import User
from cidrfield.models import IPNetworkField

IP_EXPORT_CHOICES = (
    ('l2tp-xg', '香港出口'),
    ('l2tp-hd', '海底光缆出口'),
    ('l2tp-dx', '电信精品出口'),
    ('l2tp-al', '阿里云出口'),
    ('l2tp-tx', '腾讯云出口'),

)


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
        verbose_name = "远程办公服务"
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
    # name = models.CharField(verbose_name='按钮名称', blank=False, max_length=60, default='')
    # port = models.CharField(verbose_name='端口号', max_length=60, default='')
    device = models.ForeignKey(RosRouter, verbose_name='归属ros路由器', blank=True, on_delete=False, null=True)
    ip = models.CharField(verbose_name='路由地址', null=True, max_length=100, blank=False)
    ip_export = models.CharField(verbose_name='ip出口', choices=IP_EXPORT_CHOICES, max_length=10, default='', blank=False)

    class Meta:
        verbose_name = "路由出口优化"
        verbose_name_plural = verbose_name
        db_table = "button"
        unique_together = ('ip', 'device',)
