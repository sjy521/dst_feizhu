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
            log_file = "/home/superadm/feizhu/dst_feizhu/logs/main.log"
            command = [
                "python3",
                "main.py",
            ]
            with open(log_file, "a") as log:
                subprocess.Popen(command, stdout=log, stderr=log, cwd="/home/superadm/feizhu/dst_feizhu")
        elif key == "fliggy-build-order-web-1.0.jar":
            log_file = "logs/appout.log"
            command = [
                "java", "-jar",
                "fliggy-build-order-web-1.0.jar",
            ]
            with open(log_file, "a") as log:
                subprocess.Popen(command, stdout=log, stderr=log, cwd="/home/superadm/feizhu/build_order")
    except Exception as e:
        print(f"Error starting adb_driver.py: {e}")


def main():
    for key in ["fliggy-build-order-web-1.0.jar", "main.py"]:
        if kill_existing_process(key) is False:
            start_adb_driver(key)


if __name__ == "__main__":
    main()
