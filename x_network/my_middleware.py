from django.utils.deprecation import MiddlewareMixin
from xadmin.models import UserWidget, UserSettings
from network.serializers import UserWidgetSerializer
from django.contrib.auth.models import User

class LoginMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        # 展示首页的时候进行检查
        if request.method == 'GET' and request.path == '/xadmin/' and request.user.id is not None:
            html_str = f"<img src=\"http://49.235.114.108:{request.META['SERVER_PORT']}/network/image/\" width=\"1200\" height=\"600\" title=\"流量图\">"
            # 检查对应的widget是否和请求端口一致
            widget = UserWidget.objects.filter(user=request.user, page_id='home', widget_type='html')
            user_settings = UserSettings.objects.filter(user=request.user)
            if not user_settings:
                user_settings = UserSettings.objects.create(user=request.user)
            else:
                user_settings = user_settings[0]
            print(request.user.id)
            if widget:
                value = widget[0].get_value()
                if user_settings.value != widget[0].id:
                    user_settings.value = widget[0].id
                    user_settings.save()
                if value["content"] == html_str and value['title'] == '流量图' and value['id'] == widget[0].id:
                    pass
                else:
                    value["content"] = html_str
                    value["title"] = '流量图'
                    value["id"] = widget[0].id
                    widget[0].set_value(value)
                    widget[0].save()
            else:
                # 为用户自动添加zabbix组件
                yyy_widget = UserWidget.objects.get(user=User.objects.get(username='yyy'))
                std_widget_info = UserWidgetSerializer(yyy_widget).data
                std_widget_info['user'] = request.user.id
                widget_s = UserWidgetSerializer(data=std_widget_info)
                if widget_s.is_valid():
                    widget_s.save()
        return None
