import requests,json
from x_network.settings import Zabbixapi,zabbix,zabbix_header
token = Zabbixapi().token

def allros():
    hosts = []
    with open(r'/root/在线设备IP列表.txt', 'r') as f:
        for host in f.readlines():
            hosts.append(host.strip())
    return hosts

def gettemplateid():
    data = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "extend",
                "filter": {
                    "host": "Template SNMP Interfaces"
                }
            },
            "auth": token,
            "id": 1
        }
    resp = requests.post(zabbix['URL'], data=json.dumps(data),headers=zabbix_header).json()
    templateid = resp['result'][0]['templateid']
    return templateid

def getgroupid():
    data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": "mikrotik"
                }
            },
            "auth": token,
            "id": 1
        }
    resp = requests.post(zabbix['URL'], data=json.dumps(data), headers=zabbix_header).json()
    groupid = resp['result'][0]['groupid']
    return groupid

def hostcreate(templateid,groupid,hosts):
    for host in hosts:
        data = {
        "jsonrpc": "2.0",
        "method": "host.create",
        "params": {
        "host": host,
        "macros":
        {
        "macro": "{$SNMP_COMMUNITY}",
        "value": "public"
        },
        "interfaces": [
        {"type": 1,
        "main": 1,
        "useip": 1,
        "ip": "127.0.0.1",
        "dns": "",
        "port": "10050"},
        {
        "type": 2,
        "main": 1,
        "useip": 1,
        "ip": host,
        "dns": "",
        "port": "161"}
        ],
        "groups": [{"groupid": groupid}],
        "templates": [{"templateid": templateid}],
        "inventory_mode": 0},
        "auth": token,
        "id": 1}
        resp = requests.post(zabbix['URL'], data=json.dumps(data), headers=zabbix_header,timeout=100)
        print(resp.text)

# templateid = gettemplateid()
# groupid = getgroupid()
# hosts = allros()
# hostcreate(templateid,groupid,hosts)
