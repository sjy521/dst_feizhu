# coding:utf-8
import logging.config
import os

import flask
import yaml
from dynaconf import settings


app = flask.Flask(__name__)


@app.route('/ok')
def ok():
    return 'ok'


@app.route('/download/<file_name>', methods=['get', 'post'])
def download(file_name):
    res = flask.send_file("/root/bgProjects/fliggy-mobile-control/invoice_control/{}.csv".format(file_name), as_attachment=True)
    return res


def setup_logging(default_path=settings.LOGGING, default_level=logging.DEBUG, env_key="LOG_CFG"):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == '__main__':
    config_env = os.environ.get('ENV_FOR_DYNACONF')
    if config_env is None:
        config_env = 'none'
    print('加载配置文件环境:' + config_env)
    setup_logging(default_path=settings.LOGGING)
    app.run(debug=settings.IS_DEBUG, port=8084, host='0.0.0.0', threaded=True)

