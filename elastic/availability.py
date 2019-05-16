import threading
import time
import numpy as np
from metrics import Metrics


class Availability(Metrics):
    def __init__(self, conf_path='../conf/conf.json'):
        super().__init__(conf_path)

    def compute_metric(self, interval):
        sampling_interval, update_interval = interval
        t = 0
        attempts = 0
        successes = 0
        while True:
            attempts, successes = attempts + 1, successes + int(self.ping())
            time.sleep(sampling_interval)
            t += sampling_interval
            if np.isclose(t, update_interval):
                availability = successes / attempts
                print(availability)
                t = 0
                attempts = 0
                successes = 0

    def launch_sync_update(self):
        intervals = self.conf_data['availability']['update']
        for interval in intervals:
            threading.Thread(target=self.compute_metric, args=(interval,)).start()

    def ping(self):
        return self.es.ping()


es = Availability()
es.launch_sync_update()
while True:
    time.sleep(1)
