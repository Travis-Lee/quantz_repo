from unittest import TestCase
import investpy


class InvestpyTest(TestCase):
    def test_historical_data(self):
        df = investpy.get_stock_historical_data(stock='AAPL',
                                                country='United States',
                                                from_date='01/01/2019',
                                                to_date='10/01/2020')
        print(df.head())
