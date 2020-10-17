# -*- coding: utf-8 -*-

from .date_time import now_for_log_str


def e(tag: str, msg: str):
    print('E:%s:%s:%s\n' % (now_for_log_str(), tag, msg))


def i(tag: str, msg: str):
    print('I:%s:%s:%s\n' % (now_for_log_str(), tag, msg))


def w(tag: str, msg: str):
    print('W:%s:%s:%s\n' % (now_for_log_str(), tag, msg))


def d(tag: str, msg: str):
    print('D:%s:%s:%s\n' % (now_for_log_str(), tag, msg))
