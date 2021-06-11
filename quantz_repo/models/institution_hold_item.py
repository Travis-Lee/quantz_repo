from mongoengine import Document, IntField, StringField, LongField, FloatField, connect


class InstitutionHoldItem(Document):
    '''
    机构持仓数据，参考 https://www.akshare.xyz/zh_CN/latest/data/stock/stock.html?highlight=stock_report_fund_hold#id135
    '''
    # ts_code
    ts_code = StringField(required=True)
    # 股票名字
    ticker = StringField(required=True)
    # 持有基金家数
    holder_sum = IntField(required=True)
    # 持股总数
    hold_total_vol = LongField(required=True)
    # 持股市值
    hold_total_amount = FloatField(required=True)
    # 持股变化(持平、增持、减持)
    hold_diff = StringField(required=True)
    # 持股变动数量
    hold_diff_vol = LongField(required=True)
    # 持股变动比例
    hold_diff_pct = FloatField(required=True)
    # ann_date,发布时间，每个季度最后一天,毫秒，ms
    ann_date = LongField(required=True)
    # by "基金持仓", "QFII持仓", "社保持仓", "券商持仓", "保险持仓", "信托持仓"
    by = StringField(required=True)
    meta = {
        'indexes': [
            {
                'name': 'unique_index',
                'fields': ['ts_code', 'ann_date', 'by'],
                'unique': True,
                'dropDups':True
            }
        ],
        'index_background': True,
        'auto_create_index': True
    }
