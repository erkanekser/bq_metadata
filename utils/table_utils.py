from utils.bq_utils import BqUtils
from typing import Tuple
import subprocess
import logging
import json


class TableUtils(BqUtils):
    def __init__(self, event, file_path):
        super().__init__()

        self.event = event
        self.file_path = file_path
    
    @staticmethod
    def open_file(file_path: str) -> Tuple[str, dict]:
        with open(file_path) as f:
            table_json = json.load(f)
            table_id = table_json['projectId'] + ':' + table_json['datasetId'] + '.' + table_json['tableId']

        return table_id, table_json

    @staticmethod
    def create_table(table_id: str, table_json: dict):
        bq_command = "bq mk --table"
        schema_path = "table_schema_temp.json"
        
        with open(schema_path, "w") as f:
            f.write(json.dumps(table_json['schema']['fields'], indent=4))

        if table_json.get("timePartitioning"):
            bq_command += " --time_partitioning_field " + table_json["timePartitioning"]["field"]
            bq_command += " --time_partitioning_type " + table_json["timePartitioning"]["type"]

            if table_json.get("timePartitioning").get("expirationDays"):
                bq_command += " --time_partitioning_expiration " + str(int(table_json["timePartitioning"]["expirationDays"])*24*60*60) #seconds

        if table_json.get("labels"):
            for k, v in table_json['labels'].items():
                bq_command += f" --label {k}:{v}" 

        if table_json.get("description"):
            bq_command += " --description " + table_json["description"]                

        bq_command += f" {table_id} {schema_path}"

        try:
            subprocess.run(bq_command, shell=True, check=True)
            logging.info(f"Created table successfully: {table_id}")
        except subprocess.CalledProcessError as e:
            logging.info(e)

    def apply(self) -> None:
        table_id, table_json = TableUtils.open_file(self.file_path)
        
        if self.event == "creation":
            self.create_table(table_id, table_json)
            
        elif self.event == "deletion":
            bq_utils = BqUtils()
            bq_utils.delete_table(table_id)
