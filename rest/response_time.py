#import pytz
#import numpy as np
#from datetime import datetime
from flask import Blueprint
from rest import utils as ut
from metrics import response_time as resp_time

resp_time_page = Blueprint('response_time', __name__)

QUERY_CONTENT = '*'

'''
#return a dictionary
def get_response_time(service, timestamp, time_window, minutes):
	query_ids = QUERY_CONTENT  + f' AND request.operationID:{service} AND @timestamp:{time_window}'
	res = ut.es_query(query=query_ids)
	total_hits = res['hits']['total']
	res = ut.es_query(query=query_ids, size=total_hits)
	resp_times = []
	infos = {}
	oldest_ts = datetime.now(pytz.utc)
	for hit in res['hits']['hits']:
		source = hit['_source']
		id = source['request.id']
		if id not in infos.keys():
			infos[id] = {'response_time': 0}
		if 'request.requestTime' in source:
			response_time = source['request.requestTime']
			infos[id]['response_time'] += response_time

		# Here take the timestamp of the hit: if ts < oldest_ts then oldest_ts = ts
		ts = ut.parse_timestamp(source['@timestamp'])
		if ts < oldest_ts:
			oldest_ts = ts

	for id in infos.keys():
		resp_times.append(infos[id]['response_time'] * 1e-9)
	resp_times = np.array(resp_times)

	# Delta is computed from now to the oldest hit found
	delta = (datetime.now(pytz.utc) - oldest_ts).total_seconds() / 60

	resp_time_mean = ut.body_formatter(meter='mean', value=resp_times.mean(), name='responseTime', unit='seconds',
									   timestamp=timestamp, delta=delta, delta_unit='minutes', hits=len(resp_times))
	resp_time_max = ut.body_formatter(meter='max', value=resp_times.max(), name='responseTime', unit='seconds',
									  timestamp=timestamp, delta=delta, delta_unit='minutes', hits=len(resp_times))
	resp_time_min = ut.body_formatter(meter='min', value=resp_times.min(), name='responseTime', unit='seconds',
									  timestamp=timestamp, delta=delta, delta_unit='minutes', hits=len(resp_times))
	
	dicti = {}
	dicti['mean'] = resp_time_mean
	dicti['max'] = resp_time_max
	dicti['min'] = resp_time_min

	return dicti
'''


@resp_time_page.route('/time/<int:minutes>')
def all_resp_times_of_minutes(minutes):
	# computation_timestamp, time_window = get_timestamp_timewindow(minutes)
	computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

	resp_time_dictionaries = resp_time.get_response_times_per_bp_and_method(computation_timestamp=computation_timestamp,
																			time_window=time_window)

	return ut.json_response_formatter(resp_time_dictionaries)


@resp_time_page.route('/<string:service>/time/<int:minutes>')
def service_avail_of_minutes(method, minutes):
	# computation_timestamp, time_window = get_timestamp_timewindow(minutes)
	computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

	resp_time_dictionaries = resp_time.get_response_times_per_bp_and_method(computation_timestamp=computation_timestamp,
																			time_window=time_window, service=method)

	return ut.json_response_formatter(resp_time_dictionaries)


@resp_time_page.route('/test')
def test():
	dicti = {
		"_source": ["request.id"],
		"sort": [
			{"_index": {"order": "desc"}}
		]
	}

	es_resp = ut.es_rest(body=dicti)
	return ut.json_response_formatter(es_resp)
