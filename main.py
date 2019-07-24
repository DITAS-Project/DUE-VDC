from elastic.throughput import Throughput

if __name__ == "__main__":
    es = Throughput()
    es.launch_sync_update()