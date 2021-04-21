import requests

from . import initialize_quantz_config


class Fred:
    '''
    从 Fred 获取美联储、财政部、经济等各种数据，使用参考 fred 官网 https://fred.stlouisfed.org/docs/api/fred/
    直接返回获取的 json 或者 抛出异常提示错误
    '''

    def __init__(self):
        '''
        get Fred 数据
        TODO: 通过配置或环境变量获取 Api Key
        '''
        cfg = initialize_quantz_config()
        self.api_key = cfg.fred_api_key
        # get_fred_api_key_from_cfg()
        if self.api_key is None:
            raise Exception('Fred Api Key can not be empty')
        self.path = 'https://api.stlouisfed.org/fred'

    def __get(self, args):
        print('__get:%s' % self.path)
        print(args)
        resp = None
        if len(args) == 0:
            resp = requests.get(self.path, params={
                                'api_key': self.api_key, 'file_type': 'json'})
        elif len(args) == 1:
            params = {'api_key': self.api_key, 'file_type': 'json'}
            params.update(args[0])
            print(params)
            resp = requests.get(self.path, params=params)
        else:
            print('Invalid args%s' % args)
        # TODO: 增加网络错误的处理
        # print(resp.json())
        print('Observations got from %s' % resp.url)
        return resp.json()

    def __getattr__(self, name):
        '''
        __getattr__ 在需要的属性没有找到的情况下会调用
        __getattribute__ 在读取任何属性的时候都会调用
        '''
        self.path = '%s/%s' % (self.path, name)
        return self

    def __str__(self):
        return self.path

    def __call__(self, *args):
        return self.__get(args)


'''
print(Fred().series.observations({'series_id':'wei', 'limit':'100', 'sort_order':'desc'}))
'''
