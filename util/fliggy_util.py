import logging
import time

from dynaconf import settings

from log_model.set_log import setup_logging
from util.adb_util import AdbModel
from util.ding_util import send_abnormal_alarm_for_dingding
from util.interface_util import cancelorder, payresult
from util.xpath_util import find_current_element_text, find_element_text, find_element_coordinates, \
    find_current_element_coordinates

setup_logging(default_path=settings.LOGGING)


class FliggyModel:

    def __init__(self, device_id):
        self.adbModel = AdbModel(device_id)
        self.error_num = 0

    def click(self, click_text, xml_path=None, timesleep=0):
        """
        根据文本点击
        :param click_text:
        :return:
        """
        if xml_path is None:
            xml_path = self.adbModel.convert_to_xml()
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

    def click_pay(self, click_text, timesleep=0):
        """
        根据文本点击
        :param click_text:
        :return:
        """
        for _ in range(4):
            xml_path = self.adbModel.convert_to_xml()
            coordinate = find_current_element_coordinates(xml_path, click_text)
            if coordinate:
                x, y = coordinate
                if x == y == 0:
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

    def open_mini_feizhu(self):
        """
        开启飞猪小程序
        :return:
        """
        app_name = "com.tencent.mm/.ui.LauncherUI"
        for i in range(5):
            self.adbModel.click_back()
        self.adbModel.open_app(app_name)
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
        # 订单页
        logging.info("准备点击订单页")
        self.click("订单")

    def refresh(self):
        """
        刷新订单
        :return:
        """
        logging.info("准备点击全部订单")
        self.click("全部订单")
        # 订单页
        logging.info("准备点击酒店")
        self.click("酒店")

    def pay_order(self, pay_password):
        """
        支付订单
        :return:
        """
        if self.click_pay("待付款", timesleep=5):
            self.check_error()
            # self.adbModel.click_back()
            xml_path = self.click("去付款", timesleep=5)
            if xml_path:
                order_id = self.find_orderId(xml_path, "订单号")
                logging.info("当前订单号号是：{}".format(order_id))
                xml_path = self.click(pay_password[0])
                if xml_path is False:
                    self.error_num += 1
                    send_abnormal_alarm_for_dingding("支付前异常，请及时查看")
                    self.adbModel.click_back()
                    self.adbModel.click_back()
                    if self.error_num >= 6:
                        payresult(orderId=order_id, status=0)
                    return False
                self.click(pay_password[1], xml_path)
                self.click(pay_password[2], xml_path)
                self.click(pay_password[3], xml_path)
                self.click(pay_password[4], xml_path)
                if cancelorder(order_id):
                    logging.info("验证成功")
                    # input("验证成功，点击回车继续付款...")
                else:
                    logging.info("验证失败, 准备返回")
                    # input("验证失败，点击回车继续付款...")
                    self.adbModel.click_back()
                    self.adbModel.click_back()
                    return True
                self.click(pay_password[5], xml_path)
                time.sleep(3)
                if self.pay_success("支付成功"):
                    status = 1
                else:
                    status = 0
                    send_abnormal_alarm_for_dingding("支付异常，请及时查看")
                payresult(orderId=order_id, status=status)
                logging.info("order_id:[{}] 支付完成，已成功发送通知".format(order_id))
                # input("支付完成，点击回车继续...")
                # self.click("忽略", timesleep=1)
                self.adbModel.click_back()
                # 280,1380
                time.sleep(2)
                self.adbModel.click_button(280,1380)
                # self.click("忽略", timesleep=1)
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
        xml_path = self.adbModel.convert_to_xml()
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
            xml_path = self.adbModel.convert_to_xml()
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
        for _ in range(3):
            for __ in range(3):
                xml_path = self.adbModel.convert_to_xml()
                if find_current_element_text(xml_path, "全部订单"):
                    return True
                else:
                    self.adbModel.click_back()
            logging.info("定位订单页失败，准备重启飞猪小程序...")
            self.open_mini_feizhu()

        send_abnormal_alarm_for_dingding("定位飞猪小程序订单页失败超三次")
