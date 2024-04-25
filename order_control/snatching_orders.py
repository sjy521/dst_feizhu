import requests
import json
import logging
import time
import random

from dynaconf import settings
from log_model.set_log import setup_logging
from util.orders_util import get_effective_device, get_effective_order, get_url_by_bgorderid, order_create_order, \
    build_order

setup_logging(default_path=settings.LOGGING)


if __name__ == '__main__':
    # 获取空闲可用的设备
    device_id = get_effective_device()
    if device_id is not None:
        # 查询待处理订单并锁单
        res = get_effective_order(device_id)
        if res is not None:
            tar_json = get_url_by_bgorderid(res[0], res[1])
            build_order(device_id, tar_json)
        else:
            logging.info("当前无待处理订单")
    else:
        logging.info("当前无可用的设备")


    # get_url_by_bgorderid("11111118", "240320690295")

    # order_create_order("240320001163", "12345678", "手机")

