import logging
import time
import traceback

from dynaconf import settings

from log_model.set_log import setup_logging
from util.fliggy_util import FliggyModel
from util.interface_util import select_device


def run(device):
    device_id = device.get("device_id")
    fliggy_model = FliggyModel(device_id)
    fliggy_model.open_wechat()
    while True:
        try:
            fliggy_model.click("发现")
            fliggy_model.click("扫一扫")
            time.sleep(1)
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
