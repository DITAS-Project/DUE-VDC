import json
from flask import Blueprint
from metrics import throughput as thrpt
from metrics import utils as ut

throughput_page = Blueprint('throughput', __name__)

QUERY_CONTENT = '*'

'''
# return a dictionary
def get_service_throughput(service, timestamp, time_window, minutes):
    print(service)
    query_ids = QUERY_CONTENT + f' AND request.operationID:{service} AND @timestamp:{time_window}'
    res = ut.es_query(query=query_ids)
    total_hits = res['hits']['total']
    res = ut.es_query(query=query_ids, size=total_hits)
    throughputs = []
    infos = {}
    oldest_ts = datetime.now(pytz.utc)
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

        # Here take the timestamp of the hit: if ts < oldest_ts then oldest_ts = ts
        ts = ut.parse_timestamp(source['@timestamp'])
        if ts < oldest_ts:
            oldest_ts = ts

    for id in infos.keys():
        throughputs.append((infos[id]['response_length'] / infos[id]['request_time']) * 1e9)
    throughputs = np.array(throughputs)

    # Delta is computed from now to the oldest hit found
    delta = (datetime.now(pytz.utc) - oldest_ts).total_seconds() / 60

    throughput_mean = ut.body_formatter(meter='mean', value=throughputs.mean(), name='throughput', unit='BytesPerSecond',
                                        timestamp=timestamp, delta=delta, delta_unit='minutes', hits=len(throughputs))
    throughput_max = ut.body_formatter(meter='max', value=throughputs.max(), name='throughput', unit='BytesPerSecond',
                                       timestamp=timestamp, delta=delta, delta_unit='minutes', hits=len(throughputs))

    throughput_min = ut.body_formatter(meter='min', value=throughputs.min(), name='throughput', unit='BytesPerSecond',
                                       timestamp=timestamp, delta=delta, delta_unit='minutes', hits=len(throughputs))

    dicti = {}
    dicti['mean'] = throughput_mean
    dicti['max'] = throughput_max
    dicti['min'] = throughput_min
    return dicti
'''

@throughput_page.route('/time/<int:minutes>')
def all_throughput_of_minutes(minutes):
    # computation_timestamp, time_window = get_timestamp_timewindow(minutes)
    computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

    thrpt_dictionaries = thrpt.get_throughput_per_bp_and_method(computation_timestamp=computation_timestamp,
                                                                time_window=time_window)

    return ut.json_response_formatter(thrpt_dictionaries)


@throughput_page.route('/<string:method>/time/<int:minutes>')
def service_throughput_of_minutes(method, minutes):
    # computation_timestamp, time_window = get_timestamp_timewindow(minutes)
    computation_timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'

    thrpt_dictionaries = thrpt.get_throughput_per_bp_and_method(computation_timestamp=computation_timestamp,
                                                                time_window=time_window, method=method)

    return ut.json_response_formatter(thrpt_dictionaries)


@throughput_page.route('/')
def hello():
    return json.dumps({'msg': "I'm the throughput file!"})


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

