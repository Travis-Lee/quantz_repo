# -*- coding: utf-8 -*-

from datetime import date, datetime, time, timedelta


def now_for_log_str():
    return datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]


def now_2_YYYYMMDD():
    return datetime.today().strftime('%Y%m%d')


def get_last_thursday() -> date:
    '''
    get the date of last thursday
    '''
    today = datetime.today()
    offset = (today.weekday() - 3) % 7
    last_thursday = today - timedelta(days=offset)
    return last_thursday
