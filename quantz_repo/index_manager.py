# -*- coding: utf-8 -*-

import json

import tushare as ts
from pandas import DataFrame

from . import utils
from .model import IndexDailyItem
from .quantz_exception import QuantzException
from .utils import log

_TAG = 'IndexManager'

_MANAGED_INDEX_ = ['000001.SH', '399001.SZ',
                   '399005.SZ', '399006.SH', '000902.SH']
'''
当前关注的指数：上证指数、深证成指、中小板指、创业板指、中证流通
'''


def _logd(msg: str):
    """
    打印 debug log
    :param msg: 消息
    :type msg: str
    """
    log.d('IndexManager', str)


def _logw(msg: str):
    """
    打印警告 log
    :param msg: 消息
    :type msg: str
    """
    log.w('IndexManager', str)


class IndexManager(object):
    '''
    指数数据的管理类，负责指数数据的初始化、日常维护、日常更新、数据验证、对外提供访问指数数据的接口。当前只关心上证指数、深证成指、中小板指、创业板指、中证流通。
    '''

    def initialize_index(self):
        '''
        初始化数据库中的指数数据：
        0. 000001.SH 399001.SZ 399005.SZ 399006.SZ  000902.SH(中证流通)
        1. 从网络获取指数数据，并保存到数据库
        2. 验证数据的完整性、正确性 TODO: 暂时不知如何验证数据的正确性和完整性，比如通过交易日历比对、交易起始日期
        '''
        for index in _MANAGED_INDEX_:
            log.d(_TAG, 'Initializing index:%s' % index)
            index_df = ts.pro_api().index_daily(ts_code=index)
            for index_item in IndexDailyItem.objects.from_json(index_df.to_json(orient='records')):
                # TODO: 待优化数据保存方式
                index_item.save()

    def get_index_daily(self, code: str, start_date: str = '', end_date: str = ''):
        """ 获取指数日线数据

        :param code: [description]
        :type code: str
        :param start_date: [description], defaults to ''
        :type start_date: str, optional
        :param end_date: [description], defaults to ''
        :type end_date: str, optional
        :raises QuantzException: [description]
        :return: [description]
        :rtype: [type]
        """
        if code is None or '' == code:
            raise QuantzException(
                'Failed to get_index_daily(Index code is empty)')
        if end_date == '':
            end_date = utils.now_2_YYYYMMDD()
        if (start_date != '' and int(start_date) > int(end_date)):
            raise QuantzException(
                'Failed to get_index_daily(start_date must gte end_date)'
            )
        if not self._is_data_available(code, start_date, end_date):
            _logd('Not All data available')
            if not self._obtain_delta_data(code, start_date, end_date):
                _logw('Failed to obtain data for %s' % (code))
                raise QuantzException(
                    'Could not get full data for %s from %s to %s' % (code, start_date, end_date))
        index_objects = IndexDailyItem.objects(
            ts_code=code, trade_date__gte=start_date, trade_date__lte=end_date)
        index_df = DataFrame.from_dict(json.loads(index_objects.to_json()))
        if index_df.shape[1] > 1:
            index_df = index_df.drop('_id', axis=1)
        return index_df

    def _is_data_available(self, code: str, start_date='', end_date=''):
        """
        确定当前数据库中数据库中指定时间段内的数据是否满足要求。

        :param code: 指定指数
        :type code: str
        :param start_date: 指数的起始日期, defaults to ''
        :type start_date: str, optional
        :param end_date: 指数的结束日期, defaults to ''
        :type end_date: str, optional
        :return: 如果数据满足需求，返回 True, 否则返回 False
        """
        _logw('_is_data_available to be implemented!!!')
        return True

    def _obtain_delta_data(self, code: str, start_date='', end_date=''):
        """
        若数据库中尚未包含请求的数据，那么在这里更新数据库，
        :param code: 指数代码
        :type code: str
        :param start_date: 起始日期, defaults to ''
        :type start_date: str, optional
        :param end_date: 结束日期, defaults to ''
        :type end_date: str, optional
        :return: 若获取数据成功，并且满足请求，返回 True，否则返回 False
        :rtype: [type]
        """
        return True
