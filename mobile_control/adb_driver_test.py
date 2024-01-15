import time

from util.adb_util import AdbModel
from util.xpath_util import find_element_coordinates, find_element_text, find_current_element_text


def click(click_text):
    """
    根据文本点击
    :param click_text:
    :return:
    """
    print("准备点击[{}]...".format(click_text))
    xml_path = adbModel.convert_to_xml()
    coordinate = find_element_coordinates(xml_path, click_text)
    if coordinate:
        x, y = coordinate
        print(x, y)
        adbModel.click_button(x, y)
        return True
    else:
        print("未发现[{}], 跳过点击...".format(click_text))
        time.sleep(5)
        return False


def find_orderId(click_text):
    """
    根据寻找orderId
    :param click_text:
    :return:
    """
    print("准备查找[{}]...".format(click_text))
    xml_path = adbModel.convert_to_xml()
    text = find_element_text(xml_path, click_text)
    if text:
        return text
    else:
        print("未发现[{}], 跳过点击...".format(click_text))
        return False


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


if __name__ == '__main__':
    mini_program_app_id = 'wx6a96c49f29850eb5'
    "gh_e4c5d4d5bc2f"
    device_id = "ORHQN799EI8TUWN7"
    app_name = "com.tencent.mm/.ui.LauncherUI"
    adbModel = AdbModel(device_id)
    # adbModel.is_wechat_open(app_name)
    print('==')
    # print(adbModel.is_wechat_open(app_name))
    print(click("刷新"))
    # click("酒店")
    # click("全部订单")
    # click("酒店")
    # click("全部订单")
    # click("酒店")
    # click("全部订单")
    # click("酒店")
    # click("全部订单")
    # click("酒店")
    # click("全部订单")
    # click("酒店")
    # # 发现
    # adbModel.click_button(674, 2210)
    # # 小程序
    # adbModel.click_button(300, 1828)
    # # 我的小程序
    # adbModel.click_button(200, 1000)
    # for i in ['订单', '待付款']:
    # click("确定")

    # print(res)


    # # 我的订单
    # adbModel.click_button(666, 2224)
    # adbModel.is_wechat_open()
    # # 截图
    # adbModel.screenshot("./feizhu.png")
    # # 退出微信
    # adbModel.kill_app("com.tencent.mm")