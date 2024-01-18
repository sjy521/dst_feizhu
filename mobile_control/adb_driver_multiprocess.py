import time
from multiprocessing import Pool
from dynaconf import settings

from log_model.set_log import setup_logging
from sql_tool.sql_model import SqlModel
from util.ding_util import send_abnormal_alarm_for_dingding
from util.fliggy_util import FliggyModel


def select_device():
    sql_model = SqlModel(host=settings.MYSQL_HOST, user=settings.MYSQL_USERNAME, port=settings.MYSQL_PORT,
                         pd=settings.MYSQL_PASSWORD, db=settings.MYSQL_DB)
    return sql_model.select_sql("select * from devices_library where state = 1")


def run(device):
    device_id = device.get("device_id")
    pay_password = device.get("pay_password")
    fliggy_model = FliggyModel(device_id)
    fliggy_model.open_mini_feizhu()
    pay_num = 0
    while True:
        # 定位当前页面为订单页
        fliggy_model.goto_target_page()
        # 支付订单
        pay_status = fliggy_model.pay_order(pay_password)
        if pay_status:
            pay_num += 1
            if pay_num % 5 == 0:
                send_abnormal_alarm_for_dingding("已经连续支付成功{}单".format(pay_num))
            continue
        pay_num = 0
        fliggy_model.del_order()
        time.sleep(10)
        fliggy_model.refresh()

        # input("点击回车继续")


if __name__ == '__main__':
    setup_logging(default_path=settings.LOGGING)
    devices = select_device()
    pool = Pool(2)
    pool.map(run, devices)