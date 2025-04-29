# 59 18 * * 2,4 /pjy.sh
import hashlib
import logging
import sys
import os
from datetime import datetime
import concurrent.futures
import redis
import json
import time
import requests

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from dynaconf import settings
from log_model.set_log import setup_logging
from util.ding_util import send_dingding
setup_logging(default_path=settings.LOGGING)


openlist = [
    # 李浩
    # {
    #     "open_id": "oIiOx5VPJ7OBGK9HcRkwnRVssfLc",
    #     "nuid": "99447",
    #     "name": "李浩"
    # },
    # 李小浩
    {
        "open_id": "oIiOx5UPUlc-a85OHdArycE-Khho",
        "nuid": "99624",
        "name": "李小浩"
    },
    # 胖总
    {
        "open_id": "oIiOx5axf0CpsI4WCDwL-jxM2EAM",
        "nuid": "99701",
        "name": "胖总"
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
    # 华威北里
    {
        "open_id": "oIiOx5ezlozlh-J0Y1ZTy6eXimK0",
        "nuid": "110020",
        "name": "华威北里"
    },
    # 什刹海
    {
        "open_id": "oIiOx5UQX8PG7YzOhKcNk5zO4KiM",
        "nuid": "110075",
        "name": "什刹海"
    }
]

menudist = {
    "珠宝": "nUid={}&productTypeId=1&productTypeTitle=%E7%8F%A0%E5%AE%9D%E3%80%81%E6%96%87%E5%88%9B&wxcode=123456&ticket={}",
    "玩具单": "nUid={}&productTypeId=2&productTypeTitle=%E7%8E%A9%E5%85%B7%EF%BC%88%E5%8D%95%E6%91%8A%EF%BC%89&wxcode=123456&ticket={}",
    "古玩": "nUid={}&productTypeId=3&productTypeTitle=%E5%8F%A4%E7%8E%A9%E3%80%81%E6%9D%82%E9%A1%B9&wxcode=123456&ticket={}",
    "玩具双": "nUid={}&productTypeId=70&productTypeTitle=%E7%8E%A9%E5%85%B7%EF%BC%88%E5%8F%8C%E6%91%8A%EF%BC%89&wxcode=123456&ticket={}",
    "文创": "nUid={}&productTypeId=73&productTypeTitle=%E6%96%87%E5%88%9B%E3%80%81%E9%A5%B0%E5%93%81&wxcode=123456&ticket={}"
    }

reslist = []
resdict = {}


def get_headers(open_id):
    new_time = int(time.time())
    token = hashlib.md5("QK1LNHW8QMMGJS2VUYQQTW0A7AQHYM4MA678CSR6XOU8X14B6G{}".format(new_time).encode()).hexdigest()
    headers = {
        'Host': "pjy.lansezhihui.com",
        'Connection': 'keep-alive',
        'timespan': str(new_time),
        'openId': open_id,
        'charset': 'utf-8',
        'content-type': "application/x-www-form-urlencoded",
        'token': token,
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.52(0x18003426) NetType/WIFI Language/zh_CN",
        'Referer': "https://servicewechat.com/wxdf133ab9147107d2/33/page-frame.html",
        'Accept-Encoding': 'gzip, deflate, br'
    }
    return headers


def send_request(mes):
    try:
        start_time = str(datetime.now())

        url = "https://pjy.lansezhihui.com/API/TenPayV4/"
        headers = get_headers(mes['open_id'])
        target = datetime.now().replace(hour=19, minute=0, second=10, microsecond=0)
        now = datetime.now()
        if now < target:
            delta = (target - now).total_seconds()
            time.sleep(delta)
        ticket = get_ticket()
        if ticket is False:
            return "无可用ticket"
        payload = menudist["珠宝"].format(mes['nuid'], ticket)
        req_time = datetime.now()
        response = session.post(url, data=payload, headers=headers)
        logging.info("甲：开始时间: [{}], 请求前时间:[{}], 请求时间:[{}], 结束时间[{}], [{}]: [{}]".format(start_time, str(now), req_time, str(datetime.now()), mes['name'], response.text))
        res_json = json.loads(response.text)
        if res_json['status']:
            select_result(mes['name'], res_json['data']['bespeakId'], mes['open_id'])
    except Exception as f:
        return 0
    return 1


def get_ticket():
    for i in range(100):
        ticket = redis_con.spop("ticket")
        logging.info("ticket: {}".format(ticket))
        if ticket:
            return ticket
        else:
            time.sleep(0.1)
            continue
    return False


def select_result(name, bespeakId, open_id):
    url = "https://pjy.lansezhihui.com/api/GetOneBespeak.ashx"
    headers = get_headers(open_id)
    payload = "nBId={}".format(bespeakId)
    response = requests.request("POST", url, data=payload, headers=headers)
    select_res_json = json.loads(response.text)
    send_dingding("{}预约上了: {}-{}".format(name, select_res_json['bespeakInfo']['strATitle'], select_res_json['bespeakInfo']['strSTitle']))
    return True


def select_request(mes):
    try:

        headers = get_headers(mes['open_id'])
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
            reslist.append("{}: {}预约上了 - {}".format(select_res_json['bespeakInfo']['strATitle'], mes['name'], select_res_json['bespeakInfo']['strSTitle']))

            if resdict.get(select_res_json['bespeakInfo']['strATitle']) is not None:
                resdict[select_res_json['bespeakInfo']['strATitle']] += ", " + select_res_json['bespeakInfo']['strSTitle']
            else:
                resdict[select_res_json['bespeakInfo']['strATitle']] = select_res_json['bespeakInfo']['strSTitle']
            return True
    except Exception as f:
        return False


def cancel_request(nBId, open_id):

    url = "https://pjy.lansezhihui.com/api/CancelMakeAppointment.ashx"

    payload = "nBId={}".format(nBId)
    headers = get_headers(open_id)
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def is_five_pm():
    current_time = datetime.now()
    # 判断当前时间是否为下午7点（19:00）
    if current_time.hour == 19 and current_time.minute == 0:
        return True
    return True


def use_thread_pool():
    global redis_con, session
    redis_host = "r-2ze3pe04ijr8tkn1rt.redis.rds.aliyuncs.com"
    redis_port = 6379

    redis_con = redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        password="",
        decode_responses=True  # 自动将结果解码为字符串
    )
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=40,
        pool_maxsize=40,
        max_retries=0
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.get("https://pjy.lansezhihui.com")
    with concurrent.futures.ProcessPoolExecutor(max_workers=30) as executor:
        while True:
            if is_five_pm():
                send_dingding("9 秒后准备预约！！！")
                # time.sleep(6)
                for j in range(2):
                    # 提交任务到线程池中
                    future_to_result = {executor.submit(send_request, i): i for i in openlist}
                break
            else:
                time.sleep(0.01)
                continue
    time.sleep(30)
    for openmsg in openlist:
        select_request(openmsg)
    reslist.sort()
    send_dingding("复查结果:\n{}".format("，\n".join(reslist)))
    send_text = ""
    for k, v in resdict.items():
        send_text += "{}:{}\n".format(k, v)
    send_dingding("榛榛专用:\n{}".format(send_text))


if __name__ == '__main__':
    use_thread_pool()

