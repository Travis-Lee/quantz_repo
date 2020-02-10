# -*- coding: utf-8 -*-

from mongoengine import Document, FloatField, StringField


class IndexDailyItem(Document):
    ''' 指数日线数据 '''
    # 代码
    ts_code = StringField(requqired=True)
    # 交易日
    trade_date = StringField(required=True)
    # 收盘点位
    close = FloatField(required=True)
    # 开盘点位
    open = FloatField(required=True)
    # 最高点位
    high = FloatField(required=True)
    # 最低点位
    low = FloatField(required=True)
    # 昨日收盘价
    pre_close = FloatField()
    # 涨跌点
    change = FloatField()
    # 涨跌幅
    pct_chg = FloatField()
    # 交易量(手)
    vol = FloatField(required=True)
    # 成交额(千)
    amount = FloatField(required=True)

    def __str__(self):
        return '%s %s %f %f %f %f %f %f %f %f %f' % \
            (self.ts_code, self.trade_date, self.close, self.open, self.high, self.low,
             self.pre_close, self.change, self.pct_chg, self.vol, self.amount)
