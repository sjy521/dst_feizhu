# 59 16 * * 2,4 /pjy.sh
import hashlib
import logging
import sys
import os
import requests
from datetime import datetime
import concurrent.futures
import random
import time
import json

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from dynaconf import settings
from log_model.set_log import setup_logging
from util.ding_util import send_dingding
setup_logging(default_path=settings.LOGGING)


openlist = [
    # 李浩
    {
        "open_id": "oIiOx5VPJ7OBGK9HcRkwnRVssfLc",
        "nuid": "99447",
        "name": "李浩"
    },
    # 榛小号
    {
        "open_id": "oIiOx5Xq4XDz_xRBSfdsOdIY7dZ0",
        "nuid": "99548",
        "name": "榛小号"
    },
    # 宋小号
    {
        "open_id": "oIiOx5SZDPe0L560aLqkHKyuhAbo",
        "nuid": "99449",
        "name": "宋小号"
    },
    # 丰台
    {
        "open_id": "oIiOx5Vp93EJQ4uge2ErDJAbfBTE",
        "nuid": "99587",
        "name": "丰台"
    },
    # 李小浩
    {
        "open_id": "oIiOx5UPUlc-a85OHdArycE-Khho",
        "nuid": "99624",
        "name": "李小浩"
    },
    # 榛榛
    {
        "open_id": "oIiOx5Ut64lZTbwF2_oeaw4FCQfA",
        "nuid": "98781",
        "name": "榛榛"
    },
    # 潘家园
    {
        "open_id": "oIiOx5SUacmTWggqMM0YKbdqjTCA",
        "nuid": "99784",
        "name": "潘家园"
    }
]
successlist = []


def send_request(mes):
    global successlist

    if mes['name'] in successlist:
        logging.info("成功已过滤: [{}]".format(mes['name']))
        return '已成功'
    new_time = int(time.time())
    token = hashlib.md5("QK1LNHW8QMMGJS2VUYQQTW0A7AQHYM4MA678CSR6XOU8X14B6G{}".format(new_time).encode()).hexdigest()

    url = "https://pjy.lansezhihui.com/API/TenPayV4/"
    payload = "nUid={}&productTypeId=1&productTypeTitle=%E7%8F%A0%E5%AE%9D%E3%80%81%E6%96%87%E5%88%9B&code={}&wxcode=123456".format(mes['nuid'], random.randint(1000, 9999))
    headers = {
        'Host': "pjy.lansezhihui.com",
        'timespan': str(new_time),
        'openId': mes['open_id'],
        'content-type': "application/x-www-form-urlencoded",
        'token': token,
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.52(0x18003426) NetType/WIFI Language/zh_CN",
        'Referer': "https://servicewechat.com/wxdf133ab9147107d2/31/page-frame.html",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    res_json = json.loads(response.text)
    if res_json['status']:
        successlist.append(mes['name'])
    logging.info("[{}]: [{}]".format(mes['name'], response.text))
    return 1


def is_five_pm():
    current_time = datetime.now()
    # 判断当前时间是否为下午5点（17:00）
    if current_time.hour == 17 and current_time.minute == 0:
        return True
    return False


def use_thread_pool():
    global successlist
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        while True:
            successlist = []
            if is_five_pm():
                send_dingding("10秒后准备预约！！！")
                time.sleep(9)
                for j in range(1):
                    # 提交任务到线程池中
                    future_to_result = {executor.submit(send_request, i): i for i in openlist}
                    time.sleep(0.5)
                send_dingding("任务完成, 已经预约上了: [{}]".format(successlist))
                logging.info("任务完成, 已经预约上了: [{}]".format(successlist))
                break
            else:
                continue


if __name__ == '__main__':
    use_thread_pool()


