import subprocess
import sys
import os

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))
from util.interface_util import select_device, update_device_run_status


# 查询 MySQL 数据库，获取设备ID对应的参数
def get_db_param():
    devices = []
    busy_devices = select_device()
    if len(busy_devices) > 0:
        for busy_device in busy_devices:
            # run_status = int(busy_device.get("runStatus"))
            # if run_status in [0]:
            devices.append(busy_device)
    return devices


def kill_existing_process(device_id):
    try:
        result = subprocess.run(
            ["pgrep", "-f", f"{device_id}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.stdout:
            # 获取进程ID并杀掉
            pids = result.stdout.decode().strip().split("\n")
            # 遍历所有 PID 进行 kill
            for pid in pids:
                subprocess.run(["kill", "-9", pid])
                print(f"Killed existing process with PID {pid} for device ID {device_id}.")
        else:
            print(f"No existing process found for device ID {device_id}.")
    except Exception as e:
        print(f"Error killing process: {e}")


# 启动adb_driver.py
def start_adb_driver(device_id, process_id):
    try:
        log_file = f"/root/bgProjects/fliggy-mobile-control/logs/adb_driver_{device_id}.log"
        venv_activate = "venv/bin/activate_this.py"
        command = [
            "/venv/bin/python3",
            "mobile_control/adb_driver.py",
            device_id
        ]
        subprocess.run([venv_activate], shell=True, check=True, cwd="/root/bgProjects/fliggy-mobile-control")
        with open(log_file, "a") as log:
            subprocess.Popen(command, stdout=log, stderr=log, cwd="/root/bgProjects/fliggy-mobile-control")
        print(f"adb_driver.py started for device ID {device_id}.")

        if process_id == 0:
            log_file = f"/root/bgProjects/fliggy-mobile-control/logs/snatching_order_plus_{device_id}.log"
            command = [
                "venv/bin/python3",
                "order_control/snatching_order_plus.py",
                device_id
            ]
            subprocess.run([venv_activate], shell=True, check=True, cwd="/root/bgProjects/fliggy-mobile-control")
            with open(log_file, "a") as log:
                subprocess.Popen(command, stdout=log, stderr=log, cwd="/root/bgProjects/fliggy-mobile-control")
            print(f"snatching_order_plus.py started for device ID {device_id}.")
        elif process_id == 1:
            log_file = f"/root/bgProjects/fliggy-mobile-control/logs/abnormal_order_{device_id}.log"
            command = [
                "venv/bin/python3",
                "order_control/abnormal_order.py",
                device_id
            ]
            subprocess.run([venv_activate], shell=True, check=True, cwd="/root/bgProjects/fliggy-mobile-control")
            with open(log_file, "a") as log:
                subprocess.Popen(command, stdout=log, stderr=log, cwd="/root/bgProjects/fliggy-mobile-control")
            print(f"abnormal_order.py started for device ID {device_id}.")
        elif process_id == 2:
            log_file = f"/root/bgProjects/fliggy-mobile-control/logs/comprehensive_order_{device_id}.log"
            command = [
                "venv/bin/python3",
                "order_control/comprehensive_order.py",
                device_id
            ]
            subprocess.run([venv_activate], shell=True, check=True, cwd="/root/bgProjects/fliggy-mobile-control")
            with open(log_file, "a") as log:
                subprocess.Popen(command, stdout=log, stderr=log, cwd="/root/bgProjects/fliggy-mobile-control")
            print(f"comprehensive_order.py started for device ID {device_id}.")
        update_device_run_status(device_id, 1)
    except Exception as e:
        print(f"Error starting adb_driver.py: {e}")


def main():
    # 获取数据库参数
    db_params = get_db_param()

    if len(db_params) == 0:
        return

    for device in db_params:
        # 检查进程是否已经在运行
        if int(device.get("runStatus")) == 0:
            kill_existing_process(device.get("deviceId"))
            start_adb_driver(device.get("deviceId"), int(device.get("processList")))
        if int(device.get("runStatus")) in [3,4]:
            kill_existing_process(device.get("deviceId"))


if __name__ == "__main__":
    main()
