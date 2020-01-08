from elasticsearch import Elasticsearch
import json
import uuid
from abc import ABC, abstractmethod


class Metric(ABC):
    def __init__(self, conf_path):
        with open(conf_path) as conf_file:
            conf_data = json.load(conf_file)
        self.es = Elasticsearch(hosts=conf_data['connections'])
        self.index = conf_data['index_qos']
        self.conf_data = conf_data

    def format_time_window(self, t0, t1):
        start_time = t0.isoformat()
        end_time = t1.isoformat()
        return end_time, f'[{start_time} TO {end_time}]'

    @abstractmethod
    def compute_metric(self, query_content, update_interval):
        pass

    @abstractmethod
    def launch_sync_update(self):
        pass

    def _search(self, query=None, size=10):
        if query is None:
            query = '*'
        return self.es.search(index=self.index, q=query, size=size)

    def __format_key(self, bp_id, vdc_inst, request_id, operation_id):
        return bp_id + '-' + vdc_inst + '-' + request_id + '-' + operation_id

    def write(self, bp_id, vdc_inst, request_id, operation_id, value, name, unit, hit_timestamp, computation_timestamp):
        body = {
            'meter': {
                'key': self.__format_key(bp_id, vdc_inst, request_id, operation_id),
                'operationId': operation_id,
                'value': value,
                'name': name,
                'unit': unit,
                'timestamp': hit_timestamp,
                'computation-timestamp': computation_timestamp
            }
        }
        index = self.index.split('*')[0] + computation_timestamp.split('T')[0]
        self.es.create(index=index, id=str(uuid.uuid4()), body=body)
