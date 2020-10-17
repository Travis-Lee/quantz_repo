from unittest import TestCase

from mongoengine import connect, disconnect
from quantz_repo import industrial_classificataion_manager


class IndustrialClassficationTest(TestCase):
    def setUp(self):
        connect('quant_test')

    def tearDown(self):
        disconnect()

    def test_initialize_industrial_classification(self):
        industrial_classificataion_manager.initialize_industrial_classification()

    def test_get_industrial_classification_for(self):
        print(industrial_classificataion_manager.get_industrial_classification_for(
            ts_code='300496.SZ'))

    def test_get_industrial_classifications(self):
        print(industrial_classificataion_manager.get_industrial_classifications())

    def test_get_industrial_classfication_members(self):
        print(industrial_classificataion_manager.get_industrial_classfication_members(
            '801710.SI'))
