# -*- coding: utf-8 -*-
# time: 2024/1/4 12:07
# file: Baidu.py
# author: ZPYin
import time

import allure

from Libs.Locators import BaiDu
from Libs.Selenium import WebDriver

HP = BaiDu.HomePage


def pressence_of_element_located(locator):
    def _predicate(driver):
        return driver._find_element(*locator)

    return _predicate


@allure.step("search")
def search(driver: WebDriver, keyword):
    """
    功能：在 https://www.baidu.com 页面进行输入查询操作
    :param driver:
    :param keyword: 关键字
    :return: None
    """
    driver(HP.Search_input).send_keys(keyword)
    driver(HP.Search_btn).click()
    time.sleep(10)

