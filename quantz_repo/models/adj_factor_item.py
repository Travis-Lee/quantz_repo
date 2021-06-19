from mongoengine import Document, FloatField, LongField, StringField


class AdjFactorItem(Document):
    """复权因子
    前复权价格=price * 当天复权因子 / 最新复权因子
    后复权价格=price * 当天复权因子
    """
    ts_code = StringField(required=True)
    # 交易日
    trade_date = LongField(required=True)
    # 复权因子
    adj_factor = FloatField(required=True)
    meta = {
        'indexes': [
            {
                'name': 'unique_index',
                'fields': ['ts_code', 'trade_date'],
                'unique': True,
                'dropDups':True
            }
        ],
        'index_background': True,
        'auto_create_index': True
    }
