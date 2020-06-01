from django.shortcuts import render
from django.contrib.auth.models import User
from network.serializers import UserSerializer, RosRouterSerializer
from rest_framework.response import Response
from django.http import HttpResponse
import base64
import os
from network.worker.get_zabbix_graph import get_image_by_host


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
    with open('/root/在线设备IP列表.txt', r) as f:
        ips = f.readlines()
        ips = [ip.strip() for ip in ips]
    std_user_data = UserSerializer(User.objects.get('admin257')).data
    for ip in ips:
        ros_dict = {'ip': ip}
        ros_ser = RosRouterSerializer(data=ros_dict)
        if ros_ser.is_valid():
            ros = ros_ser.save()
        else:
            print(f'{ip}入库出问题')
        ip_str = ''.join(ip.split('.'))
        username = 'admin' + ip_str
        password = 'R0s' + ip_str
        user_dict = dict(username=username, password=password, user_permissions=std_user_data['user_permissions'])
        pass
