# 59 16 * * 2,4 /pjy.sh
import hashlib
import logging
import sys
import os
import cv2
import requests
from datetime import datetime
import redis
import numpy as np
import time

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from dynaconf import settings
from log_model.set_log import setup_logging
setup_logging(default_path=settings.LOGGING)


def get_ticket(HOSTSIGN, aidEncrypted):
    start_time = time.time()
    url = "https://turing.captcha.qcloud.com/cap_union_prehandle"

    querystring = {"lang":"zh-cn","userLanguage":"zh-cn","customize_aid":"190503158","aid":"190503158","aidEncrypted": aidEncrypted}

    headers = {
        'Connection': "keep-alive",
        'X-WECHAT-HOSTSIGN': str(HOSTSIGN),
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1 wechatdevtools/1.06.2412050 MicroMessenger/8.0.5 Language/zh_CN webview/",
        'content-type': "application/json",
        'Referer': "https://servicewechat.com/wx675c8c19ec03dfee/devtools/page-frame.html"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    sess = response.json()['sess']
    img_url = "https://turing.captcha.qcloud.com" + response.json()['data']['dyn_show_info']['bg_elem_cfg']['img_url']

    response = requests.get(img_url)
    image_data = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    image = cv2.convertScaleAbs(image, alpha=0.21, beta=0)
    # 处理图片（转换为灰度并进行边缘检测）
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # 寻找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # 找到最大的轮廓（可能是缺口）
        max_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(max_contour)
        y = y - 20
        x = x - 20

        url = "https://turing.captcha.qcloud.com/cap_union_new_verify"

        payload = "sess={}&ans=%5B%7B%22elem_id%22%3A1%2C%22type%22%3A%22DynAnswerType_POS%22%2C%22data%22%3A%22{}%2C{}%22%7D%5D".format(sess, x, y)
        response = requests.request("POST", url, data=payload, headers=headers)

        logging.info(("获取滑块总耗时：{}, 当前时间：{}".format(time.time() - start_time, str(datetime.now()))))
        return response.json()['ticket']


def is_five_pm():
    current_time = datetime.now()
    # 判断当前时间是否为下午5点（17:00）
    if current_time.hour == 17 and current_time.minute == 0:
        return True
    return False


def use_thread_pool():
    global successlist
    redis_host = "r-2ze3pe04ijr8tkn1rt.redis.rds.aliyuncs.com"
    redis_port = 6379

    redis_con = redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        password="",
        decode_responses=True  # 自动将结果解码为字符串
    )
    for i in range(10):
        HOSTSIGN = redis_con.get("HOSTSIGN")
        if HOSTSIGN:
            while True:
                if is_five_pm():
                    target = datetime.now().replace(hour=19, minute=0, second=10, microsecond=0)
                    now = datetime.now()
                    if now < target:
                        delta = (target - now).total_seconds()
                        time.sleep(delta)
                    aidEncrypted = redis_con.get("aidEncrypted")
                    if aidEncrypted:
                        for j in range(3):
                            logging.info(("获取滑块, 当前时间：{}, aidEncrypted:[{}], HOSTSIGN:[{}]".format(str(datetime.now()), aidEncrypted, HOSTSIGN)))
                            ticket = get_ticket(HOSTSIGN, aidEncrypted)
                            redis_con.sadd(ticket)
                        return True
                else:
                    time.sleep(0.01)
                    continue


if __name__ == '__main__':
    use_thread_pool()


