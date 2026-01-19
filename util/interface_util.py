import json

import requests
import logging
from dynaconf import settings

from log_model.set_log import setup_logging

setup_logging(default_path=settings.LOGGING)


def cancelorder(order_id):
    """
    查询后台订单状态
    :param orderId:
    :return:
    """
    try:
        url = settings.PATH + "/api/wx/select/order?orderId={}".format(order_id)
        r = requests.get(url)
        stutas = str(r.text)
    except Exception as f:
        logging.error("确认订单状态失败" + str(f))
        stutas = "20"
    if stutas == "23":
        return False
    else:
        return True


def payresult(orderId, status):
    try:
        url = settings.PATH + "/api/wx/pay/result?status={}&message=null&orderId={}".format(status, orderId)
        r = requests.get(url)
    except Exception as f:
        logging.error("通知支付状态失败" + str(f))
    return True


def select_device():
    url = settings.ADMIN_URL81 + "/api/sht/library/all/libraries"
    res = requests.get(url)
    resjson = json.loads(res.text)
    if resjson['result']:
        return resjson['result']
    else:
        return None


def update_device(device_id, state):
    url = settings.ADMIN_URL81 + "/api/sht/library/update/library"
    data = {
        "deviceId": device_id,
        "isBusy": state
    }
    res = requests.post(url, json=data)
    resjson = json.load(res.text)
    if resjson['success']:
        return resjson['success']
    else:
        return None


def update_device_run_status(device_id, run_status):
    url = settings.ADMIN_URL81 + "/api/sht/library/update/library"
    data = {
        "deviceId": device_id,
        "runStatus": run_status
    }
    res = requests.post(url, json=data)
    resjson = json.load(res.text)
    if resjson['success']:
        return resjson['success']
    else:
        return None