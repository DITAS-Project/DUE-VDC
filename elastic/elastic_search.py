from elasticsearch import Elasticsearch
import json
import threading
import time


class ElasticSearch:
    def __init__(self, conf_path='../conf/conf.json'):
        with open(conf_path) as conf_file:
            conf_data = json.load(conf_file)
        self.es = Elasticsearch(hosts=conf_data['connections'])
        self.index = conf_data['index']
        self.update_interval = conf_data['update_interval'] * 0.001

    def _compute_metrics(self):
        res = self._search()
        self.get_response_time(res)
        return

    def update_metrics(self):
        while True:
            self._compute_metrics()
            time.sleep(self.update_interval)

    def launch_sync_update(self):
        threading.Thread(target=self.update_metrics).start()

    def ping(self):
        return self.es.ping()

    def _search(self, query=None):
        if query is None:
            query = {'match_all': {}}
        return self.es.search(index=self.index, body={'query': query})

    def get_response_time(self, res):
        return res['took'] * 0.001

    def get_throughput(self, res):
        res = self._search()


es = ElasticSearch()
es.launch_sync_update()
while True:
    print('ciao')
    time.sleep(1)

'''
print(res['hits']['total'])
for hit in res['hits']['hits']:
    print(hit)
    input()
'''
