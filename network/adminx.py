import xadmin
from xadmin import views
from network.models import RosRouter, UserManage, VPNInfo


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
    list_per_page = 15 # 分页

    def queryset(self):
        """函数作用：使当前登录的用户只能看到自己负责的设备"""
        qs = super(VPNAdmin, self).queryset()
        if self.request.user.is_superuser:
            return qs
        return VPNInfo.objects.filter(ros__usermanage__user=self.request.user)


class RosRouterAdmin(object):
    list_display = ['ip', 'ros_user', 'ros_pwd']


class UserAdmin(object):
    list_display = ['user', 'device']


xadmin.site.register(VPNInfo, VPNAdmin)
xadmin.site.register(RosRouter, RosRouterAdmin)
xadmin.site.register(UserManage, UserAdmin)
