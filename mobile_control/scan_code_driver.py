import logging
import time
import traceback
import sys
import os

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from dynaconf import settings

from util.xpath_util import find_current_element_text
from log_model.set_log import setup_logging
from util.fliggy_util import FliggyModel
from util.interface_util import select_device


def is_ok(fliggy_model):
    for _ in range(20):
        xml_path = fliggy_model.adbModel.convert_to_xml()
        if find_current_element_text(xml_path, "酒店详情"):
            return True
    else:
        return False


def run(device):
    device_id = device.get("deviceId")
    fliggy_model = FliggyModel(device_id)
    fliggy_model.open_wechat()
    fliggy_model.click("发现")
    while True:
        try:
            print("点击扫一扫")
            fliggy_model.adbModel.click_button(220, 346, 0)
            if is_ok(fliggy_model):
                fliggy_model.adbModel.click_back()
                time.sleep(1)
            else:
                print("二维码扫码错误")
                fliggy_model.adbModel.click_back()
                break
        except Exception as f:
            logging.info("异常： [{}]， 准备跳过...".format(traceback.format_exc()))
            continue


if __name__ == '__main__':
    setup_logging(default_path=settings.LOGGING)
    devices = select_device()
    if len(devices) > 0:
        for device in devices:
            print(device)
            if device['state'] == '1':
                run(device)
