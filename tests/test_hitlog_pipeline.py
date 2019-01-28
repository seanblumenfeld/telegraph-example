from unittest import TestCase
from airflow.models import DagBag

from dags.hitlog import Tasks
from tests.helper import Helper


class TestHitlogDag(TestCase):

    def setUp(self):
        self.dagbag = DagBag()
        self.dag = self.dagbag.get_dag('hitlog-dag')

    def test_task_count(self):
        self.assertEqual(len(self.dag.tasks), 1)

    def test_tasks(self):
        self.assertListEqual(
            [task.task_id for task in self.dag.tasks],
            ['process-file']
        )


class TestHitlogTasks(TestCase, Helper):

    def setUp(self):
        hitlog_content = [
            "page-name,page-url,user-id,timestamp",
            "Article 1,/articles/1,1001,1515356005",
            "Article 1,/articles/1,1002,1515356006",
            "Registration,/register,1002,1515356027",
            "Article 2,/articles/2,1006,1515356031",
            "Article 3,/articles/3,1001,1515355925",
            "Contact us,/contact-us,1001,1515355927",
            "Registration,/register,1003,1515355990",
            "Article 4,/articles/4,1004,1515355991",
            "Article 1,/articles/1,1005,1515355992",
            "Article 1,/articles/1,1006,1515355993",
            "Article 2,/articles/2,1006,1515355994",
            "Article 4,/articles/4,1006,1515355995",
            "Article 4,/articles/4,1007,1515355996"
        ]

        self.write_data_file_content(file_name='hitlog.csv', content=hitlog_content)

        # Given a source file exists
        self.assertDataFileExists('hitlog.csv')

    def test_process_file_produces_file(self):
        # When the file is processed
        Tasks.process_file()
        # Then an output file is created
        self.assertDataFileExists('out.csv')

    def test_process_file_throws_if_source_file_headers_invalid(self):
        # Given a bad source file exists
        bad_hitlog_content = [
            "page-name,page-url,user-id",
            "Registration,/register,1003"
        ]
        self.write_data_file_content(file_name='hitlog.csv', content=bad_hitlog_content)
        # When the file is processed
        # Then an exception is thrown
        self.assertRaises(AssertionError, Tasks.process_file)

    def test_process_file_headers(self):
        # When the file is processed
        Tasks.process_file()
        # Then the output file contains the headers: page-name, page-url, user-id, timestamp
        self.assertDataFileHeaders(
            file_name='out.csv',
            headers=['page-name', 'page-url', 'total']
        )

    def test_out_file_3_unique_url_rows(self):
        # When the file is processed
        Tasks.process_file()

        # Then the output file contains three rows - one per top 3 visited urls
        content = self.read_data_file_content(file_name='out.csv')
        unique_urls = {row['page-url'] for row in content}
        self.assertEqual(len(unique_urls), 3)

    def test_out_file_total_visits_of_top_3(self):
        # When the file is processed
        Tasks.process_file()

        # Then the sum of the total visits in the whole output file
        # should match the total number of visits for the top 3 articles
        content = self.read_data_file_content(file_name='out.csv')
        total_visits = 0
        for row in content:
            total_visits += int(row['total'])

        self.assertEqual(total_visits, 9)

    def test_out_file_only_contains_top_3_articles(self):
        # When the file is processed
        Tasks.process_file()

        # Then the output file should contain top 3 influential topics and their total numbers
        content = self.read_data_file_content(file_name='out.csv')
        self.assertEqual(len(content), 3)

        # Note: file should be sorted in top 3 order so we can assert like this
        self.assertEqual(content[0]['page-name'], 'Article 1')
        self.assertEqual(content[0]['total'], '4')

        self.assertEqual(content[1]['page-name'], 'Article 4')
        self.assertEqual(content[1]['total'], '3')

        self.assertEqual(content[2]['page-name'], 'Article 2')
        self.assertEqual(content[2]['total'], '2')
