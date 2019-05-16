from elasticsearch import Elasticsearch
import json
from abc import abstractmethod


class Metrics:
    def __init__(self, conf_path):
        with open(conf_path) as conf_file:
            conf_data = json.load(conf_file)
        self.es = Elasticsearch(hosts=conf_data['connections'])
        self.index = conf_data['index']
        self.conf_data = conf_data

    @abstractmethod
    def compute_metric(self):
        pass

    @abstractmethod
    def launch_sync_update(self):
        pass

    def _search(self, query=None, size=10):
        if query is None:
            query = '*'
        return self.es.search(index=self.index, q=query, size=size)
