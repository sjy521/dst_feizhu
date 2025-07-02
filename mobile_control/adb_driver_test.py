import cv2
import numpy as np
import subprocess
import os
from typing import Optional


class ScreenshotClickBot:
    def __init__(self, device_id: str):
        self.device_id = device_id

    def adb(self, *args):
        cmd = ["adb", "-s", self.device_id] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
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

    def click_template(self, template_path: str, threshold: float = 0.8) -> bool:
        coords = self.find_template(template_path, threshold)
        if coords:
            self.adb("shell", "input", "tap", str(coords[0]), str(coords[1]))
            print(f"Clicked at: {coords}")
            return True
        else:
            print("No match found for template.")
            return False

    def check_template(self, template_path: str, threshold: float = 0.8) -> bool:
        coords = self.find_template(template_path, threshold)
        if coords:
            print("true")
            return True
        else:
            print("false")
            return False


# 示例用法（将其放入 main 函数或脚本中运行）
if __name__ == "__main__":
    device_id = "4TUGJN79S89HKBOF"
    template_path = "../template_model/订单按钮.jpg"
    dingdan = "../template_model/订单页.jpg"
    bot = ScreenshotClickBot(device_id)
    if not bot.check_template(dingdan):
        bot.click_template(template_path)
