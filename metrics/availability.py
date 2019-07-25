import pytz
from datetime import datetime
from metrics import utils

QUERY_CONTENT = '*'


# return a list of availabilities computed per call
def get_service_availability_per_hit(service, computation_timestamp, time_window):
    print(service)
    query_ids = QUERY_CONTENT + f' AND request.operationID:{service} AND @timestamp:{time_window}'
    res = utils.es_query(query=query_ids)
    total_hits = res['hits']['total']
    res = utils.es_query(query=query_ids, size=total_hits)
    attempts_successes_dict = {}
    for hit in res['hits']['hits']:
        blueprint_id, vdc_instance_id = utils.extract_bp_id_vdc_id(hit['_index'], '-')
        source = hit['_source']
        request_id = source['request.id']
        operation_id = source['request.operationID']
        if blueprint_id not in attempts_successes_dict.keys():
            attempts_successes_dict[blueprint_id] = {}
        if request_id not in attempts_successes_dict[blueprint_id].keys():
            attempts_successes_dict[blueprint_id][request_id] = {"BluePrint-ID": blueprint_id,
                                                "VDC-Instance-ID": vdc_instance_id,
                                                "Operation-ID": operation_id,
                                                'Request-ID': request_id,
                                                'attempt': 0,
                                                'success': 0,
                                                "hit-timestamp": source['@timestamp']
                                                 }

        # For each request there is a corresponding response, so the request is counted as an attempt
        # and if the response is found, then it is counted as a success. In this way a response not found
        # is automatically accounted as a fail.
        if 'request.length' in source and source['request.length'] > 0:
            # It is a request hit
            attempts_successes_dict[blueprint_id][request_id]['attempt'] += 1
        elif 'response.length' in source and source['response.length'] > 0:
            # Fixing the name of the attribute: it is actually a response time
            if 'response.code' in source and source['response.code'] < 500:
                attempts_successes_dict[blueprint_id][request_id]['success'] += 1
            elif 'response.code' not in source:
                print('Response hit without response.code!!!')

    availabilities = []
    for bp_id in attempts_successes_dict.keys():
        for attempts_successes in attempts_successes_dict[bp_id].values():
            blueprint_id = attempts_successes['BluePrint-ID']
            operation_id = attempts_successes['Operation-ID']
            vdc_instance_id = attempts_successes['VDC-Instance-ID']
            request_id = attempts_successes['Request-ID']
            attempt = attempts_successes['attempt']
            success = attempts_successes['success']
            timestamp = attempts_successes['hit-timestamp']
            while attempt > 0:
                attempt -= 1
                value = False
                if success > 0:
                    success -= 1
                    value = True
                metric_per_hit = {"BluePrint-ID": blueprint_id,
                                  "VDC-Instance-ID": vdc_instance_id,
                                  "Operation-ID": operation_id,
                                  "Request-ID": request_id,
                                  "metric": "availability",
                                  "unit": "Boolean",
                                  "value": value,
                                  "hit-timestamp": timestamp,
                                  "@timestamp": computation_timestamp
                                  }
                availabilities.append(metric_per_hit)

    return availabilities


def get_availability_per_bp_and_method(computation_timestamp, time_window):
    services = utils.get_services()
    aggregate_availabilities = []

    now_ts = datetime.now(pytz.utc)
    for service in services:
        availabilities = get_service_availability_per_hit(service, computation_timestamp, time_window)
        aggregate_availabilities_per_service = {}
        infos_per_service = {}

        for availability in availabilities:
            bp_id = availability['BluePrint-ID']
            if bp_id not in aggregate_availabilities_per_service.keys():
                aggregate_availabilities_per_service[bp_id] = {'attempts': 0, 'successes': 0}
                infos_per_service[bp_id] = {'oldest_ts': now_ts, 'hits': 0}

            # Since attempt is 1 only for the request, and 0 for the response there is no risk
            # to add twice each client request (1 for request hit, and 1 for the response hit)
            aggregate_availabilities_per_service[bp_id]['attempts'] += 1
            if availability['value']:
                aggregate_availabilities_per_service[bp_id]['successes'] += availability['success']

        # Delta is computed from now to the oldest hit found
        delta = (now_ts - infos_per_service[bp_id]['oldest_ts']).total_seconds() / 60

        for bp_id in aggregate_availabilities_per_service.keys():
            dict = {
                'method': service,
                'BluePrint-ID': bp_id,
                'value': aggregate_availabilities_per_service[bp_id]['successes'] /
                         aggregate_availabilities_per_service[bp_id]['attempts'] * 100,
                'metric': 'availability',
                'unit': 'percentage',
                '@timestamp': computation_timestamp,
                'delta': delta,
                'delta_unit': 'minutes',
                'hits': infos_per_service[bp_id]['hits']

            }
            aggregate_availabilities.append(dict)

    return aggregate_availabilities


def overall_availability_of_minutes(minutes):
    timestamp, time_window = utils.get_timestamp_timewindow(minutes)
    timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    # Read list of services, of which to compute the metric
    services = utils.get_services()
    ret_dict = {}
    for service in services:
        ret_dict[service] = get_service_availability_per_hit(service, timestamp, time_window)
    return ret_dict


def service_availability_of_minutes(service, minutes):
    # timestamp, time_window = get_timestamp_timewindow(minutes)
    timestamp, time_window = '2016-06-20T22:28:46', '[2018-06-20T22:28:46 TO 2020-06-20T22:36:41]'
    ret_dict = {service: get_service_availability_per_hit(service, timestamp, time_window, minutes)}
    return ret_dict
