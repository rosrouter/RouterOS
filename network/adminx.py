import xadmin, paramiko, logging, re, json, socket

from xadmin import views
from network.models import RosRouter, UserManage, VPNInfo, Button, ToolDownload, Center
from xadmin.models import UserWidget
from network.serializers import UserWidgetSerializer
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from network.views import download_vpn_client


def action(ros_ip, ros_user, ros_pwd, command, tag=None):
    """ROS设备L2TP用户密码操作函数"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ros_ip, port=22,
                username=ros_user, password=ros_pwd,
                look_for_keys=False)
    if tag == 'add':
        _, res, _ = ssh.exec_command('/ppp secret print')
        result = str(res.read(), 'utf-8').strip()
        # ip 正则匹配规则
        ip_pattern = re.compile(
            r'(?:25[0-5]\.|2[0-4]\d\.|1\d{2}\.|[1-9]?\d\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)')
        ip_list = ip_pattern.findall(result)
        ip = max([int(i.split('.')[-1]) for i in ip_list])
        ip += 1
        assert ip <= 255, 'IP地址超出范围!'
        commands = command + 'remote-address=172.162.254.%d' % ip
    else:
        commands = command
    ssh.exec_command(commands)
    ssh.close()


def route(ros_ip, ros_user, ros_pwd, dstroute, nexthop, self):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ros_ip, port=22,
                username=ros_user, password=ros_pwd,
                look_for_keys=False)

    command = '/ip route add  dst-address=%s gateway=%s' % (dstroute, nexthop)
    stdin, stdout, stderr = ssh.exec_command(command)
    res = str(stdout.read(), 'utf-8')
    if 'invalid value' in res:
        self.message_user(u'下一跳接口未被创建，配置下发失败!', 'error')
        ssh.close()
        return 'fail'
    self.message_user(u'路由下发成功!', 'success')
    ssh.close()

def delete_route(ip, ros_user, ros_pwd, command, router):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, port=22,
                username=ros_user, password=ros_pwd,
                look_for_keys=False)
    _, res, _ = ssh.exec_command(command)
    result = str(res.read(), encoding='cp1252').strip().split('\n')
    for i in result:
        if router in i:
            num = i.strip().split(' ')[0]
            print(num)
            ssh.exec_command('/ip route remove %s' % num)
    ssh.close()


def delete(ros_ip, ros_user, ros_pwd, command, vpn_user):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ros_ip, port=22,
                username=ros_user, password=ros_pwd,
                look_for_keys=False)
    stdin, stdout, stderr = ssh.exec_command(command)
    res = str(stdout.read(), 'utf-8')
    for i in res.split('\n')[2:]:
        item = re.split(r' +', i.strip())
        if vpn_user == item[1]:
            num = item[0]
            ssh.exec_command('/ppp secret remove %s' % num)
            ssh.close()
            break
    ssh.close()


def deletes(ros_ip, ros_user, ros_pwd, command, vpn_user):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ros_ip, port=22,
                username=ros_user, password=ros_pwd,
                look_for_keys=False)
    stdin, stdout, stderr = ssh.exec_command(command)
    res = str(stdout.read(), 'utf-8')
    print(res)
    for i in res.split('\n')[2:]:
        item = re.split(r' +', i.strip())
        if vpn_user == item[1]:
            num = item[0]
            ssh.exec_command('/ppp secret remove %s' % num)
            ssh.close()
            break
    ssh.close()


class GlobalSetting(object):
    site_title = '互联网接入管理系统'
    site_footer = 'Design by LIANCHI'


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True  # use more theme


class VPNAdmin(object):
    list_display = ['vpn_user', 'vpn_pwd', 'status', 'up_time', 'remark']  # 列表页展示的字段
    list_filter = ['vpn_user']  # 列表页可以进行筛选的选项
    search_fields = []
    actions = []  # 执行操作
    preserve_filters = True
    list_editable = []  # 可直接编辑
    list_per_page = 15  # 分页
    exclude = ['ros', 'up_time', 'status']  # 在编辑也不显示的字段

    def queryset(self):
        """函数作用：使当前登录的用户只能看到自己负责的设备"""
        # 为用户自动添加zabbix组件
        if not UserWidget.objects.filter(user=self.request.user):
            std_widget_info = UserWidgetSerializer(UserWidget.objects.get(user=User.objects.get(username='yyy'))).data
            std_widget_info['user'] = self.request.user.id
            widget_s = UserWidgetSerializer(data=std_widget_info)
            if widget_s.is_valid():
                widget_s.save()
        qs = super(VPNAdmin, self).queryset()
        if self.request.user.is_superuser:
            self.list_display = ['vpn_user', 'vpn_pwd', 'status', 'up_time', 'remark', 'ros']
            return qs
        return VPNInfo.objects.filter(ros__usermanage__user=self.request.user)

    def save_models(self):
        """在增加或者修改vpn信息的时候触发"""
        obj = self.new_obj
        if obj.id is None:
            self.new_obj.ros = self.request.user.usermanage.device  # 绑定用户管理的ros设备
            ros = self.new_obj.ros
            command = f'/ppp secret add name={obj.vpn_user} password={obj.vpn_pwd} service=any profile=l2tp-server '
            action(ros.ip, ros.ros_user, ros.ros_pwd, command, tag='add')
            super(VPNAdmin, self).save_models()
        else:
            # 获取关联ros设备
            ros = self.new_obj.ros
            check_user = VPNInfo.objects.filter(vpn_user=obj.vpn_user)
            check_pwd = VPNInfo.objects.filter(vpn_pwd=obj.vpn_pwd)
            check_remark = VPNInfo.objects.filter(remark=obj.remark)
            if check_pwd and check_user and check_remark:
                pass
            elif check_pwd and check_user and not check_remark:
                super(VPNAdmin, self).save_models()
                print('not access device')
            else:
                command = f'/ppp secret set {obj.vpn_user} password={obj.vpn_pwd}'
                action(ros.ip, ros.ros_user, ros.ros_pwd, command)
                print('update a vpn info')
                super(VPNAdmin, self).save_models()

    def delete_model(self):
        """删除VPN的时候触发"""
        obj = self.obj
        ros = obj.ros
        command = '/ppp secret print'
        delete(ros.ip, ros.ros_user, ros.ros_pwd, command, obj.vpn_user)
        super(VPNAdmin, self).delete_model()

    def delete_models(self, queryset):
        """批量删除VPN的时候触发"""
        print(queryset)
        for obj in queryset:
            ros = obj.ros
            command = f'/ppp secret print'
            deletes(ros.ip, ros.ros_user, ros.ros_pwd, command, obj.vpn_user)
        super(VPNAdmin, self).delete_models(queryset)


class RosRouterAdmin(object):
    list_display = ['ip', 'ros_user', 'ros_pwd']


class UserAdmin(object):
    list_display = ['user', 'device']


class ButtonAdmin(object):
    list_display = ['ip', 'ip_export']
    exclude = ['device']

    def save_models(self):
        obj = self.new_obj
        self.new_obj.device = self.request.user.usermanage.device
        nexthop = self.request.POST['ip_export']
        routeip = self.request.POST['ip']
        exist_flag = Button.objects.filter(device=self.request.user.usermanage.device, ip=routeip)
        # 判断库内是否已经存在该组信息
        if obj.id is None and not exist_flag:
            ros_ip = self.request.user.usermanage.device.ip
            ros_user = self.request.user.usermanage.device.ros_user
            ros_passwd = self.request.user.usermanage.device.ros_pwd
            reip = re.compile(r'\d*[.]\d*[.]\d*[.]\d*[/][\d+]')
            if reip.search(routeip):
                msg = route(ros_ip, ros_user, ros_passwd, routeip, nexthop, self)
            else:
                try:
                    res = socket.getaddrinfo(routeip, 'http')[0][4][0] + '/32'
                except:
                    self.message_user(u'域名解析失败或输入IP地址格式错误', 'error')
                    return
                msg = route(ros_ip, ros_user, ros_passwd, res, nexthop, self)
            if msg == 'fail':
                return
        try:
            super(ButtonAdmin, self).save_models()
        except IntegrityError:
            self.message_user('当前添加的ip已经在库内存在', 'error')

    def delete_model(self):
        obj = self.obj
        ros = obj.device
        command = '/ip route print brief'
        print(ros.ip, ros.ros_user, ros.ros_pwd, command, obj.ip)
        delete_route(ros.ip, ros.ros_user, ros.ros_pwd, command, obj.ip)
        super(ButtonAdmin, self).delete_model()

    def queryset(self):
        return Button.objects.filter(device=self.request.user.usermanage.device)


class ToolDownloadAdmin(object):
    def get_response(self, *args, **kwargs):
        if 'update' in self.request.path:
            return download_vpn_client(request='123')
        else:
            super().get_response(*args, **kwargs)


class CenterAdmin(object):
    list_display = ['username', 'incoming', 'outgoing', 'vpn_ip', 'uptime']
    pass


# 注册xadmin控制器和对应模型
xadmin.site.register(VPNInfo, VPNAdmin)
xadmin.site.register(RosRouter, RosRouterAdmin)
xadmin.site.register(UserManage, UserAdmin)
xadmin.site.register(Button, ButtonAdmin)
xadmin.site.register(ToolDownload, ToolDownloadAdmin)
xadmin.site.register(Center, CenterAdmin)
xadmin.site.register(views.CommAdminView, GlobalSetting)
xadmin.site.register(views.BaseAdminView, BaseSetting)
