import json
from flask import Blueprint
from metrics import availability as avail
from metrics import utils as ut
from elasticsearch.exceptions import ConnectionError

avail_page = Blueprint('availability', __name__)

QUERY_CONTENT = '*'


@avail_page.route('/')
def hello():
    return ut.json_response_formatter({'msg': "I'm the availability file!"})


@avail_page.route('/time/<int:minutes>')
def all_avail_of_minutes(minutes):
    # Time window with dummy data
    #computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    computation_timestamp, time_window = ut.get_timestamp_timewindow(minutes)
    try:
        avail_dictionaries = avail.get_availability_per_bp_and_method(computation_timestamp=computation_timestamp,
                                                                  time_window=time_window)
    except ConnectionError:
        avail_dictionaries = []

    return ut.json_response_formatter(avail_dictionaries)


@avail_page.route('/<string:method>/time/<int:minutes>')
def service_avail_of_minutes(method, minutes):
    # Time window with dummy data
    #computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

    computation_timestamp, time_window = ut.get_timestamp_timewindow(minutes)
    try:
        avail_dictionaries = avail.get_availability_per_bp_and_method(computation_timestamp=computation_timestamp,
                                                                  time_window=time_window, method=method)
    except ConnectionError:
        avail_dictionaries = {
                    'method': '',
                    'BluePrint-ID': '',
                    'value': 0,
                    'metric': 'availability',
                    'unit': 'percentage',
                    '@timestamp': '',
                    'delta': '',
                    'delta_unit': '',
                    'hits': ''
                }
    return ut.json_response_formatter(avail_dictionaries)


@avail_page.route('/test')
def test():
    dicti = {
        "_source": ["request.id"],
        "sort": [
            {"_index": {"order": "desc"}}
        ]
    }

    es_resp = ut.es_rest(body=dicti)
    return ut.json_response_formatter(es_resp)
