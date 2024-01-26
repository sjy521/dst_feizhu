import os
import yaml
import logging
import logging.config as log_config
from dynaconf import settings


def setup_logging(default_path=settings.LOGGING, default_level=logging.DEBUG):
    path = os.path.abspath(os.path.join(os.getcwd(), "..")) + default_path
    if os.path.exists(path):
        with open(path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            log_config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

