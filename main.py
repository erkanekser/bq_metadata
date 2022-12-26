from utils.dataset_utils import DatasetUtils
from utils.table_utils import TableUtils
from utils.view_utils import ViewUtils
import argparse
import logging

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', default=None, help='Config Type(default=None)')
    parser.add_argument('-e', '--event', default=None, help='Event Type(default = None)')
    parser.add_argument('-f', '--file', default=None, help='File Path(default = None)')
    args = parser.parse_args()

    if args.type == 'dataset':
        utils = DatasetUtils(event=args.event, file_path=args.file)
    elif args.type == 'table':
        utils = TableUtils(event=args.event, file_path=args.file)
    elif args.type == 'view':
        utils = ViewUtils(event=args.event, file_path=args.file)
    else:
        raise Exception('Invalid config type!')

    utils.apply()
