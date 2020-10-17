import tushare as ts
from pandas import DataFrame

from .utils.log import i as logi
from .model.industrial_classification_item import IndustrialClassificationItem
from .model.industrial_classification_member_item import IndustrialClassficationMemberItem
from .utils.data_repo import mongo_2_df,  df_2_mongo

_TAG = 'IndustrialClassification'


def get_industrial_classifications(index_code=None, level='L2', src='SW') -> DataFrame:
    '''
    获取行业分类列表，采用申万的行业分类
    '''
    logi(_TAG, 'Get industrial classification: %s %s %s' %
         (index_code, level, src))
    industial_classification_df = None
    if IndustrialClassificationItem.objects(level=level).count() <= 0:
        industial_classification_df = ts.pro_api().index_classify(
            index_code=index_code, level=level, src=src)
        df_2_mongo(industial_classification_df, IndustrialClassificationItem)
    else:
        industial_classification_df = mongo_2_df(
            IndustrialClassificationItem.objects(level=level))
    return industial_classification_df


def get_industrial_classfication_members(index_code: str):
    '''
    获取某个行业分类下的成分股
    '''
    logi(_TAG, 'Get industrial classification member:%s' % index_code)
    members = None
    if IndustrialClassficationMemberItem.objects(index_code=index_code).count() <= 0:
        members = ts.pro_api().index_member(index_code=index_code,
                                            fields='index_code,index_name,con_code,con_name,in_date,out_date,is_new')
        df_2_mongo(members, IndustrialClassficationMemberItem)
    else:
        members = mongo_2_df(
            IndustrialClassficationMemberItem.objects(index_code=index_code))
    return members


def get_industrial_classification_for(ts_code: str) -> DataFrame:
    '''
    获取指定股票的行业分类
    '''
    logi(_TAG, 'Get industrial classification for %s' % ts_code)
    return mongo_2_df(IndustrialClassficationMemberItem.objects(con_code=ts_code))


def initialize_industrial_classification():
    '''
    初始化行业分类数据。不适用增量更新，不记录历史状态。
    TODO: 增加每月定期更新行业分类功能，由于不清楚申万的更新周期，可以每月20号更新
    '''
    # 1. 清空原数据库
    IndustrialClassificationItem.drop_collection()
    IndustrialClassficationMemberItem.drop_collection()
    # 2. 获取行业分类
    for level in ['L1', 'L2', 'L3']:
        level_class_df = get_industrial_classifications(level=level)
        for item in level_class_df.itertuples():
            # 3. 更新行业成分
            get_industrial_classfication_members(item.index_code)
