# -*- coding: utf-8 -*-
# time: 2024/1/3 9:09
# file: Initialization.py
# author: ZPYin
import logging
import os.path
import time

from argparse import ArgumentParser
from shutil import rmtree

from Libs.Configs import PROGRAM_FILES_PATH, INIConfig, TEMPORARY_PATH

_logger = logging.getLogger(__name__)


def argument_parser():
    """
    功能：分析通过CommandLine输入的参数
    :return: parser对象
    """
    parser = ArgumentParser()
    parser.add_argument("-m", "--mark", help="Run marked test cases")
    parser.add_argument("-e", "--env", help="Run test cases on which environment")
    parser.add_argument("-g", "--generate", action="store_true", help="Need generate test report")
    parser.add_argument("-c", "--collect", action="store_true", help="Collect test case")
    parser.add_argument("-p", "--plan", help="Execute test cases according to the testing plan")
    parser.add_argument("-spec", "--specific", help="Execute specific test case")

    args = parser.parse_args()
    _logger.info("Start test with arg:%s" % args)
    return args


# def pytesseract_environment():
#     """
#     功能：初始化pytesseract的环境，指定tesseract的Binary位置
#     :return: None
#     """
#     pytesseract.tesseract_cmd = os.path.join(PROGRAM_FILES_PATH, "Tesseract_OCR", "tesseract.exe")

def logger_format():
    """
    功能：调整logger的格式，主要用于DEBUG
    :return:None
    """
    if os.path.exists("pytest.ini"):
        log_path = INIConfig.config.log_path
        os.makedirs(log_path, exist_ok=True)
    else:
        log_path = "Logs"
        filename = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=os.path.join(log_path, filename),
                            filemode='w')


def clear_temporary():
    """
    功能：测试前清空临时目录
    :return:None
    """
    if os.path.exists(TEMPORARY_PATH):
        rmtree(TEMPORARY_PATH)
    os.makedirs(TEMPORARY_PATH)


def setup_enviroment():
    logger_format()
    # pytesseract_environment()
    clear_temporary()
