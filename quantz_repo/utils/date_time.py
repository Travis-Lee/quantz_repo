# -*- coding: utf-8 -*-

from datetime import date, datetime, time, timedelta

'''
TODO: 统一命名函数名字，YYYYMMDD 统一改为 YYYYmmdd，int 改为 ms
'''


def now_for_log_str():
    return datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]


def now_2_YYYYMMDD():
    return datetime.today().strftime('%Y%m%d')


def timestamp_2_YYYYMMDD(timestamp_in_milliseconds: int) -> str:
    return datetime.fromtimestamp(timestamp_in_milliseconds/1000).strftime('%Y%m%d')


def millisec_2_YYYYMMDD(milliseconds: int) -> int:
    return datetime.fromtimestamp(milliseconds/1000).strftime('%Y%m%d')


def get_last_thursday() -> date:
    '''
    get the date of last thursday
    '''
    today = datetime.today()
    offset = (today.weekday() - 3) % 7
    last_thursday = today - timedelta(days=offset)
    return last_thursday


def yyyymmdd_2_int(yyyymmdd: str) -> int:
    '''
    返回对应时间的毫秒值
    '''
    return int(datetime.strptime(yyyymmdd, '%Y%m%d').timestamp()) * 1000


def get_next_day_in_YYYYMMDD(ms: int):
    '''
    ms这个时间点之后一天的日期，ms单位是毫秒
    '''
    return datetime.fromtimestamp(ms/1000 + 3600 * 24).strftime('%Y%m%d')


def now_2_slash_datetime():
    '''
    格式化 当前时间为 yyyy/mm/dd hh:mm:ss
    '''
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


def now_2_milisec():
    '''
    当前时间戳，毫秒
    '''
    return int(datetime.datetime.now().timestamp())*1000


def today_2_millisec():
    '''
    获取今日的毫秒表示
    '''
    today = date.today()
    return int(datetime(today.year, today.month, today.day).timestamp()*1000)


def datetime_2_date_millisec(sometime: datetime) -> int:
    '''
    获取某个时间的日期，返回毫秒
    '''
    return int(sometime.timestamp() - sometime.timestamp() % (60*60*24))*1000
