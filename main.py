from elastic.throughput import Throughput
from elastic.response_time import ResponseTime
from elastic.availability import Availability


if __name__ == "__main__":
    es = Throughput()
    es.launch_sync_update()
    es = ResponseTime()
    es.launch_sync_update()
    es = Availability()
    es.launch_sync_update()
