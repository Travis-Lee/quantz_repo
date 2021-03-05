import json


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


def initialize_quantz_config(cfg_path: str = 'quantz_cfg.json'):
    return QuantzCfg(cfg_path)
