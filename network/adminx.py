import xadmin,paramiko,logging,re

from xadmin import views
from network.models import RosRouter, UserManage, VPNInfo

def action(rosip,rosuser,rospasswd,command,tag=None):
    """ROS设备L2TP用户密码操作函数"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=rosip, port=22,
                username=rosuser, password=rospasswd,
                look_for_keys=False)
    if tag == 'add':
        _,res,_ =  ssh.exec_command('/ppp secret print')
        result = str(res.read(), 'utf-8').strip()
        ipre = re.compile(r'\d*[.]\d*[.]\d*[.]\d*')
        iplist = ipre.findall(result)
        ip = max([int(i.split('.')[-1]) for i in iplist])
        ip+=1
        assert ip!=255,'IP地址超出范围!'
        commands = command + 'remote-address=172.162.254.%d'%ip
    else:
        commands = command
    ssh.exec_command(commands)
    ssh.close()

class GlobalSetting(object):
    site_title = '网络设备管理系统'
    site_footer = 'Design by yyy'


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True  # use more theme


xadmin.site.register(views.CommAdminView, GlobalSetting)
xadmin.site.register(views.BaseAdminView, BaseSetting)


class VPNAdmin(object):
    list_display = ['vpn_user', 'vpn_pwd', 'status', 'up_time','remark']
    list_filter = ['vpn_user']
    search_fields = []
    actions = []  # 执行操作
    preserve_filters = True
    list_editable = []  # 可直接编辑
    list_per_page = 15  # 分页
    exclude = ['ros', 'up_time', 'status']

    def queryset(self):
        """函数作用：使当前登录的用户只能看到自己负责的设备"""
        qs = super(VPNAdmin, self).queryset()
        if self.request.user.is_superuser:
            self.list_display = ['vpn_user', 'vpn_pwd', 'status', 'up_time', 'remark','ros']
            return qs
        return VPNInfo.objects.filter(ros__usermanage__user=self.request.user)

    def save_models(self):
        """在增加或者修改vpn信息的时候触发"""
        obj = self.new_obj
        if obj.id is None:
            self.new_obj.ros = self.request.user.usermanage.device  # 绑定用户管理的ros设备
            ros = self.new_obj.ros
            command = f'/ppp secret add name={obj.vpn_user} password={obj.vpn_pwd} service=any profile=l2tp-server '
            action(ros.ip,ros.ros_user,ros.ros_pwd,command,tag='add')
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
        command = f'/ppp secret remove {obj.vpn_user}'
        action(ros.ip, ros.ros_user, ros.ros_pwd, command)
        print('delete a vpn')
        super(VPNAdmin, self).delete_model()

    def delete_models(self, queryset):
        """批量删除VPN的时候触发"""
        print(queryset)
        for obj in queryset:
            ros = obj.ros
            command = f'/ppp secret remove {obj.vpn_user}'
            action(ros.ip, ros.ros_user, ros.ros_pwd, command)
        super(VPNAdmin, self).delete_models(queryset)


class RosRouterAdmin(object):
    list_display = ['ip', 'ros_user', 'ros_pwd']


class UserAdmin(object):
    list_display = ['user', 'device']


xadmin.site.register(VPNInfo, VPNAdmin)
xadmin.site.register(RosRouter, RosRouterAdmin)
xadmin.site.register(UserManage, UserAdmin)
