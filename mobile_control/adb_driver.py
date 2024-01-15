import time

import requests

from util.adb_util import AdbModel
from util.xpath_util import find_element_coordinates, find_element_text, find_current_element_text


def click(click_text, xml_path=None, timesleep=None):
    """
    根据文本点击
    :param click_text:
    :return:
    """
    print("准备点击[{}]...".format(click_text))
    if xml_path is None:
        xml_path = adbModel.convert_to_xml()
    coordinate = find_element_coordinates(xml_path, click_text)
    if coordinate:
        x, y = coordinate
        print(x, y)
        adbModel.click_button(x, y)
        if timesleep is not None:
            time.sleep(timesleep)
        return xml_path
    else:
        print("未发现[{}], 跳过点击...".format(click_text))
        if timesleep is not None:
            time.sleep(timesleep)
        return False


def find_orderId(xml_path, click_text):
    """
    根据寻找orderId
    :param click_text:
    :return:
    """
    print("准备查找[{}]...".format(click_text))
    text = find_element_text(xml_path, click_text)
    if text:
        return text
    else:
        print("未发现[{}], 跳过点击...".format(click_text))
        return None


def open_mini_feizhu():
    """
    开启飞猪小程序
    :return:
    """
    app_name = "com.tencent.mm/.ui.LauncherUI"
    for i in range(5):
        adbModel.click_back()
    adbModel.open_app(app_name)
    # if not adbModel.is_wechat_open(app_name):
    #     adbModel.open_app(app_name)
    # else:
    #     for i in range(5):
    #         adbModel.click_back()
    # 发现
    print("准备打开发现页...")
    click("发现")
    # adbModel.click_button(674, 2210)
    # 小程序
    print("准备点击小程序...")
    click("小程序")
    # adbModel.click_button(300, 360)
    # 我的小程序
    print("准备点击飞猪小程序...")
    # click("飞猪")
    adbModel.click_button(200, 1000)
    # 订单页
    print("准备点击订单页")
    click("订单")


def refresh():
    """
    刷新订单
    :return:
    """
    print("准备点击全部订单")
    click("全部订单")
    # 订单页
    print("准备点击酒店")
    click("酒店")


def pay_order():
    """
    支付订单
    :return:
    """
    if click("待付款", timesleep=5):
        xml_path = click("去付款", timesleep=5)
        # for _ in range(3):
        #     xml_path = click("去付款", timesleep=5)
        #     if xml_path:
        #         break
        #     else:
        #         click("去付款", timesleep=5)
        if xml_path:
            order_id = find_orderId(xml_path, "订单号")
            print("当前订单号号是：{}".format(order_id))
            xml_path = click("8")
            click("6", xml_path)
            click("1", xml_path)
            click("1", xml_path)
            click("0", xml_path)
            if cancelorder(order_id):
                print("验证成功")
                # input("验证成功，点击回车继续付款...")
            else:
                print("验证失败")
                # input("验证失败，点击回车继续付款...")
                adbModel.click_back()
                adbModel.click_back()
                return False
            click("5")
            time.sleep(5)
            if pay_success("支付成功"):
                status = 1
            else:
                status = 0
            payresult(orderId=order_id, status=status)
            # input("支付完成，点击回车继续...")
            adbModel.click_back()
            adbModel.click_back()
        else:
            adbModel.click_back()


def pay_success(click_text):
    """
    支付成功
    :param click_text:
    :return:
    """
    print("准备查找[{}]...".format(click_text))
    xml_path = adbModel.convert_to_xml()
    res = find_current_element_text(xml_path, click_text)
    if res:
        return res
    else:
        print("未发现[{}], 跳过点击...".format(click_text))
        return False


def cancelorder(order_id):
    """
    查询后台订单状态
    :param orderId:
    :return:
    """
    try:
        url = "http://192.168.52.111:8080/api/wx/select/order?orderId={}".format(order_id)
        r = requests.get(url)
        stutas = str(r.text)
        print(stutas)
    except Exception as f:
        print("确认订单状态失败" + str(f))
        stutas = "20"
    if stutas == "23":
        return False
    else:
        return True


def payresult(orderId, status):
    try:
        url = "http://192.168.52.111:8080/api/wx/pay/result?status={}&message=null&orderId={}".format(status, orderId)
        r = requests.get(url)
    except Exception as f:
        print("通知支付状态失败" + str(f))
    return True


def del_order():
    """
    删除订单
    :return:
    """
    if click("删除订单"):
        # 确定删除
        adbModel.click_button(750, 1260)


if __name__ == '__main__':
    mini_program_app_id = 'wx6a96c49f29850eb5'
    device_id = "ORHQN799EI8TUWN7"
    adbModel = AdbModel(device_id)
    open_mini_feizhu()
    while True:
        # for _ in range(2):

        pay_order()

        del_order()

        time.sleep(10)

        refresh()

        # input("点击回车继续")
