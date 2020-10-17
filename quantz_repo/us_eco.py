from datetime import date
import json

import akshare as ak
import pandas as pd

from .model.us_eco_models import UsJoblessInitialClaimItem
from .utils.data_repo import df_2_mongo, mongo_2_df
from .utils.date_time import get_last_thursday


def update_us_initial_jobless():
    '''
     更新美国首次申领失业金人数到 MongoDB
     TODO: 1. 增加网络异常处理 2. 增加在内存中缓存DataFrame数据，不需要每次都和抓取的数据
    '''
    us_initial_jobless = ak.macro_usa_initial_jobless()
    temp_df = pd.DataFrame(data={'when': us_initial_jobless.index.strftime(
        '%Y-%m-%d'), 'initial_jobless': us_initial_jobless.values})
    temp_df.astype({'when': 'datetime64[ns, UTC]'}, copy=False)
    item = UsJoblessInitialClaimItem.objects.order_by('-when').limit(1).first()
    if item is not None:
        temp_df = temp_df[temp_df['when'] > item.when.strftime('%Y-%m-%d')]
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
    if latest_item is None or last_thursday.strftime('%Y%m%d') > latest_item.when.strftime('%Y%m%d'):
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
