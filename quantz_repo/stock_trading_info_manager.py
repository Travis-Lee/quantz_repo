import datetime
import sys

import akshare as ak
import pandas as pd
import tushare as ts
from pandas import DataFrame, Series

from . import QuantzException, get_stock_basics
from .model import BasicStockInfoItem, BasicTradingInfoItem
from .models import TradingInfoUpdateMetaItem
from .trade_calendar_manager import (get_last_trade_date_in_ms_for,
                                     get_next_trade_date_of, is_trading_day)
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
    daily_df['freq'] = 'D'
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
    if next_trade_date > now_2_YYYYMMDD():
        log.i(__TAG__, 'Next trade date %s in future than %s, skipping update daily trading info for %s' % (
            next_trade_date, now_2_YYYYMMDD(), ts_code))
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
        daily_df['freq'] = 'D'
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


PRICE_COLS = ['open', 'close', 'high', 'low', 'pre_close']
def FORMAT(x): return '%.4f' % x


def batch_bar(ts_code='', start_date='', end_date='', freq='D', asset='E', adj=None):
    bars = ts.pro_bar(ts_code=ts_code, start_date=start_date,
                      end_date=end_date, freq=freq, asset=asset)
    bars['freq'] = 'D'
    if adj is not None:
        fcts = ts.pro_api().adj_factor(
            ts_code=ts_code, start_date=start_date, end_date=end_date)
        if fcts.shape[0] == 0:
            print('Failed to get adj factors')
            return
        result = DataFrame()
        for code in ts_code.split(','):
            code = code.strip()
            cur_bars = bars[bars['ts_code'] == code].reset_index(drop=True)
            cur_fcts = fcts[fcts['ts_code'] == code].reset_index(
                drop=True)[['trade_date', 'adj_factor']]
            if cur_bars.empty:
                print('No valid bar for %s between %s - %s, please check it' %
                      (code, start_date, end_date))
                continue
            cur_bars = cur_bars.set_index('trade_date', drop=False).merge(
                cur_fcts.set_index('trade_date'), left_index=True, right_index=True, how='left')
            if 'min' in freq:
                cur_bars = cur_bars.sort_values('trade_time', ascending=False)
            cur_bars['adj_factor'] = cur_bars['adj_factor'].fillna(
                method='bfill')
            print('cur code:%s' % code)
            print('cur_bars')
            print(cur_bars)
            print('cur_fcts')
            print(cur_fcts)
            if adj is not None and cur_fcts.empty:
                print('Could not adj price for %s between %s-%s, cause adj factor empty' %
                      (code, start_date, end_date))
            for col in PRICE_COLS:
                if adj == 'hfq' and not cur_fcts.empty:
                    cur_bars[col] = cur_bars[col] * cur_bars['adj_factor']
                if adj == 'qfq' and not cur_fcts.empty:
                    cur_bars[col] = cur_bars[col] * cur_bars['adj_factor'] / \
                        float(cur_fcts['adj_factor'][0])
                cur_bars[col] = cur_bars[col].map(FORMAT)
                cur_bars[col] = cur_bars[col].astype(float)
            cur_bars = cur_bars.drop('adj_factor', axis=1)
            if 'min' not in freq:
                cur_bars['change'] = cur_bars['close'] - cur_bars['pre_close']
                cur_bars['pct_chg'] = cur_bars['change'] / \
                    cur_bars['pre_close'] * 100
                cur_bars['pct_chg'] = cur_bars['pct_chg'].map(
                    lambda x: FORMAT(x)).astype(float)
            else:
                cur_bars = cur_bars.drop(['trade_date', 'pre_close'], axis=1)
            cur_bars.reset_index(drop=True, inplace=True)
            result = pd.concat([result, cur_bars], ignore_index=True)
        bars = result.reset_index(drop=True)
        bars['trade_date'] = bars['trade_date'].map(yyyymmdd_2_int)
    print('batch bars')
    print(bars)
    return bars


def trading_info_2_mongo(info: DataFrame):
    if info is None or info.empty:
        print('Skip empty data')
        return
    info = info.sort_values(by='trade_date', axis=0,
                            ascending=True, ignore_index=True)
    last = BasicTradingInfoItem.objects(
        ts_code=info['ts_code'][0], freq=info['freq'][0]).order_by('-trade_date').limit(1).first()
    start_date = last.trade_date if last is not None else -sys.maxsize-1
    print(info[info['trade_date'] > start_date])
    df_2_mongo(info[info['trade_date'] > start_date], BasicTradingInfoItem)
    print('done')
    return None


def update_daily_trading_info_in_batch(ts_code, start_date, end_date):
    print('Update daily trading info in batch')
    bars = batch_bar(ts_code=ts_code, start_date=start_date,
                     end_date=end_date, adj='qfq')
    if bars is None or bars.empty:
        print('None bar for %s between %s - %s' %
              (ts_code, start_date, end_date))
    for code in ts_code.split(','):
        trading_info_2_mongo(bars[bars['ts_code'] == code.strip()])
    return None


def get_last_ok_date(freq='D') -> str:
    last = TradingInfoUpdateMetaItem.objects(
        freq='D').order_by('-last_ok_date').limit(1).first()
    last_ms = last.last_ok_date if last is not None else get_last_trade_date_in_ms_for(
        exchange='SSE', adj=True)
    return timestamp_2_YYYYMMDD(last_ms)


def save_last_ok_date(trade_date, freq='D'):
    TradingInfoUpdateMetaItem(
        last_ok_date=yyyymmdd_2_int(trade_date), freq='D').save()


def update_all_daily_trading_info_in_batch():
    ''' Update all 日线数据到最新
    '''
    start_date = get_last_ok_date(freq='D')
    end_date = timestamp_2_YYYYMMDD(
        get_last_trade_date_in_ms_for(exchange='SSE', adj=True))
    if start_date is None or start_date == '' or end_date is None or end_date == '':
        print('Failed to update all daily trading info case invalid trade date(%s-%s)' %
              (start_date, end_date))
        return
    try:
        basics = get_stock_basics()
        data = basics
        count = 0
        # Tushare限制最大100个
        batch_size = 100
        # size = data.shape[0]
        done = False
        while not done:
            start = batch_size * count
            end = batch_size * (count + 1)
            if end > data.shape[0]:
                end = data.shape[0]
                done = True
            ts_codes = str(data['ts_code'][start:end].to_string(
                header=False, index=False))
            ts_codes = ts_codes.replace('\n', ',')
            # print(ts_codes)
            update_daily_trading_info_in_batch(ts_codes, start_date, end_date)
            print('####################')
            count = count + 1
    except Exception as e:
        print('Something is wrong')
        raise QuantzException('Failed to update all daily trading info') from e
    else:
        save_last_ok_date(end_date, freq='D')
        print('Update daily trading info to %s ✔✔✔' % end_date)


# update_all_daily_trading_info_in_batch()
def get_daily_trading_info_snapshot_on(day: str) -> DataFrame:
    day_in_ms = yyyymmdd_2_int(day)
    if not is_trading_day(day_in_ms):
        log.i(__TAG__, '🔥🔥🔥 %s is not trade date, returning empty DF 🔥🔥🔥')
        return DataFrame()
    try:
        return mongo_2_df(BasicTradingInfoItem.objects(trade_date=day_in_ms, freq='D'))
    except Exception as e:
        raise QuantzException(
            '🚑🚑🚑 Failed to get daily snapshot on %s 🚑🚑🚑' % day) from e
