from django.shortcuts import render
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
    return HttpResponse(file_one.read(),content_type='image/png')