import datetime

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.base import BaseTrigger
from pytz import utc

from quantz_repo import (get_us_ccsa, get_us_initial_jobless, get_us_wei,
                         initialize_daily_trading_info, initialize_db,
                         initialize_industrial_classification,
                         rank_all_industry, update_daily_trading_info,
                         update_industry_classification, update_stock_basics,
                         update_us_ccsa, update_us_initial_jobless,
                         update_us_wei)


def may_market_be_ready():
    '''
    判断当前市场交易数据是否可获取，若可能用，返回 True，否则返回 False
    '''
    return datetime.datetime.now().hour >= 17


class DailyTrigger(BaseTrigger):
    '''
    每天触发
    '''

    def __init__(self, hour, minute, seconds, name):
        """每天的什么时间触发

        :param hour: [description]
        :type hour: [type]
        :param minute: [description]
        :type minute: [type]
        :param seconds: [description]
        :type seconds: [type]
        :param name: [description]
        :type name: [type]
        """
        self.hour = hour
        self.minute = minute
        self.seconds = seconds
        self.name = name

    def get_next_fire_time(self, previous_fire_time, now):
        csttz = datetime.timezone(datetime.timedelta(hours=8))
        now = datetime.datetime.now(csttz)
        scheduled_time = datetime.datetime(
            now.year, now.month, now.day, self.hour, self.minute, self.seconds, tzinfo=csttz)
        if scheduled_time < now:
            scheduled_time = scheduled_time + datetime.timedelta(days=1)
        print('%s scheduled at %s' % (self.name, scheduled_time))
        return scheduled_time


class WeeklyTrigger(BaseTrigger):
    '''
    按照周周期触发的trigger
    '''

    def __init__(self, day=0, hour=0, minute=0, name='default'):
        """[summary]

        :param day: 一周的哪一天触发，0=周一，6=周日, defaults to 0
        :type day: int, optional
        :param hour: 几点触发, defaults to 0
        :type hour: int, optional
        :param minute: 几分触发, defaults to 0
        :type minute: int, optional
        """
        self.day = day
        self.hour = hour
        self.minute = minute
        self.name = name

    def _get_next_weekday_of(self, day) -> datetime.date:
        '''
        获取下个周N
        day:0-6, 周一为 0，递增
        '''
        today = datetime.date.today()
        next = today + datetime.timedelta((day-today.weekday()) % 7)
        return next

    def get_next_fire_time(self, previous_fire_time, now):
        '''
        如果当前就是
        '''
        csttz = datetime.timezone(datetime.timedelta(hours=8))
        next = self._get_next_weekday_of(self.day)
        scheduled_time = datetime.datetime(
            next.year, next.month, next.day, self.hour, self.minute, tzinfo=csttz)
        if scheduled_time <= datetime.datetime.now(csttz):
            scheduled_time = datetime.datetime.now(
                csttz) + datetime.timedelta(minutes=2)
        print('%s scheduled at %s' % (self.name, scheduled_time))
        return scheduled_time


def quantzrepod():
    """
    quantz repo 的守护进程，根据数据的更新时间定期更新数据
    """
    initialize_db('quantz')
    jobstores = {'default': MongoDBJobStore()}
    executors = {
        'default': ThreadPoolExecutor(8)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 8
    }
    scheduler = BlockingScheduler(  # jobstores=jobstores,
        executors=executors, job_defaults=job_defaults, timezone='Asia/Shanghai')
    scheduler.add_job(
        update_us_wei, trigger=WeeklyTrigger(3, 19, 0, 'WeiTrigger'))
    scheduler.add_job(
        update_us_initial_jobless, trigger=WeeklyTrigger(4, 19, 0, 'IcsaTrigger'))
    scheduler.add_job(
        update_us_ccsa, trigger=WeeklyTrigger(4, 19, 0, 'CcsaTrigger'))
    scheduler.add_job(update_stock_basics, trigger=DailyTrigger(
        17, 0, 0, 'update_stock_basics'))
    scheduler.add_job(update_industry_classification, trigger=DailyTrigger(
        17, 30, 0, 'update_industry_classification'))
    scheduler.add_job(update_daily_trading_info, trigger=DailyTrigger(
        18, 00, 0, 'update_daily_trading_info'))
    scheduler.add_job(rank_all_industry, trigger=DailyTrigger(
        19, 00, 0, 'rank_all_industry'))
    scheduler.start()


def quantzrepoi():
    """初始化数据，获取所有历史数据
    """
    initialize_db('quantz')
    get_us_wei()
    get_us_initial_jobless()
    get_us_ccsa()
    # 会删除现有数据后更新到最新，等同于初始化stock basics
    # TODO: 增加初始化函数，统一函数命名，initialize作为初始化，get是从本地数据库获取，update 是更新本地数据到最新
    update_stock_basics()
    initialize_industrial_classification()
    initialize_daily_trading_info()
    rank_all_industry()


def quantzrepou():
    """更新所有数据到最新
    """
    if not may_market_be_ready():
        print('☠☠☠ Market data may not be ready, try again later ☠☠☠')
        return
    initialize_db('quantz')
    update_us_wei()
    update_us_initial_jobless()
    update_us_ccsa()
    update_stock_basics()
    update_industry_classification()
    update_daily_trading_info()
    rank_all_industry()


if __name__ == "__main__":
    quantzrepod()


# FIXME: 增加命令行参数，传入quantz_config.json的路径，现在默认使用当前目录下quanz_config.json
