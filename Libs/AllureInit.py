#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/24 16:12
# @Author  : ZP Y
# @File    : AllureInit.py
# @Software: PyCharm
import json
import os
import shutil
import socket

from Libs.Configs import REPORT_PATH, ALLURE_BAT, Environment
from Libs.Utilities import get_timestamp
from imported import get_argument_parser, environment_setup


def get_dirname(env):
    history_file = os.path.join(REPORT_PATH, env, get_timestamp(time_fmt='%Y_%m'), "history.json")
    if os.path.exists(history_file):
        with open(history_file) as f:
            li = eval(f.read())
        # 根据构建次数进行排序，从大到小
        li.sort(key=lambda x: x['buildOrder'], reverse=True)
        # 返回下一次的构建次数，所以要在排序后的历史数据中的buildOrder+reports
        return li[0]["buildOrder"] + 1, li
    else:
        # 首次进行生成报告，肯定会进到这一步，先创建history.json,然后返回构建次数1（代表首次）
        os.makedirs(os.path.join(REPORT_PATH, env, get_timestamp(time_fmt='%Y_%m')), exist_ok=True)
        with open(history_file, "w") as f:
            pass
        return 1, None


def update_trend_data(dirname, old_data: list, env):
    """
    dirname：构建次数
    old_data：备份的数据
    update_trend_data(get_dirname())
    """
    # allure_report_path = 'allure-report/widgets'
    rpath = os.path.join(REPORT_PATH, env)
    allure_report_path = os.path.join(rpath, dirname, 'widgets')
    WIDGETS_DIR = allure_report_path
    # 在reports文件夹下面创建相对应的构建次数文件夹
    # folder_path = f"./reports/{dirname}"
    # folder_path = os.path.join(rpath, get_timestamp(time_fmt='%Y_%m'), str(dirname))
    folder_path = os.path.join(rpath, get_timestamp(time_fmt='%Y_%m'), 'new')
    # os.makedirs(folder_path)

    # 将allure-report中的所有文件复制到对应构建次数的文件夹中
    # 定义源文件夹路径
    # source_folder = "./allure-report"
    source_folder = os.path.join(rpath, dirname)
    # 定义目标文件夹路径
    target_folder = folder_path
    # 复制源文件夹中的所有文件和子文件夹到目标文件夹
    if os.path.exists(target_folder):
        shutil.rmtree(target_folder)
    shutil.copytree(source_folder, target_folder)

    # 读取最新生成的history-trend.json数据
    with open(os.path.join(WIDGETS_DIR, "history-trend.json")) as f:
        data = f.read()

    new_data = eval(data)
    if old_data is not None:
        new_data[0]["buildOrder"] = old_data[0]["buildOrder"] + 1
    else:
        old_data = []
        new_data[0]["buildOrder"] = 1
    # 给最新生成的数据添加reportUrl key，reportUrl要根据自己的实际情况更改
    ipadd = socket.gethostbyname(socket.gethostname())
    new_data[0]["reportUrl"] = f"http://192.168.1.63:9080/{env}/{get_timestamp(time_fmt='%y%m%d')}/index.html"
    new_data[0]["reportpath"] = f"{target_folder}"
    # 把最新的数据，插入到备份数据列表首位
    old_data.insert(0, new_data[0])

    # 把所有生成的报告中的history-trend.json都更新成新备份的数据old_data，这样的话，点击历史趋势图就可以实现新老报告切换
    with open(os.path.join(rpath, f"{get_timestamp(time_fmt='%Y_%m')}/new/widgets/history-trend.json"),
                "w+") as f:
        f.write(json.dumps(old_data))
    with open(os.path.join(allure_report_path, "history-trend.json"), "w+") as f:
        f.write(json.dumps(old_data))
    # 把数据备份到history.json
    hostory_file = os.path.join(rpath, get_timestamp(time_fmt='%Y_%m'), "history.json")
    with open(hostory_file, "w+") as f:
        f.write(json.dumps(old_data))
    return old_data, new_data[0]["reportUrl"]


if __name__ == '__main__':
    arg_parser = get_argument_parser()
    environment_setup(arg_parser)
    # path = os.path.join(REPORT_PATH, arg_parser.env)
    print(arg_parser.env)
    a, b = get_dirname(arg_parser.env)
    print(a, b)
    print(update_trend_data(a, b, arg_parser.env))
    # os.system("{allure} generate {res_env}  -o {report}".format(allure=ALLURE_BAT,
    #                                                             res_env=res_path,
    #                                                             report=report_path))
    # print(agr_parser.env)
    # print(report_path)
    # os.system("start {allure} open {report} -p {port}".format(allure=ALLURE_BAT, report=report_path,
    #                                                           port=Environment(arg_parser.env).report_port))
