import pytz
import sys
import numpy as np
from datetime import datetime
from metrics import utils

QUERY_CONTENT = '*'


# return a list of response time computed per call
def get_service_response_times_per_hit(service, computation_timestamp, time_window):
    print(service,file=sys.stderr)
    query_ids = QUERY_CONTENT + f' AND request.operationID:{service} AND @timestamp:{time_window}'
    res = utils.es_query(query=query_ids)
    total_hits = res['hits']['total']
    res = utils.es_query(query=query_ids, size=total_hits)
    times = []

    for hit in res['hits']['hits']:
        blueprint_id = utils.get_blueprint_id()
        vdc_instance_id = utils.extract_vdc_id(hit['_index'], '-')
        source = hit['_source']
        request_id = source['request.id']
        operation_id = source['request.operationID']
        if 'request.requestTime' in source and 'request.method' in source and source['request.method'] != 'OPTIONS':
            # Fixing the name of the attribute: it is actually a response time
            response_time = source['request.requestTime'] / 1000000000

            metric_per_hit = {"BluePrint-ID": blueprint_id,
                              "VDC-Instance-ID": vdc_instance_id,
                              "Operation-ID": operation_id,
                              "Request-ID": request_id,
                              "metric": "response time",
                              "unit": "second",
                              "value": float(response_time),
                              "hit-timestamp": source['@timestamp'],
                              "@timestamp": computation_timestamp
                              }

            times.append(metric_per_hit)

    return times


def get_response_times_per_bp_and_method(computation_timestamp, time_window, method=''):
    # TODO: aggregare tutte le metriche puntuali calcolate nella prima fase
    # TODO: filtrando per timestamp
    services = utils.get_services()
    aggregate_response_time = []

    now_ts = datetime.now(pytz.utc)
    for service in services:
        if method == '' or method == service:
            response_times = get_service_response_times_per_hit(service, computation_timestamp, time_window)
            aggregate_response_time_per_service = {}
            infos_per_service = {}
            for response_time in response_times:
                bp_id = response_time['BluePrint-ID']
                if bp_id not in aggregate_response_time_per_service.keys():
                    aggregate_response_time_per_service[bp_id] = []
                    infos_per_service[bp_id] = {'oldest_ts': now_ts, 'hits': 0}
                aggregate_response_time_per_service[bp_id].append(response_time['value'])

                # Here take the timestamp of the hit: if ts < oldest_ts then oldest_ts = ts
                ts = utils.parse_timestamp(response_time['hit-timestamp'])
                if ts < infos_per_service[bp_id]['oldest_ts']:
                    infos_per_service[bp_id]['oldest_ts'] = ts
                # Update the number of hit
                infos_per_service[bp_id]['hits'] += 1

            for bp_id in aggregate_response_time_per_service.keys():
                # Delta is computed from now to the oldest hit found
                delta = (now_ts - infos_per_service[bp_id]['oldest_ts']).total_seconds() / 60
                dict = {
                    'method': service,
                    'BluePrint-ID': bp_id,
                    'mean': float(np.array(aggregate_response_time_per_service[bp_id]).mean()),
                    'min': float(np.array(aggregate_response_time_per_service[bp_id]).min()),
                    'max': float(np.array(aggregate_response_time_per_service[bp_id]).max()),
                    'metric': 'response time',
                    'unit': 'second',
                    "@timestamp": computation_timestamp,
                    'delta': float(delta),
                    'delta_unit': 'minutes',
                    'hits': infos_per_service[bp_id]['hits']
                }
                aggregate_response_time.append(dict)
    return aggregate_response_time


def all_response_times_of_minutes(minutes):
    timestamp, time_window = utils.get_timestamp_timewindow(minutes)
    # Read list of services, of which to compute the metric
    services = utils.get_services()
    ret_dict = {}
    for service in services:
        ret_dict[service] = get_service_response_times_per_hit(service, timestamp, time_window)
    return ret_dict


def service_response_times_of_minutes(service, minutes):
    timestamp, time_window = utils.get_timestamp_timewindow(minutes)
    ret_dict = {service: get_service_response_times_per_hit(service, timestamp, time_window)}
    return ret_dict
