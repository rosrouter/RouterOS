from django.contrib.auth.models import User
from network.serializers import UserSerializer, RosRouterSerializer
from django.http import HttpResponse
import base64
import os
from network.worker.get_zabbix_graph import get_image_by_host
from network.models import UserManage


# Create your views here.

def image_test(request):
    # 根据用户绑定的ros设备来显示zabbix监控图
    ros = request.user.usermanage.device  # 绑定用户管理的ros设备
    path = get_image_by_host(ros.ip)
    file_one = open(path, 'rb')
    os.remove(path)
    return HttpResponse(file_one.read(), content_type='image/png')


# 批量增加用户账号和ros设备以及两者之间的管理
def add_user_ros_by_batch(request):
    """
    用户账号规则：
    比如ip地址是218.65.33.25，那用户名就是admin218653325，密码统一就用R0s218653325
    """
    # 获取ip信息
    with open('/root/在线设备IP列表.txt', 'r') as f:
        ips = f.readlines()
        ips = [ip.strip() for ip in ips]
    std_user_data = UserSerializer(User.objects.get(username='admin257')).data
    for ip in ips:
        ros_dict = {'ip': ip, 'ros_user': 'admin-zyb', 'ros_pwd': '4st77rU80@'}
        ros_ser = RosRouterSerializer(data=ros_dict)
        if ros_ser.is_valid():
            ros = ros_ser.save()
        else:
            print(f'{ip}ros设备入库出问题')
            continue
        ip_str = ''.join(ip.split('.'))
        username = 'admin' + ip_str
        password = 'R0s' + ip_str
        user = User.objects.create_user(username=username, password=password, is_active=True, is_staff=True, )
        user_dict = dict(user_permissions=std_user_data['user_permissions'])
        user_ser = UserSerializer(user, user_dict, partial=True)
        if user_ser.is_valid():
            user = user_ser.save()
        else:
            print(f'{ip}对应的user创建失败')
            continue
        UserManage.objects.create(user=user, device=ros)
