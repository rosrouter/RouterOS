from pybix import ZabbixAPI, GraphImageAPI


def get_image_by_host(ip):
    # 建立zabbix客户端
    ZAPI = ZabbixAPI(url="http://122.51.39.93/zabbix")
    # 登录zabbix
    ZAPI.login(user="Admin", password='zabbix')
    host_ids = 0
    # 获取host信息
    for host_info in ZAPI.host.get(output="extend", monitored_hosts=1):
        if host_info['host'] == ip:
            host_ids = host_info['hostid']
            break
    # 根据host_id获取指定host的graph信息(下图中的10107是某一个host_id）
    graph_info = ZAPI.graph.get(output='extend', hostids=host_ids)
    for graph_data in graph_info:
        if graph_data['name'].endswith('bridge1') or graph_data['name'].endswith('bridge-local'):
            # 创建graph image 客户端
            graph = GraphImageAPI(url="http://122.51.39.93/zabbix", user="Admin", password='zabbix')
            # 根据指定graph_id 获取graph图
            file_name = graph.get_by_graph_id(graph_data['graphid'])  # 默认会存到当前目录（也可以指定）
            return file_name
