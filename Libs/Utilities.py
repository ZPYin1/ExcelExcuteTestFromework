# -*- coding: utf-8 -*-
# time: 2024/1/4 11:09
# file: Utilities.py
# author: ZPYin
import io
import logging
import os.path
import re
import time

import pytesseract
from PIL import Image
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook

from imported import ENV

_logger = logging.getLogger(__name__)
PYTHON_REPLACE_REGEX = re.compile(r"\w")
ALPHA_REGEX = re.compile(r"^\d+_*")

join = os.path.join


def make_python_name(string):
    """Make python attribute name out of given string"""
    string = re.sub(PYTHON_REPLACE_REGEX, "", string.replace(" ", "_"))
    return re.sub(ALPHA_REGEX, "", string).lower()


def data_from_excel(excel_path, sheet_name):
    """
    功能：从Excel中读取测试数据
    :param excel_path: Excel地址
    :param sheet_name:工作表名
    :return:title,list(row_value)
    """
    wb = load_workbook(excel_path)
    ws = wb[sheet_name]
    rows = [row for row in ws.values if row]
    title = rows.pop(0)[1:]
    wb.close()
    data = list()
    for row in rows:
        status = row[0]
        if status in ["Skip", None]:
            continue
        if len(row) == 2:
            data.append(row[1])
        else:
            data.append(row[1:])
    return ",".join(title), data


def data_from_text(file_path):
    with open(file_path) as f:
        return [line.strip() for line in f.readlines()]


def image_to_string(binary_data=None, filename=None, lang=None, config='', nice=0, timeout=0):
    if binary_data is None and filename is None:
        raise ValueError("binary_data or filename must exist one.")
    if binary_data:
        image = Image.open(io.BytesIO(binary_data))
    elif filename:
        image = Image.open(filename)
    string = pytesseract.image_to_string(image=image, lang=lang, config=config, nice=nice, timeout=timeout)
    return string.strip()


def get_line_value(line, sep=""):
    line = line[line.index(sep) + 1:]
    return line.strip()


def generate_trace_spreadsheet(test_cases, save_path):
    wb = Workbook()
    test_case_sheet = wb.create_sheet("TestCases", 0)
    test_case_sheet.append(["Name", "Author", "Traced Requirement", "Description", "Last update"])
    req_to_tc = dict()
    for tc in test_cases:
        test_case_sheet.append(tc.get_row_data())
        for req in tc.get_requirements():
            if req not in req_to_tc:
                req_to_tc[req] = list()
            req_to_tc[req].append(tc.get_id())
    req_trace_sheet = wb.create_sheet("RequirementsTrace", 1)
    req_trace_sheet.append(["Requirement ID", "Test Cases"])
    for req, tc in req_to_tc.items():
        req_trace_sheet.append([req, "\n".join(tc)])
    wb.save(save_path)


def get_timestamp(time_fmt='%Y_%m_%d-%H_%M_%S', t=None):
    """
    获取带日期的时间格式
    :param time_fmt:
    :param t:
    :return:
    """
    t = t if t else time.time()
    return time.strftime(time_fmt, time.localtime(t))


def get_time(time_fmt='%H:%M:%S', t=None):
    """
    获取当前时间
    """
    t = t if t else time.time()
    return time.strftime(time_fmt, time.localtime(t))


class GetTestCases:
    """
    用作获取需要测试的测试用例名单
    from_excel: 从excel中获取
    from_xml:
    from_url:
    from_xxx
    返回：List(test_case)
    """

    @staticmethod
    def from_excel(excel_path):
        test_case = list()
        wb = load_workbook(excel_path, read_only=True)
        ws = wb["TestCases"]
        rows = [row for row in ws.values if row]
        title = rows.pop(0)
        run_index = title.index("Run")
        path_index = title.index("Automation Path")
        for row in rows:
            if row[run_index] == "Yes":
                test_case.append(row[path_index])
        return test_case


if __name__ == '__main__':
    print(ENV.data_path)
    a, data = data_from_excel(ENV.data_path, "Add")
    print(a)
    for item in data:
        print(item)
