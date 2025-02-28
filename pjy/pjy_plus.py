import os
import sys
import time
import logging
import hashlib
import random
import asyncio
import aiohttp
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from dynaconf import settings
from log_model.set_log import setup_logging
from util.ding_util import send_dingding
setup_logging(default_path=settings.LOGGING)
# 用户列表
openlist = [
    # {"open_id": "oIiOx5Ut64lZTbwF2_oeaw4FCQfA", "nuid": "98781", "name": "榛榛"},
    # {"open_id": "oIiOx5SUacmTWggqMM0YKbdqjTCA", "nuid": "99784", "name": "潘家园"},
    # {"open_id": "oIiOx5Xq4XDz_xRBSfdsOdIY7dZ0", "nuid": "99548", "name": "榛小号"},
    # {"open_id": "oIiOx5SZDPe0L560aLqkHKyuhAbo", "nuid": "99449", "name": "宋小号"},
    # {"open_id": "oIiOx5Vp93EJQ4uge2ErDJAbfBTE", "nuid": "99587", "name": "丰台"},
    # {"open_id": "oIiOx5UPUlc-a85OHdArycE-Khho", "nuid": "99624", "name": "李小浩"},
    # {"open_id": "oIiOx5VPJ7OBGK9HcRkwnRVssfLc", "nuid": "99447", "name": "李浩"},
    {"open_id": "oIiOx5axf0CpsI4WCDwL-jxM2EAM", "nuid": "99701", "name": "胖总"}
]

# 成功列表和尝试列表
successlist = set()
trylist = set()


# 生成 token
def generate_token():
    new_time = int(time.time())
    return hashlib.md5("QK1LNHW8QMMGJS2VUYQQTW0A7AQHYM4MA678CSR6XOU8X14B6G{}".format(new_time).encode()).hexdigest()


# 发送请求
async def send_request(session, mes):
    if mes['name'] in successlist:
        logging.info(f"成功已过滤: [{mes['name']}]")
        return

    try:
        start_time = datetime.now()
        token = generate_token()
        url = "https://pjy.lansezhihui.com/API/TenPayV4/"
        payload = "nUid={}&productTypeId=1&productTypeTitle=%E7%8F%A0%E5%AE%9D%E3%80%81%E6%96%87%E5%88%9B&code={}&wxcode=123456".format(mes['nuid'], random.randint(1000, 9999))
        headers = {
            'Host': "pjy.lansezhihui.com",
            'timespan': str(int(time.time())),
            'openId': mes['open_id'],
            'content-type': "application/x-www-form-urlencoded",
            'token': token,
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.52(0x18003426) NetType/WIFI Language/zh_CN",
            'Referer': "https://servicewechat.com/wxdf133ab9147107d2/31/page-frame.html",
        }

        async with session.post(url, data=payload, headers=headers, ssl=False) as response:
            res_json = await response.json()
            logging.info(f"甲：开始时间: [{start_time}], 结束时间[{datetime.now()}], [{mes['name']}]: [{res_json}]")
            print(res_json)
            if res_json.get('status'):
                successlist.add(mes['name'])
                await select_request(session, mes['name'], res_json['data']['bespeakId'], mes['open_id'])
            elif "已被约满" in res_json.get('msg'):
                # 尝试其他类型
                ding_payload = "nUid={}&productTypeId=73&productTypeTitle=%E6%96%87%E5%88%9B%E3%80%81%E9%A5%B0%E5%93%81&code={}&wxcode=123456".format(mes['nuid'], random.randint(1000, 9999))
                async with session.post(url, data=ding_payload, headers=headers, ssl=False) as response:
                    res_json = await response.json()
                    if res_json.get('status'):
                        successlist.add(mes['name'])
                        await select_request(session, mes['name'], res_json['data']['bespeakId'], mes['open_id'])
                    logging.info(f"丁：时间[{datetime.now()}], [{mes['name']}]: [{res_json}]")
    except Exception as e:
        logging.error("请求失败: ", e)


# 查询预约信息
async def select_request(session, name, bespeakId, open_id):
    token = generate_token()
    url = "https://pjy.lansezhihui.com/API/Users_BespeakV2/GetBespeakInfo/"
    payload = "bespeakId={}".format(bespeakId)
    headers = {
        'Host': "pjy.lansezhihui.com",
        'timespan': str(int(time.time())),
        'openId': open_id,
        'content-type': "application/x-www-form-urlencoded",
        'token': token,
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.52(0x18003426) NetType/WIFI Language/zh_CN",
        'Referer': "https://servicewechat.com/wxdf133ab9147107d2/31/page-frame.html",
    }

    async with session.post(url, data=payload, headers=headers) as response:
        select_res_json = await response.json()
        logging.info(f"{name} 预约上了: {select_res_json['data']['areaTitle']}-{select_res_json['data']['stallTitle']}")
        # 发送通知
        send_dingding(f"{name} 预约上了: {select_res_json['data']['areaTitle']}-{select_res_json['data']['stallTitle']}")


# 取消预约
async def cancel_request(session, nBId, open_id):
    token = generate_token()
    url = "https://pjy.lansezhihui.com/api/CancelMakeAppointment.ashx"
    payload = {"nBId": nBId}
    headers = {
        'Host': "pjy.lansezhihui.com",
        'timespan': str(int(time.time())),
        'openId': open_id,
        'content-type': "application/x-www-form-urlencoded",
        'token': token,
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.52(0x18003426) NetType/WIFI Language/zh_CN",
        'Referer': "https://servicewechat.com/wxdf133ab9147107d2/31/page-frame.html",
    }

    async with session.post(url, data=payload, headers=headers) as response:
        logging.info(f"取消预约结果: {await response.text()}")


# 判断是否为下午5点
def is_five_pm():
    current_time = datetime.now()
    return True
    # return current_time.hour == 17 and current_time.minute == 0


# 主函数
async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            if is_five_pm():
                logging.info("9 秒后准备预约！！！")
                await asyncio.sleep(8.3)  # 精确控制时间
                for _ in range(2):  # 每个用户发送20次请求
                    tasks = []
                    for mes in openlist:
                        tasks.append(send_request(session, mes))
                    await asyncio.gather(*tasks)
                    await asyncio.sleep(0.01)  # 每次请求间隔0.01秒
                break
            else:
                continue

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())