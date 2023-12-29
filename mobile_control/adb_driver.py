from util.adb_util import AdbModel
from util.xpath_util import find_element_coordinates, find_element


def click(click_text):
    """
    根据文本点击
    :param click_text:
    :return:
    """
    xml_path = adbModel.convert_to_xml()
    coordinate = find_element_coordinates(xml_path, click_text)
    if coordinate:
        x, y = coordinate
        print(x, y)
        adbModel.click_button(x, y)


def open_mini_feizhu():
    """
    开启飞猪小程序
    :return:
    """
    app_name = "com.tencent.mm/.ui.LauncherUI"
    if not adbModel.is_wechat_open(app_name):
        adbModel.open_app(app_name)
    # 发现
    adbModel.click_button(674, 2210)
    # 小程序
    adbModel.click_button(300, 1828)
    # 我的小程序
    adbModel.click_button(200, 1000)
    # 订单页
    click("订单")


def pay_order(highest_price=None):
    """
    支付订单, 根据highest_price进行比价
    :return:
    """
    find_element()
    click("待付款")
    click("去付款")


def del_order():
    """
    删除订单
    :return:
    """
    click("删除订单")
    # 确定删除
    adbModel.click_button(750, 1260)


if __name__ == '__main__':
    mini_program_app_id = 'wx6a96c49f29850eb5'
    device_id = "ORHQN799EI8TUWN7"
    adbModel = AdbModel(device_id)

    for i in ['订单', '删除订单', '确定']:
        click(i)

    # print(res)

    # # 我的订单
    # adbModel.click_button(666, 2224)
    # adbModel.is_wechat_open()
    # # 截图
    # adbModel.screenshot("./feizhu.png")
    # # 退出微信
    # adbModel.kill_app("com.tencent.mm")
