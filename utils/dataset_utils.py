from google.cloud import bigquery
from typing import Tuple
import logging
import json
from utils.bq_utils import BqUtils


class DatasetUtils(BqUtils):
    def __init__(self, event, file_path):
        super().__init__()

        self.event = event
        self.file_path = file_path

    @staticmethod
    def open_file(file_path: str) -> Tuple[str, dict]:
        with open(file_path) as f:
            dataset_json = json.load(f)
            dataset_id = dataset_json['projectId'] + '.' + dataset_json['datasetId']

        return dataset_id, dataset_json

    def create_dataset(self, dataset_id: str, dataset_json: dict):
        dataset = bigquery.Dataset(dataset_id)

        dataset.location = dataset_json['location']

        dataset = self.client.create_dataset(dataset, timeout=30)
        logging.info("Created dataset {} successfully.".format(dataset_id))

        if dataset_json.get("properties"):
            self.update_dataset(dataset_id, dataset_json)

    def delete_dateset(self, dataset_id: str):
        self.client.delete_dataset(
            dataset_id, delete_contents=True, not_found_ok=True)

        logging.info("Deleted dataset {} successfully.".format(dataset_id))

    def update_dataset(self, dataset_id: str, dataset_json: dict):
        for k, v in dataset_json['properties'].items():
            dataset = self.client.get_dataset(dataset_id)
            if getattr(dataset, k) != v:
                setattr(dataset, k, v)
                self.client.update_dataset(dataset, [f"{k}"])
                logging.info("Dataset : {} {} updated with {}".format(dataset_id, k, v))

    def apply(self):
        dataset_id, dataset_json = DatasetUtils.open_file(self.file_path)

        if self.event == 'deletion':
            self.delete_dateset(dataset_id)
        elif self.event == 'creation':
            self.create_dataset(dataset_id, dataset_json)
        elif self.event == 'update':
            self.update_dataset(dataset_id, dataset_json)
