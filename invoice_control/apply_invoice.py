import requests
import json
import pandas
import sys
import datetime
import os

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from util.orders_util import get_all_device
from util.ding_util import send_abnormal_alarm_for_dingding, send_pay_order_for_dingding


def get_all_order_info(device_id):
    global all_order
    errorpage = 0
    page = 120
    exceed_time_num = 20
    while page < 1000:
        try:
            url = "http://192.168.111.66:8083/fliggy/orderlist?device_id={}&page={}".format(device_id, page)
            payload = ""
            headers = {
                'cache-control': "no-cache",
                'Postman-Token': "9fd8ea5a-bd43-4cbb-b3cb-097a7a143c53"
            }
            response = requests.request("GET", url, data=payload, headers=headers)
            res_json = json.loads(response.text)
            for res_data in res_json['data']['order_list']:
                if res_data['order_time'] is not None:
                    if res_data['order_time'] < "{} 00:00:00".format(
                            (datetime.datetime.now() - datetime.timedelta(days=7)).date().strftime('%Y-%m-%d')):
                        exceed_time_num -= 1
                        if exceed_time_num <= 0:
                            print('到达指定时间')
                            return True
                    elif res_data['order_time'] > "{} 00:00:00".format(
                            (datetime.datetime.now() - datetime.timedelta(days=6)).date().strftime('%Y-%m-%d')):
                        continue
                    else:
                        all_order.append(res_data)
            print(page, len(all_order))
            page += 1
        except Exception as f:
            errorpage += 1
            if errorpage >=10:
                break
            continue


def getapplyinvoice(device_id):
    for i, order in enumerate(all_order):
        print(i, order)
        if order['status_value'] == "已完成":
            url = "http://192.168.111.66:8083/fliggy/getapplyinvoice?orderId={}&device_id={}".format(
                order['biz_order_id'], device_id)

            payload = ""
            headers = {
                'cache-control': "no-cache",
                'Postman-Token': "9fd8ea5a-bd43-4cbb-b3cb-097a7a143c53"
            }

            response = requests.request("GET", url, data=payload, headers=headers)

            res_json = json.loads(response.text)
            try:
                order["是否可以开发票"] = res_json['data']
                order["已开发票"] = False
            except:
                continue


def invoice(device_id):
    for i in range(len(all_order)):
        try:
            if all_order[i]['status_value'] == '已完成':
                if all_order[i]['是否可以开发票']:
                    url = "http://192.168.111.66:8083/fliggy/invoice?orderId={}&device_id={}".format(
                        all_order[i]['biz_order_id'], device_id)
                    print(url)
                    headers = {
                        'cache-control': "no-cache",
                        'Postman-Token': "9fd8ea5a-bd43-4cbb-b3cb-097a7a143c53"
                    }
                    response = requests.request("GET", url, headers=headers)
                    res1_json = json.loads(response.text)
                    if res1_json['data'] != "false":
                        all_order[i]['已开发票'] = True

        except:
            print(all_order[i]['biz_order_id'])
            continue


if __name__ == '__main__':
    args = sys.argv
    device_id = args[1]
    all_order = []
    errorlist = []
    all_device = get_all_device()
    for res in all_device:
        if res.get("deviceId") == device_id:
            device_name = res.get("deviceName")
            file_name = "{}{}发票记录".format((datetime.datetime.now() - datetime.timedelta(days=7)).date().strftime('%Y-%m-%d'), device_name)
            # file_name = "{}{}发票记录".format("2024-05-27-2024-06-02", device_name)
            get_all_order_info(device_id)
            getapplyinvoice(device_id)
            invoice(device_id)
            if len(all_order) != 0:
                for i in all_order:
                    i['biz_order_id'] = "'" + i['biz_order_id']
                pandas.DataFrame(all_order).to_csv(
                    "/root/bgProjects/fliggy-mobile-control/invoice_control/{}.csv".format(file_name))
                send_pay_order_for_dingding(
                    "{}:开发票任务结束，下载链接: {}".format(device_name, "http://192.168.1.116:8084/download/{}".format(file_name)), ["18501953880", "13520735673", "13474763052", "18911137911"])
    # args = sys.argv
    # print(args[0])
    # print("===")
    # print(args)
    # aa = [{"a": "a"}, {"b": "b"}]
    # pandas.DataFrame(aa).to_csv("./测试.csv")
