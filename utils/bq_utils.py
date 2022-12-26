from google.cloud import bigquery
from typing import Any
import subprocess
import logging
import abc


class BqUtils(metaclass=abc.ABCMeta):
    def __init__(self):
        self.client = bigquery.Client()

    def run_query(self, file_path: str):

        with open(file_path) as f:
            query = '\n'.join(f.read().splitlines())

        job_config = bigquery.QueryJobConfig(dry_run=False, use_query_cache=False)

        query_job = self.client.query(
            query,
            job_config=job_config
        ) 

        query_job.result() 
        logging.info('Query has finished: {}'.format(query))

    @staticmethod
    def delete_table(table_id: str):
        
        bq_command = f"bq rm -f -t {table_id}"

        try:
            subprocess.run(bq_command, shell=True, check=True)
            logging.info(f"Deleted operation successfully: {table_id}")
        except subprocess.CalledProcessError as e:
            logging.info(e)
"""
    @abc.abstractmethod
    def apply(self, *args, **kwargs) -> Any:
        ...

    @abc.abstractmethod
    def open_file(self, *args, **kwargs) -> Any:
        ...
"""
