import json
from unittest import TestCase

import pandas as pd
from mongoengine import Document, FloatField, StringField, connect, disconnect
from pandas import DataFrame, Series


class ModelA(Document):
    field1 = StringField(required=True)
    field2 = FloatField(required=True)

    def __str__(self):
        return '{field1:%s, field2:%s}' % (self.field1, self.field2)


class DfRxMongoTest(TestCase):
    '''
    DataFrame 与 MongoDB 之间读写测试
    '''

    def setUp(self):
        self.connection = connect(
            'quant_test', host='localhost', port=27017)

    def tearDown(self):
        ModelA.drop_collection()
        disconnect()
        # print('tearDown\n')

    def test_df_2_mongo(self):
        df = DataFrame(
            {'field1': ['test_df_2_mongo_1', 'test_df_2_mongo_2'], 'field2': [1.1, 2.2]})
        # print(df.to_json(orient='records'))
        for model in ModelA.objects.from_json(df.to_json(orient='records')):
            model.save()
        for model in ModelA.objects(field1__icontains='test_df_2_mongo'):
            self.assertTrue(model.field1 in [
                            'test_df_2_mongo_1', 'test_df_2_mongo_2'], 'MongoDB not matching DataFrame field1')
            self.assertTrue(model.field2 in [
                            1.1, 2.2], 'MongoDB not matching DataFrame field2')
        print('\n%s\n' % ModelA.objects(field1__icontains='test_df_2_mongo'))

    def test_mongo_2_df(self):
        ModelA(field1='test_mongo_2_df_1', field2=1.1).save()
        ModelA(field1='test_mongo_2_df_2', field2=2.2).save()
        df = DataFrame.from_dict(json.loads(ModelA.objects.to_json()))
        df = df.drop('_id', axis=1)
        for row in df.itertuples():
            self.assertTrue(row.field1 in [
                            'test_mongo_2_df_1', 'test_mongo_2_df_2'], 'DataFrame not matching MongoDB field1')
            self.assertTrue(
                row.field2 in [1.1, 2.2], 'DataFrame not matching MongoDB field2')
        print('\n%s\n' % df)
