from unittest import TestCase
from quantz_repo import us_eco
from quantz_repo.model.us_eco_models import UsWeiItem
import mongoengine


class UsaEcoTest(TestCase):
    def setUp(self):
        self.connection = mongoengine.connect(
            'quant_test', host='localhost', port=27017)

    def tearDown(self):
        mongoengine.disconnect()

    def test_usa_initial_jobless_claim(self):
        us_eco.update_us_initial_jobless()
        print(us_eco.get_us_initial_jobless(limit=20))

    def test_get_us_wei(self):
        print(us_eco.get_us_wei().head(10))

    def test_get_us_wei_from_gd(self):
        df = us_eco._get_us_wei_from_gd()
        UsWeiItem.objects.insert(
            UsWeiItem.objects.from_json(df.to_json(orient='records')))
        print(df.head(5))
