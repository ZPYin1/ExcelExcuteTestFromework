# -*- coding: utf-8 -*-
# time: 2024/1/4 17:04
# file: main.py
# author: ZPYin
import logging
import os.path

import pytest
from allure_pytest import plugin

from Libs.Configs import INIConfig, ALLURE_BAT
from Libs.Utilities import get_line_value, generate_trace_spreadsheet, GetTestCases, get_timestamp
from imported import environment_setup, get_argument_parser

_logger = logging.getLogger(__name__)


class CollectorPlugin(object):
    class TestCase(object):
        def __init__(self, item):
            self.__id = item.nodeid
            self.__function_name = item.name
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

    def __init__(self, callback=None):
        self.__collect = list()

    def pytest_collection_finish(self, session):
        for item in session.item:
            self.__collect.append(self.TestCase(item=item))

    def get_collect_result(self):
        return self.__collect


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
    pytest_args.append("--alluredir=./allure-results")
    try:
        pytest.main(pytest_args, plugins=[plugin])
    except ValueError:
        pytest.main(pytest_args)
    if agr_parser.generate:
        report_path = INIConfig.config.report_path
        if not os.path.exists(report_path):
            os.makedirs(report_path)
        report_path = os.path.join(report_path, get_timestamp())
        os.system("{allure} generate ./allure-results/ -o {report}".format(allure=ALLURE_BAT, report=report_path))
        os.system("start {allure} open {report}".format(allure=ALLURE_BAT, report=report_path))


if __name__ == '__main__':
    arg_parser = get_argument_parser()
    if arg_parser.collect is True:
        collect(arg_parser)
    else:
        run(arg_parser)
