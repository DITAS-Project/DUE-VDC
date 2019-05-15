from elasticsearch import Elasticsearch
import json
import threading
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

    '''def _search(self, query=None):
        if query is None:
            query = {'match_all': {}}
        return self.es.search(index=self.index, body={'query': query})

    def get_response_time(self, res):
        return res['took'] * 0.001

    def get_throughput(self, res):
        res = self._search()'''
