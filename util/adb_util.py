import os
import re
import tempfile
import time
import subprocess
import traceback


class AdbModel:
    def __init__(self, device_id):
        self.device_id = device_id

    def open_app(self, wechat_name):
        """
        启动微信应用 com.tencent.mm/.ui.LauncherUI
        :return:
        """
        subprocess.run(['adb', "-s", self.device_id, 'shell', 'am', 'start', '-n', wechat_name])
        time.sleep(2)

    def kill_app(self, wechat_name):
        """
        关闭微信应用
        :param wechat_name:
        :return:
        """
        subprocess.run(['adb', "-s", self.device_id, 'shell', 'am', 'force-stop', wechat_name])

    def start_server(self):
        """
        启动adb服务
        :param device_id:
        :return:
        """
        subprocess.run(["adb", "-s", self.device_id, "start-server"])
        time.sleep(2)

    def kill_server(self):
        """
        关闭服务
        :param device_id:
        :return:
        """
        subprocess.run(["adb", "-s", self.device_id, "kill-server"])
        time.sleep(2)

    def click_button(self, x, y, timesleep=2):
        """
        点击坐标位置
        :param device_id:
        :param x:
        :param y:
        :return:
        """
        subprocess.run(["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)])
        time.sleep(timesleep)

    def click_back(self):
        """
        返回
        :param
        :return:
        """
        print("准备点击返回...")
        subprocess.run(["adb", "-s", self.device_id, "shell", "input", "keyevent", "BACK"])

    def screenshot(self, path):
        """
        屏幕截图
        :param device_id:
        :param path:
        :return:
        """
        subprocess.run(["adb", "-s", self.device_id, "shell", "screencap", "-p", path])
        time.sleep(2)

    def swipe(self, x1, y1, x2, y2):
        """
        滑动屏幕，从（x1,y1）到（x2,y2）
        :param device_id:
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :return:
        """
        subprocess.run(["adb", "-s", self.device_id, "shell", "input", "swipe", x1, y1, x2, y2])
        time.sleep(2)

    def open_for_appid(self, app_id):
        """
        根据urlscheme打开微信小程序
        :return:
        """
        # url_scheme = f'weixin://dl/business/?link=pages/hotel-detail/standard-detail/index.html?spmUrl=181.7437890.hotelItem.item_2&wirelessStraightField=%7B%22listAdultNum%22%3A2%2C%22listCacheTime%22%3A0%2C%22listCheckIn%22%3A%222023-12-24%22%2C%22listCheckOut%22%3A%222023-12-25%22%2C%22listLowestHid%22%3A515920010788%2C%22listPrice%22%3A18000%2C%22listRateGmtTime%22%3A20231222041500%2C%22listRateId%22%3A9565385183788%2C%22listRateKey%22%3A%229565385183788%22%2C%22listTimestamp%22%3A1703213406352%2C%22searchId%22%3A%22599b39c8f0034c86bbdf1692d7961ebd%22%7D&checkIn=2023-12-24&adultNum=2&pre_pageVersion=4.3.2-flight&supportPreFetch=true&ttid=12wechat000002608&hid=0&shid=53858270&spm=181.7437890.hotelItem.item_0&abResultMap=%7B%22detail_opt_202307%22%3A%22C%22%7D&jumpToNewDetail=false&_fli_newpage=1&interChangePrice=0&searchId=599b39c8f0034c86bbdf1692d7961ebd&cityCode=110100&price=18000&cityName=%E5%8C%97%E4%BA%AC%E5%B8%82&checkOut=2023-12-25&scene=0'
        # print(url_scheme)
        try:
            print('==')
            subprocess.run(["adb", "-s", self.device_id, "shell", "am", "start", "-n",
                            f"com.tencent.mm/.plugin.appbrand.ui.AppBrandUI", "--ez", "extra_launch_from_mini_program",
                            "true", "--es", "extra_enter_scene", "from_chatting", "--es", "app_id", app_id])
            print('=')
        except:
            print('===')
            print(traceback.format_exc())
        # subprocess.run(['adb', 'shell', 'am', 'broadcast', '-a', 'com.tencent.mm.plugin.openapi.Intent.ACTION_HANDLE_APP_REGISTER', '--es', 'appId', app_id])

    def convert_to_xml(self):
        """
        使用 adb 截取当前界面的 XML
        :param :
        :return:
        """
        xml_dump_path = os.path.join(tempfile.gettempdir(), "ui_dump.xml")
        print(xml_dump_path)
        subprocess.run(["adb", "-s", self.device_id, "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"])
        # diff_info = subprocess.check_output(
        #     ["adb", "-s", self.device_id, "shell", "diff", "/sdcard/ui_dump.xml", "/sdcard/ui_dump_error.xml"]).decode(
        #     "utf-8")
        # print(diff_info)
        subprocess.run(["adb", "-s", self.device_id, "pull", "/sdcard/ui_dump.xml", xml_dump_path])
        return xml_dump_path

    def is_wechat_open(self, wechat_name):
        """
        获取当前窗口信息，判断是不是微信app
        :return:
        """
        window_info = subprocess.check_output(
            ["adb", "-s", self.device_id, "shell", "dumpsys", "window", "windows"]).decode("utf-8")
        # window_info = subprocess.check_output(
        #     ["adb", "-s", self.device_id, "shell", "dumpsys", "window", "|", "findstr" "mCurrentFocus"]).decode("utf-8")
        # 提取包名信息
        print(window_info)
        match = re.search(r"mObscuringWindow=Window\{[^/]+/([^/\s]+)}", window_info)
        if match:
            current_package = match.group(1)
            return current_package == wechat_name
        else:
            return False
