# -*- coding: utf-8 -*-
# time: 2024/1/4 13:50
# file: test_Baidu.py
# author: ZPYin
from Libs.Selenium import WebDriver


class TestCases:

    def setup(self):
        self.driver = WebDriver("Edge")