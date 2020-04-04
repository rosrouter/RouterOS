from django.test import TestCase
import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "x_network.settings")
django.setup()
# Create your tests here.
from network.models import RosRouter, VPNInfo
from network.serializers import VPNInfoSerializer
import paramiko, re


def scan_vpn():
    roses = RosRouter.objects.all()
    for ros in roses:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=ros.ip, port=22,
                    username=ros.ros_user, password=ros.ros_pwd,
                    look_for_keys=False)
        _, secret, _ = ssh.exec_command('/ppp secret print')
        _, active, _ = ssh.exec_command('/ppp active print')
        output_secret = str(secret.read(), 'utf-8').strip()
        output_active = str(active.read(), 'utf-8').strip()
        ssh.close()
        secret_pattern = re.compile(r'\d+\s*(?P<name>\S*)\s*any\s*(?P<pwd>\S*)\s*')
        active_pattern = re.compile(r'\d+\s*(?P<name>\d+)\s+l2tp\s+\S*\s*\S*\s*(?P<uptime>\S*)\s')
        # 获取全部用户账号和密码,字典 key 为用户，value为密码
        all_vpns = dict(secret_pattern.findall(output_secret))
        # 获取在线用户和时长,字典 key 为用户，value为在线时长
        active_vpn = dict(active_pattern.findall(output_active))
        for user, pwd in all_vpns.items():
            vpn_info = {}
            vpn_info.update(ros=ros.id)
            vpn_info.update(vpn_user=user)
            vpn_info.update(vpn_pwd=pwd)
            vpn_info.update(status=True if user in active_vpn else False)
            vpn_info.update(up_time=active_vpn.get(user, ''))
            # 检查数据库内是否存在
            vpn_exist_flag = VPNInfo.objects.filter(ros=ros, vpn_user=user)
            # 若存在更新原有对象数据
            if vpn_exist_flag:
                vpn_ser = VPNInfoSerializer(vpn_exist_flag[0], data=vpn_info, partial=True)
            else:
                vpn_ser = VPNInfoSerializer(data=vpn_info)
            # 检查是否符合模型要求
            if vpn_ser.is_valid():
                vpn_ser.save()
            else:
                print(vpn_ser.errors)

# def vpninfo():
#     roses = RosRouter.objects.all()
#     for ros in roses:
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh.connect(hostname=ros.ip, port=22,
#                     username=ros.ros_user, password=ros.ros_pwd,
#                     look_for_keys=False)
#         _, secret, _ = ssh.exec_command('/ppp secret print')
#         _, active, _ = ssh.exec_command('/ppp active print')
#         output_secret = str(secret.read(), 'utf-8').strip().split('\n')[2:]
#         output_active = str(active.read(), 'utf-8').strip().split('\n')[2:]
#         ssh.close()
#         print(f'------------------->{ros.ip}<------------------------')
#         l2tp_user_pwd_list = []  # 该列表存放ros路由器的所有l2tp用户名密码
#         for v in output_secret:
#             vsplit = re.split(r' +', v.strip())
#             l2tp_user = vsplit[1]
#             l2tp_pwd = vsplit[3]
#             l2tp_user_pwd_list.append({
#                 'user': l2tp_user,
#                 'pwd': l2tp_pwd
#             })
#         # -----------------
#         # 当output_active是空列表说明当前没有用户在线，可以将所有用户的状态置为False,在线时间置为None
#         if not output_active:
#             for p in l2tp_user_pwd_list:
#                 result_all_false = {}
#                 result_all_false['l2tp_user'] = p['user']
#                 result_all_false['l2tp_pwd'] = p['pwd']
#                 result_all_false['status'] = False
#                 result_all_false['uptime'] = None
#                 print(result_all_false)
#         # 当output_active列表不为空时，但可能并不是所有用户都在这个列表里，所以需要对比之前的l2tp_user_pwd_list所有用户列表
#         # 和output_active列表的用户名，当用户名匹配时才将状态置为True，匹配不到的用户置为False
#         else:
#             active_list = []
#             for k in output_active:
#                 ksplit = re.split(r' +', k.strip())
#                 active_user = ksplit[1]
#                 uptime = ksplit[5]
#                 active_list.append({
#                     'active_user': active_user,
#                     'uptime': uptime
#                 })
#             # print(active_list)
#             for p in l2tp_user_pwd_list:
#                 for l in active_list:
#                     if p['user'] == l['active_user']:
#                         result_true = {}
#                         result_true['l2tp_user'] = p['user']
#                         result_true['l2tp_pwd'] = p['pwd']
#                         result_true['status'] = True
#                         result_true['uptime'] = l['uptime']
#                         print(result_true)
#                     else:
#                         result_false = {}
#                         result_false['l2tp_user'] = p['user']
#                         result_false['l2tp_pwd'] = p['pwd']
#                         result_false['status'] = False
#                         result_false['uptime'] = None
#                         print(result_false)
