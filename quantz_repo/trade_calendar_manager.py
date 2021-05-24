# -*- coding: utf-8 -*-

import datetime

import tushare as ts
from pandas import DataFrame, Series

from .models import TradeCalendarItem
from .quantz_exception import QuantzException
from .utils import (datetime_2_date_millisec, df_2_mongo, log,
                    millisec_2_YYYYMMDD, mongo_2_df, now_2_YYYYMMDD,
                    today_2_millisec, yyyymmdd_2_int)

D = True


class TradeCalendarManager(object):
    '''
    交易日历管理类
    '''
    @classmethod
    def next_trade_date_of(cls, exchange: str, date: str):
        """ 从交易日历中获取某个日期后的下一个交易日期
        // TODO 返回的只是 tushare 定义的日期格式，如果tushare 变更格式，这里返回的就不是预期格式了

        :param exchange: 交易所名字,交易所 SSE上交所,SZSE深交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源,IB 银行间,XHKG 港交所
        :type exchange: str
        :param date: [description]
        :type date: str
        :return: 下一个交易日 YYYYMMDD格式的字符串,如果无有效交易日期，返回 None
        :rtype: str
        """
        pro = ts.pro_api()
        try:
            trade_cal = pro.trade_cal(exchange=exchange, start_date=date)
            trade_cal = trade_cal[trade_cal.is_open == 1]['cal_date']
            trade_cal = trade_cal[trade_cal > date]
            return trade_cal.iat[0]
        except Exception as e:
            log.w('TradeCalendarManager',
                  'Could not get valid trade date for %s, %s, returning None' % (e, date))
            return None

    @classmethod
    def tscode_2_exchange(cls, ts_code: str):
        if ts_code.endswith('.SH'):
            return 'SSE'
        elif ts_code.endswith('.SZ'):
            return 'SZSE'


def is_trading_day(trade_date: int, exchange: str = 'SSE') -> bool:
    '''
    判断 exchange 在 trade_date当天是否是交易日
    '''
    return TradeCalendarItem.objects(
        is_open=1, exchange=exchange, cal_date=trade_date).count() > 0


def init_trade_calendar():
    '''
    初始化交易所交易日历，保存到数据库
    '''
    TradeCalendarItem.drop_collection()
    for ex in ['SSE', 'SZSE']:
        __init_trade_calendar_for(ex)


def __init_trade_calendar_for(exchange: str):
    '''
    初始化某个交易所的交易日历， SSE上交所,SZSE深交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源,IB 银行间,XHKG 港交所

    '''
    cal = ts.pro_api().trade_cal(exchange=exchange,
                                 fields='exchange,cal_date,is_open,pretrade_date')
    cal = cal.rename({'cal_date': 'c', 'pretrade_date': 'p'}, axis=1)
    cal['cal_date'] = cal['c'].map(yyyymmdd_2_int, na_action='ignore')
    cal['pretrade_date'] = cal['p'].map(yyyymmdd_2_int, na_action='ignore')
    cal = cal.drop(['c', 'p'], axis=1)
    df_2_mongo(cal, TradeCalendarItem)


def get_last_trade_date_in_ms_for(exchange='SSE', adj=True) -> int:
    """获取某个交易所相对于今天最近一个交易日的时间

    :param exchange: 交易所名字,交易所 SSE上交所,SZSE深交所.暂不支持其他交易所：CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源,IB 银行间,XHKG 港交所
    :type exchange: str, optional,默认上交所SSE
    :param adj: 是否根据函数运行的时刻调整返回最近的交易日.由于此函数在任何时刻都可能运行，但是日线等数据不是任意时刻都是可用的，所以用此参数调整返回的参数是当天的交易日还是上一个交易日。False返回当天，True根据函数运行时间调整，若运行时间晚于18:00,返回当天，否则返回上一个交易日
    :type exchange: bool, optional,默认 False.
    :raises QuantzException: 发生异常则抛出
    :return: 最近一个交易日 milliseconds
    :rtype: int
    """
    today_in_ms = today_2_millisec()
    this_hour = datetime.datetime.now().hour
    print('this hour:%d' % this_hour)
    last_trade_date = None
    if adj and this_hour < 18:
        last_trade_date = TradeCalendarItem.objects(
            cal_date__lt=today_in_ms, is_open=1, exchange=exchange).order_by('-cal_date').limit(1).first()
    else:
        last_trade_date = TradeCalendarItem.objects(
            cal_date__lte=today_in_ms, is_open=1, exchange=exchange).order_by('-cal_date').limit(1).first()
    if last_trade_date is None:
        raise QuantzException('Failed to get last trade date')
    else:
        return last_trade_date.cal_date


def get_trade_dates_between(since: str, end: str = now_2_YYYYMMDD(), exchange='SSE') -> DataFrame:
    '''
    since:yyyymmddd的日期
    end:yyyymmddd的结束日期
    exchange:交易所，SSE 或 SZSE
    否则抛出 QuantzException
    '''
    since_ms = 0
    end_ms = 0
    try:
        since_ms = int(datetime.datetime.strptime(
            since, '%Y%m%d').timestamp())*1000
    except Exception as e:
        raise QuantzException('Invalid since format:%s' % e)
    try:
        end_ms = int(datetime.datetime.strptime(
            end, '%Y%m%d').timestamp())*1000
    except Exception as e:
        raise QuantzException('Invalid end format:%s' % e)
    return mongo_2_df(TradeCalendarItem.objects(
        is_open=1, cal_date__gte=since_ms, cal_date__lte=end_ms, exchange=exchange).order_by('cal_date'))


def get_next_trade_date_of(day: str, exchange: str = 'SSE') -> str:
    """ 获取day的下一个交易日

    :param day: 交易时间，YYYYmmdd格式
    :type day: str
    :return: day 的下一个交易日，YYYYmmdd
    :rtype: str
    """
    day_int = yyyymmdd_2_int(day)
    next = TradeCalendarItem.objects(is_open=1, cal_date__gt=day_int, exchange=exchange).order_by(
        'cal_date').limit(1).first()
    if next is not None:
        return millisec_2_YYYYMMDD(next.cal_date)
    else:
        None
