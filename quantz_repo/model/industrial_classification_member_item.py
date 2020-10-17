from mongoengine import Document, StringField


class IndustrialClassficationMemberItem(Document):
    '''
    行业分类成分股
    '''
    # 行业代码
    index_code = StringField(required=True)
    # 行业名称
    index_name = StringField(required=True)
    # 成分股代码
    con_code = StringField(required=True)
    # 成分股名称
    con_name = StringField(required=True)
    # 进入行业分类的时间
    in_date = StringField(required=True)
    # 从行业分类移除的时间
    out_date = StringField(required=True)
    # 是否是最新的数据, Y/N
    is_new = StringField(required=True)
