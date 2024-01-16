import logging
import pymysql
from dynaconf import settings
from log_model.set_log import setup_logging

setup_logging(default_path=settings.LOGGING)


class SqlModel:
    def __init__(self, host, user, port, pd, db):
        self.host = host
        self.user = user
        self.port = port
        self.pd = pd
        self.db = db
        self.conn = None
        self.cursor = None

    def get_cursor(self):
        if self.cursor is None or self.conn is None:
            self.conn = pymysql.connect(
                host=self.host,  # MySQL服务器地址
                user=self.user,  # 用户名
                port=self.port,
                password=self.pd,  # 密码
                database=self.db  # 数据库名称
            )
            self.cursor = self.conn.cursor()
            logging.info("mysql 创建连接成功")
            return self.cursor
        else:
            return self.cursor

    def select_sql(self, sql):
        """
        根据sql语句查询数据库，返回查询后的所有结果
        :param sql:
        :return: list
        """
        self.get_cursor().execute(sql)
        datalist = []
        results = self.get_cursor().fetchall()
        if len(results) > 0:
            field_names = [field[0] for field in self.get_cursor().description]
        else:
            return None
        for result in results:
            resdict = {}
            for field, value in zip(field_names, result):
                resdict[field] = value
            datalist.append(resdict)
        logging.info("[{}]语句查询到了[{}]条结果".format(sql, len(results)))
        return datalist

    def insert_sql(self, sql, values):
        """
        根据sql语句插入数据
        :param sql:
        :param values:
        :return:
        """
        self.cursor.execute(sql, values)
        res = self.conn.commit()
        logging.info("[{}]语句插入了[{}]条结果".format(sql, self.cursor.rowcount))
        return res

    def update_sql(self, sql, values):
        """
        根据sql语更新数据
        :param sql:
        :param values:
        :return:
        """
        self.cursor.execute(sql, values)
        res = self.conn.commit()
        logging.info("[{}]语句更新了[{}]条结果".format(sql, self.cursor.rowcount))
        return res
