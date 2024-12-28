import logging
import logging
import time
import traceback
import sys
import os
from collections import deque

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from util.orders_util import get_effective_device
from order_control.abnormal_order import abnormal_start_order
from order_control.hybridization_order import hybridization_start_order
from order_control.snatching_order_plus import snatching_start_order


def run(tar_device_id):
    error_list = deque(maxlen=50)
    devices_error_count = {}
    # 获取空闲可用的设备
    while True:
        try:
            device_info = get_effective_device(tar_device_id)
            if device_info is not None:
                device_id = device_info.get('deviceId')
                device_name = device_info.get('deviceName')
                if not devices_error_count.get(device_name):
                    devices_error_count[device_name] = 0
                is_busy = int(device_info.get('isBusy'))
                phone = device_info.get('accountNo')
                delay_num = device_info.get('delayNum')

                # 混投
                logging.info("准备处理混投列表")
                hybridization_res = hybridization_start_order(device_name, delay_num, phone, is_busy, devices_error_count, error_list, device_id)
                if hybridization_res:
                    continue
                # 变价
                # logging.info("准备处理变价列表")
                # abnormal_res = abnormal_start_order(device_name, delay_num, phone, is_busy, devices_error_count, error_list, device_id)
                # if abnormal_res:
                #     continue
                # # 未处理
                logging.info("准备处理未处理列表")
                snatching_res = snatching_start_order(device_name, delay_num, phone, is_busy, devices_error_count, error_list, device_id)

            else:
                logging.info("当前无可用的设备")
                time.sleep(5)
        except Exception as f:
            logging.error("异常：{}".format(str(traceback.format_exc())))
            time.sleep(5)


if __name__ == '__main__':
    args = sys.argv
    device_id = args[1]
    run(device_id)
