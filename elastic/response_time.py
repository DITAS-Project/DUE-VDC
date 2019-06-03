import time
from datetime import datetime
import threading
import numpy as np
from metrics import Metrics


class ResponseTime(Metrics):
    def __init__(self, conf_path='../conf/conf.json', services_path='../conf/services.json'):
        super().__init__(conf_path, services_path)

    def compute_metric(self, query_content, update_interval):
        while True:
            # Compute time window of interest for the query
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
                resp_times = []
                infos = {}
                for hit in res['hits']['hits']:
                    source = hit['_source']
                    id = source['request.id']
                    if id not in infos.keys():
                        infos[id] = {'response_time': 0}
                    if 'request.requestTime' in source:
                        response_time = source['request.requestTime']
                        infos[id]['response_time'] += response_time
                for id in infos.keys():
                    resp_times.append(infos[id]['response_time'] * 1e-9)
                resp_times = np.array(resp_times)
                self._write(operationID=service, value=resp_times.mean(), name='responseTimeMean', unit='seconds', timestamp=timestamp, delta=update_interval, hits=len(resp_times))
                self._write(operationID=service, value=resp_times.max(), name='responseTimeMax', unit='seconds', timestamp=timestamp, delta=update_interval, hits=len(resp_times))
                self._write(operationID=service, value=resp_times.min(), name='responseTimeMin', unit='seconds', timestamp=timestamp, delta=update_interval, hits=len(resp_times))
            print()

    def launch_sync_update(self):
        queries = self.conf_data['response_time']['queries']
        for query in queries:
            query_content = query['query_content']
            update_interval = query['update_interval']
            threading.Thread(target=self.compute_metric, args=(query_content, update_interval)).start()
            break  # TODO: delete this line


es = ResponseTime()
es.launch_sync_update()
