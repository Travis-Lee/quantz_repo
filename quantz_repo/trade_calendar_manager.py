# -*- coding: utf-8 -*-

import tushare as ts
from pandas import Series

from .utils import log
from .utils import df_2_mongo, yyyymmdd_2_int
from .models import TradeCalendarItem

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


def init_trade_calendar():
    '''
    初始化交易所交易日历，保存到数据库
    '''
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


def get_last_trade_date_timestamp__for(exchange: str) -> int:
    '''
    FIXME:实现获取最近一个交易日
    '''
    pass
