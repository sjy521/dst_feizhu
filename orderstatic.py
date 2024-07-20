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

def send_pay_order_for_dingding(text, atphone=None):
    url ="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=92c89055-3410-4824-9b4b-c0ea17412464"
    headers = {
        'Content-Type': "application/json;charset=UTF-8",
    }
    data = {
        'msgtype': "text",
        'text':{
            "content":text,
            "mentioned_list":[],
        }
    }
    r= requests.post(url, headers=headers, json=data)
    res_json = json.loads(r.text)
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
                        if (value == '20001'):
                            message += "去哪儿阿信："
                        if (value == '20002'):
                            message += "美团："
                        if (value == '20003'):
                            message += "飞猪："
                        if (value == '20004'):
                            message += "去哪儿："
                        if (value == '20005'):
                            message += "携程："
                        if (value == '20006'):
                            message += "百度："
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
                        if (value == '20001'):
                            message += "去哪儿阿信确认订单："
                        if (value == '20002'):
                            message += "美团确认订单："
                        if (value == '20003'):
                            message += "飞猪确认订单："
                        if (value == '20004'):
                            message += "去哪儿四海通确认订单："
                        if (value == '20005'):
                            message += "携程确认订单："
                        if (value == '20006'):
                            message += "百度确认订单："
                    if (column == 'count(*)'):
                        message += str(value) + "\n"
                        confirm += int(value)
            message += "总确认订单数：" + str(confirm) + "\n\n" + "售前利润：\n"

            cursor.execute(
                "SELECT bg.distributor_id,CASE 	WHEN bg.distributor_id=20003 THEN 		sum(bg.seller_price*0.9-bg.price) 	WHEN bg.supplier_id=10004 THEN 		sum(bg.seller_price-(so.price-so.brokerage)) 	ELSE 		sum(bg.seller_price-bg.price) END as profit from db_bg_order bg,db_supplier_order so where bg.bg_order_id=so.bg_order_id and bg.create_time>DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00')  and bg.create_time<NOW() and bg.order_status=11 GROUP BY bg.distributor_id;")
            record = cursor.fetchall()
            for row in record:
                for column, value in row.items():
                    if (column == 'distributor_id'):
                        if (value == '20001'):
                            message += "去哪儿阿信售前利润："
                        if (value == '20002'):
                            message += "美团售前利润："
                        if (value == '20003'):
                            message += "飞猪售前利润："
                        if (value == '20004'):
                            message += "去哪儿四海通售前利润："
                        if (value == '20005'):
                            message += "携程售前利润："
                        if (value == '20006'):
                            message += "百度售前利润："
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
                            message += "飞猪四海通销售额："
                    if (column == 'price'):
                        message += str("%.2f" % (float(value) / 100)) + "\n"
                        message += "飞猪四海通佣金：" + str(
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
# scheduler.every().hour.do(job)

# while True:
# scheduler.run_pending()
# time.sleep(1)
if __name__ == '__main__':
    job()