# -*- coding: utf-8 -*-
'''
QuantZ 数据库操作模块
'''

from mongoengine import connect, disconnect

from .quantz_exception import QuantzException

from .us_eco import get_us_initial_jobless, get_us_wei
from .industrial_classificataion_manager import initialize_industrial_classification, get_industrial_classifications, get_industrial_classfication_members, get_industrial_classification_for


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
