from django.conf import settings
import json
import requests


class ZabbixApi(object):

    @property
    def token(self):
        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": 'Admin',
                "password": 'zabbix'},
            "id": 1}
        requests_token = requests.post(url=settings.ZABBIX_URL,
                                       data=json.dumps(data),
                                       headers=settings.ZABBIX_HEADER,
                                       timeout=30)
        token = json.loads(requests_token.content)["result"]
        return token
