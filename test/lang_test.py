# -*- coding: utf-8 -*-

import os
from unittest import TestCase

from quantz_repo import utils


class LangTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_import_specified_file(self):
        utils.import_specified_file(
            '~/a.py')
        try:
            import a
            a.func_a()
        except:
            self.assertTrue(
                False, '~/a.py maust exist and defines a function called func_a()')
