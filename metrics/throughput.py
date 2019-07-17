import pytz
import numpy as np
from datetime import datetime
from metrics import utils

QUERY_CONTENT = '*'


# return a list of throughputs computed per call
def get_service_throughput_per_hit(service, computation_timestamp, time_window):
    print(service)
    query_ids = QUERY_CONTENT + f' AND request.operationID:{service} AND @timestamp:{time_window}'
    res = utils.es_query(query=query_ids)
    total_hits = res['hits']['total']
    res = utils.es_query(query=query_ids, size=total_hits)
    throughputs = []

    oldest_ts = datetime.now(pytz.utc)
    for hit in res['hits']['hits']:
        blueprint_id, vdc_instance_id = utils.extract_bp_id_vdc_id(hit['_index'])
        source = hit['_source']
        request_id = source['request.id']
        operation_id = source['request.operationID']
        if 'response.length' in source:
            response_length = source['response.length']
        if 'request.requestTime' in source:
            # Fixing the name of the attribute: it is actually a response time
            response_time = source['request.requestTime']
        current_throughput = response_length / response_time * 1e9

        # Here take the timestamp of the hit: if ts < oldest_ts then oldest_ts = ts
        ts = utils.parse_timestamp(source['@timestamp'])
        if ts < oldest_ts:
            oldest_ts = ts

        metric_per_hit = {"BluePrint-ID": blueprint_id,
                          "VDC-Instance-ID": vdc_instance_id,
                          "Operation-ID": operation_id,
                          "Request-ID": request_id,
                          "metric": "throughput",
                          "unit": "bytesPerSecond",
                          "value": current_throughput,
                          "hit-timestamp": "",
                          "@timestamp": computation_timestamp
                          }

        throughputs.append(metric_per_hit)

    return throughputs

def get_throughput_per_bp_and_method(computation_timestamp, time_window):
    # TODO: aggregare tutte le metriche puntuali calcolate nella prima fase
    # TODO: filtrando per timestamp


def all_throughput_of_minutes(minutes):
    timestamp, time_window = utils.get_timestamp_timewindow(minutes)
    timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    # Read list of services, of which to compute the metric
    services = utils.get_services()
    ret_dict = {}
    for service in services:
        ret_dict[service] = get_service_throughput_per_hit(service, timestamp, time_window)
    return ret_dict


def service_throughput_of_minutes(service, minutes):
    # timestamp, time_window = get_timestamp_timewindow(minutes)
    timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    ret_dict = {service: get_service_throughput_per_hit(service, timestamp, time_window, minutes)}
    return ret_dict
