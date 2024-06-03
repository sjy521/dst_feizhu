import requests
import json
import pandas
import sys
import datetime
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from util.orders_util import get_all_device


def get_all_order_info(device_id):
    global all_order
    page = 1
    while True:
        try:
            url = "http://build-order.bingotravel.com.cn/fliggy/orderlist?device_id={}&page={}".format(device_id, page)
            payload = ""
            headers = {
                'cache-control': "no-cache",
                'Postman-Token': "9fd8ea5a-bd43-4cbb-b3cb-097a7a143c53"
            }
            response = requests.request("GET", url, data=payload, headers=headers)
            res_json = json.loads(response.text)
            if len(res_json['data']['order_list']) > 0:
                all_order += res_json['data']['order_list']
            else:
                print(res_json)
                break
            if res_json['data']['order_list'][0]['order_time'] is not None:
                if res_json['data']['order_list'][0]["order_time"] < "{} 00:00:00".format((datetime.datetime.now()- datetime.timedelta(days=3)).date().strftime('%Y-%m-%d')):
                    print('到达指定时间')
                    break
            print(page, len(all_order))
            page += 1
        except Exception as f:
            continue


def getapplyinvoice(device_id):
    for i, order in enumerate(all_order):
        print(i, order)
        if order['status_value'] == "已完成":
            url = "http://build-order.bingotravel.com.cn/fliggy/getapplyinvoice?orderId={}&device_id={}".format(order['biz_order_id'], device_id)

            payload = ""
            headers = {
                'cache-control': "no-cache",
                'Postman-Token': "9fd8ea5a-bd43-4cbb-b3cb-097a7a143c53"
            }

            response = requests.request("GET", url, data=payload, headers=headers)

            res_json = json.loads(response.text)
            try:
                order["是否可以开发票"] = res_json['data']
            except:
                continue


def invoice(device_id):
    for i in range(len(all_order)):
        try:
            if all_order[i]['status_value'] == '已完成':
                if all_order[i]['invoice']:
                    url = "http://build-order.bingotravel.com.cn/fliggy/invoice?orderId={}&device_id={}".format(
                        all_order[i]['biz_order_id'], device_id)
                    print(url)
                    headers = {
                        'cache-control': "no-cache",
                        'Postman-Token': "9fd8ea5a-bd43-4cbb-b3cb-097a7a143c53"
                    }
                    response = requests.request("GET", url, headers=headers)
                    print(response.text)
                    res1_json = json.loads(response.text)
                    if res1_json['data'] != "false":
                        all_order[i]['已开发票'] = True

        except:
            print(all_order[i]['biz_order_id'])
            continue


if __name__ == '__main__':
    # args = sys.argv
    # device_id = args[0]
    # all_order = []
    # errorlist = []
    # all_device = get_all_device()
    # for res in all_device:
    #     if res.get("deviceId") == device_id:
    #         device_name = res.get("deviceName")
    #         file_name = "{} {}发票记录.csv".format(datetime.datetime.now().date().strftime('%Y-%m-%d'), device_name)
    #         get_all_order_info(device_id)
    #         getapplyinvoice(device_id)
    #         invoice(device_id)
    #         for i in all_order:
    #             print(i)
    #             i['biz_order_id'] = "'" + i['biz_order_id']
    #         pandas.DataFrame(all_order).to_csv("./{}.csv".format(file_name))
    args = sys.argv
    print(args[0])
    aa = [{"a": "a"}, {"b": "b"}]
    pandas.DataFrame(aa).to_csv("./测试.csv")

