from django.test import TestCase
import os
import django
import paramiko
import re


# Create your tests here.


def action():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='218.1.6.202',
                port=22,
                username='',
                password='4st77@',
                look_for_keys=False)
    command = '/ip route print brief'
    _, res, _ = ssh.exec_command(command)
    result = str(res.read(),encoding='cp1252').strip().split('\n')
    for i in result:
        if re.compile(r'91.9.9.0/24').search(i):
            num = i.split(' ')[0]
            ssh.exec_command('/ip route remove %s'%num)
            break
    ssh.close()

l = ' 7 A S  5.5.5.5/32                         l2tp-xg                   1'
print('5.5.5.5/32' in l)

