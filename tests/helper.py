import os
from csv import DictReader, writer
from typing import List


class Helper:
    data_dir = os.environ['DATA_DIR']

    def write_data_file_content(self, file_name: str, content: List[str]):
        with open(os.path.join(self.data_dir, file_name), 'w') as f:
            f.write('\n'.join(content))

    def read_data_file_content(self, file_name: str):
        with open(os.path.join(self.data_dir, file_name), 'r') as f:
            reader = DictReader(f)
            content = [r for r in reader]
        return content

    def assertDataFileExists(self, file_name: str):
        return self.assertIn(file_name, os.listdir(self.data_dir))

    def assertDataFileHeaders(self, file_name: str, headers: List[str]):
        with open(os.path.join(self.data_dir, file_name), 'r') as f:
            reader = DictReader(f)
            self.assertListEqual(reader.fieldnames, headers)
