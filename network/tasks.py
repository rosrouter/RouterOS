from x_network.celery import app
from network.worker.l2tp_vpn_info import tasks_test
@app.task(queue='taskstest')
def query_tasks():
    tasks_test()