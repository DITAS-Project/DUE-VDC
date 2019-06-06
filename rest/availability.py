import json
from datetime import datetime, timedelta
import numpy as np
from flask import Blueprint, Response
from utils import *

avail_page = Blueprint('availability', __name__)

QUERY_CONTENT = '*'

@avail_page.route('/')
def hello():
    return json.dumps({'msg': "I'm availability file!"})

#return a dictionary
def get_service_avail(service, timestamp, time_window, minutes):
    print(service)
    query_ids = QUERY_CONTENT + f' AND request.operationID:{service} AND @timestamp:{time_window}'
    res = es_query(query=query_ids)
    total_hits = res['hits']['total']
    res = es_query(query=query_ids, size=total_hits)
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

    avail_mean = body_formatter(meter='mean', value=availabilities.mean(), name='availability', unit='percentage',
                                timestamp=timestamp, delta=minutes, delta_unit='minutes', hits=len(availabilities))
    avail_max = body_formatter(meter='max', value=availabilities.max(), name='availability', unit='percentage',
                               timestamp=timestamp, delta=minutes, delta_unit='minutes', hits=len(availabilities))
    avail_min = body_formatter(meter='min', value=availabilities.min(), name='availability', unit='percentage',
                               timestamp=timestamp, delta=minutes, delta_unit='minutes', hits=len(availabilities))

    dicti = {}
    dicti['mean'] = avail_mean
    dicti['max'] = avail_max
    dicti['min'] = avail_min

    return dicti


@avail_page.route('/time/<int:minutes>')
def all_avail_of_minutes(minutes):
    # timestamp, time_window = get_timestamp_timewindow(minutes)
    timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    # Read list of services, of which to compute the metric
    services = get_services()
    ret_dict = {}
    for service in services:
        ret_dict[service] = get_service_avail(service, timestamp, time_window, minutes)
    return json_response_formatter(ret_dict)

@avail_page.route('/<string:service>/time/<int:minutes>')
def service_avail_of_minutes(service, minutes):
    # timestamp, time_window = get_timestamp_timewindow(minutes)
    timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    ret_dict = {}
    ret_dict[service] = get_service_avail(service, timestamp, time_window, minutes)
    return json_response_formatter(ret_dict)

# Compute time window of interest for the query
def get_timestamp_timewindow(minutes):
    t0 = datetime.now()
    t1 = t0 - timedelta(minutes=minutes)
    return format_time_window(t0, t1)

@avail_page.route('/test')
def test():
    dicti = {
        "_source": ["request.id"],
        "sort": [
            {"_index": {"order": "desc"}}
        ]
    }

    es_resp = es_rest(body=dicti)
    return json_response_formatter(es_resp)
