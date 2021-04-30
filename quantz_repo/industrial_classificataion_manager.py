import datetime
import json
import time

import numpy as np
import pandas as pd
import requests
import tushare as ts
from pandas import DataFrame

from .model.industrial_classification_item import IndustrialClassificationItem
from .model.industrial_classification_member_item import \
    IndustrialClassficationMemberItem
from .models.industry_classification_meta import IndustryClassificatoinMetaItem
from .quantz_exception import QuantzException
from .trade_calendar_manager import is_trading_day
from .utils import (millisec_2_YYYYMMDD, now_2_milisec, today_2_millisec,
                    yyyymmdd_2_int)
from .utils.data_repo import df_2_mongo, mongo_2_df
from .utils.log import d as logd
from .utils.log import e as loge
from .utils.log import i as logi

'''
从 Tushare 获取获取行业分类数据，从SW网站获取更新通知。收到行业分类数据更新通知后，更新行业分类数据
TODO: SW行业信息是经常改变的，当前根据SW网站更新公告来更新行业分类数据并不能保证获取最新的行业分类数据，需要每天获取最新的分类数据，与本地对比来确定是否有更新
'''

_TAG = 'IndustrialClassification'


def _now_2_slash_datetime():
    '''
    格式化 当前时间为 yyyy/mm/dd hh:mm:ss,从SW获取数据需要此格式的时间
    '''
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


def _get_industry_member_declaredate_from_sw() -> DataFrame:
    '''
    从申万网站获取行业信息更新时间
    title declaredate
    '''
    try:
        page = requests.post('http://www.swsindex.com/handler.aspx',
                             headers={'Accept': 'application/json, text/javascript, */*', 'X-Requested-With': 'XMLHttpRequest', 'Referer': 'http://www.swsindex.com/Idx0400.aspx',  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
                                      'Content-Type': 'application/x-www-form-urlencoded',
                                      'Origin': 'http://www.swsindex.com'},
                             cookies={
                                 'ASP.NET_SessionId': 'gr53xl45x5ihlaiswo3avcnj'},
                             data={'tablename': 'SwIndexAnnouncement', 'key': 'title', 'p': '1', 'where': "DeclareDate<='%s' and declaredate >'2020/10/22'" % (_now_2_slash_datetime()), 'dist': 'dist', 'orderby': 'DeclareDate_1', 'fieldlist': 'title,declaredate', 'pagecount': '13', 'timed': '1618911316668'})
        json_str = page.text.replace("'", '"')
        json_str = json_str.replace('/', '-')
        # print(json.loads(json_str)['root'])
        df = pd.DataFrame.from_dict(json.loads(json_str)['root'])
        # df.drop(axis=1, columns=['Id'],inplace=True)
        df = df[df['title'].str.contains('申万股价系列指数成份股临时调整公告')]
        date_serie = df['declaredate'].astype(np.datetime64)
        date_serie = date_serie.astype(np.int64)/1000000
        date_serie = date_serie.astype(np.int64)
        df['declaredate'] = date_serie
        return df
    except BaseException as e:
        loge(_TAG, 'Failed to get declaredate from SW cause %s' % e)
        return DataFrame()


def _get_industry_classification_from_tushare(index_code=None, declaredate=int(datetime.datetime.now().timestamp())*1000, level='L2', src='SW') -> DataFrame:
    try:
        logi(_TAG, 'Get industry classification for %s' % level)
        industial_classification_df = ts.pro_api().index_classify(
            index_code=index_code, level=level, src=src,
            fields='index_code,industry_name,industry_code,level,industry_code,src')
        industial_classification_df['declaredate'] = declaredate
        df_2_mongo(industial_classification_df, IndustrialClassificationItem)
        return industial_classification_df
    except BaseException as e:
        loge(_TAG, 'Failed to get industry classification from tushare cause %s' % e)
        return DataFrame()


def get_industrial_classifications(trade_date=int(datetime.datetime.now().timestamp())*1000, level='L2', src='SW') -> DataFrame:
    '''
    从本地数据库获取指定日期的行业分类数据，默认采用申万的行业分类
    返回DataFrame
    '''
    logi(_TAG, 'Get industrial classification: %s %d %s' %
         (level, trade_date, src))
    latest_declare_meta = IndustryClassificatoinMetaItem.objects(
        declaredate__lte=trade_date).order_by('-declaredate').limit(1).first()
    if latest_declare_meta is None:
        latest_declare_meta = IndustryClassificatoinMetaItem.objects(
            declaredate__gte=trade_date).order_by('+declaredate').limit(1).first()
    if latest_declare_meta is None:
        loge(_TAG, 'Failed to get industry classification, not meta data found')
        return DataFrame()
    return mongo_2_df(
        IndustrialClassificationItem.objects(level=level, declaredate=latest_declare_meta.declaredate, src='SW'))


def _get_industry_classificatoin_members_from_tushare(index_code: str, declaredate: int) -> DataFrame:
    try:
        logi(_TAG, 'Get classification members from tushare for %s on %d' %
             (index_code, declaredate))
        members = ts.pro_api().index_member(index_code=index_code,
                                            fields='index_code,index_name,con_code,con_name,in_date,out_date,is_new')
        members = members.rename(
            {'in_date': 'in',  'out_date': 'out'}, axis=1)
        members['in_date'] = members['in'].map(
            yyyymmdd_2_int)
        members['out_date'] = members['out'].map(
            yyyymmdd_2_int, na_action='ignore')
        members = members.drop(
            ['in', 'out'], axis=1)
        members['declaredate'] = declaredate
        df_2_mongo(members, IndustrialClassficationMemberItem)
        return members
    except BaseException as e:
        loge(_TAG, 'Failed to get classification memebers for %s from tushare cause %s' % (
            index_code, e))
        return DataFrame()


def get_industrial_classfication_members(index_code: str, trade_date=int(datetime.datetime.now().timestamp())*1000) -> DataFrame:
    '''
    获取某天某个行业分类下的成分股,如果失败，返回空的 DataFrame
    '''
    logi(_TAG, 'Get industrial classification member:%s %d' %
         (index_code, trade_date))
    latest_declare_meta = IndustryClassificatoinMetaItem.objects(
        declaredate__lte=trade_date).order_by('-declaredate').limit(1).first()
    if latest_declare_meta is None:
        latest_declare_meta = IndustryClassificatoinMetaItem.objects(
            declaredate__gte=trade_date).order_by('+declaredate').limit(1).first()
    if latest_declare_meta is None:
        loge(_TAG, 'Failed to get industry classification members, not meta data found')
        return DataFrame()
    return mongo_2_df(
        IndustrialClassficationMemberItem.objects(index_code=index_code, declaredate=latest_declare_meta.declaredate))


def get_industrial_classification_for(ts_code: str, trade_date=int(datetime.datetime.now().timestamp())*1000) -> DataFrame:
    '''
    获取指定股票的行业分类index code
    '''
    latest_declare_meta = IndustryClassificatoinMetaItem.objects(
        declaredate__lte=trade_date).order_by('-declaredate').limit(1).first()
    if latest_declare_meta is None:
        latest_declare_meta = IndustryClassificatoinMetaItem.objects(
            declaredate__gte=trade_date).order_by('+declaredate').limit(1).first()
    if latest_declare_meta is None:
        loge(_TAG, 'Failed to get industry classification, not meta data found')
        return DataFrame()
    logi(_TAG, 'Get industrial classification for %s' % ts_code)
    return mongo_2_df(IndustrialClassficationMemberItem.objects(con_code=ts_code, declaredate=latest_declare_meta.declaredate))


def _update_industry_classification(title: str, declaredate: int):
    '''
    使用参数的更新日期来获取行业分类，并保存到数据库
    '''
    # 保存meta到数据库
    meta = IndustryClassificatoinMetaItem(
        title=title, declaredate=declaredate)
    meta.save()
    # 更新行业分类数据
    for level in ['L1', 'L2', 'L3']:
        level_class_df = _get_industry_classification_from_tushare(
            level=level, declaredate=declaredate)
        if level_class_df.empty:
            loge(_TAG, 'Empty industry classification for %s' % level)
        else:
            for item in level_class_df.itertuples():
                # 3. 更新行业成分
                _get_industry_classificatoin_members_from_tushare(
                    item.index_code, declaredate)
                # 每分钟最多调用150次
                time.sleep(0.4)


def initialize_industrial_classification():
    '''
    初始化行业分类数据。不适用增量更新，不记录历史状态。
    '''
    # 1. 清空原数据库
    IndustrialClassificationItem.drop_collection()
    IndustrialClassficationMemberItem.drop_collection()
    IndustryClassificatoinMetaItem.drop_collection()
    # 2. 从 SW 获取最新的数据更新时间，并保存到数据库
    declaredate_df = _get_industry_member_declaredate_from_sw()
    if declaredate_df.empty:
        loge(_TAG, 'Failed to get declaredate from SW')
        raise QuantzException('Failed to get declaredate from SW')
    else:
        _update_industry_classification(
            title=declaredate_df.iloc[0][0], declaredate=declaredate_df.iloc[0][1])


def update_industry_classification():
    '''
    根据数据库中的数据和SW发布的公告的时间差来更新行业分数据，
    建议每天运行一次,在调用此函数之前，必须确保行业分类数据已经初始化过
    '''
    schedule_by_sw = False
    decdate_df = None
    if schedule_by_sw:
        decdate_df = _get_industry_member_declaredate_from_sw()
    else:
        today_in_ms = today_2_millisec()
        if not is_trading_day(today_in_ms):
            loge(_TAG, '%s is not a trading day, skipping update industry classification' %
                 millisec_2_YYYYMMDD(today_in_ms))
            return
        decdate_df = DataFrame(
            {'title': ['trade_date'], 'declaredate': today_2_millisec()})
    local_decdate_item = IndustryClassificatoinMetaItem.objects().order_by(
        '-declaredate').limit(1).first()
    if local_decdate_item is None:
        logi(_TAG, 'Loccal industry classification meta empty, Initialize industry classification first')
        return
    if decdate_df.iloc[0][1] > local_decdate_item.declaredate:
        logi(_TAG, 'Updating industry classification')
        # 更新数据库
        _update_industry_classification(
            title=decdate_df.iloc[0][0], declaredate=decdate_df.iloc[0][1])
    else:
        logi(_TAG, 'Local industry classification already latest, skip updating')
