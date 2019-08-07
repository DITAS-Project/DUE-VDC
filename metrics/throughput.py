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

    throughput_dict = {}
    for hit in res['hits']['hits']:
        blueprint_id, vdc_instance_id = utils.extract_bp_id_vdc_id(hit['_index'], '-')
        source = hit['_source']
        request_id = source['request.id']
        operation_id = source['request.operationID']
        if blueprint_id not in throughput_dict.keys():
            throughput_dict[blueprint_id] = {}
        if request_id not in throughput_dict[blueprint_id].keys():
            throughput_dict[blueprint_id][request_id] = {"BluePrint-ID": blueprint_id,
                                                        "VDC-Instance-ID": vdc_instance_id,
                                                        "Operation-ID": operation_id,
                                                        'Request-ID': request_id,
                                                        'response-length': 0,
                                                        'request-time': 0,
                                                        "hit-timestamp": source['@timestamp']
                                                        }
        if 'response.length' in source:
            throughput_dict[blueprint_id][request_id]['response-length'] += source['response.length']
        if 'request.requestTime' in source:
            throughput_dict[blueprint_id][request_id]['request-time'] += source['request.requestTime']

    throughputs = []
    for bp_id in throughput_dict.keys():
        for throughput in throughput_dict[bp_id].values():
            blueprint_id = throughput['BluePrint-ID']
            operation_id = throughput['Operation-ID']
            vdc_instance_id = throughput['VDC-Instance-ID']
            request_id = throughput['Request-ID']
            length = throughput['response-length']
            time = throughput['request-time']
            timestamp = throughput['hit-timestamp']
            metric_per_hit = {"BluePrint-ID": blueprint_id,
                            "VDC-Instance-ID": vdc_instance_id,
                            "Operation-ID": operation_id,
                            "Request-ID": request_id,
                            "metric": "throughput",
                            "unit": "bytesPerSecond",
                            "value": length / time * 1e9,
                            "hit-timestamp": timestamp,
                            "@timestamp": computation_timestamp
                            }
            throughputs.append(metric_per_hit)

    return throughputs


def get_throughput_per_bp_and_method(computation_timestamp, time_window, method=''):
    # TODO: aggregare tutte le metriche puntuali calcolate nella prima fase
    # TODO: filtrando per timestamp
    services = utils.get_services()
    aggregate_throughputs = []

    now_ts = datetime.now(pytz.utc)
    for service in services:
        if method == '' or method == service:
            throughputs = get_service_throughput_per_hit(service, computation_timestamp, time_window)
            aggregate_throughputs_per_service = {}
            infos_per_service = {}
            for throughput in throughputs:
                bp_id = throughput['BluePrint-ID']
                if bp_id not in aggregate_throughputs_per_service.keys():
                    aggregate_throughputs_per_service[bp_id] = []
                    infos_per_service[bp_id] = {'oldest_ts': now_ts, 'hits': 0}
                aggregate_throughputs_per_service[bp_id].append(throughput['value'])

                # Here take the timestamp of the hit: if ts < oldest_ts then oldest_ts = ts
                ts = utils.parse_timestamp(throughput['hit-timestamp'])
                if ts < infos_per_service[bp_id]['oldest_ts']:
                    infos_per_service[bp_id]['oldest_ts'] = ts
                # Update the number of hit
                infos_per_service[bp_id]['hits'] += 1

            for bp_id in aggregate_throughputs_per_service.keys():
                # Delta is computed from now to the oldest hit found
                delta = (now_ts - infos_per_service[bp_id]['oldest_ts']).total_seconds() / 60
                dict = {
                    'method': service,
                    'BluePrint-ID': bp_id,
                    'mean': np.array(aggregate_throughputs_per_service[bp_id]).mean(),
                    'min': np.array(aggregate_throughputs_per_service[bp_id]).min(),
                    'max': np.array(aggregate_throughputs_per_service[bp_id]).max(),
                    'metric': 'throughput',
                    'unit': 'bytesPerSecond',
                    "@timestamp": computation_timestamp,
                    'delta': delta,
                    'delta_unit': 'minutes',
                    'hits': infos_per_service[bp_id]['hits']
                }
                aggregate_throughputs.append(dict)
    return aggregate_throughputs


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
