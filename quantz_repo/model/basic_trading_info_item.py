from mongoengine import (Document, DynamicDocument, FloatField, LongField,
                         StringField)

'''
此集合数据量巨大，TODO::需要创建索引
'''


class BasicTradingInfoItem(DynamicDocument):
    '''
    日线、周线等基本交易数据，股票的ts_code，交易时间、OHLC、成交量(收)、成交额(千)
    '''
    ts_code = StringField()
    '''ts_code'''
    trade_date = LongField()
    ope = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    pre_close = FloatField()
    change = FloatField()
    pct_change = FloatField()
    vol = FloatField()
    amount = FloatField()
    # 数据的时间间隔，D表示日线，W表示周线，M表示月线，1min表示1分钟，以此类推，1、5、15、30、60min
    freq = StringField(default='D')
    meta = {
        'indexes': [
            {
                'name': 'basic_trading',
                'fields': ['ts_code', 'trade_date', 'freq'],
                'unique': True
            }
        ],
        'index_background': True,
        'auto_create_index': True
    }
