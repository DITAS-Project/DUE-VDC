import json
from flask import Blueprint
from metrics import throughput as thrpt
from metrics import utils as ut
from elasticsearch.exceptions import ConnectionError

throughput_page = Blueprint('throughput', __name__)

QUERY_CONTENT = '*'


@throughput_page.route('/time/<int:minutes>')
def all_throughput_of_minutes(minutes):
    # Time window with dummy data
    # computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

    computation_timestamp, time_window = ut.get_timestamp_timewindow(minutes)

    try:
        thrpt_dictionaries = thrpt.get_throughput_per_bp_and_method(computation_timestamp=computation_timestamp,
                                                                time_window=time_window)
    except ConnectionError:
        thrpt_dictionaries  = []

    return ut.json_response_formatter(thrpt_dictionaries)


@throughput_page.route('/<string:method>/time/<int:minutes>')
def service_throughput_of_minutes(method, minutes):
    # Time window with dummy data
    # computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

    computation_timestamp, time_window = ut.get_timestamp_timewindow(minutes)

    try:
        thrpt_dictionaries = thrpt.get_throughput_per_bp_and_method(computation_timestamp=computation_timestamp,
                                                                time_window=time_window, method=method)[0]
    except (ConnectionError,IndexError):
        thrpt_dictionaries = {
                    'method': method,
                    'BluePrint-ID': '',
                    'value': 0,
                    'metric': 'throughput',
                    'unit': 'percentage',
                    '@timestamp': '',
                    'delta': 0,
                    'delta_unit': '',
                    'hits': 0
                }

    return ut.json_response_formatter(thrpt_dictionaries)


@throughput_page.route('/')
def hello():
    return ut.json_response_formatter({'msg': "I'm the throughput file!"})


@throughput_page.route('/test')
def test():
    dicti = {
        "_source": ["request.id"],
        "sort": [
            {"_index": {"order": "desc"}}
        ]
    }

    es_resp = ut.es_rest(body=dicti)
    return ut.json_response_formatter(es_resp)

