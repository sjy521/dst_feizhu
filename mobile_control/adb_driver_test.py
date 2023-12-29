
from util.adb_util import AdbModel
from util.xpath_util import find_element_coordinates


def click(click_text):
    xml_path = adbModel.convert_to_xml()
    coordinate = find_element_coordinates(xml_path, click_text)
    if coordinate:
        x, y = coordinate
        print(x, y)
        adbModel.click_button(x, y)


if __name__ == '__main__':
    mini_program_app_id = 'wx6a96c49f29850eb5'
    "gh_e4c5d4d5bc2f"
    device_id = "ORHQN799EI8TUWN7"
    app_name = "com.tencent.mm/.ui.LauncherUI"
    adbModel = AdbModel(device_id)
    # if not adbModel.is_wechat_open(app_name):
    #     adbModel.open_app(app_name)
    # # 发现
    # adbModel.click_button(674, 2210)
    # # 小程序
    # adbModel.click_button(300, 1828)
    # # 我的小程序
    # adbModel.click_button(200, 1000)
    # for i in ['订单', '待付款']:
    click("确定")

    # print(res)


    # # 我的订单
    # adbModel.click_button(666, 2224)
    # adbModel.is_wechat_open()
    # # 截图
    # adbModel.screenshot("./feizhu.png")
    # # 退出微信
    # adbModel.kill_app("com.tencent.mm")