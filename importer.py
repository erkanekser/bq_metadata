from google.cloud import bigquery
from typing import NoReturn
import argparse
import logging
import json
import os
import io


class Importer:
    def __init__(self, project):
        self.client = bigquery.Client()
        self.project = project

    def remove_key(self, container, key):
        if type(container) is dict:
            if key in container:
                del container[key]
            for v in container.values():
                self.remove_key(v, key)
        if type(container) is list:
            for v in container:
                self.remove_key(v, key)

    def write_table_json(self, table: bigquery.Table) -> None:
        """Creates a json file contains the given BigQuery table configurations"""

        f = io.StringIO("")

        self.client.schema_to_json(table.schema, f)

        content = {
            "projectId": "{}".format(table.project),
            "datasetId": "{}".format(table.dataset_id),
            "tableId": "{}".format(table.table_id),
            "schema": {
                "fields": json.loads(f.getvalue())
            }
        }
        self.remove_key(content['schema'], 'policyTags')

        if getattr(table, "labels"):
            content["labels"] = getattr(table, "labels")

        if getattr(table, "time_partitioning"):
            content["timePartitioning"] = {}
            content["timePartitioning"]["field"] = table.time_partitioning.field
            content["timePartitioning"]["type"] = table.time_partitioning.type_

            if getattr(getattr(table, "time_partitioning"), "expiration_ms"):
                expiration_day = table.time_partitioning.expiration_ms / 1000 / 60 / 60 / 24  # ms to day
                content["timePartitioning"]["expirationDays"] = int(expiration_day)

        with open(f'./bq_metadata/{self.project}/{table.dataset_id}/tables/{table.table_id}.json', 'w',
                  encoding='utf-8') as f:
            f.write(json.dumps(content, indent=4))

    def write_view_sql(self, dataset: str, table: bigquery.Table) -> None:
        """Creates a json file contains the given BigQuery table configurations"""

        content = f"create or replace view `{self.project}.{dataset}.{table.table_id}` \nas\n"
        content += table.view_query
        with open(f'./bq_metadata/{self.project}/{dataset}/views/{table.table_id}.sql', 'w', encoding='utf-8') as f:
            f.write(content)

    def write_dataset_json(self, dataset: bigquery.Dataset = None) -> None:
        """Creates a json file contains dataset information"""

        content = {
            "location": "{}".format(dataset.location),
            "projectId": "{}".format(dataset.project),
            "datasetId": "{}".format(dataset.dataset_id),
            "properties": {
            }
        }

        properties = ["description", "default_table_expiration_ms", "default_partition_expiration_ms", "labels"]
        for property in properties:
            if getattr(dataset, property):
                content["properties"][property] = getattr(dataset, property)

        with open(f'./bq_metadata/{self.project}/{dataset.dataset_id}/{dataset.dataset_id}.json', 'w',
                  encoding='utf-8') as f:
            f.write(json.dumps(content, indent=4))

    def run(self) -> NoReturn:
        logging.info("Importing has been started...")

        # Create Project folder if not exist
        if not os.path.exists(f'./bq_metadata/{self.project}'):
            os.mkdir(f'./bq_metadata/{self.project}')

        # Get Datasets and tables
        self.client.project = self.project
        datasets = list(self.client.list_datasets())
        logging.info(f"There are {len(datasets)} datasets in the project {self.project}")

        if datasets:
            logging.info("Datasets in project {}:".format(self.project))
            for dataset in datasets:
                # Check schema folders if not exists create
                is_dataset_folder_exists = os.path.exists(f'./bq_metadata/{self.project}/{dataset.dataset_id}')
                if not is_dataset_folder_exists:
                    os.mkdir(f'./bq_metadata/{self.project}/{dataset.dataset_id}')
                    #os.mkdir(f'./bq_metadata/{self.project}/{dataset.dataset_id}/views')
                    #os.mkdir(f'./bq_metadata/{self.project}/{dataset.dataset_id}/tables')

                # Create json file
                self.write_dataset_json(dataset=self.client.get_dataset(dataset.dataset_id))

                logging.info("{}".format(dataset.dataset_id))
"""
                # Get tables, and views in the given dataset
                tables = self.client.list_tables(dataset)
                for table in tables:
                    logging.info("\t{}".format(table.table_id))

                    if table.table_type == "VIEW":
                        self.write_view_sql(dataset.dataset_id, self.client.get_table(table))
                    if table.table_type == "TABLE":
                        self.write_table_json(table=self.client.get_table(table))
"""
        #else:
         #   logging.info("{} project does not contain any datasets.".format(self.project))


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Get Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', default=None, help='Project Name (default = None)')
    args = parser.parse_args()
    logging.info(f"Parameters: {args}")

    # Path configurations
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    importer = Importer(project=args.project)
    importer.run()
