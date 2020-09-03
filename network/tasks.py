from x_network.celery import app
from network.worker.l2tp_vpn_info import l2tp
from network.worker.master import update_center_data


@app.task(queue='l2tp_vpn_scan')
def l2tp_vpn_scan():
    l2tp()


@app.task(queue='traffic')
def master_traffic():
    update_center_data()
