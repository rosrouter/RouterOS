from django.contrib.auth.models import User
from network.serializers import UserSerializer, RosRouterSerializer
from django.http import HttpResponse, StreamingHttpResponse
import base64
import os, json
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


def apiechart(request):
    data = json.dumps({
        "Cisco": 29, "Juniper": 60, "Paloalto": 30, "Checkpoint": 20, "Fortinet": 50, "Radware": 100
    })
    return HttpResponse(data)


def download_vpn_client(request):
    # 项目根目录
    file_name = 'vpnclient.rar'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, file_name)

    if not os.path.isfile(file_path):  # 判断下载文件是否存在
        return HttpResponse("Sorry but Not Found the File")

    def file_iterator(file_path, chunk_size=512):
        """
        文件生成器,防止文件过大，导致内存溢出
        :param file_path: 文件绝对路径
        :param chunk_size: 块大小
        :return: 生成器
        """
        with open(file_path, mode='rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    try:
        # 设置响应头
        # StreamingHttpResponse将文件内容进行流式传输，数据量大可以用这个方法
        response = StreamingHttpResponse(file_iterator(file_path))
        # 以流的形式下载文件,这样可以实现任意格式的文件下载
        response['Content-Type'] = 'application/octet-stream'
        # Content-Disposition就是当用户想把请求所得的内容存为一个文件的时候提供一个默认的文件名
        response['Content-Disposition'] = f'attachment;filename="{file_name}"'
    except:
        return HttpResponse("Sorry but Not Found the File")

    return response
