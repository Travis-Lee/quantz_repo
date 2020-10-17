from unittest import TestCase
from quantz_repo import us_eco
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
