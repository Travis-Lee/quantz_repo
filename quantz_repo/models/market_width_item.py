from mongoengine import Document, StringField, FloatField, LongField


class MarketWidthItem(Document):
    # 行业名字
    industry_name = StringField(required=True)
    # 申万行业id
    index_code = StringField(required=True)
    # 申万行业级别
    industry_level = StringField(required=True)
    # 交易日期
    trade_date = LongField(required=True)
    # 分数
    rank = FloatField(required=True)
    meta = {
        'indexes': [
            {
                'name': 'industry_code_index',
                'fields': ['index_code'],
                'unique': False
            },
            {
                'name': 'industry_code_date_index',
                'fields': ['index_code', 'trade_date'],
                'unique': False
            },
            {
                'name': 'index_code_level_date_index',
                'fields': ['index_code', 'industry_level', 'trade_date'],
                'unique': False
            }
        ],
        'index_background': True,
        'auto_create_index': True
    }
