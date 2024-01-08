# -*- coding: utf-8 -*-
# time: 2023/12/21 16:38
# file: imported.py
# author: ZPYin
from Libs import Initialization
from Libs.Configs import *

ENV = Environment("Test")


def get_argument_parser():
    return Initialization.argument_parser()


def environment_setup(agr_parser):
    global ENV
    Initialization.setup_enviroment()
    ENV = Environment(agr_parser.env)
