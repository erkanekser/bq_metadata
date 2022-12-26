from utils.bq_utils import BqUtils


class ViewUtils(BqUtils):
    def __init__(self, event, file_path):
        super().__init__()

        self.event = event
        self.file_path = file_path

    def apply(self):

        utils = BqUtils()

        if self.event == "creation" or self.event == "update":
            utils.run_query(self.file_path)

        elif self.event == "deletion":
            table_id = self.file_path
            utils.delete_table(table_id)
