# -*- coding: utf-8 -*-

from unittest import TestCase
from quantz_repo import utils

import re


class UtilsTest(TestCase):
    def test_now_for_log_str(self):
        print(utils.now_for_log_str())
        self.assertNotEqual(
            re.match(r'^\d{8}-\d{2}:\d{2}:\d{2}\.\d{3}$', utils.now_for_log_str()), None)
