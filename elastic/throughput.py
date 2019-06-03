import time
from datetime import datetime
import threading
import numpy as np
from metrics import Metrics


class Throughput(Metrics):
    def __init__(self, conf_path='../conf/conf.json', services_path='../conf/services.json'):
        super().__init__(conf_path, services_path)

    def compute_metric(self, query_content, update_interval):
        while True:
            t0 = datetime.now()
            time.sleep(update_interval)
            t1 = datetime.now()
            services = self.read_services()
            timestamp, time_window = self.format_time_window(t0, t1)
            timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'  # TODO: delete this line
            for service in services:
                print(service)
                query_ids = query_content + f' AND request.operationID:{service} AND @timestamp:{time_window}'
                res = self._search(query=query_ids)
                total_hits = res['hits']['total']
                res = self._search(query=query_ids, size=total_hits)
                throughputs = []
                infos = {}
                for hit in res['hits']['hits']:
                    source = hit['_source']
                    id = source['request.id']
                    if id not in infos.keys():
                        infos[id] = {'response_length': 0, 'request_time': 0}
                    if 'response.length' in source:
                        response_length = source['response.length']
                        infos[id]['response_length'] += response_length
                    if 'request.requestTime' in source:
                        request_time = source['request.requestTime']
                        infos[id]['request_time'] += request_time
                for id in infos.keys():
                    throughputs.append((infos[id]['response_length'] / infos[id]['request_time']) * 1e9)
                throughputs = np.array(throughputs)
                self._write(operationID=service, value=throughputs.mean(), name='throughputMean', unit='BytesPerSecond', timestamp=timestamp, delta=update_interval, hits=len(throughputs))
                self._write(operationID=service, value=throughputs.max(), name='throughputMax', unit='BytesPerSecond', timestamp=timestamp, delta=update_interval, hits=len(throughputs))
                self._write(operationID=service, value=throughputs.min(), name='throughputMin', unit='BytesPerSecond', timestamp=timestamp, delta=update_interval, hits=len(throughputs))
            print()

    def launch_sync_update(self):
        queries = self.conf_data['throughput']['queries']
        for query in queries:
            query_content = query['query_content']
            update_interval = query['update_interval']
            threading.Thread(target=self.compute_metric, args=(query_content, update_interval)).start()
            break  # TODO: delete this line


es = Throughput()
es.launch_sync_update()
