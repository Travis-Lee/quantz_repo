from mongoengine import Document, StringField, LongField


class MetaDataItem(Document):
    # 针对哪个数据集的meta
    data_set = StringField(required=True)
    # metadata 的更新日期
    update_date = LongField(required=True)
    # metadata 信息
    metadata = StringField(required=True)
