from network.models import RosRouter, VPNInfo
from network.serializers import VPNInfoSerializer
import paramiko, re,logging

logger = logging.getLogger(__name__)

def scan_vpn():
    roses = RosRouter.objects.all()
    for ros in roses:
        try:
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
        except Exception as error:
            logging.error(f'Device:{ros.ip} with {error}')
            continue
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
                logging.info('Task Success!')
            else:
                logging.error(f'Device:{ros.ip} with {vpn_ser.errors}')


def l2tp():
    scan_vpn()

# def test():
#     print(1)
#     return True
# def tasks_test():
#     test()