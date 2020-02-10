# -*- coding: utf-8 -*-

import tushare as ts

from .utils import log
from .model import IndexDailyItem

_TAG = 'IndexManager'

_MANAGED_INDEX_ = ['000001.SH', '399001.SZ',
                   '399005.SZ', '399006.SH', '000902.SH']
'''
当前关注的指数：上证指数、深证成指、中小板指、创业板指、中证流通
'''


class IndexManager(object):
    '''
    指数数据的管理类，负责指数数据的初始化、日常维护、日常更新、数据验证、对外提供访问指数数据的接口。当前只关心上证指数、深证成指、中小板指、创业板指、中证流通。
    '''

    def initializeIndex(self):
        '''
        初始化数据库中的指数数据：
        0. 000001.SH 399001.SZ 399005.SZ 399006.SZ  000902.SH(中证流通)
        1. 从网络获取指数数据，并保存到数据库
        2. 验证数据的完整性、正确性 TODO: 暂时不知如何验证数据的正确性和完整性
        '''
        for index in _MANAGED_INDEX_:
            log.d(_TAG, 'Initializing index:%s' % index)
            index_df = ts.pro_api().index_daily(ts_code=index)
            for index_item in IndexDailyItem.objects.from_json(index_df.to_json(orient='records')):
                index_item.save()
