#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/25 16:44
# @Author  : ZP Y
# @Email   : zhanpeng.yin@kcomber.com
# @File    : main.py
# @Software: PyCharm
import logging
import os

import pytest
from allure_pytest import plugin

from Libs.AllureInit import update_trend_data, get_dirname
from Libs.Configs import INIConfig, ALLURE_BAT, ALLURE_RESULT_PATH
from Libs.Utilities import get_line_value, generate_trace_spreadsheet, GetTestCases, get_timestamp
from imported import get_argument_parser, environment_setup

_logger = logging.getLogger(__name__)


class CollectorPlugin(object):

    def __init__(self, callback=None):
        self.__collect = list()

    def pytest_collection_finish(self, session):
        for item in session.items:
            self.__collect.append(self.TestCase(item=item))

    def get_collect_result(self):
        return self.__collect

    class TestCase(object):
        def __init__(self, item):
            self.__id = item.nodeid
            self.__functon_name = item.name
            self.__author = "NOT_SET"
            self.__requirements = ["NOT_SET"]
            self.__description = "NOT_SET"
            self.__last_update = "NOT_SET"
            self.__doc_parser(item.obj.__doc__)

        def get_row_data(self):
            return self.__id, self.__author, ",".join(self.__requirements), self.__description, self.__last_update

        def get_requirements(self):
            return self.__requirements

        def get_id(self):
            return self.__id

        def __doc_parser(self, doc):
            if doc is None:
                _logger.warning("{0} not contains any test case description".format(self.__id))
                return
            for line in doc.splitlines():
                line = line.strip()
                if not line:
                    pass
                elif line.startswith("Author"):
                    self.__author = get_line_value(line)
                elif line.startswith("Date"):
                    self.__last_update = get_line_value(line)
                elif line.startswith("Requirement"):
                    self.__requirements = [req.strip() for req in get_line_value(line).split(",") if req]
                elif line.startswith("Description"):
                    self.__description = get_line_value(line)
                else:
                    self.__description += "\n"
                    self.__description += line.strip()


def collect(agr_parser):
    if agr_parser.output and agr_parser.endwith(".xlsx"):
        output = agr_parser.output
    else:
        _logger.warning("Not provided valid output path, using default <Trace.xlsx>")
        output = "Trace.xlsx"
    collector_plugin = CollectorPlugin()
    ret = pytest.main(["--collect-only", "-qq"], plugins=[collector_plugin])
    if ret != pytest.ExitCode.OK:
        raise ValueError(ret)
    test_cases = collector_plugin.get_collect_result()
    generate_trace_spreadsheet(test_cases=test_cases, save_path=output)


def run(agr_parser):
    time_str = get_timestamp()
    environment_setup(agr_parser)
    pytest_args = list()
    if agr_parser.plan:
        if os.path.exists(agr_parser.plan):
            test_cases = GetTestCases.from_excel(agr_parser.plan)
            if not test_cases:
                raise ValueError("Unable to find any test cases to executed." % agr_parser.plan)
            pytest_args.extend(test_cases)
        else:
            raise OSError("Unable to find a valid test plan file:%s" % agr_parser.plan)
    elif agr_parser.specific:
        pytest_args.append(agr_parser.specific)
    elif agr_parser.mark and agr_parser.mark != "all":
        pytest_args.append("-m")
        pytest_args.append(agr_parser.mark)
    # pytest_args.append(f"--alluredir=./allure-results/{agr_parser.env}")
    res_path = os.path.join(ALLURE_RESULT_PATH, agr_parser.env, get_timestamp())
    pytest_args.append("--alluredir={allurepath}".format(allurepath=res_path))
    try:
        # pytest.main(pytest_args, plugins=[plugin])
        pytest.main(pytest_args)
    except ValueError:
        pytest.main(pytest_args)
    if agr_parser.generate:
        report_path = INIConfig.config.report_path
        if not os.path.exists(report_path):
            os.makedirs(report_path)
        report_path = os.path.join('.', report_path, agr_parser.env, time_str)
        # print(res_path)
        # os.system("{allure} generate ./allure-results/{env} -o {report}".format(allure=ALLURE_BAT, env=agr_parser.env,
        #                                                                         report=report_path))
        print("{allure} generate {res_env} --clean -o {report}".format(allure=ALLURE_BAT,
                                                                       res_env=res_path,
                                                                       report=report_path))
        os.system("{allure} generate {res_env} --clean -o {report}".format(allure=ALLURE_BAT,
                                                                           res_env=res_path,
                                                                           report=report_path))
        # print(agr_parser.env)
        print(report_path)
        # os.system("{allure} open {report} -p {port}".format(allure=ALLURE_BAT, report=report_path,
        #                                                     port=Environment(agr_parser.env).report_port))
        # os.system("{allure} -q open {report} -p {port} ".format(allure=ALLURE_BAT, report=report_path,
        #                                                         port=Environment(agr_parser.env).report_port))
    a, b = get_dirname(arg_parser.env)
    update_trend_data(time_str, b, arg_parser.env)
    if agr_parser.browser:
        pass


if __name__ == '__main__':
    arg_parser = get_argument_parser()
    if arg_parser.collect is True:
        collect(arg_parser)
    else:
        run(arg_parser)

