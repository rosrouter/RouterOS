import paramiko,re
import requests,json
from x_network.settings import Zabbixapi,zabbix,zabbix_header
from network.serializers import CenterSerializer
from network.models import Center
def action():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='218.1.3.254', port=22222,
                username='zb', password='18017565515',
                look_for_keys=False)
    command = '/ppp active print detail'
    _, res, _ = ssh.exec_command(command)
    result = str(res.read(), 'utf-8').strip()
    data_re = re.findall('name="(.*?)"[ ]service=(.*?) .*?address=(\S*) .*?uptime=(.*?) ', result, re.S)
    res = []
    for i in data_re:
        name = i[1] + '-' + i[0]
        res.append((name, i[2], i[-1]))
    resp = [dict(zip(('name', 'address', 'uptime'), i)) for i in res]
    return resp
token = Zabbixapi().token
resp = action()

def actions():
    for i in resp:
        key = ['ifHCInOctets[<%s>]'%i['name'],'ifHCOutOctets[<%s>]'%i['name']]
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
            u = requests.post(data=json.dumps(data), url=zabbix['URL'], headers=zabbix_header,
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
                u = requests.post(data=json.dumps(data), url=zabbix['URL'], headers=zabbix_header,
                                  timeout=300)
                result = json.loads(u.content)['result'][0]['value']
                if 'HCIn' in q:
                    i['incoming'] = str(result) + 'bps'
                if 'HCOut' in q:
                    i['outgoing'] = str(result) + 'bps'
            except:
                i['incoming'] = None
                i['outgoing'] = None
        # print(i)
        try:
            username = Center.objects.get(username=i['name'])
            serializer = CenterSerializer(username, data=i)
        except:
            serializer = CenterSerializer(data=i)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)

def traffic():
    actions()