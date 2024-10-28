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


def get_my_ding_url():
    # https://oapi.dingtalk.com/robot/send?access_token=77b8e267e68c2eb651316ab583e1b7150c695f03328c2b76549f42eb3e603b7c
    timestamp = str(round(time.time() * 1000))
    secret = "SEC2c58988a0c18de696d97de8e9ff9b7d5eb91c205e1c5ca2f116fd27432d76855"
    access_token = "77b8e267e68c2eb651316ab583e1b7150c695f03328c2b76549f42eb3e603b7c"
    secret_enc = secret.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(access_token, timestamp,
                                                                                             sign)
    return url


def get_ding_pay_url():
    # timestamp = str(round(time.time() * 1000))
    # secret = "SEC26b241f0640272d1d31dbcdff40fef0432a3be08606396230fb78dcc3794788b"
    # access_token = "7369d4bbe26545da0c96ce4102c7b0101c7b9e316da46e22e747eb9e568df12f"
    # secret_enc = secret.encode("utf-8")
    # string_to_sign = "{}\n{}".format(timestamp, secret)
    # string_to_sign_enc = string_to_sign.encode("utf-8")
    # hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    # sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    # url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(access_token, timestamp,
    #                                                                                          sign)
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=303013f2-3152-42b8-b5d6-0ca5c736d04e"
    return url


def send_abnormal_alarm_for_dingding(text):
    # 个人的，勿用
    url = get_ding_url()
    data = {
        "at": {
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


def send_dingding(text):
    # 个人的，勿用
    url = get_my_ding_url()
    data = {
        "at": {
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


def send_pay_order_for_dingding(text, atphone=None):
    if atphone is not None:
        atMobiles = atphone
    else:
        atMobiles = ["18518020709"]
    url = get_ding_pay_url()
    data = {
        "at": {
            "atMobiles": atMobiles,
            "isAtAll": True
        },
        "mentioned_mobile_list": atMobiles,
        "text": {
            "content": text
        },
        "msgtype": "text"
    }
    res = requests.post(url, json=data)
    res_json = json.loads(res.text)
    return res_json.get("errmsg")


if __name__ == '__main__':
    print(send_dingding("大家好!"))
