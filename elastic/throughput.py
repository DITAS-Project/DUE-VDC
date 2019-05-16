import time
import threading
from metrics import Metrics


class Throughput(Metrics):
    def __init__(self, conf_path='../conf/conf.json'):
        super().__init__(conf_path)

    def compute_metric(self, query_content, update_interval):
        query_ids = query_content + ' AND request.id:*'
        while True:
            res = self._search(query=query_ids)
            total_hits = res['hits']['total']
            res = self._search(query=query_ids, size=total_hits)
            infos = {}
            for hit in res['hits']['hits']:
                id = hit['_source']['request.id']
                infos[id] = {'response_length': 0, 'request_time': 0}
            for hit in res['hits']['hits']:
                source = hit['_source']
                if 'response.length' in source and 'request.requestTime' in source:
                    id = source['request.id']
                    response_length = source['response.length']
                    request_time = source['request.requestTime']
                    infos[id]['response_length'] += response_length
                    infos[id]['request_time'] += request_time * 1e-9
            for id in infos.keys():
                throughput = infos[id]['response_length'] / infos[id]['request_time']
                print(throughput)
            time.sleep(update_interval)

    def launch_sync_update(self):
        queries = self.conf_data['throughput']['queries']
        for query in queries:
            query_content = query['query_content']
            update_interval = query['update_interval']
            threading.Thread(target=self.compute_metric, args=(query_content, update_interval)).start()
            break  # TODO: delete this line


es = Throughput()
es.launch_sync_update()
