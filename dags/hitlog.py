import os

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from csv import DictWriter, DictReader
from datetime import datetime

DATA_DIR = os.environ['DATA_DIR']


def _validate_header(header: List[str]):
    expected_header = ['page-name', 'page-url', 'user-id', 'timestamp']
    assert header == expected_header, f'Expected header {expected_header} but found {header}.'


def _is_article_visit(page_url: str):
    if page_url[:10] == '/articles/':
        return True
    return False


def _select_top_3(url_visits: List):
    sorted_url_visits = sorted(url_visits.values(), key=lambda k: k['total'], reverse=True)
    return sorted_url_visits[:3]


def _count_url_visits(reader):
    url_visits = {}

    # Key optimisations here are:
    #   - only iterate the file once here
    #   - reader is a generator object so the entire file is never loaded to memory. The only
    #     memory used is to save an aggregate of all page-url visits (i.e. 1 row per page-url)
    for row in reader:
        if not _is_article_visit(row['page-url']):
            continue

        current_total = url_visits.get(row['page-url'], {'total': 0})['total']

        url_visits[row['page-url']] = {
            'page-name': row['page-name'],
            'page-url': row['page-url'],
            'total': current_total + 1
        }

    return url_visits


def _write_out_file(file_name: str, headers: List[str], content: List[dict]):
    with open(os.path.join(DATA_DIR, file_name), 'w') as out_file:
        writer = DictWriter(out_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(content)


class Tasks:

    @staticmethod
    def process_file():
        with open(os.path.join(DATA_DIR, 'hitlog.csv'), 'r') as in_file:
            reader = DictReader(in_file)
            _validate_header(header=reader.fieldnames)

            url_visits = _count_url_visits(reader)
            top_3_url_visits = _select_top_3(url_visits)

            _write_out_file(
                file_name='out.csv',
                headers=['page-name', 'page-url', 'total'],
                content=top_3_url_visits
            )


default_args = {
    'owner': 'airflow',
    'start_date': datetime.today()
}

dag = DAG('hitlog-dag', schedule_interval='0 * * * *', default_args=default_args)

python_operator = PythonOperator(
    task_id='process-file',
    python_callable=Tasks.process_file,
    dag=dag
)
