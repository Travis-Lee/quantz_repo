from mongoengine import Document, FloatField, LongField


class UsJoblessInitialClaimItem(Document):
    when = LongField(required=True,  unique=False)
    initial_jobless = FloatField(required=True)
    meta = {
        'indexes': [
            {
                'name': 'when_index',
                'fields': ['when']
            }
        ],
        'index_background': True,
        'auto_create_index': True
    }


class UsWeiItem(Document):
    '''
    美联储每周经济指数（Weekly Economic Index (WEI)），来自 https://www.jimstock.org/
    '''
    # 对应美联储表格中 Date 列数据
    date = LongField(required=True, unique=True)
    # 对应美联储表格中 WEI 列数据
    value = FloatField(required=True)
    meta = {
        'indexes': [
            {
                'name': 'date_index',
                'fields': ['date']
            }
        ],
        'index_background': True,
        'auto_create_index': True
    }
