from unittest import TestCase

from quantz_repo.trade_calendar_manager import TradeCalendarManager


class TradeCalendarManagerTest(TestCase):
    def test_getNextTradeOf(self):
        self.assertTrue(TradeCalendarManager.next_trade_date_of(
            exchange='SSE', date='20200228') == '20200302', 'Incorrect next trade date of %s' % ('20200228'))
        self.assertFalse(TradeCalendarManager.next_trade_date_of(
            exchange='SSE', date='20201231') == '20200302', 'Incorrect next trade date of %s' % ('20201231'))
        self.assertFalse(TradeCalendarManager.next_trade_date_of(
            exchange='SSE', date='20211231') == '20200302', 'Incorrect next trade date of %s' % ('20211231'))
