import os
import json


class Read:

    def __init__(self, filename):
        self.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'configs', 'dev', filename))

    def get_json_file(self):
        with open(self.file_path, mode='r', encoding='utf-8') as f:
            value = json.load(f)
        return value
