import json
import numpy as np
from flask import Blueprint, Response
from utils import *

throughput_page = Blueprint('throughput', __name__)

QUERY_CONTENT = '*'

@throughput_page.route('/')
def hello():
    return json.dumps({'msg': "I'm throughput file!"})

#return a dictionary
def get_service_throughput(service, timestamp, time_window, minutes):
    print(service)
    query_ids = QUERY_CONTENT + f' AND request.operationID:{service} AND @timestamp:{time_window}'
    res = es_query(query=query_ids)
    total_hits = res['hits']['total']
    res = es_query(query=query_ids, size=total_hits)
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

    throughput_mean = body_formatter(meter='mean', value=throughputs.mean(), name='throughput', unit='BytesPerSecond',
                                timestamp=timestamp, delta=minutes, delta_unit='minutes', hits=len(throughputs))
    throughput_max = body_formatter(meter='max', value=throughputs.max(), name='throughput', unit='BytesPerSecond',
                               timestamp=timestamp, delta=minutes, delta_unit='minutes', hits=len(throughputs))
    throughput_min = body_formatter(meter='min', value=throughputs.min(), name='throughput', unit='BytesPerSecond',
                               timestamp=timestamp, delta=minutes, delta_unit='minutes', hits=len(throughputs))

    dicti = {}
    dicti['mean'] = throughput_mean
    dicti['max'] = throughput_max
    dicti['min'] = throughput_min
    return dicti


@throughput_page.route('/time/<int:minutes>')
def all_throughput_of_minutes(minutes):
    # timestamp, time_window = get_timestamp_timewindow(minutes)
    timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    # Read list of services, of which to compute the metric
    services = get_services()
    ret_dict = {}
    for service in services:
        ret_dict[service] = get_service_throughput(service, timestamp, time_window, minutes)
    return json_response_formatter(ret_dict)

@throughput_page.route('/<string:service>/time/<int:minutes>')
def service_throughput_of_minutes(service, minutes):
    # timestamp, time_window = get_timestamp_timewindow(minutes)
    timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    ret_dict = {}
    ret_dict[service] = get_service_throughput(service, timestamp, time_window, minutes)
    return json_response_formatter(ret_dict)
