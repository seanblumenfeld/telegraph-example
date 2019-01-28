FROM puckel/docker-airflow:1.10.1

# This allows docker to cache requirements, and so only changes to
# requirements.txt will trigger a new pip install
ADD requirements-dags.txt /requirements-dags.txt
ADD requirements-test.txt /requirements.txt

RUN pip install --user -r /requirements.txt

ENV PATH="${PATH}:/usr/local/airflow/.local/bin"
