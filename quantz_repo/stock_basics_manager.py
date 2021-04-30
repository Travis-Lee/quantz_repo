import tushare as ts
from pandas import DataFrame

from .model import BasicStockInfoItem
from .utils import df_2_mongo, mongo_2_df, log, yyyymmdd_2_int

'''
管理A股股票基本信息
'''
__TAG__ = 'StockBasics'


def update_stock_basics():
    '''
    更新股票基本信息，先清空已有信息后更新
    '''
    log.i(__TAG__, 'Updating stock basics')
    BasicStockInfoItem.drop_collection()
    try:
        basics_df = ts.pro_api().stock_basic(
            fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
        if not basics_df.empty:
            basics_df = basics_df.rename(
                {'list_date': 'l', 'delist_date': 'd'}, axis=1)
            basics_df['list_date'] = basics_df['l'].map(yyyymmdd_2_int)
            basics_df = basics_df.drop(['l', 'd'], axis=1)
            df_2_mongo(basics_df, BasicStockInfoItem)
            return basics_df
        else:
            log.e(__TAG__, 'Failed to get stock basic from ts')
    except BaseException as e:
        log.e(__TAG__, 'Get exception while getting stock basics from ts:\n%s' % e)
        return DataFrame()


def get_stock_basics() -> DataFrame:
    items = BasicStockInfoItem.objects()
    if items.count() > 0:
        log.i(__TAG__, 'Get stock basics from mongo')
        return mongo_2_df(items)
    else:
        log.i(__TAG__, 'Get stock basics from ts')
        return update_stock_basics()
