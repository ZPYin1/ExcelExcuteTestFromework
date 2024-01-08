# -*- coding: utf-8 -*-
# time: 2024/1/4 13:50
# file: test_Example.py
# author: ZPYin
import allure
import pytest
from pytest import mark
from selenium.webdriver.common.by import By

from Libs import Assert
from Libs.Selenium import WebDriver
from Libs.Utilities import data_from_excel
from imported import *


@pytest.mark.smoking
@pytest.mark.regression
@pytest.mark.skipif(ENV >= PROD, reason="Not test in product environment.")
@allure.title("会在生成环境上跳过执行的例子")
def test_smoking_test_will_skipped_on_prod_env():
    """
    通常有多个测试环境，如：开发，测试，预发布，生成环境
    但有些测试用例如果在生产环境上被执行，会污染生产环境的数据，所以不能在生产环境上被执行
    这条用例演示了同一条测试用例可以根据不同的环境被执行或体哦爱国
    :return:
    """
    Assert.Equal(1, 1)


@mark.smoking
@allure.title("不同环境可以引入不同环境配置的测试用例")
def test_diff_env_with_diff_cfg():
    """
    通常测试环境的不同，也会带来不同环境上配置的差异，比如最基础 base_url 的不同
    这样可以通过配置环境来达到测试用例的复用
    :return:
    """
    driver = WebDriver("Edge")
    driver.get(ENV.base_url)
    driver.attach_screenshot("Different base_url")
    driver.quit()


@allure.title("这是一个给空间没有找到的异常测试用例")
def test_element_not_found_error():
    """
    这个测试在执行过程中找不到对应控件，将会自动截图
    :return:
    """
    driver = WebDriver("Edge")
    driver.get(ENV.base_url)
    driver.find_element(By.ID, "dddddd").click()
    driver.quit()


@allure.title("这是一个从Excel读取数据然后相加的测试用例")
@pytest.mark.parametrize(*data_from_excel(ENV.data_path, "Add"))
def test_add(x, y, result):
    """
    这个从 TestData.xlsx 的 Add 工作表中获取参数，并执行测试用例
    :param x:
    :param y:
    :param result:
    :return:
    """
    Assert.Equal(actual=x + y, expect=result)
