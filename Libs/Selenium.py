#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/25 14:09
# @Author  : ZP Y
# @File    : Selenium.py
# @Software: PyCharm
import logging
import os.path
from typing import List
from uuid import uuid1

from selenium import webdriver
from selenium.webdriver import Chrome, Firefox, Edge, FirefoxProfile
import allure
from selenium.common import NoSuchElementException
from selenium.webdriver.common import action_chains, alert
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote import webelement, switch_to
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import select
from selenium.webdriver.support.wait import WebDriverWait

from Libs.Configs import TEMPORARY_PATH, LOCATOR_FILES_PATH
from Libs.Utilities import get_operating_system

_logger = logging.getLogger(__name__)


# 对整个给 selenium 进行 allure 封装，增加 DEBUG 信息，增加报告信息
class WebElement(webelement.WebElement):

    def __init__(self, parent, _id):
        super(WebElement, self).__init__(parent=parent, id_=_id)

    def __call__(self, locator) -> WebElement:
        return self.find_element_by_locator(locator)

    @allure.step("Click the element.")
    def click(self) -> None:
        super(WebElement, self).click()

    @allure.step("Clear the text if it's a text entry element.")
    def clear(self) -> None:
        super(WebElement, self).clear()

    @allure.step("Simulate typing into the element.")
    def send_keys(self, *value) -> None:
        super(WebElement, self).send_keys(value)

    @allure.step("Simulate select into the element")
    def select(self, visable_text):
        _ = Select(self)
        _.select_by_visible_text(visable_text)

    def find_element_by_locator(self, locator) -> WebElement:
        @allure.step("Find a child element with a locator.[Chr:{0}]".format(self._id))
        def _(by, value, name, comment):
            return self.find_element(by, value)

        return _(by=locator.by, value=locator.value, name=locator.name, comment=locator.comment)

    def find_elements_by_locator(self, locator) -> List[WebElement]:
        def _(by, value, name, comment):
            return super(WebElement, self).find_elements(by, value)

        return _(by=locator.by, value=locator.value, name=locator.name, comment=locator.comment)

    def find_element(self, by=By.ID, value=None) -> WebElement:
        try:
            return self.find_element(by=by, value=value)
        except NoSuchElementException:
            self.catch_no_such_element_exception(by=by, value=value)
            raise NoSuchElementException("Unable to locate the child element.")

    @allure.step("No Such Element Exception")
    def catch_no_such_element_exception(self, **kwargs):
        self.attach_screenshot("No Such Element Exception")

    def attach_screenshot(self, comment):
        filename = "{uuid}.png".format(uuid=uuid1())
        filepath = os.path.join(TEMPORARY_PATH, filename)
        self.screenshot(filepath)
        allure.attach.file(filepath, comment, allure.attachment_type.PNG)

    @allure.step("Move to element")
    def move_to_element(self):
        _ = ActionChains(self._parent)
        return _.move_to_element(to_element=self).perform()

    @allure.step("Move to element and click")
    def move_to_element_click(self):
        _ = ActionChains(self._parent)
        return _.move_to_element(to_element=self).click(on_element=self).perform()


class WebDriver(object):

    @allure.step("Creates a new instance of the driver")
    def __init__(self, driver_name, **kwargs):
        driver = driver_name
        system = get_operating_system()
        if system == "Windows":
            if driver_name in ["chrome", "edge", "firefox"]:
                if driver_name == "chrome":
                    driver = Chrome
                elif driver_name == "firefox":
                    driver = Firefox
                else:
                    driver = Edge
                driver._web_element_cls = WebElement
            else:
                raise NotImplementedError(f"{driver_name} is not support now")
            self._driver = driver()
        elif system == "Linux":
            if driver_name in ["chrome", "firefox"]:
                option = None
                profile = None
                if driver_name == "firefox":
                    options = webdriver.FirefoxOptions()
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--headless')
                    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain")
                    # browser = webdriver.Firefox(options=options)
                    profile = FirefoxProfile()
                    profile.set_preference('intl.accept_languages', 'en-us, en')
                    driver = Firefox
                    driver._web_element_cls = WebElement
                    self._driver=Firefox(options=options,firefox_profile=profile)
                else:
                    option = webdriver.ChromeOptions()
                    option.add_argument('--disable-gpu')
                    option.add_argument('--headless')
                    option.add_argument('--no-sandbox')
                    option.add_argument('--disable-extensions')
                    option.add_argument('--disable-dev-shm-usage')
                    option.add_argument('lang=en-us')
                    driver = Chrome
                    driver._web_element_cls = WebElement
                    self._driver = driver(options=option)
            else:
                _logger.error("{driver_name} is not support now")
                raise NotImplementedError(f"{driver_name} is not support now")
        else:
            raise NotImplementedError(f"{system} is not support now")

            # if driver == "edge":
            #     self._driver = driver(service_log_path=os.path.join(LOCATOR_FILES_PATH, "Chrom.log"))
            # elif driver == "firefox":
            #     self._driver = driver(service=Service(log_path=os.path.join(LOCATOR_FILES_PATH, "geckodriver.log")))
            # else:

        self._driver._switch_to = SwitchTo(self._driver)

    def __call__(self, locator):
        return self.find_element_by_locator(locator)

    @allure.step
    def _get_cdp_detatils(self):
        _logger.debug("Call <_get_cdp_details>")
        return self._driver._get_cdp_details()

    @allure.step
    def _unwrap_value(self, value):
        _logger.debug("Call <_unwrap_value>")
        _logger.debug("value: %s" % value)
        return self._driver._unwrap_value(value)

    @allure.step
    def _wrap_value(self, value):
        _logger.debug("Call <_wrap_value>")
        _logger.debug("value: %s" % value)
        return self._driver._wrap_value(value)

    @allure.step
    def add_cookie(self, cookies_dice):
        _logger.debug("Call <add_cookie>")
        _logger.debug("cookies_dice: %s" % cookies_dice)
        return self._driver.add_cookie(cookies_dice)

    @allure.step
    def add_credential(self, *args, **kwargs):
        _logger.debug("Call <add_credential>")
        _logger.debug("args: %s" % args)
        _logger.debug("kwarg: %s" % kwargs)
        return self._driver.add_credential(*args, **kwargs)

    @allure.step
    def add_virtual_authenticator(self, options):
        _logger.debug("Call <add_virtual_authenticator>")
        _logger.debug("options: %s" % options)
        return self._driver.add_virtual_authenticator(options)

    @allure.step("For one step backward in the browser history")
    def back(self):
        _logger.debug("Call <back>")
        return self._driver.back()

    @allure.step("Closes the current window")
    def close(self):
        _logger.debug("Call <close>")
        return self._driver.close()

    @allure.step
    def create_web_element(self, element_id):
        _logger.debug("Call <create_web_element>")
        _logger.debug("element_id: %s" % element_id)
        return self._driver.create_web_element(element_id)

    @allure.step
    def delete_all_cookies(self):
        _logger.debug("Call <delete_all_cookies>")
        return self._driver.delete_all_cookies()

    @allure.step
    def delete_cookie(self, name):
        _logger.debug("Call <delete_cookie>")
        return self._driver.delete_cookie(name)

    @allure.step
    def execute_async_script(self, script, **args):
        _logger.debug("Call <execute_async_script>")
        _logger.debug("script: %s" % script)
        _logger.debug("args: %s" % args)
        return self._driver.execute_async_script(script, *args)

    @allure.step("Goes one step forward in the browser history.")
    def forward(self):
        _logger.debug("Call <forward>")
        return self._driver.forward()

    @allure.step("Full screen window.")
    def fullscreen_window(self):
        _logger.debug("Call <fullscreen_window>")
        return self._driver.fullscreen_window()

    @allure.step("Loads a web page in the current browser session")
    def get(self, url):
        _logger.debug("Call <get>")
        _logger.debug("url: %s" % url)
        return self._driver.get(url)

    @allure.step("Get a single cookies by name.")
    def get_cookie(self, name):
        _logger.debug("Call <get_cookie>")
        _logger.debug("name: %s" % name)
        return self._driver.get_cookie(name)

    @allure.step("Get cookies.")
    def get_cookies(self):
        _logger.debug("Call <get_cookies>")
        return self._driver.get_cookies()

    @allure.step
    def get_credentials(self, *args, **kwargs):
        _logger.debug("Call <get_credentials>")
        _logger.debug("arge: %s" % args)
        _logger.debug("kwargs: %s" % kwargs)
        return self._driver.get_credentials(*args, **kwargs)

    @allure.step
    def get_log(self, log_type):
        _logger.debug("Call <get_log>")
        _logger.debug("log_type: %s" % log_type)
        return self._driver.get_log(log_type)

    @allure.step
    def get_pinned_script(self):
        _logger.debug("Call <get_pinned_scripts>")
        return self._driver.get_pinned_scripts()

    @allure.step("Get screenshot as bases64")
    def get_screenshot_as_base64(self):
        _logger.debug("Call <get_screenshot_as_base64>")
        return self._driver.get_screenshot_as_base64()

    @allure.step("Get screenshot as file")
    def get_screenshot_as_file(self, filename):
        _logger.debug("Call <get_screenshot_as_file>")
        _logger.debug("filename: %s" % filename)
        return self._driver.get_screenshot_as_file(filename)

    @allure.step("Get screenshot as png")
    def get_screenshot_as_png(self):
        _logger.debug("Call <get_screenshot_as_png>")
        return self._driver.get_screenshot_as_png()

    @allure.step
    def get_window_rect(self):
        _logger.debug("Call <get_window_rect>")
        return self._driver.get_window_rect()

    @allure.step
    def implicitly_wait(self, time_to_wait):
        _logger.debug("Call <implicitly_wait>")
        _logger.debug("time_to_wait: %s" % time_to_wait)
        return self._driver.implicitly_wait(time_to_wait)

    @allure.step("Maximizes the current window that webdriver is using.")
    def maximize_window(self):
        _logger.debug("Call <maximize_window>")
        return self._driver.maximize_window()

    @allure.step("Minimizes the current window that webdriver is using.")
    def minimize_window(self):
        _logger.debug("Call <minimize_window>")
        return self._driver.minimize_window()

    @allure.step("Closes the browser and shuts down the Driver.")
    def quit(self):
        _logger.debug("Call <quit>")
        self._driver.close()
        return self._driver.quit()

    @allure.step("Refresh the current page.")
    def refresh(self):
        _logger.debug("Call <refresh>")
        return self._driver.refresh()

    @allure.step
    def remove_all_credentials(self, *args, **kwargs):
        _logger.debug("Call <remove_all_credentials>")
        _logger.debug("args: %s" % args)
        _logger.debug("kwargs: %s" % kwargs)
        return self._driver.remove_all_credentials(*args, **kwargs)

    @allure.step
    def remove_credentials(self, *args, **kwargs):
        _logger.debug("Call <remove_credentials>")
        _logger.debug("args: %s" % args)
        _logger.debug("kwargs: %s" % kwargs)
        return self._driver.remove_credential(*args, **kwargs)

    @allure.step
    def remove_virtual_authenticator(self, *args, **kwargs):
        _logger.debug("Call <remove_virtual_authenticator>")
        _logger.debug("args: %s" % args)
        _logger.debug("kwargs: %s" % kwargs)
        return self._driver.remove_virtual_authenticator(*args, **kwargs)

    @allure.step("Get screenshot as file")
    def save_screenshot(self, filename):
        _logger.debug("Call <save_screenshot>")
        _logger.debug("filename: %s" % filename)
        return self._driver.save_screenshot(filename)

    @allure.step
    def set_page_load_timeout(self, time_to_wait):
        _logger.debug("Call <set_page_load_timeout>")
        _logger.debug("time_to_wait: %s" % time_to_wait)
        return self._driver.set_page_load_timeout(time_to_wait)

    @allure.step
    def set_script_timeout(self, time_to_wait):
        _logger.debug("Call <set_script_timeout>")
        _logger.debug("time_to_wait: %s" % time_to_wait)
        return self._driver.set_script_timeout(time_to_wait)

    @allure.step
    def set_user_verified(self, *args, **kwargs):
        _logger.debug("Call <set_user_verified>")
        _logger.debug("args: %s" % args)
        _logger.debug("kwargs: %s" % kwargs)
        return self._driver.set_user_verified(*args, **kwargs)

    @allure.step
    def start_client(self):
        _logger.debug("Call <start_client>")
        return self._driver.start_client()

    @allure.step
    def unpin(self, script_key):
        _logger.debug("Call <unpin>")
        _logger.debug("script_key: %s" % script_key)
        return self._driver.unpin(script_key)

    @allure.step
    def execute(self, driver_command, params=None):
        _logger.debug("Call <set_user_verified>")
        _logger.debug("driver_command: %s" % driver_command)
        _logger.debug("params: %s" % params)
        return self._driver.execute(driver_command, params)

    def _find_element(self, by=By.ID, value=None) -> WebElement:
        return self._driver.find_element(by=by, value=value)

    def find_element(self, by=By.ID, value=None) -> WebElement:
        try:
            return self._find_element(by, value)
        except NoSuchElementException:
            self.catch_no_such_element_exception(by=by, value=value)
            raise NoSuchElementException("Unable to locate the element")

    def catch_no_such_element_exception(self, **kwargs):
        self.attach_screenshot(f"No Such Element Exception {kwargs}")

    @allure.step("Find elements given a By strategy and locator.")
    def find_elements(self, by=By.ID, value=None) -> List[WebElement]:
        _logger.debug("Call <find_elements>")
        _logger.debug("by: %s" % by)
        _logger.debug("valur: %s" % value)
        return self._driver.find_elements(by=by, value=value)

    @allure.step
    def get_window_position(self, windowHandle="current"):
        _logger.debug("Call <get_window_position>")
        _logger.debug("windowHandle: %s" % windowHandle)
        return self._driver.get_window_position(windowHandle)

    @allure.step
    def pin_script(self, script, script_key=None):
        _logger.debug("Call <pin_script>")
        _logger.debug("script: %s" % script)
        _logger.debug("script_key: %s" % script_key)
        return self._driver.pin_script(script, script_key)

    @allure.step
    def print_page(self, print_options=None):
        _logger.debug("Call <print_page>")
        _logger.debug("print_options: %s" % print_options)
        return self._driver.print_page(print_options)

    @allure.step
    def set_window_position(self, x, y, windowHandle="current"):
        _logger.debug("Call <set_window_position>")
        _logger.debug("x: %s" % x)
        _logger.debug("y: %s" % y)
        _logger.debug("windowHandle: %s" % windowHandle)
        return self._driver.set_window_position(x, y, windowHandle)

    @allure.step
    def set_window_rect(self, x=None, y=None, width=None, height=None):
        _logger.debug("Call <set_window_rect>")
        _logger.debug("x: %s" % x)
        _logger.debug("y: %s" % y)
        _logger.debug("width: %s" % width)
        _logger.debug("height: %s" % height)
        return self._driver.set_window_rect(x, y, width, height)

    @allure.step
    def set_window_size(self, x, y, windowHandle="current"):
        _logger.debug("Call <set_window_size>")
        _logger.debug("x: %s" % x)
        _logger.debug("y: %s" % y)
        _logger.debug("windowHandle: %s" % windowHandle)
        return self._driver.set_window_size(x, y, windowHandle)

    @allure.step
    def start_session(self, capabilities, browser_profile=None):
        _logger.debug("Call <start_session>")
        _logger.debug("capabilities: %s" % capabilities)
        _logger.debug("browser_profile: %s" % browser_profile)
        return self._driver.start_session(capabilities, browser_profile)

    @property
    @allure.step("Gets application cache.")
    def application_cache(self):
        _logger.debug("Property <application_cache>")
        return self._driver.application_cache()

    @property
    @allure.step("Gets capabilities.")
    def capabilities(self):
        _logger.debug("Property <capabilities>")
        return self._driver.capabilities

    @property
    @allure.step("Gets current url.")
    def current_url(self):
        _logger.debug("Property <current_url>")
        return self._driver.current_url

    @property
    @allure.step("Gets current handle.")
    def current_window_handle(self):
        _logger.debug("Property <current_window_handle>")
        return self._driver.current_window_handle

    @property
    @allure.step("Gets desired capabilities.")
    def desired_capabilities(self):
        _logger.debug("Property <desired_capabilities>")
        return self._driver.capabilities

    @property
    @allure.step("Gets file_detector.")
    def file_detector(self):
        _logger.debug("Property <file_detector>")
        return self._driver.file_detector

    @property
    @allure.step("Gets log_types.")
    def log_types(self):
        _logger.debug("Property <log_types>")
        return self._driver.log_types

    @property
    @allure.step("Gets mobile.")
    def mobile(self):
        _logger.debug("Property <mobile>")
        return self._driver.mobile

    @property
    @allure.step("Gets name.")
    def name(self):
        _logger.debug("Property <name>")
        return self._driver.name

    @property
    @allure.step("Gets orientation.")
    def orientation(self):
        _logger.debug("Property <orientation>")
        return self._driver.orientation

    @property
    @allure.step("Gets page_source.")
    def page_source(self):
        _logger.debug("Property <page_source>")
        return self._driver.page_source

    @property
    @allure.step("Gets switch_to.")
    def switch_to(self):
        _logger.debug("Property <switch_to>")
        return self._driver.switch_to

    @property
    @allure.step("Gets timeouts.")
    def timeouts(self):
        _logger.debug("Property <timeouts>")
        return self._driver.timeouts

    @property
    @allure.step("Gets title.")
    def title(self):
        _logger.debug("Property <title>")
        return self._driver.title

    @property
    @allure.step("Gets virtual_authenticator_id.")
    def virtual_authenticator_id(self):
        _logger.debug("Property <virtual_authenticator_id>")
        return self._driver.virtual_authenticator_id

    def attach_screenshot(self, comment):
        filename = "{uuid}.png".format(uuid=uuid1())
        filepath = os.path.join(TEMPORARY_PATH, filename)
        self._driver.get_screenshot_as_file(filepath)
        allure.attach.file(filepath, comment, allure.attachment_type.PNG)

    def find_element_by_locator(self, locator) -> WebElement:
        # @allure.step("Find an element with a locator")
        def _(by, value, name, comment):
            return self.find_element(by=by, value=value)

        return _(by=locator.by, value=locator.value, name=locator.name, comment=locator.comment)

    def find_elements_by_locator(self, locator) -> List[WebElement]:
        # @allure.step("Find an elements with a locator")
        def _(by, value, name, comment):
            return self._driver.find_elements(by=by, value=value)

        return _(by=locator.by, value=locator.value, name=locator.name, comment=locator.comment)

    def wait_unit(self, method, message="", timeout=3, poll_frequency=0.5, ignored_exceptions=None):
        wait = WebDriverWait(self, timeout=timeout, ignored_exceptions=ignored_exceptions,
                             poll_frequency=poll_frequency)
        wait.until(method, message)

    def switch_handle(self, cur_hand=None):
        if cur_hand == None:
            cur_hand = self._driver.current_window_handle
        for handle in self._driver.window_handles:
            if handle != cur_hand:
                self._driver.switch_to.window(handle)

    def window_handles(self):
        return self._driver.window_handles

    def execute_script(self, script, *args):
        _logger.debug("Property <execute_script>")
        return self._driver.execute_script(script, *args)


class Alert(alert.Alert):
    def __init__(self, driver):
        super(Alert, self).__init__(driver)

    @property
    @allure.step("Gets the text of the Alert.")
    def text(self):
        return super(Alert, self).text()

    @allure.step("Dismiss the alert available.")
    def dismiss(self):
        return super(Alert, self).dismiss()

    @allure.step("Accepts the alert available.")
    def accept(self):
        return super(Alert, self).accept()

    @allure.step("Send keys to the Alert.")
    def send_keys(self, keys):
        return super(Alert, self).send_keys(keys)


class ActionChains(action_chains.ActionChains):
    def __init__(self, driver, duration=250):
        super(ActionChains, self).__init__(driver, duration)

    def move_to_element(self, to_element):
        return super(ActionChains, self).move_to_element(to_element)



class Select(select.Select):
    def __init__(self, element):
        super(Select, self).__init__(webelement=element)

    @property
    @allure.step("Gets a list of all options belonging to this select tag.")
    def options(self):
        return super(Select, self).options()

    @property
    @allure.step("Gets a list of all selected options belonging to this select tag.")
    def all_selected_options(self):
        return super(Select, self).all_selected_options()

    @property
    @allure.step("Gets the first selected options this select tag.")
    def first_selected_option(self):
        return super(Select, self).first_selected_option()

    @allure.step("Select all options that have a value matching the argument.")
    def select_by_value(self, value):
        return super(Select, self).select_by_value(value)

    @allure.step("Select the options at the given index.")
    def select_by_index(self, index):
        return super(Select, self).select_by_index(index)

    @allure.step("Select all options that display text matching the argument.")
    def select_by_visible_text(self, text):
        return super(Select, self).select_by_visible_text(text)

    @allure.step("Clear all selected entries.")
    def deselect_all(self) -> None:
        super(Select, self).deselect_all()

    @allure.step("Deselect all options that have a value matching the argument.")
    def deselect_by_value(self, value):
        return super(Select, self).deselect_by_value(value)

    @allure.step("Deselect the options at the given index.")
    def deselect_by_index(self, index):
        return super(Select, self).deselect_by_index(index)

    @allure.step("Deselect all options that display text matching the argument.")
    def deselect_by_visible_text(self, text):
        return super(Select, self).deselect_by_visible_text(text)


class SwitchTo(switch_to.SwitchTo):
    """
        element = driver.switch_to.active_element
        alert = driver.switch_to.alert
        driver.switch_to.default_content()
        driver.switch_to.frame('frame_name)
        driver.switch_to.frame(1)
        driver.switch_to.frame(driver.find_elements(By.TAG_NAME,"iframe")[0])
        driver.switch_to.parent_frame()
        driver.switch_to.window('main')
        """

    def __init__(self, driver):
        super(SwitchTo, self).__init__(driver=driver)

    @property
    @allure.step("Switches focus to an active element")
    def active_element(self) -> WebElement:
        return super(SwitchTo, self).active_element

    @property
    @allure.step("Switches focus to an alert on the page.")
    def alert(self) -> Alert:
        return Alert(self._driver)

    @allure.step("Switch focus to default frame.")
    def default_content(self) -> None:
        super(SwitchTo, self).default_content()

    @allure.step("Switch focus to the specified frame.")
    def frame(self, frame_reference) -> None:
        super(SwitchTo, self).frame(frame_reference)

    @allure.step("Switch focus to a new top-level browsing context.")
    def new_window(self, type_hint) -> None:
        super(SwitchTo, self).new_window(type_hint=type_hint)

    @allure.step("Switch focus to parent context.")
    def parent_frame(self) -> None:
        super(SwitchTo, self).parent_frame()

    @allure.step("Switch focus to the specified window.")
    def window(self, window_name) -> None:
        super(SwitchTo, self).window(window_name=window_name)
