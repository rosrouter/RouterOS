from django.test import TestCase
import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "x_network.settings")
django.setup()
# Create your tests here.

from textfsm import TextFSM

output = '''
N7K# show vlan

---- -------------------------------- --------- -------------------------------
1 default active Eth1/1, Eth1/2, Eth1/3
 Eth1/5, Eth1/6, Eth1/7
2 VLAN0002  active Po100, Eth1/49, Eth1/50
3 VLAN0003 active Po100, Eth1/49, Eth1/50

'''
f = open('/data/test.template')
template = TextFSM(f)
result = []
for i in template.ParseText(output):
    result.append({
    'vlan_id' : i[0],
    'vlan_name' : i[1],
    'vlan_status' : i[-1]})
print(result)