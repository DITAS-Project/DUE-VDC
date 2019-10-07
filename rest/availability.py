import json
from flask import Blueprint
from flask import Response
from metrics import availability as avail
from metrics import utils as ut

avail_page = Blueprint('availability', __name__)

QUERY_CONTENT = '*'


@avail_page.route('/')
def hello():
    js = json.dumps({'msg': "I'm the availability file!"})
    return Response(js, status=200, mimetype='application/json')


@avail_page.route('/time/<int:minutes>')
def all_avail_of_minutes(minutes):
    # Time window with dummy data
    #computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    computation_timestamp, time_window = ut.get_timestamp_timewindow(minutes)

    avail_dictionaries = avail.get_availability_per_bp_and_method(computation_timestamp=computation_timestamp,
                                                                  time_window=time_window)

    return ut.json_response_formatter(avail_dictionaries)


@avail_page.route('/<string:method>/time/<int:minutes>')
def service_avail_of_minutes(method, minutes):
    # Time window with dummy data
    #computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

    computation_timestamp, time_window = ut.get_timestamp_timewindow(minutes)

    avail_dictionaries = avail.get_availability_per_bp_and_method(computation_timestamp=computation_timestamp,
                                                                  time_window=time_window, method=method)
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
