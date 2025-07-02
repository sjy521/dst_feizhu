import os
import yaml
import logging
import logging.config as log_config
from dynaconf import settings


def setup_logging(default_path=settings.LOGGING, default_level=logging.DEBUG):
    path = os.path.abspath(os.path.join(os.getcwd(), "..")) + default_path
    if os.path.exists(path):
        print("加载了日志文件")
        logging.info("加载了日志文件")
        with open(path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            log_config.dictConfig(config)
    else:
        print("没有加载日志文件")
        logging.info("没有加载日志文件")
        logging.basicConfig(level=default_level)

