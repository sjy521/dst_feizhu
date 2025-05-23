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
    totalProfit = 0.0
    totalBrokerage = 0.0
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

            # Total Orders with Ring and YoY
            cursor.execute("""
                SELECT 
                    distributor_id, 
                    COUNT(*) as count,
                    (SELECT COUNT(*) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 1 DAY) 
                     AND distributor_id = t.distributor_id) as count_prev_day,
                    (SELECT COUNT(*) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 7 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 7 DAY) 
                     AND distributor_id = t.distributor_id) as count_prev_week
                FROM db_bg_order t
                WHERE create_time > DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00') 
                AND create_time < NOW()
                GROUP BY distributor_id;
            """)
            record = cursor.fetchall()
            for row in record:
                distributor_id = row['distributor_id']
                count = row['count']
                count_prev_day = row['count_prev_day'] or 0
                count_prev_week = row['count_prev_week'] or 0
                distributor_map = {
                    '20001': "去哪儿阿信",
                    '20002': "美团",
                    '20003': "飞猪",
                    '20004': "去哪儿",
                    '20005': "携程",
                    '20006': "百度",
                    '30004': "同程商旅",
                    '20007': "同程艺龙",
                    '20008': "去哪儿缤果",
                    '20009': "抖音"
                }
                distributor_name = distributor_map.get(distributor_id, distributor_id)
                message += f"{distributor_name}：{count}，{count_prev_day}，{count_prev_week}\n"
                totalCount += int(count)
            totalCount_prev_day = sum([row['count_prev_day'] or 0 for row in record])
            totalCount_prev_week = sum([row['count_prev_week'] or 0 for row in record])
            message += f"总订单数：{totalCount}，{totalCount_prev_day}，{totalCount_prev_week}\n\n确认订单：\n"

            # Confirmed Orders with Ring and YoY
            cursor.execute("""
                SELECT 
                    distributor_id, 
                    COUNT(*) as count,
                    (SELECT COUNT(*) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 1 DAY) 
                     AND order_status IN (11, 12) 
                     AND distributor_id = t.distributor_id) as count_prev_day,
                    (SELECT COUNT(*) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 7 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 7 DAY) 
                     AND order_status IN (11, 12) 
                     AND distributor_id = t.distributor_id) as count_prev_week
                FROM db_bg_order t
                WHERE create_time > DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00') 
                AND create_time < NOW() 
                AND order_status IN (11, 12)
                GROUP BY distributor_id;
            """)
            record = cursor.fetchall()
            for row in record:
                distributor_id = row['distributor_id']
                count = row['count']
                count_prev_day = row['count_prev_day'] or 0
                count_prev_week = row['count_prev_week'] or 0
                distributor_map = {
                    '20001': "去哪儿阿信确认订单",
                    '20002': "美团确认订单",
                    '20003': "飞猪确认订单",
                    '20004': "去哪儿四海通确认订单",
                    '20005': "携程确认订单",
                    '20006': "百度确认订单",
                    '30004': "同程商旅确认订单",
                    '20007': "同程艺龙确认订单",
                    '20008': "去哪儿缤果确认订单",
                    '20009': "抖音确认订单"
                }
                distributor_name = distributor_map.get(distributor_id, distributor_id)
                message += f"{distributor_name}：{count}，{count_prev_day}，{count_prev_week}\n"
                confirm += int(count)
            totalConfirm_prev_day = sum([row['count_prev_day'] or 0 for row in record])
            totalConfirm_prev_week = sum([row['count_prev_week'] or 0 for row in record])
            message += f"总确认订单数：{confirm}，{totalConfirm_prev_day}，{totalConfirm_prev_week}\n\n售前利润：\n"

            # Pre-sale Profits with Ring and YoY
            cursor.execute("""
                SELECT 
                    bg.distributor_id, 
                    SUM(bg.seller_price - bg.price) as totalprofit,
                    (SELECT SUM(seller_price - price) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 1 DAY) 
                     AND order_status IN (11, 12) 
                     AND distributor_id = bg.distributor_id) as profit_prev_day,
                    (SELECT SUM(seller_price - price) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 7 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 7 DAY) 
                     AND order_status IN (11, 12) 
                     AND distributor_id = bg.distributor_id) as profit_prev_week
                FROM db_bg_order bg
                WHERE bg.create_time > DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00') 
                AND bg.create_time < NOW() 
                AND bg.order_status IN (11, 12)
                GROUP BY bg.distributor_id;
            """)
            record = cursor.fetchall()
            for row in record:
                distributor_id = row['distributor_id']
                totalprofit = float(row['totalprofit'] or 0) / 100
                profit_prev_day = float(row['profit_prev_day'] or 0) / 100
                profit_prev_week = float(row['profit_prev_week'] or 0) / 100
                distributor_map = {
                    '20001': "去哪儿阿信售前利润",
                    '20002': "美团售前利润",
                    '20003': "飞猪售前利润",
                    '20004': "去哪儿四海通售前利润",
                    '20005': "携程售前利润",
                    '20006': "百度售前利润",
                    '30004': "同程商旅售前利润",
                    '20007': "同程艺龙售前利润",
                    '20008': "去哪儿缤果售前利润",
                    '20009': "抖音售前利润"
                }
                distributor_name = distributor_map.get(distributor_id, distributor_id)
                message += f"{distributor_name}：{totalprofit:.2f}，{profit_prev_day:.2f}，{profit_prev_week:.2f}\n"
                totalProfit += totalprofit
            totalProfit_prev_day = sum([float(row['profit_prev_day'] or 0) / 100 for row in record])
            totalProfit_prev_week = sum([float(row['profit_prev_week'] or 0) / 100 for row in record])
            message += f"总售前利润：{totalProfit:.2f}，{totalProfit_prev_day:.2f}，{totalProfit_prev_week:.2f}\n\n供应商：\n"

            # Supplier Metrics with Ring and YoY
            cursor.execute("""
                SELECT 
                    o.supplier_id, 
                    COUNT(*) AS orderCount, 
                    SUM(CAST(o.seller_price AS DECIMAL(10,2)) - CAST(o.price AS DECIMAL(10,2))) AS totalprofit, 
                    SUM(CAST(o.price AS DECIMAL(10,2))) AS price, 
                    SUM(CASE 
                        WHEN o.supplier_id = 10002 THEN CAST(o.price AS DECIMAL(10,2)) * 0.045 
                        WHEN o.supplier_id = 10004 THEN (
                            SELECT COALESCE(SUM(CAST(so.brokerage AS DECIMAL(10,2))), 0) 
                            FROM db_supplier_order so 
                            WHERE so.bg_order_id = o.bg_order_id
                        ) 
                        ELSE 0 
                    END) AS brokerage,
                    (SELECT COUNT(*) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 1 DAY) 
                     AND order_status IN (11, 12) 
                     AND supplier_id = o.supplier_id) as orderCount_prev_day,
                    (SELECT COUNT(*) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 7 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 7 DAY) 
                     AND order_status IN (11, 12) 
                     AND supplier_id = o.supplier_id) as orderCount_prev_week,
                    (SELECT SUM(CAST(seller_price AS DECIMAL(10,2)) - CAST(price AS DECIMAL(10,2))) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 1 DAY) 
                     AND order_status IN (11, 12) 
                     AND supplier_id = o.supplier_id) as totalprofit_prev_day,
                    (SELECT SUM(CAST(seller_price AS DECIMAL(10,2)) - CAST(price AS DECIMAL(10,2))) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 7 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 7 DAY) 
                     AND order_status IN (11, 12) 
                     AND supplier_id = o.supplier_id) as totalprofit_prev_week,
                    (SELECT SUM(CAST(price AS DECIMAL(10,2))) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 1 DAY) 
                     AND order_status IN (11, 12) 
                     AND supplier_id = o.supplier_id) as price_prev_day,
                    (SELECT SUM(CAST(price AS DECIMAL(10,2))) 
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 7 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 7 DAY) 
                     AND order_status IN (11, 12) 
                     AND supplier_id = o.supplier_id) as price_prev_week,
                    (SELECT SUM(CASE 
                        WHEN supplier_id = 10002 THEN CAST(price AS DECIMAL(10,2)) * 0.045 
                        WHEN supplier_id = 10004 THEN (
                            SELECT COALESCE(SUM(CAST(so.brokerage AS DECIMAL(10,2))), 0) 
                            FROM db_supplier_order so 
                            WHERE so.bg_order_id = db_bg_order.bg_order_id
                        ) 
                        ELSE 0 
                    END)
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 1 DAY) 
                     AND order_status IN (11, 12) 
                     AND supplier_id = o.supplier_id) as brokerage_prev_day,
                    (SELECT SUM(CASE 
                        WHEN supplier_id = 10002 THEN CAST(price AS DECIMAL(10,2)) * 0.045 
                        WHEN supplier_id = 10004 THEN (
                            SELECT COALESCE(SUM(CAST(so.brokerage AS DECIMAL(10,2))), 0) 
                            FROM db_supplier_order so 
                            WHERE so.bg_order_id = db_bg_order.bg_order_id
                        ) 
                        ELSE 0 
                    END)
                     FROM db_bg_order 
                     WHERE create_time > DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 7 DAY), '%Y-%m-%d 00:00:00') 
                     AND create_time < DATE_SUB(NOW(), INTERVAL 7 DAY) 
                     AND order_status IN (11, 12) 
                     AND supplier_id = o.supplier_id) as brokerage_prev_week
                FROM db_bg_order o 
                WHERE o.create_time > DATE_FORMAT(NOW(), '%Y-%m-%d 00:00:00') 
                AND o.create_time < NOW() 
                AND o.order_status IN (11, 12) 
                AND o.supplier_id IN (10002, 10004) 
                GROUP BY o.supplier_id;
            """)
            record = cursor.fetchall()
            for row in record:
                supplier_id = row['supplier_id']
                supplier_map = {
                    '10002': "飞猪四海通",
                    '10004': "阿信"
                }
                supplier_name = supplier_map.get(supplier_id, supplier_id)
                message += f"{supplier_name}：\n"
                price = float(row['price'] or 0) / 100
                price_prev_day = float(row['price_prev_day'] or 0) / 100
                price_prev_week = float(row['price_prev_week'] or 0) / 100
                message += f"销售额：{price:.2f}，{price_prev_day:.2f}，{price_prev_week:.2f}\n"
                orderCount = row['orderCount']
                orderCount_prev_day = row['orderCount_prev_day'] or 0
                orderCount_prev_week = row['orderCount_prev_week'] or 0
                message += f"确认单：{orderCount}，{orderCount_prev_day}，{orderCount_prev_week}\n"
                totalprofit = float(row['totalprofit'] or 0) / 100
                totalprofit_prev_day = float(row['totalprofit_prev_day'] or 0) / 100
                totalprofit_prev_week = float(row['totalprofit_prev_week'] or 0) / 100
                message += f"售前利润：{totalprofit:.2f}，{totalprofit_prev_day:.2f}，{totalprofit_prev_week:.2f}\n"
                brokerage = float(row['brokerage'] or 0) / 100
                brokerage_prev_day = float(row['brokerage_prev_day'] or 0) / 100
                brokerage_prev_week = float(row['brokerage_prev_week'] or 0) / 100
                message += f"佣金：{brokerage:.2f}，{brokerage_prev_day:.2f}，{brokerage_prev_week:.2f}\n\n"
                totalBrokerage += brokerage
            totalBrokerage_prev_day = sum([float(row['brokerage_prev_day'] or 0) / 100 for row in record])
            totalBrokerage_prev_week = sum([float(row['brokerage_prev_week'] or 0) / 100 for row in record])
            message += f"总佣金：{totalBrokerage:.2f}，{totalBrokerage_prev_day:.2f}，{totalBrokerage_prev_week:.2f}\n\n"

            # Hourly Orders with Ring and YoY
            cursor.execute("""
                SELECT 
                    COUNT(*) as hourOrder,
                    (SELECT COUNT(*) 
                     FROM db_bg_order 
                     WHERE create_time > CONCAT(DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d %H:'), '00')
                     AND create_time < CONCAT(DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 DAY), '%Y-%m-%d %H:'), '59')) as hourOrder_prev_day,
                    (SELECT COUNT(*) 
                     FROM db_bg_order 
                     WHERE create_time > CONCAT(DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 7 DAY), '%Y-%m-%d %H:'), '00')
                     AND create_time < CONCAT(DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 7 DAY), '%Y-%m-%d %H:'), '59')) as hourOrder_prev_week
                FROM db_bg_order 
                WHERE create_time > CONCAT(DATE_FORMAT(NOW(), '%Y-%m-%d %H:'), '00')
                AND create_time < CONCAT(DATE_FORMAT(NOW(), '%Y-%m-%d %H:'), '59');
            """)
            record = cursor.fetchall()
            for row in record:
                hourOrder = row['hourOrder']
                hourOrder_prev_day = row['hourOrder_prev_day'] or 0
                hourOrder_prev_week = row['hourOrder_prev_week'] or 0
                message += f"一小时进单数：{hourOrder}，{hourOrder_prev_day}，{hourOrder_prev_week}\n\n"

            # Failure Rates (unchanged)
            connectionOrder = mysql.connector.connect(
                host='pc-2ze1l4f34v5ql1rsu.rwlb.rds.aliyuncs.com',
                database='hotel_admin',
                user='admin_db_user',
                password='VvTUbbEp$D6uGiLDb'
            )
            cursorOrder = connectionOrder.cursor(dictionary=True)
            cursorOrder.execute("""
                SELECT distribute_id, count(*) as total, 
                       sum(CASE WHEN status=0 THEN 1 ELSE 0 END) AS fail, 
                       sum(CASE WHEN new_price=0 THEN 1 ELSE 0 END) AS full 
                FROM db_check_price_record 
                WHERE create_time > CONCAT(DATE_FORMAT(NOW(), '%Y-%m-%d %H:'), '00')
                AND create_time < CONCAT(DATE_FORMAT(NOW(), '%Y-%m-%d %H:'), '59') 
                GROUP BY distribute_id;
            """)
            record = cursorOrder.fetchall()
            for row in record:
                total = row['total']
                fail = row['fail']
                full = row['full']
                distributor_map = {
                    20001: "去哪儿阿信失败率",
                    20002: "美团失败率",
                    20004: "去哪儿四海通失败率",
                    20006: "百度售失败率",
                    30004: "同程商旅失败率",
                    20007: "同程艺龙失败率",
                    20008: "去哪儿缤果失败率",
                    30002: "夏洛特失败率",
                    20009: "抖音失败率"
                }
                distributor_name = distributor_map.get(row['distribute_id'], row['distribute_id'])
                totalRate = str(Decimal((fail / total) * 100).quantize(Decimal('0.01')))
                priceChange = str(Decimal(((fail - full) / total) * 100).quantize(Decimal('0.01')))
                fullRate = str(Decimal((full / total) * 100).quantize(Decimal('0.01')))
                message += f"{distributor_name}：{totalRate}%\n\t变价率：{priceChange}%\n\t满房率：{fullRate}%\n"

            cursorOrder.close()
            connectionOrder.close()
            print(message)
            # send_pay_order_for_dingding(message)
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    except Error as e:
        print("Error while connecting to MySQL", e)

def job():
    print("任务执行中...")
    orderstatic()
    print("任务执行完成")

if __name__ == '__main__':
    job()