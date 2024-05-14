import logging
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from dynaconf import settings

from log_model.set_log import setup_logging
from util.adb_util import AdbModel
from util.ding_util import send_abnormal_alarm_for_dingding, send_pay_order_for_dingding
from util.orders_util import set_not_effective_device
from util.xpath_util import find_current_element_text, find_element_text, find_element_coordinates, \
    find_current_element_coordinates, find_setting, find_current_element_num

setup_logging(default_path=settings.LOGGING)


class FliggyModel:

    def __init__(self, device_id):
        self.adbModel = AdbModel(device_id)
        self.error_num = 0
        self.device_id = device_id
        self.adbshakedown = None

    def click(self, click_text, xml_path=None, timesleep=0):
        """
        根据文本点击
        :param click_text:
        :return:
        """
        if xml_path is None:
            xml_path = self.adbModel.convert_to_xml(self.device_id)
        coordinate = find_element_coordinates(xml_path, click_text)
        if coordinate:
            x, y = coordinate
            logging.info("准备点击[{}], 坐标[{},{}]...".format(click_text, x, y))
            self.adbModel.click_button(x, y, timesleep=timesleep)
            return xml_path
        else:
            logging.info("未发现[{}], 跳过点击...".format(click_text))
            if timesleep is not None:
                time.sleep(timesleep)
            return False

    def click_setting(self, click_text, xml_path=None, timesleep=0):
        """
        根据文本点击
        :param click_text:
        :return:
        """
        if xml_path is None:
            xml_path = self.adbModel.convert_to_xml(self.device_id)
        coordinate = find_setting(xml_path, click_text)
        if coordinate:
            x, y = coordinate
            logging.info("准备点击[{}], 坐标[{},{}]...".format(click_text, x, y))
            self.adbModel.click_button(x, y, timesleep=timesleep)
            return xml_path
        else:
            logging.info("未发现[{}], 跳过点击...".format(click_text))
            if timesleep is not None:
                time.sleep(timesleep)
            return False

    def click_pay(self, click_text, timesleep=0):
        """
        根据文本点击
        :param click_text:
        :return:
        """
        for _ in range(4):
            xml_path = self.adbModel.convert_to_xml(self.device_id)
            coordinate = find_current_element_coordinates(xml_path, click_text)
            if coordinate:
                x, y = coordinate
                if x == y == 0 or y > 2110:
                    self.adbModel.swipe(500, 1700, 500, 600)
                    continue
                logging.info("准备点击[{}], 坐标[{},{}]...".format(click_text, x, y))
                self.adbModel.click_button(x, y, timesleep=timesleep)
                return xml_path
            else:
                logging.info("未发现[{}], 跳过点击...".format(click_text))
                if timesleep is not None:
                    time.sleep(timesleep)
                return False
        else:
            return False

    def get_pay_num(self):
        """
        获取待支付订单数量
        :param click_text:
        :return:
        """
        xml_path = self.adbModel.convert_to_xml(self.device_id)
        coordinate = find_current_element_num(xml_path, "待支付")
        if coordinate:
            return coordinate
        else:
            return False

    def find_orderId(self, xml_path, click_text):
        """
        根据寻找orderId
        :param click_text:
        :return:
        """
        logging.info("准备查找[{}]...".format(click_text))
        text = find_element_text(xml_path, click_text)
        if text:
            return text
        else:
            logging.info("未发现[{}], 跳过点击...".format(click_text))
            return None

    def open_wechat(self):
        app_name = "com.tencent.mm/.ui.LauncherUI"
        for i in range(5):
            self.adbModel.click_back()
        self.adbModel.open_app(app_name)

    def open_mini_feizhu(self):
        """
        开启飞猪小程序
        :return:
        """
        if self.click_setting("更多", timesleep=1):
            self.click("重新进入\n小程序", timesleep=5)
        else:
            self.open_wechat()
            # 发现
            logging.info("准备打开发现页...")
            self.click("发现", timesleep=1)
            # 小程序
            logging.info("准备点击小程序...")
            self.click("小程序", timesleep=2)
            # 我的小程序
            logging.info("准备点击飞猪小程序...")
            # click("飞猪")
            self.adbModel.click_button(200, 1000)
            time.sleep(2)
            if self.click_setting("更多", timesleep=1):
                self.click("重新进入\n小程序", timesleep=5)
        # 订单页
        logging.info("准备点击订单页")
        self.click("订单")

    def refresh(self, click_type):
        """
        刷新订单
        :return:
        """
        if click_type == 1:
            logging.info("准备点击全部订单")
            self.click("全部订单")
            return 0
        # 订单页
        if click_type == 0:
            logging.info("准备点击酒店")
            self.click("酒店")
            return 1

    def pay_order(self, pay_password, device_name):
        """
        支付订单
        :return:
        """
        if self.click_pay("待付款", timesleep=5):
            self.check_error()
            xml_path = self.click("去付款", timesleep=4)
            if xml_path:
                order_id = self.find_orderId(xml_path, "订单号")
                logging.info("{}: 当前订单号号是：{}".format(device_name, order_id))
                xml_path = self.click(pay_password[0])
                if xml_path is False:
                    self.error_num += 1
                    send_pay_order_for_dingding("{}: 支付前异常, 请查看网络或是否有广告, 飞猪订单号: {}".format(device_name, order_id))
                    self.adbModel.click_back()
                    self.adbModel.click_back()
                    if self.error_num >= 6:
                        set_not_effective_device(self.device_id, 0, 0)
                    return False
                self.click(pay_password[1], xml_path)
                self.click(pay_password[2], xml_path)
                self.click(pay_password[3], xml_path)
                self.click(pay_password[4], xml_path)
                # if cancelorder(order_id):
                #     logging.info("验证成功")
                #     # input("验证成功，点击回车继续付款...")
                # else:
                #     logging.info("验证失败, 准备返回")
                #     # input("验证失败，点击回车继续付款...")
                #     self.adbModel.click_back()
                #     self.adbModel.click_back()
                #     return True
                self.click(pay_password[5], xml_path)
                time.sleep(3)
                if self.pay_success("支付成功"):
                    self.error_num = 1
                    status = 1
                else:
                    status = 0
                    send_pay_order_for_dingding("{}: 支付异常, 飞猪订单号: {}".format(device_name, order_id))
                    # cancel_order(self.device_id, order_id)
                    set_not_effective_device(self.device_id, 0, 0)
                    # unlock(bg_order_id, self.device_id)
                logging.info("{}: order_id:[{}] 支付完成, 状态：[{}]".format(device_name, order_id, status))
                self.adbModel.click_back()
                time.sleep(2)
                self.adbModel.click_button(280, 1380)
                self.adbModel.click_back()
                return True
            else:
                self.adbModel.click_back()
                return False
        else:
            return False

    def pay_success(self, click_text):
        """
        支付成功
        :param click_text:
        :return:
        """
        logging.info("准备查找[{}]...".format(click_text))
        xml_path = self.adbModel.convert_to_xml(self.device_id)
        res = find_current_element_text(xml_path, click_text)
        if res:
            return res
        else:
            logging.info("未发现[{}], 跳过点击...".format(click_text))
            return False

    def del_order(self):
        """
        删除订单
        :return:
        """
        if self.click("删除订单", timesleep=1):
            # 确定删除
            self.adbModel.click_button(750, 1260)
            logging.info("成功删除一条过期订单...")

    def check_error(self):
        """
        检查是否是异常页面
        :return:
        """
        for _ in range(2):
            xml_path = self.adbModel.convert_to_xml(self.device_id)
            if find_current_element_text(xml_path, "无法打开页面"):
                self.adbModel.click_button(530, 900)
                time.sleep(5)
                self.adbModel.click_button(530, 900)
                continue
            if find_current_element_text(xml_path, "长按识别二维码关注服务号"):
                self.adbModel.click_button(1000, 1000)
                continue
            return True
        return True

    def goto_target_page(self):
        """
        跳转到目标页面
        :return:
        """
        for _ in range(10):
            for __ in range(3):
                xml_path = self.adbModel.convert_to_xml(self.device_id)
                if find_current_element_text(xml_path, "全部订单"):
                    return True
                else:
                    self.adbModel.click_back()
            logging.info("定位订单页失败，准备重启飞猪小程序...")
            self.open_mini_feizhu()

        send_abnormal_alarm_for_dingding("定位飞猪小程序订单页失败超10次")

    def is_targat_device(self, device_name):
        if self.adbshakedown is None:
            self.adbshakedown = 0
        if self.adbModel.library():
            if self.adbshakedown == 1:
                # 钉钉通知
                send_pay_order_for_dingding("{}: adb调试已经打开，程序恢复正常".format(device_name))
                self.adbshakedown = 0
            return True
        else:
            if self.adbshakedown == 0:
                # 钉钉通知
                send_pay_order_for_dingding("{}: 当前程序异常：请查看手机是否连接 或者 adb调试是否开启".format(device_name))
                self.adbshakedown = 1
            return False
