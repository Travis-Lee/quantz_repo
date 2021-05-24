from mongoengine import Document, LongField, StringField

'''
行业信息更新记录
'''


class IndustryClassificatoinMetaItem(Document):
    '''
    记录行业信息更新的时间，每次SW更新后，这里同步重新获取行业分类数据
    '''
    declaredate = LongField(required=True)
    '''
    声明标题
    '''
    title = StringField(required=True)


class IndustryClassificatoinRankMetaItem(Document):
    """记录各个行业评分最近成功的时间

    """
    level = StringField(required=True)
    trade_date = LongField(required=True)
