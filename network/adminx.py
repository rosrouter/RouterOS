import xadmin,paramiko,logging

from xadmin import views
from network.models import RosRouter, UserManage, VPNInfo

def action(rosip,rosuser,rospasswd,command):
    """ROS设备L2TP用户密码操作函数"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=rosip, port=22,
                username=rosuser, password=rospasswd,
                look_for_keys=False)
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
    list_display = ['vpn_user', 'vpn_pwd', 'status', 'up_time']
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
            self.list_display = ['vpn_user', 'vpn_pwd', 'status', 'up_time', 'ros']
            return qs
        return VPNInfo.objects.filter(ros__usermanage__user=self.request.user)

    def save_models(self):
        """在增加或者修改vpn信息的时候触发"""
        obj = self.new_obj
        if obj.id is None:  # 新增的时候
            self.new_obj.ros = self.request.user.usermanage.device  # 绑定用户管理的ros设备
            ros = self.new_obj.ros
            command = f'/ppp secret add name={obj.vpn_user} password={obj.vpn_pwd} service=any profile=l2tp-server'
            action(ros.ip,ros.ros_user,ros.ros_pwd,command)
            # print(f'ros_ip:{ros.ip}')
            # print(f'ros_user:{ros.ros_user}')
            # print(f'ros_pwd:{ros.ros_pwd}')
            # vpn账号信息
            # print(f'vpn_user:{obj.vpn_user}')
            # print(f'vpn_pwd:{obj.vpn_pwd}')
            # print(type(self.new_obj.ros))
            print('create a new vpn')
        else:  # 修改的时候
            # 获取关联ros设备
            ros = self.new_obj.ros
            command = f'/ppp secret add name={obj.vpn_user} password={obj.vpn_pwd} service=any profile=l2tp-server'
            action(ros.ip, ros.ros_user, ros.ros_pwd, command)
            # ros 设备信息
            # print(f'ros_ip:{ros.ip}')
            # print(f'ros_user:{ros.ros_user}')
            # print(f'ros_pwd:{ros.ros_pwd}')
            # # vpn账号信息
            # print(f'vpn_user:{obj.vpn_user}')
            # print(f'vpn_pwd:{obj.vpn_pwd}')
            # print(type(self.new_obj.ros))
            print('update a vpn info')
        super(VPNAdmin, self).save_models()

    def delete_model(self):
        """删除VPN的时候触发"""
        obj = self.obj
        ros = obj.ros
        # ros 设备信息
        print(f'ros_ip:{ros.ip}')
        print(f'ros_user:{ros.ros_user}')
        print(f'ros_pwd:{ros.ros_pwd}')
        # vpn账号信息
        print(f'vpn_user:{obj.vpn_user}')
        print(f'vpn_pwd:{obj.vpn_pwd}')
        ros = self.new_obj.ros
        command = f'/ppp secret remove {obj.vpn_user}'
        action(ros.ip, ros.ros_user, ros.ros_pwd, command)
        print('delete a vpn')
        super(VPNAdmin, self).delete_model()

    def delete_models(self, queryset):
        """批量删除VPN的时候触发"""
        for obj in queryset:
            ros = obj.ros
            # ros 设备信息
            print(f'ros_ip:{ros.ip}')
            print(f'ros_user:{ros.ros_user}')
            print(f'ros_pwd:{ros.ros_pwd}')
            # vpn账号信息
            print(f'vpn_user:{obj.vpn_user}')
            print(f'vpn_pwd:{obj.vpn_pwd}')
        super(VPNAdmin, self).delete_models(queryset)


class RosRouterAdmin(object):
    list_display = ['ip', 'ros_user', 'ros_pwd']


class UserAdmin(object):
    list_display = ['user', 'device']


xadmin.site.register(VPNInfo, VPNAdmin)
xadmin.site.register(RosRouter, RosRouterAdmin)
xadmin.site.register(UserManage, UserAdmin)
