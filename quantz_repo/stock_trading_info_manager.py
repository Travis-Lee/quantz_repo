import akshare as ak
import datetime
import pandas as pd
import tushare as ts
from pandas import DataFrame, Series

from . import get_stock_basics
from .model import BasicStockInfoItem, BasicTradingInfoItem
from .utils import (df_2_mongo, get_next_day_in_YYYYMMDD, mongo_2_df,
                    timestamp_2_YYYYMMDD, yyyymmdd_2_int, log)


__TAG__ = 'StockTradingInfo'


def ma_for(data: DataFrame, args: dict) -> DataFrame:
    '''
    对于指定的 DataFrame 的某些列计算不同时间间隔的 SMA, 并将结果追加到原DataFrame
    '''
    for col in args:
        for w in args[col]:
            data['ma_%s_%d' % (col, w)] = data[col].rolling(w).mean().round(4)
    return data


def initialize_daily_trading_info():
    '''
    日线信息初始化，从TS获取数据，并计算SMA 20 60 收存入数据库
    TODO:增加时间周期标识标识，
    '''
    # count = 0
    basics = get_stock_basics()
    if not basics.empty:
        for i in basics.itertuples():
            # count += 1
            daily_df = ts.pro_bar(
                ts_code=i.ts_code, asset='E', adj='qfq', freq='D')
            daily_df = daily_df.sort_values(
                by=['trade_date'], ascending=True, ignore_index=True)
            daily_df = daily_df.rename({'trade_date': 't'}, axis=1)
            daily_df['trade_date'] = daily_df['t'].map(yyyymmdd_2_int)
            daily_df = daily_df.drop('t', axis=1)
            daily_df = ma_for(daily_df, {'close': [20, 60]})
            df_2_mongo(daily_df, BasicTradingInfoItem)
            print(daily_df.tail(3))
            # if count > 3:
            #    break


def update_daily_trading_info_for(ts_code: str):
    '''
    更新某只股票的日线数据到最新
    '''
    log.i(__TAG__, 'Updating daily for %s' % ts_code)
    latest_item = BasicTradingInfoItem.objects(
        ts_code=ts_code).order_by('-trade_date').first()
    if latest_item is None:
        log.i(__TAG__, 'No data for %s, please check ts_code and make sure your DB initialized' % ts_code)
        return
    if latest_item.trade_date >= datetime.datetime.today().timestamp() * 1000:
        # TODO: 待改进，使用整天时间对比
        log.i(__TAG__, 'No need to get data from future')
        return
    daily_df = ts.pro_bar(ts_code=ts_code, start_date=get_next_day_in_YYYYMMDD(
        latest_item.trade_date), asset='E', adj='qfq', freq='D')
    if daily_df is None:
        log.i(__TAG__, 'No data updated since %s for %s' %
              (timestamp_2_YYYYMMDD(latest_item.trade_date), ts_code))
        return
    if not daily_df.empty:
        daily_df = daily_df.sort_values(
            by=['trade_date'], ascending=True, ignore_index=True)
        daily_df = daily_df.rename({'trade_date': 't'}, axis=1)
        daily_df['trade_date'] = daily_df['t'].map(yyyymmdd_2_int)
        daily_df = daily_df.drop('t', axis=1)
        latest_items = mongo_2_df(BasicTradingInfoItem.objects(
            ts_code=ts_code).order_by('-trade_date').limit(60))
        latest_items = latest_items.append(daily_df)
        latest_items = ma_for(latest_items, {'close': [20, 60]})
        df_2_mongo(latest_items[-daily_df.shape[0]:], BasicTradingInfoItem)
        return latest_items[-daily_df.shape[0]:]
    else:
        log.i(__TAG__, 'No data updated since %s for %s' %
              (timestamp_2_YYYYMMDD(latest_item.trade_date), ts_code))


def update_daily_trading_info():
    basics = get_stock_basics()
    if basics is None:
        log.e(__TAG__,  'Failed to get stock list, please make sure your db initialized or available network connection')
        return
    if not basics.empty:
        for i in basics.itertuples():
            log.i(__TAG__, 'Updating for %s:%s' % (i.ts_code, i.name))
            print(update_daily_trading_info_for(i.ts_code))
    else:
        log.e(__TAG__,  'Empty stock list got, please make sure your db initialized or available network connection')
