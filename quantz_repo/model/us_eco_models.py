from mongoengine import Document, FloatField, LongField


class UsJoblessInitialClaimItem(Document):
    when = LongField(required=True,  unique=False)
    initial_jobless = FloatField(required=True)


class UsWeiItem(Document):
    '''
    美联储每周经济指数（Weekly Economic Index (WEI)），来自 https://www.jimstock.org/
    '''
    # 对应美联储表格中 Date 列数据
    when = LongField(required=True, unique=True)
    # 对应美联储表格中 WEI 列数据
    WEI = FloatField(required=True)
