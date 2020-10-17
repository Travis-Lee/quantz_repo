from pandas import DataFrame
from mongoengine import Document, QuerySet
import json

from .log import e as loge


def df_2_mongo(df: DataFrame, doc: Document):
    '''
    Save DataFrame to mongodb
    '''
    if df is not None and df.shape[0] > 0:
        doc.objects.insert(doc.objects.from_json(df.to_json(orient='records')))
    else:
        loge('data_repo', 'DataFrame failed to save, invalide data[%s]!' % df)


def mongo_2_df(querySet: QuerySet) -> DataFrame:
    '''
    将数据库中查询到的数据转换为DataFrame
    '''
    return DataFrame.from_dict(json.loads(querySet.to_json())).drop('_id', axis=1)
