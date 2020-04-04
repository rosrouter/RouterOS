from django.test import TestCase
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "x_network.settings")
django.setup()
# Create your tests here.
from network.models import RosRouter
import paramiko,re
def vpninfo():
    info = []
    res = RosRouter.objects.all()
    for i in res:
        info.append({
            'ip':i.ip,
            'ros_user': i.ros_user,
            'ros_pwd': i.ros_pwd,
        })
    for x in info:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=x['ip'], port=22,
                    username=x['ros_user'], password=x['ros_pwd'],
                    look_for_keys=False)
        _, secret, _ = ssh.exec_command('/ppp secret print')
        _, active, _ = ssh.exec_command('/ppp active print')
        output_secret = str(secret.read(), 'utf-8').strip().split('\n')[2:]
        output_active = str(active.read(), 'utf-8').strip().split('\n')[2:]
        ssh.close()
        print(f'------------------->{x["ip"]}<------------------------')
        l2tp_user_pwd_list = []#该列表存放ros路由器的所有l2tp用户名密码
        for v in output_secret:
            vsplit = re.split(r' +', v.strip())
            l2tp_user= vsplit[1]
            l2tp_pwd = vsplit[3]
            l2tp_user_pwd_list.append({
                'user':l2tp_user,
                'pwd':l2tp_pwd
            })
        #-----------------
        #当output_active是空列表说明当前没有用户在线，可以将所有用户的状态置为False,在线时间置为None
        if not output_active:
            for p in l2tp_user_pwd_list:
                result_all_false = {}
                result_all_false['l2tp_user'] = p['user']
                result_all_false['l2tp_pwd'] = p['pwd']
                result_all_false['status'] = False
                result_all_false['uptime'] = None
                print(result_all_false)
        #当output_active列表不为空时，但可能并不是所有用户都在这个列表里，所以需要对比之前的l2tp_user_pwd_list所有用户列表
        #和output_active列表的用户名，当用户名匹配时才将状态置为True，匹配不到的用户置为False
        else:
            active_list = []
            for k in output_active:
                ksplit = re.split(r' +', k.strip())
                active_user = ksplit[1]
                uptime = ksplit[5]
                active_list.append({
                    'active_user':active_user,
                    'uptime':uptime
                })
            # print(active_list)
            for p in l2tp_user_pwd_list:
                for l in active_list:
                    if p['user'] == l['active_user']:
                        result_true = {}
                        result_true['l2tp_user'] = p['user']
                        result_true['l2tp_pwd'] = p['pwd']
                        result_true['status'] = True
                        result_true['uptime'] = l['uptime']
                        print(result_true)
                    else:
                        result_false = {}
                        result_false['l2tp_user'] = p['user']
                        result_false['l2tp_pwd'] = p['pwd']
                        result_false['status'] = False
                        result_false['uptime'] = None
                        print(result_false)

vpninfo()
