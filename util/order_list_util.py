import requests
import json
import sys
import os
import logging
from dynaconf import settings
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from log_model.set_log import setup_logging
setup_logging(default_path=settings.LOGGING)


def order_list(device_id):
    url = "http://127.0.0.1:8083/fliggy/orderlist?device_id={}&page=1".format(device_id)
    payload = ""
    headers = {
        'cache-control': "no-cache",
        'Postman-Token': "9fd8ea5a-bd43-4cbb-b3cb-097a7a143c53"
    }
    response = requests.request("GET", url, data=payload, headers=headers)
    res_json = json.loads(response.text)
    order_info = res_json['data']['order_list'][0]
    print(order_info)
    return order_info


def check_order(device_id, tar_sr_name, tar_price):
    res = {}
    for i in range(2):
        order_info = order_list(device_id)
        biz_order_id = order_info.get("biz_order_id")
        sr_name = order_info.get("sr_name")
        price = order_info.get("price")
        print(sr_name, tar_sr_name)
        if sr_name is not None:
            print(sr_name, tar_sr_name)
            if sr_name == tar_sr_name:
                select_order = get_bongo_order(biz_order_id)
                logging.info("超时校验, 目标房型:{} 价格:{}, 下单房型:{} 价格:{} 秉功查询:{}".format(tar_sr_name, tar_price, sr_name, price, select_order))
                print("超时校验, 目标房型:{} 价格:{}, 下单房型:{} 价格:{} 秉功查询:{}".format(tar_sr_name, tar_price, sr_name, price, select_order))
                if select_order is False:
                    res['biz_order_id'] = biz_order_id
                    res['price'] = price
                    return res
                else:
                    continue
            else:
                return res
    return res


def get_bongo_order(sorder_id):
    url = settings.ADMIN_URL + "/hotel/bgorder/getBingoOrderByPage"
    payload = {"pageNum": 1, "pageSize": 10, "param": {"sOrderId": sorder_id}}
    response = requests.request("POST", url, json=payload)
    res_json = json.loads(response.text)
    if res_json.get("code") == 200:
        results = res_json.get("result")
        if len(results.get("rows")) > 0:
            return True
        else:
            return False
    return None


# if __name__ == '__main__':
#     device_id = "HYT4897HSSAUZLNZ"
#     tar_sr_name = "特惠电竞大床房"
#     tar_price = "16800"
#     print(check_order(device_id, tar_sr_name, tar_price))