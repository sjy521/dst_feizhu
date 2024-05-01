import logging
import time
import traceback
import sys
import os

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from multiprocessing import Pool
from dynaconf import settings
from util.orders_util import set_not_effective_device
from log_model.set_log import setup_logging
from util.ding_util import send_abnormal_alarm_for_dingding
from util.fliggy_util import FliggyModel
from util.interface_util import select_device


def run(device):
    device_id = device.get("deviceId")
    pay_password = device.get("payPassword")
    is_busy = int(device.get("isBusy"))
    is_enable = device.get("isEnable")
    fliggy_model = FliggyModel(device_id)
    fliggy_model.open_mini_feizhu()
    pay_num = 0
    click_type = 0
    while True:
        try:
            # 定位当前页面为订单页
            fliggy_model.goto_target_page()
            # 支付订单
            click_type = fliggy_model.refresh(click_type)
            pay_status = fliggy_model.pay_order(pay_password)
            if pay_status:
                pay_num += 1
                busy_devices = select_device()
                if len(busy_devices) > 0:
                    for busy_device in busy_devices:
                        if busy_device['deviceId'] == device_id:
                            is_busy = int(busy_device.get("isBusy"))
                if is_busy > 0:
                    is_busy -= 1
                set_not_effective_device(device_id, "", is_busy)
                if pay_num % 5 == 0:
                    send_abnormal_alarm_for_dingding("已经连续支付成功{}单".format(pay_num))
                continue
            pay_num = 0
            # fliggy_model.del_order()
            time.sleep(1)
        except Exception as f:
            logging.info("异常： [{}]， 准备跳过...".format(traceback.format_exc()))
            continue



if __name__ == '__main__':
    setup_logging(default_path=settings.LOGGING)
    devices = select_device()
    pool = Pool(2)
    pool.map(run, devices)