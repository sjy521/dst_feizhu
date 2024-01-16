import time

from dynaconf import settings

from sql_tool.sql_model import SqlModel
from util.adb_util import AdbModel
from util.xpath_util import find_element_coordinates, find_element_text, find_current_element_text


if __name__ == '__main__':
    sql_model = SqlModel(host=settings.MYSQL_HOST, user=settings.MYSQL_USERNAME, port=settings.MYSQL_PORT, pd=settings.MYSQL_PASSWORD, db=settings.MYSQL_DB)
    print(sql_model.select_sql("select * from devices_library"))

    a = 5
    print(a%5)

    # mini_program_app_id = 'wx6a96c49f29850eb5'
    # "gh_e4c5d4d5bc2f"
    # device_id = "ORHQN799EI8TUWN7"
    # app_name = "com.tencent.mm/.ui.LauncherUI"
    # adbModel = AdbModel(device_id)
    # adbModel.is_wechat_open(app_name)
    print('==')
    # print(adbModel.is_wechat_open(app_name))
    # print(click("刷新"))
    # xml_path = adbModel.convert_to_xml()
    # print(find_current_element_text(xml_path, "全部订单"))
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