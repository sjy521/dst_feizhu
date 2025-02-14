import subprocess
import sys
import os


def kill_existing_process(key):
    try:
        result = subprocess.run(
            ["pgrep", "-f", f"{key}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.stdout:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error killing process: {e}")


# 启动adb_driver.py
def start_adb_driver(key):
    try:
        if key == "main.py":
            log_file = "/root/bgProjects/fliggy-mobile-control/logs/main.log"
            command = [
                "/root/bgProjects/fliggy-mobile-control/venv/bin/python3",
                "/root/bgProjects/fliggy-mobile-control/main.py",
            ]
            with open(log_file, "a") as log:
                subprocess.Popen(command, stdout=log, stderr=log)
        elif key == "fliggy-build-order-web-1.0.jar":
            log_file = "/root/bgProjects/fliggy-build-order/logs/appout.log"
            command = [
                "java", "-jar",
                "/root/bgProjects/fliggy-build-order/fliggy-build-order-web-1.0.jar",
            ]
            with open(log_file, "a") as log:
                subprocess.Popen(command, stdout=log, stderr=log)
    except Exception as e:
        print(f"Error starting adb_driver.py: {e}")


def main():
    for key in ["fliggy-build-order-web-1.0.jar", "main.py"]:
        if kill_existing_process(key) is False:
            start_adb_driver(key)


if __name__ == "__main__":
    main()
