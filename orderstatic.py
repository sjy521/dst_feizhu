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
                        if (value == '30004'):
                            message += "同程商旅："
                        if (value == '20007'):
                            message += "同程艺龙："
                        if (value == '20008'):
                            message += "去哪儿缤果："
                        if (value == '20009'):
                            message += "抖音："
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
                        if (value == '30004'):
                            message += "同程商旅确认订单："
                        if (value == '20007'):
                            message += "同程艺龙确认订单："
                        if (value == '20008'):
                            message += "去哪儿缤果确认订单："
                        if (value == '20009'):
                            message += "抖音确认订单："
                    if (column == 'count(*)'):
                        message += str(value) + "\n"
                        confirm += int(value)
            message += "总确认订单数：" + str(confirm) + "\n\n" + "售前利润：\n"

            cursor.execute(
                "SELECT     bg.distributor_id,    SUM(CASE         WHEN bg.distributor_id = 20003 THEN bg.seller_price * 0.9 - bg.price        WHEN bg.supplier_id = 10004 THEN bg.seller_price - (so.price - so.brokerage)        ELSE bg.seller_price - bg.price    END) as profit,    SUM(CASE         WHEN bg.distributor_id = 20003 THEN bg.seller_price * 0.9 - bg.price        WHEN bg.supplier_id = 10004 THEN bg.seller_price - (so.price - so.brokerage)        ELSE bg.seller_price - bg.price    END) as totalprofit FROM db_bg_order bg INNER JOIN (    SELECT bg_order_id, price, brokerage    FROM (        SELECT bg_order_id, price, brokerage,               ROW_NUMBER() OVER (PARTITION BY bg_order_id ORDER BY create_time DESC) as rn        FROM db_supplier_order        WHERE order_status = 11    ) t    WHERE rn = 1) so ON bg.bg_order_id = so.bg_order_id WHERE bg.create_time >= DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00')  AND bg.create_time < NOW()  AND bg.order_status = 11 GROUP BY bg.distributor_id;")
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
                        if (value == '30004'):
                            message += "同程商旅售前利润："
                        if (value == '20007'):
                            message += "同程艺龙售前利润："
                        if (value == '20008'):
                            message += "去哪儿缤果售前利润："
                        if (value == '20009'):
                            message += "抖音售前利润："
                    if (column == 'totalprofit'):
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
                    message += "一小时进单数：" + str(value) +"\n\n"
            connectionOrder = mysql.connector.connect(
                host='pc-2ze1l4f34v5ql1rsu.rwlb.rds.aliyuncs.com',
                database='hotel_admin',
                user='admin_db_user',
                password='VvTUbbEp$D6uGiLDb'
            )

            cursorOrder = connectionOrder.cursor(dictionary=True)
            cursorOrder.execute(
                "SELECT distribute_id,count(*) as total,sum(CASE WHEN status=0 THEN 1 ELSE 0 END) AS fail,sum(CASE WHEN new_price=0 THEN 1 ELSE 0 END) AS full FROM db_check_price_record  where create_time>CONCAT(DATE_FORMAT(NOW(), '%Y-%m-%d %H:'), '00')and create_time<CONCAT(DATE_FORMAT(NOW(), '%Y-%m-%d %H:'), '59') GROUP BY distribute_id;")
            record = cursorOrder.fetchall()

            for row in record:
                total=0
                fail=0
                full=0
                for column, value in row.items():
                    if (column == 'distribute_id'):
                        if (value == 20001):
                            message += "去哪儿阿信失败率："
                        if (value == 20002):
                            message += "美团失败率："
                        if (value == 20004):
                            message += "去哪儿四海通失败率："
                        if (value == 20006):
                            message += "百度售失败率："
                        if (value == 30004):
                            message += "同程商旅失败率："
                        if (value == 20007):
                            message += "同程艺龙失败率："
                        if (value == 20008):
                            message += "去哪儿缤果失败率："
                        if (value == 30002):
                            message += "夏洛特失败率："
                        if (value == 20009):
                            message += "抖音失败率："
                    if (column == 'total'):
                        total=value
                    if (column == 'fail'):
                        fail=value
                    if (column == 'full'):
                        full=value
                print(row)
                totalRate=str(Decimal((fail / total)*100).quantize(Decimal('0.01')))
                priceChange=str(Decimal(((fail-full) / total)*100).quantize(Decimal('0.01')))
                fullRate=str(Decimal((full / total)*100).quantize(Decimal('0.01')))
                message += totalRate +"%\n\t变价率："+priceChange+"%\n\t满房率："+fullRate+"%\n"
            cursorOrder.close()
            connectionOrder.close()

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