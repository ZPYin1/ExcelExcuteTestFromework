# -*- coding: utf-8 -*-
# time: 2024/1/4 13:50
# file: test_Baidu.py
# author: ZPYin
import pytest

from Libs.Selenium import WebDriver
from Libs.Utilities import data_from_excel
from Steps.Baidu import search
from imported import ENV


class TestCases:

    def setup(self):
        self.driver = WebDriver("Edge")
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()

    def tear_down(self):
        self.driver.close()

    @pytest.mark.new
    @pytest.mark.parametrize(*data_from_excel(ENV.data_path, "baidu"))
    def test_001_Baidu_search(self, keyword):
        self.driver.get(ENV.base_url)
        search(self.driver, keyword)
        self.driver.attach_screenshot("search %s Page" % keyword)
        title = self.driver.title
        keyword.replace(" ", "")
        assert title.__contains__(keyword)
