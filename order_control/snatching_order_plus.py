import logging
import time
import traceback
import sys
import os
from collections import deque

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from dynaconf import settings
from log_model.set_log import setup_logging
from util.order_list_util import check_order
from util.ding_util import send_pay_order_for_dingding
from util.orders_util import get_effective_device, get_effective_order, get_url_by_bgorderid, order_create_order, \
    build_order, fail_order_unlock, unlock, set_not_effective_device, cancel_order, build_error_warn

setup_logging(default_path=settings.LOGGING)


def bulu(is_busy, device_id, bg_order_id, biz_order_id, price, device_name):
    try:
        is_busy += 1
        set_not_effective_device(device_id, 1, is_busy)
        create_order_res = order_create_order(bg_order_id, biz_order_id, price, device_id)
        if create_order_res is False:
            cancel_order(device_id, biz_order_id)
            logging.info("[{}]补录失败, 取消订单号：[{}]".format(bg_order_id, biz_order_id))
        else:
            logging.info("[{}]下单完成, 订单号：[{}]".format(bg_order_id, biz_order_id))
    except Exception as f:
        cancel_order(device_id, biz_order_id)
        logging.info("[{}]补录失败, 取消订单号：[{}]".format(bg_order_id, biz_order_id))
        unlock(bg_order_id, device_name)


def timeout_main(start_time, device_id, tar_json, is_busy, bg_order_id, device_name):
    if time.time() - start_time > 15:
        try:
            order_res = check_order(device_id, tar_json['sr_name'], tar_json['price'])
            if order_res:
                biz_order_id = order_res['biz_order_id']
                price = order_res['price']
                bulu(is_busy, device_id, bg_order_id, biz_order_id, price, device_name)
                return True
            else:
                return False
        except Exception as f:
            return False
    else:
        return False


def except_main(bg_order_id, error_list, device_id, device_name):
    if bg_order_id in error_list:
        fail_order_unlock(0, 1, bg_order_id, device_id, device_name)
    else:
        error_list.append(bg_order_id)
        unlock(bg_order_id, device_name)
    time.sleep(1)


def run(tar_device_id):
    error_list = deque(maxlen=20)
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
                res = get_effective_order(device_id, error_list, device_name)
                if res is not None:
                    d_ordr_id, bg_order_id = res
                    start_time = 0
                    try:
                        tar_json = get_url_by_bgorderid(d_ordr_id, bg_order_id)
                    except Exception as f:
                        logging.error("获取地址异常：{}".format(str(traceback.format_exc())))
                        fail_order_unlock(0, 1, bg_order_id, device_id, device_name)
                        continue
                    try:
                        start_time = time.time()
                        build_res = build_order(device_id, tar_json, phone)
                        if build_res is not None:
                            if build_res == "满房":
                                fail_order_unlock(0, 1, bg_order_id, device_id, device_name)
                                logging.info("[{}]下单完成, 满房".format(bg_order_id))
                            elif build_res == "变价":
                                fail_order_unlock(1, 0, bg_order_id, device_id, device_name)
                                logging.info("[{}]下单完成, 变价".format(bg_order_id))
                            elif build_res == "下单重复":
                                order_res = check_order(device_id, tar_json['sr_name'], tar_json['price'])
                                if order_res:
                                    biz_order_id = order_res['biz_order_id']
                                    price = order_res['price']
                                    bulu(is_busy, device_id, bg_order_id, biz_order_id, price, device_name)
                                    logging.info("[{}]下单完成, 重复找单".format(bg_order_id))
                                else:
                                    send_pay_order_for_dingding("{}: 当前订单可能未粘贴订单号，及时确认".format(device_name))
                                    unlock(bg_order_id, device_name)
                            else:
                                biz_order_id, price = build_res
                                bulu(is_busy, device_id, bg_order_id, biz_order_id, price, device_name)
                            devices_error_count[device_name] = 0
                            continue
                        else:
                            if timeout_main(start_time, device_id, tar_json, is_busy, bg_order_id, device_name):
                                continue
                            except_main(bg_order_id, error_list, device_id, device_name)
                            logging.info("[{}]下单失败".format(bg_order_id))
                            build_error_warn(devices_error_count, device_name, device_id)
                            continue
                    except Exception as f:
                        if timeout_main(start_time, device_id, tar_json, is_busy, bg_order_id, device_name):
                            continue
                        except_main(bg_order_id, error_list, device_id, device_name)
                        logging.error("异常：{}".format(str(traceback.format_exc())))
                else:
                    logging.info("当前无待处理订单")
                    time.sleep(1)
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


