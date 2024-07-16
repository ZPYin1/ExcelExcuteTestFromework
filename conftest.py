# -*- coding: utf-8 -*-
# time: 2024/1/8 10:32
# file: conftest.py
# author: ZPYin
import logging

import pytest

from Libs.Selenium import WebDriver
from imported import ENV

_logger = logging.getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
def driver():
    driver = WebDriver(ENV.browser_select)
    driver.implicitly_wait(10)
    driver.maximize_window()
    yield
    driver.quit()


@pytest.fixture(scope="function", autouse=True)
def clearcookies(driver: WebDriver):
    driver.delete_all_cookies()
    yield
    # 刷新页面，减少缓存
    driver.refresh()
    driver.delete_all_cookies()
