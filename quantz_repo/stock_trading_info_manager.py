import datetime

import akshare as ak
import pandas as pd
import tushare as ts
from pandas import DataFrame, Series

from . import QuantzException, get_stock_basics
from .model import BasicStockInfoItem, BasicTradingInfoItem
from .trade_calendar_manager import get_next_trade_date_of
from .utils import (df_2_mongo, get_next_day_in_YYYYMMDD, log,
                    millisec_2_YYYYMMDD, mongo_2_df, now_2_YYYYMMDD,
                    timestamp_2_YYYYMMDD, yyyymmdd_2_int)

__TAG__ = 'StockTradingInfo'


def ma_for(data: DataFrame, args: dict) -> DataFrame:
    '''
    对于指定的 DataFrame 的某些列计算不同时间间隔的 SMA, 并将结果追加到原DataFrame
    '''
    for col in args:
        for w in args[col]:
            data['ma_%s_%d' % (col, w)] = data[col].rolling(w).mean().round(4)
    return data


def initialize_daily_trading_info_for(ts_code: str):
    '''
    初始化某只股票的日线数据到本地mongo
    '''
    log.i(__TAG__, ts_code)
    daily_df = ts.pro_bar(
        ts_code=ts_code, asset='E', adj='qfq', freq='D')
    if daily_df is None or daily_df.empty:
        log.i(__TAG__, 'No daily trading info for %s initialization, might be new listed' % ts_code)
        return
    daily_df = daily_df.sort_values(
        by=['trade_date'], ascending=True, ignore_index=True)
    daily_df = daily_df.rename({'trade_date': 't'}, axis=1)
    daily_df['trade_date'] = daily_df['t'].map(yyyymmdd_2_int)
    daily_df = daily_df.drop('t', axis=1)
    daily_df = ma_for(daily_df, {'close': [20, 60]})
    df_2_mongo(daily_df, BasicTradingInfoItem)
    log.d(__TAG__, daily_df.tail(3))


def initialize_daily_trading_info():
    '''
    日线信息初始化，从TS获取数据，并计算SMA 20 60 收存入数据库
    TODO:增加时间周期标识标识，
    '''
    # count = 0
    basics = get_stock_basics()
    if not basics.empty:
        for i in basics.itertuples():
            if BasicTradingInfoItem.objects(ts_code=i.ts_code).count() == 0:
                initialize_daily_trading_info_for(i.ts_code)
            else:
                update_daily_trading_info_for(i.ts_code)
            # count += 1
            # if count > 3:
            #    break
        log.i(__TAG__, 'Daily trading info initialized ✔ ✔ ✔')
    else:
        log.i(
            __TAG__, 'Failed to initialize daily trading info cause empty stock list ✘ ✘ ✘')


def update_daily_trading_info_for(ts_code: str):
    '''
    更新某只股票的日线数据到最新
    '''
    log.i(__TAG__, 'Updating daily for %s' % ts_code)
    latest_item = BasicTradingInfoItem.objects(
        ts_code=ts_code).order_by('-trade_date').first()
    if latest_item is None:
        '''
        上市新股，在初始化数据库时未包含在数据库中，现在初始化这个新股的数据
        '''
        initialize_daily_trading_info_for(ts_code)
        return
    next_trade_date = get_next_trade_date_of(
        millisec_2_YYYYMMDD(latest_item.trade_date))
    if next_trade_date is None:
        log.i(__TAG__, 'No trade date since %s for %s' %
              (latest_item.trade_date, ts_code))
        return
    if next_trade_date >= now_2_YYYYMMDD():
        log.i(__TAG__, 'Next trade date in future, skipping update daily trading info for %s' % ts_code)
        return
    if latest_item.trade_date >= datetime.datetime.today().timestamp() * 1000:
        # TODO: 待改进，使用整天时间对比
        log.i(__TAG__, 'Already latest daily info for %s' % ts_code)
        return
    daily_df = ts.pro_bar(ts_code=ts_code, start_date=get_next_day_in_YYYYMMDD(
        latest_item.trade_date), asset='E', adj='qfq', freq='D')
    # TODO: 将get_next_day_in_YYYYMMDD 改为获取下一个交易日，如果下一个交易日是未来，跳过更新
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
    if basics is None or basics.empty:
        log.e(__TAG__,  'Failed to get stock list, please make sure your db initialized or available network connection')
        return
    if not basics.empty:
        start = datetime.datetime.now()
        for i in basics.itertuples():
            log.i(__TAG__, 'Updating for %s:%s' % (i.ts_code, i.name))
            print(update_daily_trading_info_for(i.ts_code))
        end = datetime.datetime.now()
        log.i(__TAG__,  'Update start at %s end at %s, %s' %
              (start.strftime('%H:%M:%S'), end.strftime('%H:%M:%S'), end - start))
    else:
        log.e(__TAG__,  'Empty stock list got, please make sure your db initialized or available network connection')
