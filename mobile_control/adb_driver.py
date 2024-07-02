import logging
import time
import traceback
import sys
import os

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from dynaconf import settings
from util.orders_util import set_not_effective_device
from log_model.set_log import setup_logging
from mobile_control.mitmproxy_driver import mitmproxy_run
from util.fliggy_util import FliggyModel
from util.interface_util import select_device


def run(device):
    device_id = device.get("deviceId")
    device_name = device.get("deviceName")
    pay_password = device.get("payPassword")
    is_busy = int(device.get("isBusy"))
    is_enable = device.get("isEnable")
    while True:
        fliggy_model = FliggyModel(device_id)
        fliggy_model.open_mini_feizhu()
        click_type = 0
        if is_enable == '1' or is_enable == '2':
            while True:
                try:
                    # 判断手机是否连接
                    if not fliggy_model.is_targat_device(device_name):
                        time.sleep(10)
                        continue
                    # 定位当前页面为订单页
                    fliggy_model.goto_target_page()
                    # 支付订单
                    click_type = fliggy_model.refresh(click_type)
                    busy_devices = select_device()
                    print("设备信息", busy_devices)
                    if len(busy_devices) > 0:
                        for busy_device in busy_devices:
                            if busy_device['deviceId'] == device_id:
                                print(busy_device)
                                is_busy = int(busy_device.get("isBusy"))
                                get_cookie = busy_device.get("getCookie")
                                if get_cookie == "1":
                                    print("准备刷新cookie")
                                    mitmproxy_run(busy_device, fliggy_model)
                    pay_status = fliggy_model.pay_order(pay_password, device_name)
                    if pay_status:
                        if is_busy > 0:
                            is_busy -= 1
                        set_not_effective_device(device_id, "", is_busy)
                        continue
                    busy_id = fliggy_model.get_pay_num()
                    if busy_id is not False:
                        set_not_effective_device(device_id, "", busy_id)
                    time.sleep(1)
                except Exception as f:
                    logging.info("异常： [{}]， 准备跳过...".format(traceback.format_exc()))
                    continue
        else:
            busy_devices = select_device()
            if len(busy_devices) > 0:
                for busy_device in busy_devices:
                    if busy_device['deviceId'] == device_id:
                        is_busy = int(busy_device.get("isBusy"))
                        is_enable = busy_device.get("isEnable")
            print("{}: 当前未启动".format(device_name))
            time.sleep(10)


if __name__ == '__main__':
    args = sys.argv
    tar_device_id = args[1]
    setup_logging(default_path=settings.LOGGING)
    devices = select_device()
    tar_devices = []
    for ii in devices:
        device_id = ii.get("deviceId")
        if device_id == tar_device_id:
            run(ii)
