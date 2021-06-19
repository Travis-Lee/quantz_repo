import tushare as ts

from .models import AdjFactorItem, MetaDataItem
from .quantz_exception import QuantzException
from .trade_calendar_manager import (get_last_n_trade_dates_b4,
                                     get_trade_dates_between)
from .utils import (df_2_mongo, logi, logw, mongo_2_df, now_2_YYYYMMDD,
                    timestamp_2_YYYYMMDD)

__DATA_NAME = 'ts_adj_factor'
__INIT_ADJ_SUM = 750
__TAG = 'AdjFactor'


def get_latest_adj_factor_meta() -> MetaDataItem:
    return MetaDataItem.objects(data_set=__DATA_NAME).order_by('-update_date').limit(1).first()


def get_adj_factor_meta_on(day) -> MetaDataItem:
    """
    day in ms
    """
    return MetaDataItem.objects(data_set=__DATA_NAME, update_date=day).first()


def __adj_factor_ts_2_mongo(day_ms):
    try:
        meta = get_adj_factor_meta_on(day_ms)
        if meta is None:
            df_2_mongo(ts.pro_api().adj_factor(
                trade_date=timestamp_2_YYYYMMDD(day_ms)), AdjFactorItem)
        else:
            logw(__TAG, 'Adj factor on %s already exists, skip' %
                 timestamp_2_YYYYMMDD(day_ms))
            return
    except Exception as e:
        raise QuantzException('Failed to get adj factor on %s' %
                              timestamp_2_YYYYMMDD(day_ms)) from e
    else:
        MetaDataItem(data_set=__DATA_NAME,
                     update_date=day_ms, metadata='OK').save()
        logi(__TAG, 'Adj Factors on %s updated' % timestamp_2_YYYYMMDD(day_ms))


def init_adj_factors():
    """
    初始化最近3年，750个交易日的复权因子
    """
    try:
        days = get_last_n_trade_dates_b4(
            n=__INIT_ADJ_SUM, day=now_2_YYYYMMDD(), inc=True)
        days.sort_values(by='cal_date', ascending=True,
                         inplace=True, ignore_index=True)
        for day in days['cal_date'].values:
            __adj_factor_ts_2_mongo(day)
    except Exception as e:
        raise QuantzException('Failed to initialize adj factors') from e
    else:
        logi(__TAG, 'Adj factor initialized')


def update_adj_factors():
    """
    更新复权因子到最新
    """
    logi(__TAG, 'Update adj factors to latest')
    try:
        meta = get_latest_adj_factor_meta()
        if meta is None:
            raise Exception(
                'Failed to update adj factors, make sure you have initialized the dada')
        days = get_trade_dates_between(timestamp_2_YYYYMMDD(meta.update_date))
        for day in days['cal_date'].values:
            __adj_factor_ts_2_mongo(day)
    except Exception as e:
        raise QuantzException('Failed to update adj factors') from e
    else:
        logi(__TAG, 'Adj factor updated')
