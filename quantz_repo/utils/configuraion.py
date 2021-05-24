import json
import os
import sys
from pathlib import Path


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# Since Python3.3, 禁用了相对路径import

_quantz_config = None


class QuantzCfg:
    def __init__(self, cfg: str = '%s/.quantz/quantz_cfg.json' % Path.home()):
        try:
            with open(cfg, 'r') as f:
                self.__config = json.load(f)
                self.__cfg_path = cfg
        except Exception as e:
            from quantz_exception import QuantzException
            raise QuantzException(
                'Failed to read quantz config from %s cause %s' % (cfg, e))

    def __getattr__(self, name):
        print('get %s' % name)
        if name in self.__config:
            return self.__config[name]
        else:
            raise Exception('%s not in %s' % (name, self.__cfg_path))


def initialize_quantz_config(cfg_path: str = '%s/.quantz/quantz_cfg.json' % Path.home(), force: bool = False):
    '''
    默认配置文件:~/.quantz/quantz_cfg.json .
    初始化配置，其中是简单的 json 即可
    {
        "aaa":"BBB",
        "xxx"：“YYY”
    }
    通过 config.aaa 即可访问
    '''
    if _quantz_config is None or force == True:
        _config = QuantzCfg(cfg_path)
    return _config
