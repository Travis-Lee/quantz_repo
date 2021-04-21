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
