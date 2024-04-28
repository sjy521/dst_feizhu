import datetime

import requests
import json
import logging
import random

from dynaconf import settings
from log_model.set_log import setup_logging

setup_logging(default_path=settings.LOGGING)


# 查询可用的设备
def get_effective_device():
    """
    从数据库查询可用且空闲的device_id
    :return: device_id
    """
    device_id_list = []
    url = settings.ADMIN_URL81 + "/library/all/libraries"
    response = requests.request("GET", url)
    res_json = json.loads(response.text)
    print(res_json)
    if res_json.get("code") == 200:
        results = res_json.get("result")
        for result in results:
            if result.get('isEnable') == "1" and result.get('isBusy') <= 1:
                device_id_list.append(result)
    if len(device_id_list) > 0:
        return random.choices(device_id_list)
    else:
        return None


# 设置不可用的设备
def set_not_effective_device(device_id, is_enable, is_busy):
    """
    从数据库更新的device_id为不可用或不空闲
    :return: device_id
    """
    url = settings.ADMIN_URL81 + "/library/update/library"
    payload = {"deviceId": device_id,
               "isEnable": str(is_enable),
               "isBusy": is_busy
               }
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        logging.info("数据库更新成功, result: {}".format(str(res_json)))
        return True
    logging.info("数据库更新失败, result: {}".format(str(res_json)))
    return False


# 查询有效订单，并锁单
def get_effective_order(device_id):
    """
    查询有效订单，并锁单
    :return: bgorderid
    """
    url = settings.ADMIN_URL + "/hotel/bgorder/getNoReadyOrderByPage"
    payload = {"pageNum": 1, "pageSize": 10, "param": {}}
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        results = res_json.get("result")
        if len(results.get("rows")) > 0:
            for result in results.get("rows"):
                bg_order_id = result.get("bgOrderId")
                d_ordr_id = result.get("dorderId")
                # 加锁
                url = settings.ADMIN_URL + "/hotel/bgorder/lockBySystem"
                querystring = {"orderId": bg_order_id, "userName": device_id}
                order_response = requests.request("GET", url, params=querystring)
                order_res_json = json.loads(order_response.text)
                if order_res_json['result']['islock'] is True:
                    return [d_ordr_id, bg_order_id]
                else:
                    logging.info("bgorderid: {}, result: {}".format(bg_order_id, str(order_res_json)))
    return None


# 订单备注更新并解锁
def fail_order_unlock(change_status, full_status, bg_order_id, device_id):
    """
    订单解锁，订单通知失败
    :param change_status:
    :param bg_order_id:
    :param full_status:
    :param device_id:
    :return: true，false
    """
    url = settings.ADMIN_URL + "/hotel/bgorder/editChangePrieOrFullBySystem"
    payload = {"changeStatus": change_status, "fullStatus": full_status, "bgOrderId": bg_order_id}
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    logging.info('[{}]更新了变价满房状态, res: {}'.format(bg_order_id, str(res_json)))
    unlock(bg_order_id, device_id)


# 订单解锁
def unlock(bg_order_id, device_id):
    url = settings.ADMIN_URL + "/hotel/bgorder/unlockBySystem"
    querystring = {"orderId": bg_order_id, "userName": device_id}
    response = requests.request("GET", url, params=querystring)
    order_res_json = json.loads(response.text)
    if order_res_json['result'] is True:
        logging.info("bgorderid: {}，通知解锁result: {}".format(bg_order_id, str(order_res_json)))
    logging.info("bgorderid: {}，解锁失败result: {}".format(bg_order_id, str(order_res_json)))


# 根据bgOrderId 获取供应商下单地址
def get_url_by_bgorderid(d_order_id, bg_order_id):
    """
    根据bgOrderId 获取供应商下单地址
    :return: json
    """
    url = settings.ADMIN_URL + "/hotel/dorder/selectDOrderItem"
    payload = {"dOrderId": d_order_id, "bgOrderId": bg_order_id}
    response = requests.request("GET", url, params=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        results = res_json.get("result")
        order_item = results['orderItem']
        d_order = results['dOrder']
        tar_json = {
            "contact_phone": order_item.get("consumerPhone"),
            "guest_list": [order_item.get("consumerName"), order_item['contact'] if order_item.get("contact") else [
                order_item.get("consumerName")]],
            "check_in": d_order.get("checkInTime").split(" ")[0],
            "check_out": d_order.get("checkOutTime").split(" ")[0],
            "sr_name": order_item.get("productName"),
            "price": d_order.get("price")
        }
        supplier_product_id = json.loads(d_order['productItem'])['supplierProductId']
        supplier_hotel_id = json.loads(d_order['productItem'])['supplierHotelId']

        url = settings.SPA_URL + "/client/spa/check"

        payload = {"checkIn": tar_json['check_in'], "checkOut": tar_json['check_out'], "roomNum": 1, "totalPrice": -999,
                   "supplierId": 10002, "sHotelId": supplier_hotel_id,
                   "sproductId": supplier_product_id}
        response = requests.request("POST", url, json=payload)
        res_json1 = json.loads(response.text)
        tar_json['wx_link'] = res_json1['result']['message']
        return tar_json


# 下单
def build_order(device_id, tar_json):
    """
    创建订单
    :param device_id:
    :return:  成功，变价，满房，失败
    """
    url = "http://192.168.52.112:8083/fliggy/buildorder"
    payload = {
        "wx_link": tar_json['wx_link'],
        "sr_name": tar_json['sr_name'],
        "contact_phone": tar_json['contact_phone'],
        "guest_list": tar_json['guest_list'],
        "check_in": tar_json['check_in'],
        "check_out": tar_json['check_out'],
        "price": tar_json['price'],
        "device_id": device_id,
    }
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json['status'] is True:
        status = res_json['data']['status']
        if status is True:
            biz_order_id = res_json['data']['bizOrderId']
            return biz_order_id
        else:
            if "满房" in res_json['data']['message']:
                return "满房"
            elif "比价" in res_json['data']['message']:
                return "变价"
            return None
    else:
        return None


def cancel_order(device_id, biz_order_id):
    """
    取消订单
    :param device_id:
    :return:
    """
    url = "http://192.168.52.112:8083/fliggy/cancelorder"
    payload = {
        "biz_order_id": biz_order_id,
        "device_id": device_id,
    }
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json['status'] is True:
        status = res_json['data']['status']
        if status is True:
            return True
        else:
            return False
    else:
        return False


def edit_change_full(change_status, full_status, bg_order_id):
    """
    更新变价满房状态
    :return:
    """
    url = settings.ADMIN_URL + "/hotel/bgorder/editChangePrieOrFullBySystem"
    payload = {"changeStatus": change_status, "fullStatus": full_status, "bgOrderId": bg_order_id}
    response = requests.request("POST", url, data=payload)
    res_json = json.loads(response.text)
    logging.info('[{}]更新了变价满房状态, res: {}'.format(bg_order_id, str(res_json)))
    return res_json


# order创建订单
def order_create_order(bg_order_id, sorder_id, device_id):
    """
    order 补录订单
    :return: 成功，失败
    """
    url = settings.ADMIN_URL + "/hotel/bgorder/getOrderItemAndSnapshoot"
    payload = {
        "bgOrderId": bg_order_id,
    }
    response = requests.request("GET", url, params=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        payload = res_json['result']
        url = settings.ADMIN_URL + "/hotel/sorder/createSOrderBySystem"
        payload["sOrderId"] = sorder_id
        payload["bgOrderId"] = bg_order_id
        payload["supplierId"] = 10002
        payload["remark"] = "机器下单"
        payload["operator"] = device_id
        payload["productItem"] = "机器补录"
        payload["payType"] = 1
        payload["brokerage"] = 0
        payload["paymentTransactionVO"] = {
            "sOrderId": sorder_id,
            "bgOrderId": bg_order_id,
            "orderStatus": payload['orderStatus'],
            "payType": 1,
            "payTime": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        }
        response = requests.request("POST", url, json=payload)
        res_json = json.loads(response.text)
        if res_json.get("code") == 200:
            if res_json['success'] is True:
                return True
            else:
                return False
        else:
            return False
