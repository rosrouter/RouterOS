from network.models import RosRouter
import paramiko, re


def vpninfo():
    info = []
    res = RosRouter.objects.all()
    for i in res:
        info.append({
            'ip': i.ip,
            'ros_user': i.ros_user,
            'ros_pwd': i.ros_pwd,
        })
    for x in info:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=x['ip'], port=22,
                    username=x['ros_user'], password=x['ros_pwd'],
                    look_for_keys=False)
        _, stdout, _ = ssh.exec_command('/ppp secret print')
        output = str(stdout.read(), 'utf-8').strip().split('\n')[2:]
        ssh.close()
        print('----->%s信息<-----' % x['ip'])
        for v in output:
            vsplit = re.split(r' +', v.strip())
            l2tp_user = vsplit[1]
            l2tp_pwd = vsplit[3]
            l2tp_user_status = 1 if vsplit[-1] else 0
            print('l2tp用户名:%s,l2tp密码:%s,是否在线:%s' % (l2tp_user, l2tp_pwd, l2tp_user_status))


vpninfo()
