# -*- coding: utf-8 -*-
'''
QuantZ 数据库操作模块
'''

from mongoengine import connect, disconnect

from .industrial_classificataion_manager import (
    get_industrial_classfication_members, get_industrial_classification_for,
    get_industrial_classifications, initialize_industrial_classification,
    update_industry_classification)
from .model.index_daily_item import IndexDailyItem
from .quantz_exception import QuantzException
from .stock_basics_manager import get_stock_basics, update_stock_basics
from .stock_trading_info_manager import (initialize_daily_trading_info,
                                         update_daily_trading_info,
                                         update_daily_trading_info_for)
from .trade_calendar_manager import (get_trade_dates_between,
                                     init_trade_calendar, is_trading_day)
from .us_eco import get_us_ccsa, get_us_initial_jobless, get_us_wei


def initialize_db(db: str, host: str, port: int):
    '''
    初始化仓库使用的 MongoDB
    '''
    connect(db, host=host, port=port)


def deinitialize_db():
    '''
    断开数据库连接
    '''
    disconnect()
