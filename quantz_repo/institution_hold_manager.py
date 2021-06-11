import datetime

import akshare as ak
from mongoengine import (Document, FloatField, IntField, LongField,
                         StringField, connect)
from pandas import DataFrame

from .models import InstitutionHoldItem
from .quantz_exception import QuantzException
from .trade_calendar_manager import (get_last_quarter_end_date,
                                     get_last_quarter_end_date_b4)
from .utils import df_2_mongo, mongo_2_df

"""
    机构持仓数据管理
"""


institutions = ("基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓")


def symbol_2_ts_code(symbol: str) -> str:
    return '%s.%s' % (symbol, 'SH' if symbol.startswith('6') else 'SZ')


def _get_institution_hold_on_for_from_akshare(ann_date, which) -> DataFrame:
    if which in institutions:
        df = None
        try:
            df = ak.stock_report_fund_hold(
                date=ann_date.strftime('%Y%m%d'), symbol=which)
            print(df.head(6))
            # 映射股票代码到ts_code
            df['ts_code'] = df['股票代码'].apply(symbol_2_ts_code)
            df['by'] = which
            df['ann_date'] = int(ann_date.timestamp())*1000
            # 移除无用的列
            df.drop(axis=1, inplace=True, columns=['序号', '股票代码'])
            # 空数据填充为0
            df['持有基金家数'].replace('', '0', inplace=True)
            df['持股变动数值'].replace('', '0', inplace=True)
            df['持股总数'].replace('', '0', inplace=True)
            df['持股市值'].replace('', '0', inplace=True)
            df['持股变化'].replace('', '0', inplace=True)
            df['持股变动比例'].replace('', '0', inplace=True)
            # 重命名列
            df.rename(columns={'股票简称': 'ticker', '持有基金家数': 'holder_sum', '持股总数': 'hold_total_vol', '持股市值': 'hold_total_amount',
                               '持股变化': 'hold_diff', '持股变动数值': 'hold_diff_vol', '持股变动比例': 'hold_diff_pct'}, inplace=True)
            print(df.head(3))
        except Exception as e:
            raise QuantzException(
                'Failed to get institution hold for %s on %s' % (which, ann_date)) from e
        else:
            return df
    else:
        raise QuantzException('Invalide institution:%s' % which)


def init_institution_hold():
    '''
    获取最近两年的机构持仓数据
    注意，akshare 使用的爬虫可能不稳定，注意错误处理，增加重试
    初始化时会删除已有数据
    '''
    print('🚀🚀🚀 Initializing institution holdings 🚀🚀🚀')
    try:
        InstitutionHoldItem.drop_collection()
        q = get_last_quarter_end_date()
        count = 0
        while count < 8:
            # 获取最近两年数据
            for inst in institutions:
                print('🚚🚚🚚 Initializing institution hold on %s 🚚🚚🚚' %
                      q.strftime('%Y%m%d'))
                df = _get_institution_hold_on_for_from_akshare(
                    ann_date=q, which=inst)
                df_2_mongo(df, InstitutionHoldItem)
            q = get_last_quarter_end_date_b4(q)
            count = count + 1
    except Exception as e:
        raise QuantzException('🚑🚑🚑 Failed to init institution hold 🚑🚑🚑') from e
    else:
        print('👍👍👍 Institution hold initialized successfully 👍👍👍')


def update_institution_hold():
    '''
    更新机构持仓数据
    注意，akshare 使用的爬虫可能不稳定，注意错误处理，增加重试
    初始化时会删除已有数据
    '''
    print('🚀🚀🚀 Updating institution holdings 🚀🚀🚀')
    try:
        q = get_last_quarter_end_date()
        last_ann_date_in_ms = InstitutionHoldItem.objects().order_by(
            '-ann_date').limit(1).first().ann_date
        while last_ann_date_in_ms < int(q.timestamp()) * 1000:
            # 获取最近两年数据
            for inst in institutions:
                print('🚚🚚🚚 Updating institution hold on %s 🚚🚚🚚' %
                      q.strftime('%Y%m%d'))
                df = _get_institution_hold_on_for_from_akshare(
                    ann_date=q, which=inst)
                df_2_mongo(df, InstitutionHoldItem)
            q = get_last_quarter_end_date_b4(q)
    except Exception as e:
        raise QuantzException(
            '🚑🚑🚑 Failed to update institution hold 🚑🚑🚑') from e
    else:
        print('👍👍👍 Institution hold updated successfully 👍👍👍')


def get_instituion_hold_on_by_for(day: str, by: str = None, ts_code: str = None) -> DataFrame:
    '''
    从本地获取在某一天之前的季度结束，某个类型机构的持仓
    day: YYYYmmdd,必选参数
    by: 可选参数，若为空，获取所有机构持仓，"基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"
    ts_code: 获取某一只股票的机构持仓，若为空，获取所有股票的数据
    '''
    print('🚀🚀🚀 Get institution hold on %s by %s for %s 🚀🚀🚀' % (day, by, ts_code))
    if by is not None and by not in institutions:
        raise QuantzException('🚑🚑🚑 No institution called %s 🚑🚑🚑' % by)
    df = None
    try:
        lasq_q = get_last_quarter_end_date_b4(
            datetime.datetime.strptime(day, '%Y%m%d'))
        print('🏗🏗🏗 WIP %s 🏗🏗🏗' % lasq_q.strftime('%Y%m%d'))
        where = {'ann_date': int(lasq_q.timestamp()) * 1000}
        if by is not None:
            where['by'] = by
        if ts_code is not None:
            where['ts_code'] = ts_code
        holds = InstitutionHoldItem.objects(**where)
        df = mongo_2_df(holds)
        if df is None or df.empty:
            print('😔😔😔 Got empty institution hold on %s by %s for %s, something may by wrong or not 😔😔😔😔' % (
                by, day, ts_code))
        else:
            print('👍👍👍 Got institution hold on %s by %s for %s 👍👍👍' %
                  (by, day, ts_code))
    except Exception as e:
        raise QuantzException('🚑🚑🚑 Failed to get institution hold on %s by %s for %s🚑🚑🚑' % (
            day, by, ts_code)) from e
    else:
        return df
