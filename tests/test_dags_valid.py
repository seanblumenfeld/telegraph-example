from unittest import TestCase
from airflow.models import DagBag


class TestDagsValid(TestCase):

    def setUp(self):
        self.dagbag = DagBag()

    def test_import_dags(self):
        self.assertEqual(len(self.dagbag.import_errors), 0)
