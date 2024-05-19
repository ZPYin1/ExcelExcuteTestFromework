# -*- coding: utf-8 -*-
# time: 2023/12/21 18:14
# file: DataBase.py
# author: ZPYin
import logging

import allure
import cx_Oracle

import pymysql

_logger = logging.getLogger(__name__)


def tranf_str(spllitwd, *args):
    res = ''
    temp = []
    for word in args:
        temp.append(word)
    res = spllitwd.join(temp)
    return res


class MySQLBase(object):

    @allure.step("Create a new connection of database.")
    def __init__(self, host="localhost", user="root", password="", db="", port=3306):
        """
        MySQL 连接
        :param host: IP
        :param user: 用户名
        :param password: 密码
        :param db: 数据库
        :param port: 接口
        """
        self._host = host
        self._user = user
        self._password = password
        self._db = db
        self._port = port
        self.__conn = None
        self.__cursor = None

    def open_conn(self):
        try:
            _logger.info(f"开始连接MySQL数据库 {self._host} {self._db}")
            self.__conn = pymysql.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._db,
                port=self._port
            )
            self.__cursor = self.__conn.cursor()
        except pymysql.Error as e:
            _logger.error(f"连接MySQL数据库失败 {self._host} {self._db}")
            raise e

    def fetchone(self, sql):
        self.open_conn()
        self.__cursor.execute(sql)
        return self.__cursor.fetchone()

    def fetchall(self, sql):
        self.open_conn()
        self.__cursor.execute(sql)
        return self.__cursor.fetchall()

    def exec(self, sql):
        self.open_conn()
        try:
            # 如果连接和游标存在，执行 SQL 语句并提交事务
            if self.__conn and self.__cursor:
                self.__cursor.execute(sql)
                self.__conn.commit()
        except Exception as ex:
            # 如果发生异常，回滚事务并记录错误日志
            self.__conn.rollback()
            _logger.error(f"SQL 执行失败 {sql}")
            _logger.error(f"SQL 执行失败 {ex.__str__()}")
            raise ex

    def __del__(self):
        # 关闭游标和连接
        if self.__cursor is not None:
            self.__cursor.close()
        if self.__conn is not None:
            self.__conn.close()


class OracleBase():
    # 老版 Oracle 专用 11g

    def __init__(self, hostname, username, pwd, db):
        self._hostname = hostname
        self._username = username
        self._pwd = pwd
        self._db = db
        self.__conn = None
        self.__cursor = None

    def open_conn(self):
        con_info = tranf_str('/', self._username, tranf_str('@', self._pwd, self._hostname), )
        try:
            _logger.info(f"开始连接 {con_info}")
            self.__conn = cx_Oracle.connect(con_info)
            self.__cursor = self.__conn.cursor()
        except Exception as e:
            _logger.error(f"连接 Oracle 失败 {con_info}")
            raise e

    def fetchall(self, statrment, **paraments):
        self.open_conn()
        rs = None
        try:
            # 操作数据库（SQL语句不需要；号）
            self.__cursor.execute(statrment, paraments)
            rs = self.__conn.fetchall()
        except Exception as e:
            _logger.error(f"查询失败 {statrment}")
        return rs

    def fetchone(self, statrment, **paraments):
        self.open_conn()
        rs = None
        try:
            # 操作数据库（SQL语句不需要；号）
            self.__cursor.execute(statrment, paraments)
            rs = self.__conn.fetchone()
        except Exception as e:
            _logger.error(f"查询失败 {statrment}")

        if rs:
            return rs
        else:
            return None

    def exec_update(self, statement, **paraments):
        self.open_conn()
        try:
            self.__cursor.execute(statement, paraments)
            self.__cursor.commit()
        except Exception as e:
            pass
        finally:
            rowcount = self.__cursor.rowcount
        return rowcount

    def callsp(self, proc, *params):
        self.open_conn()
        # construct parament list
        param_array = ()
        for param in params:
            p = self.__cursor.var(param.param_type)
            print(p)
            if not param.out:
                p.setvalue(0, param.value)
            param_array += p
            # call store procedure
        try:
            self.__cursor.callproc(proc, param_array)
            for i, param in enumerate(params):
                if param.out:
                    param.value = param_array[i].getvalue()
        except Exception as e:
            print(e)


def SQLset(config, db):
    dbase = None
    try:
        if config['Type'] == 'Oracle':
            dbase = OracleBase(hostname=config['dsn'], username=config['username'],
                               pwd=config['password'], db=db)
        elif config['Type'] == 'Mysql':
            dbase = MySQLBase(host=config['dsn'].split(':')[0], user=config['username'],
                              password=config['password'], db=db,
                              port=config['dsn'].split(':')[1])
    except Exception as e:
        _logger.error("can not this database %s" % e.__str__())
        raise e
    return dbase
