# -*- coding: utf-8 -*-
'''
Python 语言工具
'''

import os
import sys

from . import log


def import_specified_file(path: str):
    '''
    import 指定 Python 文件
    :param: path，import 的文件路径
    '''

    if path is not None and path.startswith('~'):
        path = os.path.expanduser(path)
    if os.path.exists(path):
        if os.path.isfile(path):
            module_dir = os.path.dirname(os.path.abspath(path))
            module_name = os.path.basename(path)
            sys.path.extend([module_dir])
            log.d('Lang', 'dir=%s name=%s' % (module_dir, module_name))
        elif os.path.isdir(path):
            sys.path.extend([path])
        else:
            log.w('Lang', 'Failed to import %s' % (path))
    else:
        log.w('Lang', 'Failed to import %s(path not found)' % (path))


def rimport(rel_path: str):
    pass
