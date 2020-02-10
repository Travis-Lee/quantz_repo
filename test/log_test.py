# -*- coding: utf-8 -*-

from unittest import TestCase
from quantz_repo.utils import log


class LogTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_log_w(self):
        log.w('Log', 'This is log unittest')
