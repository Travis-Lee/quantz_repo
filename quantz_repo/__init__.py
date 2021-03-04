# -*- coding: utf-8 -*-
'''
QuantZ 数据库操作模块
'''

from mongoengine import connect, disconnect

from .quantz_exception import QuantzException

from .us_eco import get_us_initial_jobless, get_us_wei
from .industrial_classificataion_manager import initialize_industrial_classification, get_industrial_classifications, get_industrial_classfication_members, get_industrial_classification_for

from .model.index_daily_item import IndexDailyItem

from .stock_basics_manager import update_stock_basics, get_stock_basics
from .trade_calendar_manager import init_trade_calendar
from .stock_trading_info_manager import initialize_daily_trading_info, update_daily_trading_info_for, update_daily_trading_info


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
