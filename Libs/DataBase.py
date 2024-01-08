# -*- coding: utf-8 -*-
# time: 2023/12/21 18:14
# file: DataBase.py
# author: ZPYin
import allure


class SQL(object):

    @allure.step("Create a new connection of database.")
    def __init__(self, host="localhost", user="root", password="", db=""):
        """
        初始化
        :param host: IP
        :param user: 用户名
        :param password: 密码
        :param db: 数据库名
        """
        self._host = host
        self._user = user
        self._password = password
        self._database = db
        self.con = cx_Oracle
