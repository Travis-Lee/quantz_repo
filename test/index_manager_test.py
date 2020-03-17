from unittest import TestCase

from mongoengine import connect, disconnect

from quantz_repo import QuantzException
from quantz_repo.index_manager import IndexManager


class IndexManagerTest(TestCase):
    def setUp(self):
        connect('quant_test')

    def tearDown(self):
        disconnect()

    def test_initialize_index(self):
        im = IndexManager()
        im.initialize_index()

    def test_get_index_daily(self):
        im = IndexManager()
        date_checked = False
        try:
            im.get_index_daily(
                code='000001.SH', start_date='20200101', end_date='19990101')
        except QuantzException as e:
            print(e)
            date_checked = True
        finally:
            self.assertTrue(date_checked, 'Failed to check trade date')
        recent_sh_index = im.get_index_daily(
            '000001.SH', start_date='20200203', end_date='20200205')
        print('%s\n' % recent_sh_index['trade_date'])
        recent_sh_index = im.get_index_daily(
            '000001.SH', start_date='20200203')
        print('%s\n' % recent_sh_index['trade_date'])
        recent_sh_index = im.get_index_daily(
            '000001.SH', end_date='19901225')
        print('%s\n' % recent_sh_index['trade_date'])
        recent_sh_index = im.get_index_daily('000001.SH')
        print('%s\n' % recent_sh_index['trade_date'])

    def test_update_index_daily(self):
        im = IndexManager()
        im.update_index_daily()
