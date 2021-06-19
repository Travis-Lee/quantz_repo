# -*- coding: utf-8 -*-
'''
QuantZ 数据库操作模块
TODO: 整理统一的命名规范
'''

from mongoengine import connect, disconnect

from .adj_factor_manager import init_adj_factors, update_adj_factors
from .industrial_classificataion_manager import (
    get_industrial_classfication_members, get_industrial_classification_for,
    get_industrial_classifications, initialize_industrial_classification,
    rank_all_industry, rank_all_industry_between,
    update_industry_classification)
from .institution_hold_manager import (get_instituion_hold_on_by_for,
                                       init_institution_hold,
                                       update_institution_hold)
from .model.index_daily_item import IndexDailyItem
from .quantz_exception import QuantzException
from .stock_basics_manager import (get_stock_basics,
                                   get_stock_basics_listed_earlier_than,
                                   update_stock_basics)
from .stock_trading_info_manager import (
    get_daily_trading_info_snapshot_on, initialize_daily_trading_info,
    update_all_daily_trading_info_in_batch, update_daily_trading_info,
    update_daily_trading_info_for)
from .trade_calendar_manager import (get_last_n_trade_date_b4,
                                     get_last_n_trade_dates_b4,
                                     get_last_quarter_end_date,
                                     get_last_quarter_end_date_b4,
                                     get_last_trade_date_in_ms_for,
                                     get_last_trade_date_of,
                                     get_next_trade_date_of,
                                     get_trade_dates_between,
                                     init_trade_calendar, is_trading_day)
from .us_eco import (get_us_ccsa, get_us_initial_jobless, get_us_wei,
                     update_us_ccsa, update_us_initial_jobless, update_us_wei)


def initialize_db(db: str, host='localhost', port=27017):
    '''
    初始化仓库使用的 MongoDB
    '''
    return connect(db, host=host, port=port)


def deinitialize_db():
    '''
    断开数据库连接
    '''
    disconnect()
