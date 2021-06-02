from mongoengine import Document, LongField, StringField


class TradingInfoUpdateMetaItem(Document):
    # D W M Y H Min
    freq = StringField(required=True)
    # 上次成功更新的时间，以 ms 表示
    last_ok_date = LongField(required=True)
