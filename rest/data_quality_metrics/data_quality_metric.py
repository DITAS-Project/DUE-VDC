from elasticsearch import Elasticsearch
import json
import uuid
from abc import ABC, abstractmethod


class DataQualityMetric(ABC):
    def __init__(self, conf_path):
        with open(conf_path) as conf_file:
            conf_data = json.load(conf_file)
        self.es = Elasticsearch(hosts=conf_data['connections'])
        self.index = conf_data['index_data_quality']
        self.conf_data = conf_data

    @abstractmethod
    def compute_metric(self, body_request, blueprint):
        pass

    def __format_key(self, bp_id, vdc_inst, request_id, operation_id):
        return bp_id + '-' + vdc_inst + '-' + request_id + '-' + operation_id

    def write(self, bp_id, vdc_inst, request_id, operation_id, value, name, unit, hit_timestamp, computation_timestamp):
        body = {
            'meter': {
                'key': self.__format_key(bp_id, vdc_inst, request_id, operation_id),
                'value': value,
                'name': name,
                'unit': unit,
                'hit-timestamp': hit_timestamp,
                'computation-timestamp': computation_timestamp
            }
        }
        index = self.index.split('*')[0] + computation_timestamp.split('T')[0]
        self.es.create(index=index, id=str(uuid.uuid4()), body=body)
