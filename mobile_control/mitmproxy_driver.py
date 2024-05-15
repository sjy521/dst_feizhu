import logging
import time
import traceback
import sys
import os

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

from util.orders_util import get_all_device, set_get_cookie_device
from util.ding_util import send_pay_order_for_dingding


def mitmproxy_run(result, fliggy_model):
    device_id = result.get("deviceId")
    set_get_cookie_device(device_id)
    adb_model = fliggy_model.adbModel
    ip_address = adb_model.get_proxy_ip()
    if ip_address is not None:
        adb_model.open_proxy("{}:8892".format(str(ip_address)))
        pid = adb_model.open_mitmproxy()
        adb_model.click_button(500, 1000)
        time.sleep(5)
        adb_model.click_back()
        adb_model.close_proxy()
        adb_model.kill_pid(pid)
        all_devies = get_all_device()
        time.sleep(3)
        if all_devies is not None:
            for result1 in all_devies:
                if result1.get("deviceId") == device_id:
                    device_name = result1.get("deviceName")
                    if result1.get("getCookie") != "1":
                        send_pay_order_for_dingding("{}: cookie刷新完成".format(device_name))
    return True


if __name__ == '__main__':
    all_devices = get_all_device()
    for result in all_devices:
        get_cookie = result.get("getCookie")
        if get_cookie == "1":
            mitmproxy_run(result)
            break