import sys
import os
import mitmproxy.http

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from util.orders_util import get_all_device, set_get_cookie_device


def request(flow: mitmproxy.http.HTTPFlow):
    """
    :param flow:
    :return:
    """
    host = flow.request.host
    if 'acs-m.feizhu.com' in host:
        get_appmsg(flow)
    else:
        pass


def get_appmsg(flow: mitmproxy.http.HTTPFlow):
    """
    @param flow:
    @return:
    """
    cookie = flow.request.cookies
    cookie2 = _m_h5_tk_enc = _m_h5_tk = x5sec = ""
    print(cookie)
    for k, v in cookie.items():
        if 'cookie2' in k:
            print(v)
            cookie2 = v
            continue
        if '_m_h5_tk_enc' in k:
            print(v)
            _m_h5_tk_enc = v
            continue
        if '_m_h5_tk' in k and "_m_h5_tk_enc" not in k:
            print(v)
            _m_h5_tk = v
            continue
    for k, v in cookie.items():
        if 'x5sec' in k:
            print(v)
            x5sec = v
            update_cookie_device(cookie2, "{}|{}".format(x5sec, _m_h5_tk + ";" + _m_h5_tk_enc))
            return 1
    if cookie2 != "" and _m_h5_tk != "" and _m_h5_tk_enc != "":
        update_cookie_device(cookie2, "{}".format(_m_h5_tk + ";" + _m_h5_tk_enc))
        return 1
    else:
        return 0


def update_cookie_device(cookie, x5sec):
    """
    更新cookie
    :return:
    """
    all_devies = get_all_device()
    if all_devies is not None:
        for result in all_devies:
            if result.get("isMyCookie") == "1":
                device_id = result.get("deviceId")
                set_get_cookie_device(device_id, cookie, x5sec)
    else:
        return None
