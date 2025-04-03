# 59 16 * * 2,4 /pjy.sh
import hashlib
import logging
import sys
import os
import requests
from datetime import datetime
import concurrent.futures
import redis
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
    },
    # 胖总
    {
        "open_id": "oIiOx5axf0CpsI4WCDwL-jxM2EAM",
        "nuid": "99701",
        "name": "胖总"
    }
]

menudist = {
    "珠宝": "nUid={}&productTypeId=1&productTypeTitle=%E7%8F%A0%E5%AE%9D%E3%80%81%E6%96%87%E5%88%9B&wxcode=123456&ticket={}",
    "玩具单": "nUid={}&productTypeId=2&productTypeTitle=%E7%8E%A9%E5%85%B7%EF%BC%88%E5%8D%95%E6%91%8A%EF%BC%89&wxcode=123456&ticket={}",
    "古玩": "nUid={}&productTypeId=3&productTypeTitle=%E5%8F%A4%E7%8E%A9%E3%80%81%E6%9D%82%E9%A1%B9&wxcode=123456&ticket={}",
    "玩具双": "nUid={}&productTypeId=70&productTypeTitle=%E7%8E%A9%E5%85%B7%EF%BC%88%E5%8F%8C%E6%91%8A%EF%BC%89&wxcode=123456&ticket={}",
    "文创": "nUid={}&productTypeId=73&productTypeTitle=%E6%96%87%E5%88%9B%E3%80%81%E9%A5%B0%E5%93%81&wxcode=123456&ticket={}"
    }

successlist = []
trylist = []


def send_request(mes):
    global successlist
    global trylist

    if mes['name'] in successlist:
        logging.info("成功已过滤: [{}]".format(mes['name']))
        return '已成功'
    try:
        start_time = str(datetime.now())
        new_time = int(time.time())
        token = hashlib.md5("QK1LNHW8QMMGJS2VUYQQTW0A7AQHYM4MA678CSR6XOU8X14B6G{}".format(new_time).encode()).hexdigest()

        url = "https://pjy.lansezhihui.com/API/TenPayV4/"
        ticket = get_ticket()
        if ticket is False:
            return "无可用ticket"
        payload = menudist["珠宝"].format(mes['nuid'], ticket)
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
        logging.info("甲：开始时间: [{}], 结束时间[{}], [{}]: [{}]".format(start_time, str(datetime.now()), mes['name'], response.text))
        if res_json['status']:
            successlist.append(mes['name'])
    except Exception as f:
        return 0
    return 1


def get_ticket():
    ticket = redis_con.spop("ticket")
    logging.info("ticket: {}".format(ticket))
    if ticket:
        return ticket
    else:
        return False


def select_request(mes):
    try:
        new_time = int(time.time())
        token = hashlib.md5("QK1LNHW8QMMGJS2VUYQQTW0A7AQHYM4MA678CSR6XOU8X14B6G{}".format(new_time).encode()).hexdigest()

        headers = {
            'Host': "pjy.lansezhihui.com",
            'timespan': str(new_time),
            'openId': mes['open_id'],
            'content-type': "application/x-www-form-urlencoded",
            'token': token,
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.52(0x18003426) NetType/WIFI Language/zh_CN",
            'Referer': "https://servicewechat.com/wxdf133ab9147107d2/31/page-frame.html",
        }
        url = "https://pjy.lansezhihui.com/api/home"
        payload = "nUId={}&userStatus=2".format(mes['nuid'])
        response = requests.request("POST", url, data=payload, headers=headers)
        home_res_json = json.loads(response.text)
        nBid = home_res_json['data']['nightMarket']['nBid']
        if nBid != "0":
            url = "https://pjy.lansezhihui.com/api/GetOneBespeak.ashx"
            payload = "nBId={}".format(nBid)
            response = requests.request("POST", url, data=payload, headers=headers)
            select_res_json = json.loads(response.text)
            send_dingding("{}预约上了: {}-{}".format(mes['name'], select_res_json['bespeakInfo']['strATitle'], select_res_json['bespeakInfo']['strSTitle']))
            return True
    except Exception as f:
        return False


def cancel_request(nBId, open_id):
    new_time = int(time.time())
    token = hashlib.md5("QK1LNHW8QMMGJS2VUYQQTW0A7AQHYM4MA678CSR6XOU8X14B6G{}".format(new_time).encode()).hexdigest()

    url = "https://pjy.lansezhihui.com/api/CancelMakeAppointment.ashx"

    payload = "nBId={}".format(nBId)
    headers = {
        'Host': "pjy.lansezhihui.com",
        'timespan': str(new_time),
        'openId': open_id,
        'content-type': "application/x-www-form-urlencoded",
        'token': token,
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.52(0x18003426) NetType/WIFI Language/zh_CN",
        'Referer': "https://servicewechat.com/wxdf133ab9147107d2/31/page-frame.html",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def is_five_pm():
    current_time = datetime.now()
    # 判断当前时间是否为下午7点（19:00）
    if current_time.hour == 19 and current_time.minute == 0:
        return True
    return False


def use_thread_pool():
    global successlist, redis_con
    redis_host = "r-2ze3pe04ijr8tkn1rt.redis.rds.aliyuncs.com"
    redis_port = 6379

    redis_con = redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        password="",
        decode_responses=True  # 自动将结果解码为字符串
    )
    with concurrent.futures.ProcessPoolExecutor(max_workers=100) as executor:
        while True:
            successlist = []
            if is_five_pm():
                send_dingding("9 秒后准备预约！！！")
                time.sleep(8.6)
                for j in range(3):
                    # 提交任务到线程池中
                    future_to_result = {executor.submit(send_request, i): i for i in openlist}
                break
            else:
                continue
    time.sleep(10)
    for openmsg in openlist:
        select_request(openmsg)


if __name__ == '__main__':
    use_thread_pool()


