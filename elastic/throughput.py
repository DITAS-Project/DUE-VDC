import time
import threading
import sys
import traceback
from datetime import datetime, timedelta
from .metric import Metric
from metrics.throughput import *
from elasticsearch.exceptions import ConnectionError


class Throughput(Metric):
    def __init__(self, conf_path='conf/conf.json'):
        super().__init__(conf_path)

    def compute_metric(self, query_content, update_interval, update_delay):
        while True:
            try:
                t0 = datetime.now() - timedelta(seconds=update_delay)
                time.sleep(update_interval)
                t1 = datetime.now() - timedelta(seconds=update_delay)
                services = utils.get_services()
                timestamp, time_window = self.format_time_window(t0, t1)
                #timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
                for service in services:
                    hits = get_service_throughput_per_hit(service, timestamp, time_window)
                    for hit in hits:
                        self.write(hit['BluePrint-ID'], hit['VDC-Instance-ID'], hit['Request-ID'], hit['Operation-ID'], hit['value'], hit['metric'], hit['unit'], hit['hit-timestamp'], hit['@timestamp'])
                        print('throughput data written',file=sys.stderr)
            except ConnectionError:
                traceback.print_exc(file=sys.stderr)
                    

    def launch_sync_update(self):
        queries = self.conf_data['throughput']['queries']
        for query in queries:
            query_content = query['query_content']
            update_interval = query['update_interval']
            update_delay = query['update_delay']
            threading.Thread(target=self.compute_metric, args=(query_content, update_interval, update_delay)).start()
            break  # TODO: delete this line



