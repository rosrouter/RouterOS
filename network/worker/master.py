import paramiko
import re
import requests
import json
from django.conf import settings
from x_network.utils.zabbix_client import ZabbixApi
from network.serializers import CenterSerializer
from network.models import Center


def action():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='218.1.3.254',
                port=22222,
                username='zb',
                password='18017565515',
                look_for_keys=False)
    command = '/ppp active print detail'
    _, res, _ = ssh.exec_command(command)
    result = str(res.read(), 'utf-8').strip()
    data_re = re.findall('name="(.*?)"[ ]service=(.*?) .*?address=(\S*) .*?uptime=(.*?) ', result, re.S)
    res = []
    for i in data_re:
        name = i[1] + '-' + i[0]
        res.append((name, i[2], i[-1]))
    resp = [dict(zip(('username', 'vpn_ip', 'uptime'), i)) for i in res]
    return resp


def update_center_data():
    token = ZabbixApi().token
    resp = action()
    for i in resp:
        key = ['ifHCInOctets[<%s>]'%i['username'],'ifHCOutOctets[<%s>]'%i['username']]
        for q in key:
            data = {
                'jsonrpc': '2.0',
                'method': 'item.get',
                'params': {
                    'output': 'extend',
                    'hostids': 10367,
                    'search': {
                        'key_': q
                    },
                    'sortfield': 'name'
                },
                'auth': token,
                'id': 1
            }
            u = requests.post(data=json.dumps(data),
                              url=settings.ZABBIX_URL,
                              headers=settings.ZABBIX_HEADER,
                              timeout=300)
            try:
                itemid = json.loads(u.content)['result'][0]['itemid']
                data = {
                    'jsonrpc': '2.0',
                    'method': 'history.get',
                    'params': {
                        'output': 'extend',
                        'history': 3,
                        'itemids': itemid,
                        'sortfield': 'clock',
                        'sortorder': 'DESC',
                        'limit': 1
                    },
                    'auth': token,
                    'id': 1
                }
                u = requests.post(data=json.dumps(data), url=settings.ZABBIX_URL, headers=settings.ZABBIX_HEADER,
                                  timeout=300)
                result = json.loads(u.content)['result'][0]['value']
                if 'HCIn' in q:
                    i['incoming'] = str(result) + 'bps'
                if 'HCOut' in q:
                    i['outgoing'] = str(result) + 'bps'
            except:
                i['incoming'] = 'isNone'
                i['outgoing'] = 'isNone'
        # print(i)
        try:
            username = Center.objects.get(username=i['username'])
            serializer = CenterSerializer(username, data=i)
        except:
            serializer = CenterSerializer(data=i)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
