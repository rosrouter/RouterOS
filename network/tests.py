from django.test import TestCase
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "x_network.settings")
django.setup()
# Create your tests here.
from network.models import RosRouter
from librouteros import connect
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
    # for x in info:
    #     print(x)
    #     api = connect(username=x['ros_user'], password=x['ros_pwd'], host=x['ip'],port=7777)
    #     res = api(cmd='/ppp/secret/print')
    #     for v in res:
    #         print(v)
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
        # print('----->%s信息<-----'%x['ip'])
        l2tp_user_pwd_list = []
        for v in output_secret:
            vsplit = re.split(r' +', v.strip())
            l2tp_user= vsplit[1]
            l2tp_pwd = vsplit[3]
            l2tp_user_pwd_list.append({
                'user':l2tp_user,
                'pwd':l2tp_pwd
            })
        print(l2tp_user_pwd_list)
        # if output_active:
        #     db_res = {}
        #     for q in output_active:
        #         qsplit = re.split(r' +', q.strip())
        #         quser = qsplit[1]
        #         quptime = qsplit[5]
        #
        # else:
        #     db_res = {}
        #     db_res['ip'] = x['ip']
        #     db_res['l2tp_user'] = ''
        #     db_res['l2tp_pwd'] = ''
        #     db_res['status'] = False
        #     db_res['uptime'] = False
        #     print(db_res)
            #入库

#['0', '101', 'l2tp', '218.1.3.254', '172.162.254.101', '3m22s', 'MPPE128', 'stateless']
vpninfo()
