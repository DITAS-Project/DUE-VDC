import time
from datetime import datetime
import threading
import numpy as np
from metrics import Metrics


class Availability(Metrics):
    def __init__(self, conf_path='../conf/conf.json', services_path='../conf/services.json'):
        super().__init__(conf_path, services_path)

    def compute_metric(self, query_content, update_interval):
        while True:
            # Compute time window of interest for the query
            t0 = datetime.now()
            time.sleep(update_interval)
            t1 = datetime.now()
            # Read list of services, of which to compute the metric
            services = self.read_services()
            timestamp, time_window = self.format_time_window(t0, t1)
            timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'  # TODO: delete this line
            for service in services:
                print(service)
                query_ids = query_content + f' AND request.operationID:{service} AND @timestamp:{time_window}'
                res = self._search(query=query_ids)
                total_hits = res['hits']['total']
                res = self._search(query=query_ids, size=total_hits)
                availabilities = []
                infos = {}
                for hit in res['hits']['hits']:
                    source = hit['_source']
                    id = source['request.id']
                    if id not in infos.keys():
                        infos[id] = {'successes': 0, 'attempts': 0}
                    # TODO: check if it always contains a request.length attribute, it should
                    request_length = source['request.length']
                    if request_length > 0:
                        # It is a request hit
                        infos[id]['attempts'] += 1
                    elif 'response.length' in source and source['response.length'] > 0:
                        # It is a response hit
                        # TODO: check if it always contains a response.code attribute, it should
                        if 'response.code' in source:
                           if source['response.code'] < 500:
                               infos[id]['successes'] += 1
                        else:
                            print('Response hit without response.code!!!')
                for id in infos.keys():
                    availabilities.append((infos[id]['successes'] / infos[id]['attempts']) * 100)
                availabilities = np.array(availabilities)
                self._write(operationID=service, value=availabilities.mean(), name='availabilityMean', unit='percentage', timestamp=timestamp)
                self._write(operationID=service, value=availabilities.max(), name='availabilityMax', unit='percentage', timestamp=timestamp)
                self._write(operationID=service, value=availabilities.min(), name='availabilityMin', unit='percentage', timestamp=timestamp)
            print()

    def launch_sync_update(self):
        queries = self.conf_data['availability']['queries']
        for query in queries:
            query_content = query['query_content']
            update_interval = query['update_interval']
            threading.Thread(target=self.compute_metric, args=(query_content, update_interval)).start()
            break  # TODO: delete this line


es = Availability()
es.launch_sync_update()
