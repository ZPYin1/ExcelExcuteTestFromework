# -*- coding: utf-8 -*-
# time: 2023/12/21 16:31
# file: Assert.py
# author: ZPYin
import logging

import allure
from selenium.common import NoSuchElementException

_logger = logging.getLogger(__name__)


@allure.step("Assert equals")
def Equal(actual, expect):
    assert actual == expect


@allure.step("Assert value in")
def In(actual, expect):
    assert actual in expect


@allure.step("Assert Not equal")
def NotEqual(actual, expect):
    assert actual != expect


@allure.step("Assert value Not In")
def NotIn(actual, expect):
    assert actual not in expect

def elemExist(driver, locator):
    try:
        driver.find_element(*locator)
        return True
    except NoSuchElementException:
        return False