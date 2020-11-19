from mongoengine import Document, LongField, StringField


class BasicStockInfoItem(Document):
    ts_code = StringField()
    # 股票代码
    symbol = StringField()
    # 股票名字
    name = StringField()
    # 地区
    area = StringField()
    # 行业
    industry = StringField()
    # 全称
    fullname = StringField()
    # 英文名
    enname = StringField()
    # 市场类型 （主板/中小板/创业板/科创板）
    market = StringField()
    # 交易所代码SZSE SSE
    exchange = StringField()
    # 交易货币
    curr_type = StringField()
    # 上市状态  L上市 D退市 P暂停上市
    list_status = StringField()
    # 上市日期
    list_date = LongField()
    # 退市日期，默认 sys.maxsize
    delist_date = LongField()
    # 是否沪港通标的
    is_hs = StringField()
