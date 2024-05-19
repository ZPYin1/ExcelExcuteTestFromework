# -*- coding: utf-8 -*-
# time: 2023/12/21 16:45
# file: Configs.py
# author: ZPYin
import json
import os
from configparser import ConfigParser

VERSION = "0.0.1"
TOOL_ROOT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
PYTEST_INI_PATH = os.path.join(TOOL_ROOT_PATH, "pytest.ini")

TEMPORARY_PATH = os.path.join(TOOL_ROOT_PATH, "Temporary")
RESOURCES_PATH = os.path.join(TOOL_ROOT_PATH, "Resources")

DATA_FILES_PATH = os.path.join(RESOURCES_PATH, "DataFiles")
PROGRAM_FILES_PATH = os.path.join(RESOURCES_PATH, "ProgramFiles")
LOCATOR_FILES_PATH = os.path.join(RESOURCES_PATH, "LocatorFiles")

ALLURE_BAT = os.path.join(PROGRAM_FILES_PATH, "allure", "bin", "allure.bat")

PROD = 40
STAGING = 30
TEST = 20
DEV = 10
NOTSET = 0

PRE_RELEASE = STAGING
PRODUCT = PROD

NameToEnv = {
    'PROD': PROD,
    'PRODUCT': PRODUCT,
    'STAGING': STAGING,
    'PRE_RELEASE': PRE_RELEASE,
    'TEST': TEST,
    'DEV': DEV
}

EnvToName = {
    PROD: 'PROD',
    STAGING: 'STAGING',
    TEST: 'TEST',
    DEV: 'DEV'
}

EnvToConfig = {
    PROD: 'ProdEnv',
    STAGING: 'StagEnv',
    TEST: 'TestEnv',
    DEV: 'DevEnv'
}


def _read(path, section):
    parser = ConfigParser()
    parser.read(path)
    if not parser.has_section(section):
        return dict()
    dict_section = dict()
    for option in parser.options(section):
        dict_section[option] = parser.get(section=section, option=option)
    return dict_section


def _write(path, section, option, value):
    parser = ConfigParser()
    parser.read(path)
    if not parser.has_section(section):
        parser.add_section(section)
    parser.set(section=section, option=option, value=value)
    with option(path, "w+") as config:
        parser.write(config)


def _remove(path, section, option):
    parser = ConfigParser()
    parser.read(path)
    if not parser.has_section(section):
        return
    parser.remove_option(section=section, option=option)
    with open(path, "w+") as config:
        parser.write(config)


class _BaseConfig(object):
    def __init__(self, path, section):
        self.__path = path
        self.__section = section
        mapping = _read(path, section)
        for key, value in mapping.items():
            key = key.lower()
            super(_BaseConfig, self).__setattr__(key, value)

    def __setattr__(self, key, value):
        if not key.startswith("_BaseConfig__"):
            _write(self.__path, self.__section, key, value)
        return super(_BaseConfig, self).__setattr__(key, value)

    def __getattribute__(self, item):
        if not item.startswith("_BaseConfig__"):
            item = item.lower()
        return super(_BaseConfig, self).__getattribute__(item)

    def get(self, item, default=None):
        if not hasattr(self, item) or self.__getattribute__(item) == "":
            self.__setattr__(item, default)
        return self.__getattribute__(item)

    def set(self, item, valur):
        self.__setattr__(item, valur)


class Environment:
    # 环境配置
    # 根据不同环境获取不同的配置数据
    def __init__(self, env_name, browser_name='edge'):
        env_name = env_name.upper()
        if env_name in NameToEnv.keys():
            self.__env = NameToEnv[env_name]
            self.__configs = _BaseConfig(PYTEST_INI_PATH, EnvToConfig[self.__env])
        else:
            raise ValueError(f"Environment: {env_name} not in one of the environment key words")

        self.__browser = browser_name.lower()

    @property
    def base_url(self):
        return self.__configs.base_url

    @property
    def configs(self):
        return self.__configs

    @property
    def SQLconfigs(self):
        sqlconf = self.__configs.SQL
        return json.loads(sqlconf)

    @property
    def data_path(self):
        data_path = self.__configs.data_path
        if os.path.exists(data_path):
            return data_path
        return os.path.join(TOOL_ROOT_PATH, data_path)

    def get(self, item, default):
        return self.__configs.get(item, default)

    def __lt__(self, other):
        return self.__env < other

    def __le__(self, other):
        return self.__env <= other

    def __gt__(self, other):
        return self.__env > other

    def __ge__(self, other):
        return self.__env >= other

    def __eq__(self, other):
        return self.__env == other

    def __ne__(self, other):
        return self.__env != other


class INIConfig(object):
    pytest = _BaseConfig(PYTEST_INI_PATH, "pytest")
    config = _BaseConfig(PYTEST_INI_PATH, "config")


if __name__ == '__main__':
    print(TOOL_ROOT_PATH)
