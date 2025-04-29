import hashlib
import logging
import sys
import os
import redis
import time
import requests
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from dynaconf import settings
from log_model.set_log import setup_logging
from pjy.pjy_1 import get_headers, is_five_pm

setup_logging(default_path=settings.LOGGING)

openlist = [
    # 李浩
    {
        "open_id": "oIiOx5VPJ7OBGK9HcRkwnRVssfLc",
        "nuid": "99447",
        "name": "李浩"
    }
]


def get_aidEncrypted(mes):
    redis_host = "r-2ze3pe04ijr8tkn1rt.redis.rds.aliyuncs.com"
    redis_port = 6379

    redis_con = redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        password="",
        decode_responses=True  # 自动将结果解码为字符串
    )
    session = requests.Session()
    session.get("https://pjy.lansezhihui.com")
    target = datetime.now().replace(hour=19, minute=0, second=10, microsecond=0)
    now = datetime.now()
    if now < target:
        delta = (target - now).total_seconds()
        time.sleep(delta)
    for i in range(5):
        logging.info("{} aidEncrypted 开始".format(str(datetime.now())))
        url = "https://pjy.lansezhihui.com/API/Users_Bespeak/Create/"
        data = "isBespek=1"
        header = get_headers(mes['open_id'])
        response = session.post(url, data=data, headers=header)
        logging.info("encrypted请求结果：{}".format(response.text))
        aidEncrypted = response.json().get('aidEncrypted')
        if not aidEncrypted:
            logging.info("{} aidEncrypted 失败：[{}]".format(str(datetime.now()), response.text))
            time.sleep(0.01)
            continue
        redis_con.set("aidEncrypted", aidEncrypted, ex=300)
        logging.info("{} aidEncrypted 保存：{}".format(str(datetime.now()), aidEncrypted))
        return True


if __name__ == '__main__':
    while True:
        if is_five_pm():
            logging.info("{} aidEncrypted 准备".format(str(datetime.now())))
            get_aidEncrypted(openlist[0])
        else:
            time.sleep(0.05)