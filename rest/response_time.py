import json
from flask import Blueprint
from metrics import response_time as resp_time
from metrics import utils as ut
from elasticsearch.exceptions import ConnectionError

resp_time_page = Blueprint('response_time', __name__)

QUERY_CONTENT = '*'


@resp_time_page.route('/time/<int:minutes>')
def all_resp_times_of_minutes(minutes):
	# Time window with dummy data
	# computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

	computation_timestamp, time_window = ut.get_timestamp_timewindow(minutes)

	try:
		resp_time_dictionaries = resp_time.get_response_times_per_bp_and_method(computation_timestamp=computation_timestamp,
																			time_window=time_window)
	except ConnectionError:
		resp_time_dictionaries = []

	return ut.json_response_formatter(resp_time_dictionaries)


@resp_time_page.route('/<string:method>/time/<int:minutes>')
def service_response_time_of_minutes(method, minutes):
	# Time window with dummy data
	# computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

	computation_timestamp, time_window = ut.get_timestamp_timewindow(minutes)

	try:
		resp_time_dictionaries = resp_time.get_response_times_per_bp_and_method(computation_timestamp=computation_timestamp,
																			time_window=time_window, method=method)
	except ConnectionError:
		resp_time_dictionaries = []

	return ut.json_response_formatter(resp_time_dictionaries)


@resp_time_page.route('/')
def hello():
	return json.dumps({'msg': "I'm the response time file!"})


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
