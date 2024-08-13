import requests
import json
import mysql.connector
import sys, os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from util.ding_util import send_abnormal_alarm_for_dingding


def get_expire_time():
    try:
        # 建立数据库连接
        connection = mysql.connector.connect(
            host='pc-2ze0t0vwxj392d111.mysql.polardb.rds.aliyuncs.com',       # 例如 'localhost'
            database='hotel_base_info',   # 数据库名称
            user='dbadmin',   # 用户名
            password='VvTUbbEp$D6uGiLDb' # 密码
        )

        if connection.is_connected():
            cursor = connection.cursor()
            # 执行查询
            cursor.execute('SELECT expire_time FROM proxy_ip WHERE ip_key = "test"')
            result = cursor.fetchone()
            return result[0]
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 关闭数据库连接
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

url = "https://share.proxy.qg.net/balance?key=SR7KHE10"
r = requests.get(url)
r_json = json.loads(r.text)
if r_json['data']['balance'] < 100:
    send_abnormal_alarm_for_dingding("代理IP剩余量: {}".format(r_json['data']['balance']))

expire_time = get_expire_time()
if datetime.now() > expire_time:
    send_abnormal_alarm_for_dingding("代理IP异常，已过期: {}".format(expire_time))

