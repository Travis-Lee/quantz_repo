from unittest import TestCase

from mongoengine import connect, disconnect

from quantz_repo.index_manager import IndexManager


class IndexManagerTest(TestCase):
    def setUp(self):
        connect()

    def tearDown(self):
        disconnect

    def test_initializeIndex(self):
        im = IndexManager()
        im.initializeIndex()
