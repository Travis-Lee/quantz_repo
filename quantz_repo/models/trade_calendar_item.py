from mongoengine import Document, LongField, StringField


class TradeCalendarItem(Document):
    exchange = StringField()
    cal_date = LongField()
    is_open = StringField()
    pretrade_date = LongField()
    meta = {
        'indexes': [
            {
                'name': 'exchange_index',
                'fields': ['exchange'],
                'unique': False,
            },
            {
                'name': 'exchange_is_open_index',
                'fields': ['exchange', 'is_open'],
                'unique': False,
            },
            {
                'name': 'exchange_cal_date_index',
                'fields': ['exchange', 'cal_date'],
                'unique': False,
            },
            {
                'name': 'cal_date_index',
                'fields': ['cal_date'],
                'unique': False,
            },
        ],
        'index_background': True,
        'auto_create_index': True
    }
