import base64
import hashlib
from sched import scheduler
import hmac
import json
import urllib.parse
import requests
import mysql.connector
from mysql.connector import Error
from decimal import Decimal
import time


def get_ding_pay_url():
    timestamp = str(round(time.time() * 1000))
    secret = "SEC90d9680ab0c7e1fae4ec8dbaa23b94af5c412e93f1031ed15a043bf93dff3b09"
    access_token = "36f21a1ff5e7dbf329454965d11d4f6ede771cfc0137676b470c2bd773154f96"
    secret_enc = secret.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(access_token, timestamp,
                                                                                             sign)
    return url


def send_pay_order_for_dingding(text, atphone=None):
    if atphone is not None:
        atMobiles = atphone
    else:
        atMobiles = []
    url = get_ding_pay_url()
    data = {
        "at": {
            "atMobiles": atMobiles,
            "isAtAll": False
        },
        "text": {
            "content": text
        },
        "msgtype": "text"
    }
    res = requests.post(url, json=data)
    res_json = json.loads(res.text)
    return res_json.get("errmsg")


def orderstatic():
    message = "当日订单统计：\n"
    totalCount = 0
    confirm = 0
    totalPofit = 0.0
    fliggyPrice = 0
    try:
        connection = mysql.connector.connect(
            host='pc-2ze1l4f34v5ql1rsu.rwlb.rds.aliyuncs.com',
            database='hotel_order',
            user='order_db_user',
            password='i7Nbreoq%vMJYbX0b'
        )
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT distributor_id,count(*) from db_bg_order where create_time>DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00') and create_time<NOW()  GROUP BY distributor_id;")
            record = cursor.fetchall()
            for row in record:
                for column, value in row.items():
                    if (column == 'distributor_id'):
                        if (value == '20002'):
                            message += "美团："
                        if (value == '20003'):
                            message += "飞猪："
                        if (value == '20004'):
                            message += "去哪儿："
                        if (value == '20005'):
                            message += "携程："
                    if (column == 'count(*)'):
                        message += str(value) + "\n"
                        totalCount += int(value)
            message += "总订单数：" + str(totalCount) + "\n\n" + "确认订单：\n"
            cursor.execute(
                "SELECT distributor_id,count(*) from db_bg_order where create_time>DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00') and order_status=11 and create_time<NOW()  GROUP BY distributor_id;")
            record = cursor.fetchall()
            for row in record:
                for column, value in row.items():
                    if (column == 'distributor_id'):
                        if (value == '20002'):
                            message += "美团确认订单："
                        if (value == '20003'):
                            message += "飞猪确认订单："
                        if (value == '20004'):
                            message += "去哪儿确认订单："
                        if (value == '20005'):
                            message += "携程确认订单："
                    if (column == 'count(*)'):
                        message += str(value) + "\n"
                        confirm += int(value)
            message += "总确认订单数：" + str(confirm) + "\n\n" + "售前利润：\n"

            cursor.execute(
                "SELECT distributor_id,sum(seller_price-price) as profit from db_bg_order where create_time>DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00') and create_time<NOW() and order_status=11 GROUP BY distributor_id;")
            record = cursor.fetchall()
            for row in record:
                for column, value in row.items():
                    if (column == 'distributor_id'):
                        if (value == '20002'):
                            message += "美团售前利润："
                        if (value == '20003'):
                            message += "飞猪售前利润："
                        if (value == '20004'):
                            message += "去哪儿售前利润："
                        if (value == '20005'):
                            message += "携程售前利润："
                    if (column == 'profit'):
                        message += str("%.2f" % (float(value) / 100)) + "\n"
                        totalPofit += float("%.2f" % (float(value) / 100))
            message += "总售前利润：" + str(float("%.2f" % totalPofit)) + "\n\n销售额：\n"

            cursor.execute(
                "SELECT supplier_id,sum(price) as price from db_bg_order where create_time>DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00') and create_time<NOW() and order_status=11 and supplier_id=10002 GROUP BY supplier_id;")
            record = cursor.fetchall()
            for row in record:
                for column, value in row.items():
                    if (column == 'supplier_id'):
                        if (value == '10002'):
                            message += "飞猪销售额："
                    if (column == 'price'):
                        message += str("%.2f" % (float(value) / 100)) + "\n"
                        message += "飞猪佣金：" + str(
                            (Decimal(value * Decimal(0.045)) / 100).quantize(Decimal('0.01'))) + "\n\n"

            cursor.execute(
                "SELECT count(*) as hourOrder from db_bg_order where create_time>CONCAT(DATE_FORMAT(NOW(), '%Y-%m-%d %H:'), '00')and create_time<CONCAT(DATE_FORMAT(NOW(), '%Y-%m-%d %H:'), '59');")
            record = cursor.fetchall()
            for row in record:
                for column, value in row.items():
                    message += "一小时进单数：" + str(value)

            print(message)  # 输出空行以区分不同的行
            send_pay_order_for_dingding(message)
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    except Error as e:
        print("Error while connecting to MySQL", e)


def job():
    print("任务执行中...")
    orderstatic()
    print("任务执行完成")


# 每小时执行一次任务
scheduler.every().hour.do(job)

while True:
    scheduler.run_pending()
    time.sleep(1)
