# -*- coding: utf-8 -*-

import tushare as ts
from pandas import Series

from .utils import log

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
