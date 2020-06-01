import base64
import functools
import json
from unittest import TestCase

from mongoengine import Document, connect, disconnect
from quantz_repo.model import IndexDailyItem

params = '''
{
	"filters":["ts_code=399006.SZ", "trade_date__lte=20200501"],
	"order_by": ["-trade_date", "close"],
	"page": 2,
	"per_page": 20
}
'''

safe_params = base64.urlsafe_b64encode(str.encode(params))


def _base64_filters_to_dict(filters: str) -> dict:
    '''
    将Base64的查询参数转换成dict
    '''
    return json.loads(base64.urlsafe_b64decode(filters))


def _query(doc: Document, filters: tuple = None, page: int = 0, per_page: int = 0, order_by: str = None):
    print('\nQuery params:\n')
    print('filters:%s\norder_by:%s\npage:%d per_page:%d' %
          (filters, order_by, page, per_page))
    objects = None
    if filters:
        objects = doc.objects(**filters)
    else:
        objects = doc.objects()
    if order_by is not None:
        objects = objects.order_by(*order_by)
    if per_page > 0 and per_page > 0:
        objects = objects.limit(per_page).skip((page - 1) * per_page)
    return objects


def handle_query(query_params: str = None):
    params_dict = _base64_filters_to_dict(query_params)
    local = {}

    if 'filters' in params_dict:
        filters_str = 'filters = {'
        for f in params_dict['filters']:
            f_list = f.split('=')
            filters_str += '"%s":"%s",' % (f_list[0], f_list[1])
        filters_str = filters_str[:len(filters_str) - 1] + '}'
        print('\nfilters_str=%s\n' % filters_str)
        exec(filters_str, {}, local)
        print('\nfilters = %s\n' % local['filters'])
    if 'order_by' in params_dict:
        order_by_str = 'order_by = ('
        for o in params_dict['order_by']:
            order_by_str += '"%s",' % o
        order_by_str = order_by_str[:len(order_by_str) - 1] + ')'
        print('order_by_str:%s\n' % order_by_str)
        exec(order_by_str, {}, local)
        print('order_by:%s' % type(local['order_by']))
    if 'page' in params_dict:
        exec('page = %d' % params_dict['page'], {}, local)
    if 'per_page' in params_dict:
        exec('per_page = %d' % params_dict['per_page'], {}, local)
    print(_query(IndexDailyItem,
                 filters=local['filters'], order_by=local['order_by'], page=local['page'], per_page=local['per_page']))


class FuncPartialTest(TestCase):
    def setUp(self):
        connect(db='quant_test')

    def test_partial_query(self):
        indices = functools.partial(_query, doc=eval('IndexDailyItem'))(
            order_by='-trade_date', page=2, per_page=20)
        print('\n%s\n' % indices)
        self.assertTrue(len(indices) == 20, msg='Failed to get data from db')

    def test_randomly(self):
        '''
        print(eval('IndexDailyItem'))
        print(IndexDailyItem)
        print(IndexDailyItem.objects.filter(
            ts_code='000001.SH', trade_date='20200422'))
        p = _parse_params(safe_params)
        print(p['filter'])
        '''
        handle_query(safe_params)

    def tearDown(self):
        disconnect()
