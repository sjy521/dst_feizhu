import logging
import random
import time
import os
import sys
import cv2
import subprocess
from typing import Optional
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from dynaconf import settings

from log_model.set_log import setup_logging
from util.adb_util import AdbModel
from util.order_list_util import get_bongo_order, adb_order_list
from util.ding_util import send_abnormal_alarm_for_dingding, send_pay_order_for_dingding
from util.orders_util import set_not_effective_device, cancel_order
from util.xpath_util import find_current_element_text, find_element_text, find_element_coordinates, \
    find_current_element_coordinates, find_setting, find_current_element_num, find_all_current_element_text, \
    find_success_element_text

setup_logging(default_path=settings.LOGGING)


class FliggyModel:

    def __init__(self, device_id):
        self.adbModel = AdbModel(device_id)
        self.error_num = 0
        self.device_id = device_id
        self.adbshakedown = None

    def adb(self, *args):
        cmd = ["adb", "-s", self.device_id] + list(args)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0:
            raise RuntimeError(f"ADB command failed: {' '.join(cmd)}\n{result.stderr}")
        return result.stdout.strip()

    def get_screenshot(self, local_path: str = "screen.png") -> str:
        self.adb("shell", "screencap", "-p", "/sdcard/screen.png")
        self.adb("pull", "/sdcard/screen.png", local_path)
        return local_path

    def find_template(self, template_path: str, threshold: float = 0.8) -> Optional[tuple]:
        screen_path = self.get_screenshot()
        screen_img = cv2.imread(screen_path, 0)
        template = cv2.imread(template_path, 0)

        result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = template.shape
            return max_loc[0] + w // 2, max_loc[1] + h // 2
        else:
            return None

    def click_template(self, template_name: str, threshold: float = 0.8) -> bool:
        template_path = os.getcwd() + "/template_model/" + template_name + ".jpg"
        coords = self.find_template(template_path, threshold)
        if coords:
            self.adb("shell", "input", "tap", str(coords[0]), str(coords[1]))
            logging.info(f"点击{template_name} Clicked at: {coords}")
            return True
        else:
            logging.info(f"没有找到 {template_name}")
            return False

    def check_template(self, template_name: str, threshold: float = 0.8):
        logging.info("当前工作目录: {}".format(os.getcwd()))
        template_path = os.getcwd() + "/template_model/" + template_name + ".jpg"
        coords = self.find_template(template_path, threshold)
        if coords:
            logging.info(f"找到了{template_name}")
            return coords
        else:
            logging.info(f"没有找到{template_name}")
            return False

    def click(self, click_text, xml_path=None, timesleep=0):
        """
        根据文本点击
        :param click_text:
        :return:
        """
        if click_text not in ['酒店', '全部订单', '去付款']:
            if xml_path is None:
                xml_path = self.adbModel.convert_to_xml(self.device_id)
            coordinate = find_element_coordinates(xml_path, click_text)
        else:
            if click_text == '酒店':
                coordinate = [726, 297]
            elif click_text == '全部订单':
                coordinate = [162, 297]
            elif click_text == '去付款':
                xml_path = self.adbModel.convert_to_xml(self.device_id)
                if find_all_current_element_text(xml_path, "去付款"):
                    # time.sleep(1)
                    coordinate = [170, 555]
                else:
                    return False
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
            if click_text == "待付款":
                x, y = 170, 975
                logging.info("准备点击[{}], 坐标[{},{}]...".format(click_text, x, y))
                self.adbModel.click_button(x, y, timesleep=timesleep)
                return y
            xml_path = self.adbModel.convert_to_xml(self.device_id)
            coordinate = find_current_element_coordinates(xml_path, click_text)
            if coordinate:
                x, y = coordinate
                if x == y == 0 or y > 2110:
                    self.adbModel.swipe(500, 1700, 500, 600)
                    continue
                logging.info("准备点击[{}], 坐标[{},{}]...".format(click_text, x, y))
                self.adbModel.click_button(x, y, timesleep=timesleep)
                return y
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
            self.adbModel.click_button(145, 1133)
            time.sleep(2)
            if self.click_setting("更多", timesleep=1):
                self.click("重新进入\n小程序", timesleep=5)
        # 订单页
        logging.info("准备点击订单页")
        self.click("订单")
        time.sleep(3)

    def refresh(self, click_type):
        """
        刷新订单
        :return:
        """
        # 我的
        # time.sleep(2)
        # self.adbModel.click_button(975, 2211)
        # 首页
        # time.sleep(2)
        # self.adbModel.click_button(130, 2211)
        self.adbModel.click_button(70, 200)
        time.sleep(3)
        self.adbModel.click_button(768, 2211)
        time.sleep(1)
        self.adbModel.click_button(768, 2211)
        time.sleep(4)
        # self.adbModel.swipe(800, 400, 800, 1200)
        # if click_type == 1:
        #     logging.info("准备点击全部订单")
        #     self.click("全部订单")
        #     return 0
        # # 订单页
        # if click_type == 0:
        #     logging.info("准备点击酒店")
        #     self.click("酒店")
        #     return 1

    def get_fukuan(self, device_id, device_name):
        num, order_info = adb_order_list(device_id)
        if num is None:
            return None, None
        order_id = order_info.get("biz_order_id")
        sr_name = order_info.get("sr_name")
        price = order_info.get("price")
        logging.info("{}: 当前订单号号是：{} {}".format(device_name, order_id, sr_name))
        time.sleep(1)
        bgorder = get_bongo_order(order_id)
        if bgorder is False:
            cancel_order(device_id, order_id)
            logging.info("{}: 当前订单可能未粘贴订单号：{}，已取消该订单".format(device_name, order_id))
            # self.adbModel.click_back()
            # self.adbModel.click_back()
            return None, None, None
        return num, order_id, price

    def pay_order(self, pay_password, device_name, order_num, order_id, ysf_money, price):
        """
        支付订单
        :return:
        """
        if order_num > 0:
            send_pay_order_for_dingding("{}: 有多笔订单，请人工确认后支付".format(device_name))
            return False
        pay_res = self.click_pay("待付款", timesleep=2)
        time.sleep(2)
        xml_path = self.click_template("去付款")
        time.sleep(random.randint(2, 3))
        if xml_path is False:
            return False
        self.check_lijizhifu()
        self.adbModel.click_button(950, 2121)
        time.sleep(random.randint(2, 3))
        self.adbModel.click_button(950, 2151)
        if ysf_money is not None and int(ysf_money) != 0 and int(price) > int(ysf_money):
            return self.yun_shan_fu_pay(pay_password, device_name, order_num, order_id)
        else:
            return self.weixin_pay(pay_password, device_name, order_num, order_id)

    def weixin_pay(self, pay_password, device_name, order_num, order_id):
        self.adbModel.click_button(180, 1737, timesleep=0.1)
        self.adbModel.click_button(180, 2047, timesleep=0.1)
        self.adbModel.click_button(539, 1892, timesleep=0.1)
        self.adbModel.click_button(899, 1737, timesleep=0.1)
        self.adbModel.click_button(899, 1737, timesleep=0.1)
        self.adbModel.click_button(539, 2047, timesleep=0.1)
        time.sleep(3)
        if self.check_template("支付成功"):
            self.error_num = 1
            status = 1
        else:
            status = 0
            send_pay_order_for_dingding("{}: 支付异常, 飞猪订单号: {}".format(device_name, order_id))
            set_not_effective_device(self.device_id, 0, 0)
        logging.info("{}: order_id:[{}] 支付完成, 状态：[{}]".format(device_name, order_id, status))
        self.adbModel.click_button(598, 1950)
        time.sleep(2)
        return True

    def yun_shan_fu_pay(self, pay_password, device_name, order_num, order_id):
        """
        云闪付支付
        :return:
        """
        # 点击支付渠道
        self.adbModel.click_button(928, 1320, timesleep=0.5)
        # 选择云闪付
        xml_path = self.click_template("云闪付")
        if xml_path is False:
            return False
        time.sleep(2)
        # 确定支付
        self.adbModel.click_button(560, 2040, timesleep=0.5)
        # 点击允许跳转
        self.adbModel.click_button(762, 1337, timesleep=1)
        self.adbModel.click_button(180, 1737, timesleep=0.1)
        self.adbModel.click_button(180, 2047, timesleep=0.1)
        self.adbModel.click_button(539, 1892, timesleep=0.1)
        self.adbModel.click_button(899, 1737, timesleep=0.1)
        self.adbModel.click_button(899, 1737, timesleep=0.1)
        self.adbModel.click_button(539, 2047, timesleep=0.1)
        time.sleep(1)
        self.adbModel.click_button(78, 1174, timesleep=0.5)
        time.sleep(3)
        if self.check_template("支付成功"):
            self.error_num = 1
            status = 1
        else:
            status = 0
            send_pay_order_for_dingding("{}: 支付异常, 飞猪订单号: {}".format(device_name, order_id))
            set_not_effective_device(self.device_id, 0, 0)
        logging.info("{}: order_id:[{}] 支付完成, 状态：[{}]".format(device_name, order_id, status))
        self.adbModel.click_button(598, 1950)
        time.sleep(2)
        return True

    def pay_success(self, click_text):
        """
        支付成功
        :param click_text:
        :return:
        """
        logging.info("准备查找[{}]...".format(click_text))
        xml_path = self.adbModel.convert_to_xml(self.device_id)
        res = find_success_element_text(xml_path, click_text)
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

    def check_lijizhifu(self):
        """
        检查立即支付
        :return:
        """

        coordinate = self.check_template("微信支付选择")
        if coordinate is not False and 1597 > coordinate[1] > 1534:
            self.adbModel.click_button(991, 1573)
        time.sleep(1)

    def goto_target_page(self):
        """
        跳转到目标页面
        :return:
        """
        res1 = True
        for i in range(3):
            res = self.check_template("订单页")
            if res is False:
                res1 = self.click_template("订单按钮")
                time.sleep(2)
            else:
                return True
        if res1 is False:
            self.adbModel.click_back()

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
