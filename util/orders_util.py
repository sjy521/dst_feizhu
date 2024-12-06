import datetime
import os
import requests
import json
import logging
import random
import sys
from dynaconf import settings

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from log_model.set_log import setup_logging
from util.ding_util import send_pay_order_for_dingding, send_abnormal_alarm_for_dingding

setup_logging(default_path=settings.LOGGING)


# 查询可用的设备
def get_effective_device(tar_device_id=None):
    """
    从数据库查询可用且空闲的device_id
    :return: device_id
    """
    device_id_list = []
    url = settings.ADMIN_URL81 + "/library/all/libraries"
    response = requests.request("GET", url)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        results = res_json.get("result")
        if tar_device_id is not None:
            for result in results:
                if result.get("deviceId") == tar_device_id:
                    if result.get('isEnable') == "1" and int(result.get('isBusy')) < 1:
                        # if result.get(""):
                        #     return result
                        device_id_list.append(result)
        else:
            for result in results:
                if result.get('isEnable') == "1" and int(result.get('isBusy')) < 1:
                    # if result.get(""):
                    #     return result
                    device_id_list.append(result)
    if len(device_id_list) > 0:
        return random.choices(device_id_list)[0]
    else:
        return None


def get_all_device():
    """
    从数据库查询所有
    :return: device_id
    """
    url = settings.ADMIN_URL81 + "/library/all/libraries"
    response = requests.request("GET", url)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        results = res_json.get("result")
        return results
    else:
        return None


# 设置正在抓取的cookie的设备
def set_get_cookie_device(device_id, cookie=None, x5sec=None):
    """
    从数据库更新的device_id为不可用或不空闲
    :return: device_id
    """
    url = settings.ADMIN_URL81 + "/library/update/library"
    if cookie is not None:
        payload = {"deviceId": device_id,
                   "cookie2": cookie,
                   "backUp": x5sec,
                   "getCookie": "0",
                   "isMyCookie": "0"
                   }
    else:
        payload = {"deviceId": device_id,
                   "isMyCookie": "1",
                   }
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        logging.info("数据库更新成功, result: {}".format(str(res_json)))
        return True
    logging.info("数据库更新失败, result: {}".format(str(res_json)))
    return False


# 设置不可用的设备
def set_not_effective_device(device_id, is_enable, is_busy):
    """
    从数据库更新的device_id为不可用或不空闲
    :return: device_id
    """
    url = settings.ADMIN_URL81 + "/library/update/library"
    if is_enable == "":
        payload = {"deviceId": device_id,
                   "isBusy": is_busy
                   }
    else:
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
def get_effective_order(device_id, error_list, device_name, delay_num):
    """
    查询有效订单，并锁单
    :return: bgorderid
    """
    url = settings.ADMIN_URL + "/hotel/bgorder/getNoReadyOrderByPage"
    payload = {"pageNum": 1, "pageSize": 30, "param": {}}
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        results = res_json.get("result")
        if len(results.get("rows")) > int(delay_num):
            for _ in range(len(results.get("rows")) - 1, -1, -1):
                # result = random.choices(results.get("rows"))[0]
                result = results.get("rows")[_]
                if result.get("source") != "10002":
                    continue
                order_data = {
                    "bg_order_id": result.get("bgOrderId"),
                    "d_ordr_id": result.get("dorderId"),
                    "hotel_id": result.get("hotelId"),
                    "product_id": result.get("productId"),
                    "check_in": result.get("checkInTime"),
                    "check_out": result.get("checkOutTime")
                }
                # 加锁
                url = settings.ADMIN_URL + "/hotel/bgorder/lockBySystem"
                querystring = {"orderId": order_data['bg_order_id'], "userName": device_name}
                order_response = requests.request("GET", url, params=querystring)
                order_res_json = json.loads(order_response.text)
                if order_res_json['result']['islock'] is True:
                    return order_data
                else:
                    logging.info("bgorderid: {}, result: {}".format(order_data['bg_order_id'], str(order_res_json)))
    return None


# 查询变价满房有效订单，并锁单
def get_abnormal_effective_order(device_id, error_list, device_name):
    """
    查询有效订单，并锁单
    :return: bgorderid
    """
    url = settings.ADMIN_URL + "/hotel/bgorder/getChangeOrderByPage"
    payload = {"pageNum": 1, "pageSize": 20, "param": {}}
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        results = res_json.get("result")
        if len(results.get("rows")) > 0:
            result = random.choices(results.get("rows"))[0]
            if result.get("source") != "10002":
                return None
            bg_order_id = result.get("bgOrderId")
            if bg_order_id in error_list:
                return None
            d_ordr_id = result.get("dorderId")
            # 加锁
            url = settings.ADMIN_URL + "/hotel/bgorder/lockBySystem"
            querystring = {"orderId": bg_order_id, "userName": device_name}
            order_response = requests.request("GET", url, params=querystring)
            order_res_json = json.loads(order_response.text)
            if order_res_json['result']['islock'] is True:
                return [d_ordr_id, bg_order_id]
            else:
                logging.info("bgorderid: {}, result: {}".format(bg_order_id, str(order_res_json)))
    return None


# 订单备注更新并解锁
def fail_order_unlock(change_status, full_status, bg_order_id, device_id, device_name):
    """
    订单解锁，订单通知失败
    :param change_status:
    :param bg_order_id:
    :param full_status:
    :param device_id:
    :return: true，false
    """
    if full_status == 2:
        url = settings.ADMIN_URL + "/hotel/bgorder/editTimeOutBySystem"
        payload = {"timeOutStatus": 1, "bgOrderId": bg_order_id}
    else:
        url = settings.ADMIN_URL + "/hotel/bgorder/editChangePrieOrFullBySystem"
        payload = {"changeStatus": change_status, "fullStatus": full_status, "bgOrderId": bg_order_id}
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    logging.info('[{}]更新了变价满房状态, res: {}'.format(bg_order_id, str(res_json)))
    unlock(bg_order_id, device_name)


# 订单解锁
def unlock(bg_order_id, device_name):
    url = settings.ADMIN_URL + "/hotel/bgorder/unlockBySystem"
    querystring = {"orderId": bg_order_id, "userName": device_name}
    response = requests.request("GET", url, params=querystring)
    order_res_json = json.loads(response.text)
    if order_res_json['result'] is True:
        logging.info("bgorderid: {}，通知解锁result: {}".format(bg_order_id, str(order_res_json)))
    else:
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
            "guest_list": [order_item.get("consumerName")],
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
def build_order(device_id, tar_json, phone):
    """
    创建订单
    :param device_id:
    :return:  成功，变价，满房，失败
    """
    url = "http://127.0.0.1:8083/fliggy/buildorder"
    # url = "http://build-order.bingotravel.com.cn/fliggy/buildorder"
    payload = {
        "wx_link": tar_json['wx_link'],
        "sr_name": tar_json['sr_name'],
        "contact_phone": phone,
        "guest_list": tar_json['guest_list'],
        "check_in": tar_json['check_in'],
        "check_out": tar_json['check_out'],
        "price": tar_json['price'],
        "device_id": device_id,
    }
    response = requests.request("POST", url, json=payload, timeout=120)
    res_json = json.loads(response.text)
    if res_json['status'] is True:
        status = res_json['data']['status']
        if status is True:
            biz_order_id = res_json['data']['biz_order_id']
            price = res_json['data']['price']
            return [biz_order_id, price]
        else:
            if "满房" in res_json['data']['message']:
                return "满房"
            elif "比价" in res_json['data']['message']:
                return "变价"
            elif "下单重复" in res_json['data']['message']:
                return "下单重复"
            return None
    else:
        return None


def handle_mt_full(build_order_res):
    url = "http://spa.bingotravel.com.cn/client/spa/handleMtFull"
    payload = {
        "checkIn": build_order_res['check_in'],
        "checkOut": build_order_res['check_out'],
        "hotelId": build_order_res['hotel_id'],
        "productId": build_order_res['product_id'],
        "supplierId": 10002
    }
    response = requests.request("POST", url, json=payload, timeout=120)
    res_json = json.loads(response.text)
    logging.info("拉黑酒店：param:[{}], res: [{}]".format(payload, res_json))
    return True


def cancel_order(device_id, biz_order_id):
    """
    取消订单
    :param device_id:
    :return:
    """
    # url = "http://192.168.52.112:8083/fliggy/cancelorder"
    url = "http://build-order.bingotravel.com.cn/fliggy/cancelorder"
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
            send_pay_order_for_dingding("！！！{}有取消失败的订单：{}: ，请人工取消！！！".format(device_id, biz_order_id))
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
def order_create_order(bg_order_id, sorder_id, price, device_id):
    """
    order 补录订单
    :return: 成功，失败
    """
    url = settings.ADMIN_URL + "/hotel/bgorder/deleteFlagBySystem"
    payload = {
        "bgOrderId": bg_order_id,
    }
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        pass
    else:
        send_abnormal_alarm_for_dingding("状态更新失败：{}".format(sorder_id))
    url = settings.ADMIN_URL + "/hotel/bgorder/getOrderItemAndSnapshoot"
    payload = {
        "bgOrderId": bg_order_id,
    }
    response = requests.request("GET", url, params=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        payload = res_json['result']
        order_item = payload['orderItemVO']
        url = settings.ADMIN_URL + "/hotel/sorder/createSOrderBySystem"
        payload["sOrderId"] = sorder_id
        payload["bgOrderId"] = bg_order_id
        payload["supplierId"] = 10002
        payload["orderStatus"] = 10
        payload["remark"] = "机器下单"
        payload["operator"] = device_id
        payload["productItem"] = "机器补录"
        payload["payType"] = 1
        payload["brokerage"] = 0
        payload["price"] = price
        payload["orderItemVO"] = {
            "hotelName": order_item.get("hotelName"),
            "productId": 0,
            "orderId": None,
            "source": None,
            "roomCount": order_item.get("roomCount"),
            "productName": order_item.get("productName"),
            "consumerName": order_item.get("consumerName"),
            "consumerPhone": order_item.get("consumerPhone"),
            "idCard": None,
            "contact": order_item.get("contact"),
            "refundRule": order_item.get("refundRule"),
            "operator": None,
            "createTime": None,
            "updateTime": None
        }
        payload["paymentTransactionVO"] = {
            "sOrderId": sorder_id,
            "bgOrderId": bg_order_id,
            "orderStatus": 10,
            "payType": 1,
            "payTime": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        }
        payload["id"] = None
        response = requests.request("POST", url, json=payload)
        res_json = json.loads(response.text)
        logging.info("[{}]补录: [{}]".format(bg_order_id, str(res_json)))
        if res_json.get("code") == 200:
            if res_json['success'] is True:
                return True
            else:
                return False
        else:
            return False


def build_error_warn(devices_error_count, device_name, device_id):
    if devices_error_count[device_name] >= 10:
        set_not_effective_device(device_id, 0, 0)
        send_pay_order_for_dingding("{}: 账号可能出现问题，点开一家酒店核验查看".format(device_name))
        devices_error_count[device_name] = 0
        return True
    devices_error_count[device_name] += 1


# 以下是混投的相关订单接口
def get_hybridization_order(device_name, delay_num):
    url = settings.ADMIN_URL + "/hotel/bgorder/getMixedNoReadyOrderByPage"
    payload = {"pageNum": 1, "pageSize": 30, "param": {}}
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        results = res_json.get("result")
        if len(results.get("rows")) > int(delay_num):
            for _ in range(len(results.get("rows")) - 1, -1, -1):
                result = results.get("rows")[_]
                # if result.get("bgOrderId") != 241023626668:
                #     continue
                if result.get("source") != "10004":
                    return None
                # 初始化定义包含所有字段的第一个JSON
                original_json = {
                    "sOrderId": None,
                    "bgOrderId": None,
                    "supplierId": None,
                    "hotelId": None,
                    "checkInTime": None,
                    "checkOutTime": None,
                    "orderStatus": None,
                    "failResult": None,
                    "price": None,
                    "sellerPrice": None,
                    "brokerage": None,
                    "payType": None,
                    "remark": None,
                    "finish": None,
                    "operator": None,
                    "productItem": {
                        "supplierProductId": None,
                        "supplierHotelId": None,
                        "name": None,
                        "totalPrice": None,
                        "sellerPrice": None,
                        "maxOccupancy": None,
                        "isBreakfast": None,
                        "breakfast": None,
                        "isRefund": None,
                        "remarks": None,
                        "qrCodeUrl": None,
                        "createKey": None,
                        "subPrice": None,
                        "initialTotalPrice": None,
                        "promotionTotalPrice": None,
                        "supplierId": None
                    },
                    "orderItemVO": {
                        "productId": None,
                        "orderId": None,
                        "hotelName": None,
                        "productName": None,
                        "roomCount": None,
                        "consumerName": None,
                        "consumerPhone": None,
                        "idCard": None,
                        "contact": None,
                        "refundRule": None
                    },
                    "paymentTransactionVO": {
                        "serialNum": None,
                        "serialOrderId": None,
                        "payChannel": None,
                        "payType": None,
                        "payPrice": None,
                        "commission": None,
                        "payTime": None,
                        "remark": None,
                        "orderStatus": None
                    }
                }

                order_data = update_json(original_json, result)
                # 加锁
                order_data['sOrderId'] = result.get("sorderId")
                url = settings.ADMIN_URL + "/hotel/bgorder/lockBySystem"
                querystring = {"orderId": order_data['bgOrderId'], "userName": device_name}
                order_response = requests.request("GET", url, params=querystring)
                order_res_json = json.loads(order_response.text)
                if order_res_json['result']['islock'] is True:
                    order_data, state = get_bgproduct_id(original_json, result.get("distributorId"))
                    d_order_id = result.get("dorderId")
                    return order_data, d_order_id, state
                else:
                    logging.info("bgorderid: {}, result: {}".format(order_data['bgOrderId'], str(order_res_json)))
    return None, None, None


def update_json(original, new):
    for key in original:
        # 如果是嵌套字典，递归处理
        if isinstance(original[key], dict):
            update_json(original[key], new)
        # 如果是JSON字符串格式的嵌套对象，先转换为字典
        elif isinstance(original[key], str) and original[key].startswith("{") and original[key].endswith("}"):
            original_json_obj = json.loads(original[key])
            new_json_obj = json.loads(new.get(key, "{}"))
            update_json(original_json_obj, new_json_obj)
            original[key] = json.dumps(original_json_obj)
        else:
            # 更新普通字段
            original[key] = new.get(key, None)
    return original


def get_bgproduct_id(order_data, distributor_id):
    url = settings.SPA_URL + "/hotel/v1.0/axin/getCpsInfoByAxinProductId"
    payload = {"distributorId": distributor_id, "bgProductId": order_data['orderItemVO']['productId'], "bgHotelId": order_data['hotelId']}
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json.get("result"):
        result = res_json.get("result")
        order_data['productItem']['supplierProductId'] = result.get("cpsProductId")
        order_data['productItem']['supplierHotelId'] = result.get("cpsHotelId")
        order_data['productItem']['productId'] = result.get("cpsToBgProductId")
        order_data['productItem']['name'] = order_data.get("productName")
        return order_data, 1
    else:
        return order_data, 0


def hybridization_create_order(order_data, bg_order_id, sorder_id, price, device_id, supplier_id):
    """
    order 混投补录订单
    :return: 成功，失败
    """
    if supplier_id == '10002':
        url = settings.ADMIN_URL + "/hotel/bgorder/getOrderItemAndSnapshoot"
        payload = {
            "bgOrderId": bg_order_id,
        }
        response = requests.request("GET", url, params=payload)
        res_json = json.loads(response.text)
        if res_json.get("code") == 200:
            result = res_json['result']
            productItem = json.loads(result['snapshootVOList'][-1]['productItem'])

            order_data['productItem']['isBreakfast'] = productItem['isBreakfast']
            order_data['productItem']['breakfast'] = productItem['breakfast']
            order_data['productItem']['qrCodeUrl'] = productItem['qrCodeUrl']

            url = settings.ADMIN_URL + "/hotel/sorder/convertSorderInfoByRobot"
            order_data['sOrderId'] = sorder_id
            order_data['productItem']['totalPrice'] = price
            order_data['productItem']['supplierId'] = supplier_id
            order_data['remark'] = "机器补录"
            order_data['orderItemVO']['productId'] = order_data['productItem']['productId']
            order_data['productItem'].pop('productId')
            order_data['productItem'] = json.dumps(order_data['productItem'])
    else:
        url = settings.ADMIN_URL + "/hotel/sorder/createSOrderBySystem"
        order_data['productItem'] = "机器补录"
        order_data['remark'] = "阿信支付"
    order_data["payType"] = 1
    order_data["brokerage"] = 0
    order_data["orderStatus"] = 10
    order_data['checkInTime'] = order_data['checkInTime'] + " 00:00:00"
    order_data['checkOutTime'] = order_data['checkOutTime'] + " 00:00:00"
    order_data['supplierId'] = supplier_id
    order_data['operator'] = device_id
    order_data["paymentTransactionVO"] = {
        "sOrderId": order_data['sOrderId'],
        "bgOrderId": bg_order_id,
        "orderStatus": 10,
        "payType": 1,
        "payTime": str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    }
    response = requests.request("POST", url, json=order_data)
    res_json = json.loads(response.text)
    logging.info("[{}]补录: [{}]".format(bg_order_id, str(res_json)))
    if res_json.get("code") == 200:
        if res_json['success'] is True:
            return True
        else:
            return False
    else:
        return False


def pay_axin(s_order_id):
    url = settings.SPA_URL + "/hotel/v1.0/axin/axinPayBySorderId"
    payload = {
        "sOrderId": s_order_id,
    }
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json:
        return 1
    else:
        return 0

