import requests
import json
import redis
from collections import deque
import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from util.ding_util import send_pay_order_for_dingding

error_list = deque(maxlen=30)
r = redis.Redis(host='r-2ze3m1fsvz6z4hpk2l.redis.rds.aliyuncs.com', port=6379)
# r.delete("xiechengid")
print("数据:{}".format(r.lrange("xiechengid", 0, -1)))

queue_name = 'xiechengid'


# 添加新元素并修剪队列
def push_to_queue(element):
    with r.pipeline() as pipe:
        pipe.lpush(queue_name, element)
        pipe.ltrim(queue_name, 0, 29)
        pipe.execute()
        print('储存成功')


# 检查元素是否在队列中
def is_in_queue(element):
    queue_elements = r.lrange(queue_name, 0, -1)
    # 将字节字符串转换为普通字符串
    queue_elements = [elem.decode('utf-8') for elem in queue_elements]
    return element in queue_elements


def xiechengcheck():
    url = "https://www.vipdlt.com/order/api/scrollOrderList"
    querystring = {"v": "0.6726812331766832"}
    payload = "{\"cityId\":0,\"cityName\":\"\",\"hotelId\":0,\"hotelName\":\"\",\"lockHuid\":\"\",\"dltOrderStatus\":\"\",\"formType\":\"\",\"orderTag\":[],\"payStatus\":\"2\",\"clientName\":\"\",\"orderId\":\"\",\"issueOrderId\":\"\",\"issueStatus\":\"NotIssue\",\"issueBackStatus\":\"\",\"queryDates\":[{\"orderDateType\":\"0\",\"startTime\":\"2024-07-04 00:00:00\",\"endTime\":\"2024-07-04 00:00:00\"}],\"channel\":\"\",\"pageIndex\":1,\"pageSize\":20,\"brandId\":\"\",\"bookingNo\":\"\",\"channelOrderId\":\"\",\"orderby\":\"formdate desc\",\"bookingNoIsEmpty\":\"All\",\"clientComplaintReason\":\"\",\"searchAll\":\"\",\"sortList\":null}"
    headers = {
        'Content-Type': "application/json",
        'cookie': "downloadFileJava=T; Eventplugin=T; scrollTop=5384; UBT_VID=1720092390452.e8e2TWMjhWhW; CurrentLanguage=SimpChinese; _RSG=06KZ7V4y1wAbN9PbFIrsA8; _RDG=28c1c1459233482ba512ca3594fc835bc2; _RGUID=ae81f047-c78d-4180-82b6-d523e56495e5; randomkey=827acfa3-c775-4f8f-9a12-b63f26b15b2b; usertoken=827acfa3-c775-4f8f-9a12-b63f26b15b2b; MipHuName=U%2BJJWeUCRowvMDNA9JuL0Q%3D%3D; MipHuid=NsJryo4eC7JmOTcqZKR8kw%3D%3D; huid=10147845; ebk_basedata_Huid=10147845; loginName=%E6%9D%A8%E9%87%91%E9%BE%9913371; PageState=TWlwSHVOYW1lTmV3PeadqOmHkem%2BmTEzMzcx; hotel_user_token=6c4fa5c9-5b7c-4422-9a6d-1ce83d9e339b; autoLogin=T; DonotShowNotice=F; CtripSaleCloseHotelCount=T; rememberMe=false; _RF1=2408%3A8409%3A3081%3Ab20%3A210c%3A51fd%3A4fb2%3Ae183; lastPageRefreshTime=1720093845726; _bfa=1.1720092390452.e8e2TWMjhWhW.1.1720093837805.1720093846078.1.8.10650032074; lastClickEventTime=1720097239969",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        'Referer': "https://www.vipdlt.com/order/orderList",
        'X-Requested-With': "XMLHttpRequest",
        'cache-control': "no-cache",
        'Postman-Token': "d8a77ac2-bfb5-432e-9bf6-f7dcae988661"
    }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    r_json = json.loads(response.text)
    infoBos = r_json['data']['infoBos']
    for info in infoBos:
        comConfirmNo = info['comConfirmNo']
        channelOrderId = info['channelOrderId']
        if comConfirmNo == "" and not is_in_queue(channelOrderId):
            push_to_queue(channelOrderId)
            send_pay_order_for_dingding("携程漏单了, 商家订单号: {}".format(channelOrderId), ["18501953880", "13520735673", "13474763052", "18911137911"])


if __name__ == '__main__':
    xiechengcheck()
