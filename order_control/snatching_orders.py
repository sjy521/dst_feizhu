import logging
import time
import traceback

import dynaconf
from dynaconf import settings
from log_model.set_log import setup_logging
from util.orders_util import get_effective_device, get_effective_order, get_url_by_bgorderid, order_create_order, \
    build_order, edit_change_full, fail_order_unlock, unlock, set_not_effective_device

setup_logging(default_path=settings.LOGGING)


if __name__ == '__main__':
    # 获取空闲可用的设备
    while True:
        try:
            device_info = get_effective_device()
            if device_info is not None:
                device_id = device_info.get('deviceId')
                is_busy = int(device_info.get('isBusy'))
                for i in range(20):
                    # 查询待处理订单并锁单
                    res = get_effective_order(device_id)
                    if res is not None:
                        d_ordr_id, bg_order_id = res
                        try:
                            tar_json = get_url_by_bgorderid(d_ordr_id, bg_order_id)
                            build_res = build_order(device_id, tar_json)
                            if build_res is not None:
                                if build_res == "满房":
                                    fail_order_unlock(0, 1, bg_order_id, device_id)
                                    logging.info("[{}]下单完成, 满房".format(bg_order_id))
                                elif build_res == "变价":
                                    fail_order_unlock(1, 0, bg_order_id, device_id)
                                    logging.info("[{}]下单完成, 变价".format(bg_order_id))
                                else:
                                    biz_order_id, price = build_res
                                    is_busy += 1
                                    set_not_effective_device(device_id, 1, is_busy)
                                    order_create_order(bg_order_id, biz_order_id, price, device_id)
                                    logging.info("[{}]下单完成, 订单号：[{}]".format(bg_order_id, biz_order_id))
                                break
                            else:
                                logging.info("[{}]下单失败".format(bg_order_id))
                                unlock(bg_order_id, device_id)
                                time.sleep(5)
                                continue
                        except Exception as f:
                            logging.error("异常：{}".format(str(traceback.format_exc())))
                            unlock(bg_order_id, device_id)
                            time.sleep(2)
                    else:
                        logging.info("当前无待处理订单")
                        time.sleep(2)
            else:
                logging.info("当前无可用的设备")
                time.sleep(10)
        except Exception as f:
            logging.error("异常：{}".format(str(traceback.format_exc())))
            time.sleep(5)


    # get_url_by_bgorderid("11111118", "240320690295")

    # order_create_order("240320001163", "12345678", "手机")

