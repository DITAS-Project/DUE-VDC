import json
import numpy as np
from flask import Blueprint
from utils import *

resp_time_page = Blueprint('response_time', __name__)

QUERY_CONTENT = '*'

#return a dictionary
def get_response_time(service, timestamp, time_window, minutes):
	query_ids = QUERY_CONTENT  + f' AND request.operationID:{service} AND @timestamp:{time_window}'
	res = es_query(query=query_ids)
	total_hits = res['hits']['total']
	res = es_query(query=query_ids, size=total_hits)
	resp_times = []
	infos = {}
	for hit in res['hits']['hits']:
		source = hit['_source']
		id = source['request.id']
		if id not in infos.keys():
			infos[id] = {'response_time': 0}
		if 'request.requestTime' in source:
			response_time = source['request.requestTime']
			infos[id]['response_time'] += response_time
	for id in infos.keys():
		resp_times.append(infos[id]['response_time'] * 1e-9)
	resp_times = np.array(resp_times)
	
	resp_time_mean = body_formatter(meter='mean', value=resp_times.mean(), name='responseTime', unit='seconds',
									timestamp=timestamp, delta=minutes, delta_unit='minutes', hits=len(resp_times))
	resp_time_max = body_formatter(meter='max', value=resp_times.max(), name='responseTime', unit='seconds',
								   timestamp=timestamp, delta=minutes, delta_unit='minutes', hits=len(resp_times))
	resp_time_min = body_formatter(meter='min', value=resp_times.min(), name='responseTime', unit='seconds',
								   timestamp=timestamp, delta=minutes, delta_unit='minutes', hits=len(resp_times))
	
	dicti = {}
	dicti['mean'] = resp_time_mean
	dicti['max'] = resp_time_max
	dicti['min'] = resp_time_min

	return dicti

@resp_time_page.route('/time/<int:minutes>')
def all_resp_times_of_minutes(minutes):
	# timestamp, time_window = get_timestamp_timewindow(minutes)
	timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
	# Read list of services, of which to compute the metric
	services = get_services()
	ret_dict = {}
	for service in services:
		ret_dict[service] = get_response_time(service, timestamp, time_window, minutes)
		return json_response_formatter(ret_dict)


@resp_time_page.route('/<string:service>/time/<int:minutes>')
def service_avail_of_minutes(service, minutes):
	# timestamp, time_window = get_timestamp_timewindow(minutes)
	timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
	ret_dict = {}
	ret_dict[service] = get_resp_time(service, timestamp, time_window, minutes)
	return json_response_formatter(ret_dict)

@resp_time_page.route('/test')
def test():
	dicti = {
        "_source": ["request.id"],
        "sort": [
            {"_index": {"order": "desc"}}
        ]
	}

	es_resp = es_rest(body=dicti)
	return json_response_formatter(es_resp)
