from xadmin.plugins.actions import BaseActionView
import xadmin
from xadmin import views
<<<<<<< HEAD
from network.models import L2TP, UserManage, NetworkManage
=======
from network.models import RosRouter, UserManage, VPNInfo
>>>>>>> master


class GlobalSetting(object):
    site_title = '网络设备管理系统'
    site_footer = 'Design by yyy'
    # menu_style = "accordion"  # 菜单可折叠


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True  # use more theme


xadmin.site.register(views.CommAdminView, GlobalSetting)
xadmin.site.register(views.BaseAdminView, BaseSetting)


<<<<<<< HEAD
class L2TPAdmin(object):
    list_display = ['username', 'password', 'status']

    # list_filter = []
    # search_fields = []
    # actions = []   # 执行操作
    # preserve_filters = True
    # list_editable = []  # 可直接编辑
    # def queryset(self):
    #     """函数作用：使当前登录的用户只能看到自己负责的设备"""
    #     qs = super(NetworkAdmin, self).queryset()
    #     if self.request.user.is_superuser:
    #         return qs
    #     return Network.objects.filter(member__contains=self.request.user.username)


class NetworkAdmin(object):
    list_display = ['ip', 'vpns']
=======
class VPNAdmin(object):
    list_display = ['vpn_user', 'vpn_pwd', 'status']

    list_filter = []
    search_fields = []
    actions = []  # 执行操作
    preserve_filters = True
    list_editable = []  # 可直接编辑

    def queryset(self):
        """函数作用：使当前登录的用户只能看到自己负责的设备"""
        qs = super(VPNAdmin, self).queryset()
        if self.request.user.is_superuser:
            return qs
        return VPNInfo.objects.filter(ros__usermanage__user=self.request.user)


class RosRouterAdmin(object):
    list_display = ['ip', 'ros_user', 'ros_pwd']
>>>>>>> master


class UserAdmin(object):
    list_display = ['user', 'device']


<<<<<<< HEAD
xadmin.site.register(L2TP, L2TPAdmin)
xadmin.site.register(NetworkManage, NetworkAdmin)
xadmin.site.register(UserManage, NetworkAdmin)
=======
xadmin.site.register(VPNInfo, VPNAdmin)
xadmin.site.register(RosRouter, RosRouterAdmin)
xadmin.site.register(UserManage, UserAdmin)
>>>>>>> master
