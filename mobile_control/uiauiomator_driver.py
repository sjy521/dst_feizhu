import uiautomator2 as u2
import time

# 连接到设备
d = u2.connect("192.168.52.124")
try:
    element = d(resourceId="//text")
    if element.exists:
        bounds = element.bounds()
        print(bounds["left"], bounds["top"])
    else:
        print(f"Element with resource ID '' not found.")
except Exception as e:
    print(f"Error: {e}")
