import base64
import hashlib
import hmac
import json
import time
import urllib.parse

import requests


def get_ding_url():
    timestamp = str(round(time.time() * 1000))
    secret = "SEC7141e9edff7eb6905e91ae8c8f29a27533fdf1a0af5328f233ae1adebf889f34"
    access_token = "2ed07a870f42ded3c83a14675f336f425aaecb6191b1fa6bb472a6ed91908c94"
    secret_enc = secret.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(access_token, timestamp,
                                                                                             sign)
    return url


def send_abnormal_alarm_for_dingding(text):
    url = get_ding_url()
    data = {
        "at": {
            "atMobiles": [
                "18518020709"
            ],
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


if __name__ == '__main__':
    print(send_abnormal_alarm_for_dingding("告警机器人测试"))
