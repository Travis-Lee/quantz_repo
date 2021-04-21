
from mongoengine import Document, StringField, LongField


class IndustrialClassificationItem(Document):
    '''
    行业分类
    '''
    # 指数代码
    index_code = StringField(required=True)
    # 行业名字
    industry_name = StringField(required=True)
    # 行业级别
    level = StringField(required=True)
    # 行业代码
    industry_code = StringField(required=True)
    # 发布时间
    declaredate = LongField(required=True)
    # 行业分类来源
    src = StringField(required=True)
    meta = {
        'indexes': [
            {
                'name': 'level_index',
                'fields': ['level', 'declaredate'],
            }
        ],
        'index_background': True,
        'auto_create_index': True
    }
