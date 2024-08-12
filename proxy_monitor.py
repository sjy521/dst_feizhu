import requests
import json
import sys, os

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from util.ding_util import send_abnormal_alarm_for_dingding

url = "https://share.proxy.qg.net/balance?key=SR7KHE10"
r = requests.get(url)
r_json = json.loads(r.text)
if r_json['data']['balance'] < 100:
    send_abnormal_alarm_for_dingding("代理IP剩余量: {}".format(r_json['data']['balance']))


