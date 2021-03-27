import json

_quantz_config = None


class QuantzCfg:
    def __init__(self, cfg: str = 'quantz_cfg.json'):
        with open(cfg, 'r') as f:
            self.__config = json.load(f)
            self.__cfg_path = cfg

    def __getattr__(self, name):
        print('get %s' % name)
        if name in self.__config:
            return self.__config[name]
        else:
            raise Exception('%s not in %s' % (name, self.__cfg_path))


def initialize_quantz_config(cfg_path: str = 'quantz_cfg.json', force: bool = False):
    '''
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
