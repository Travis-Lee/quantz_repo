# -*- coding: utf-8 -*-

from datetime import date, datetime, time


def now_for_log_str():
    return datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]


def now_2_YYYYMMDD():
    return datetime.today().strftime('%Y%m%d')
