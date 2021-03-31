import json
from datetime import date, datetime, timedelta
import os

import akshare as ak
import gdown
import numpy as np
import pandas as pd
from pandas import DataFrame

from .model.us_eco_models import UsJoblessInitialClaimItem, UsWeiItem
from .utils.data_repo import df_2_mongo, mongo_2_df
from .utils.date_time import get_last_thursday
from .utils.fred import Fred
from .utils import log


def update_us_initial_jobless():
    '''
     更新美国首次申领失业金人数到 MongoDB
     TODO: 1. 增加网络异常处理 2. 增加在内存中缓存DataFrame数据，不需要每次都和抓取的数据
    '''
    us_initial_jobless = ak.macro_usa_initial_jobless()
    temp_df = pd.DataFrame(data={'when': us_initial_jobless.index.astype(
        np.int64)/1000000, 'initial_jobless': us_initial_jobless.values})
    item = UsJoblessInitialClaimItem.objects.order_by('-when').limit(1).first()
    if item is not None:
        temp_df = temp_df[temp_df['when'] > item.when]
    # temp_df = temp_df.sort_values(
    #     by=['when'], ascending=False, ignore_index=True)
    if (temp_df.shape[0] > 0):
        df_2_mongo(temp_df, UsJoblessInitialClaimItem)
    return temp_df


def jobless_transformer(x):
    if isinstance(x, dict):
        a = date.fromtimestamp(x['$date']/1000)
        return a
    else:
        return x


def get_us_initial_jobless(limit: int = 300):
    '''
    获取美国首次申领失业金人数，默认获取最近300条数据，如果本地数据库中的数据不是最新的，
    会通过 akshare  更新数据库中的数据
    本方法调用较慢，使用时请自己增加缓存。
    失业数据由美国 Department of Labour 每周四更新一次。
    '''
    # DOL publish jobless claims every thursday, so check whether we have the latest data in
    # local db, if not,get it from akshare
    last_thursday = get_last_thursday()
    latest_item = UsJoblessInitialClaimItem.objects.order_by(
        '-when').limit(1).first()
    if latest_item is None or last_thursday.timestamp() > latest_item.when:
        update_us_initial_jobless()
    jobless_claims = UsJoblessInitialClaimItem.objects.order_by(
        '-when').limit(limit)
    jobless_claims_df = pd.DataFrame.from_dict(
        json.loads(jobless_claims.to_json()))
    # remove column _id
    if jobless_claims_df.shape[1] > 1:
        jobless_claims_df = jobless_claims_df.drop('_id', axis=1)
    # transform date time
    result = jobless_claims_df.applymap(jobless_transformer)
    return result


def _get_us_wei_from_fred() -> DataFrame:
    # 从 fred 下载 wei 数据
    try:
        wei_json = Fred().series.observations(
            {'series_id': 'wei', 'sort_order': 'desc'})
        wei_df = DataFrame(wei_json['observations'])
        wei_df['WEI'] = wei_df['value'].astype(np.float)
        # 将 yyyy-mm-dd 格式的日期转换成 ms
        wei_df['DATE'] = wei_df['date'].astype(np.datetime64)
        wei_df['DATE'] = wei_df['DATE'].astype(np.int64)
        wei_df['DATE'] = wei_df['DATE']/1000000
        wei_df['DATE'] = wei_df['DATE'].astype(np.int64)
        wei_df.drop(axis=1, inplace=True, columns=[
                    'realtime_start', 'realtime_end', 'date', 'value'])
        print(wei_df.dtypes)
        print(wei_df.head)
        return wei_df
    except BaseException as e:
        log.e('Failed to obtain WEI from fred cause %s' % e)
        return DataFrame()


def _get_us_wei_from_gd() -> pd.DataFrame:
    '''
    从 Google Drive 下载 WEI 数据，并保存到数据库中,参考 https://www.jimstock.org/
    '''
    wei_file = gdown.download('https://drive.google.com/uc?id=192MTTC1Tqol_LLgF-00R7-2c8jel-QmV',
                              output=os.path.join(os.path.expanduser('~'), 'wei.xlsx'), quiet=False)
    print('\n%s' % wei_file)
    with pd.ExcelFile(wei_file) as xls:
        wei_df = pd.read_excel(xls, sheet_name='Sheet1')
    wei_date = wei_df['Date'].astype(np.int64)
    print(wei_date)
    # 以毫秒时间戳保存时间
    wei_date = wei_date / 1000000
    print(wei_date)
    wei_df['DATE'] = wei_date.astype(np.int64)
    # wei_df.rename(axis=1, columns={'Date': 'when'})
    wei_df = wei_df.drop('Date', axis=1)
    # wei_df.rename(columns={'WEI': 'value'}, inplace=True)
    # wei_df = wei_df.sort_values(
    #     by=['when'], ascending=False, ignore_index=True)
    os.remove(wei_file)
    return wei_df


def update_us_wei():
    '''
    更新数据库中 WEI 数据到最新。若有更新，返回最新的全量 WEI 数据， 否则返回 None
    '''
    latest_wei_item = UsWeiItem.objects.order_by('-DATE').limit(1).first()
    result_df = None
    if latest_wei_item is None:
        # 数据库中没有WEI数据，初始化
        # result_df = _get_us_wei_from_gd(),不再从Google drive 下载wei数据
        result_df = _get_us_wei_from_fred()
        df_2_mongo(result_df, UsWeiItem)
    elif datetime.today() - datetime.fromtimestamp(latest_wei_item.DATE/1000) >= timedelta(days=12):
        # 数据库中包含了WEI数据，但是最新 WEI 距今1周及以上
        # FIXME: WEI 数据的时间与WEI的发布时间存在大概5天时间差，可能导致重复多次下载数据，
        # 上边的12=7+5是经验值，随着使用增加继续优化这个数值
        UsWeiItem.drop_collection()
        result_df = _get_us_wei_from_gd()
        df_2_mongo(result_df, UsWeiItem)
    return result_df


def get_us_wei() -> DataFrame:
    '''
    获取 WEI 数据， 若数据库为空或数据库中不是最新的数据，则从网络获取
    返回按照时间逆序排列的 WEI
    '''
    wei_df = update_us_wei()
    if wei_df is not None and not wei_df.empty:
        return wei_df
    else:
        return mongo_2_df(UsWeiItem.objects.order_by('-DATE'))
