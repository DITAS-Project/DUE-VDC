import pytz
import sys
from datetime import datetime
from metrics import utils

QUERY_CONTENT = '*'


# return a list of availabilities computed per call
def get_service_availability_per_hit(service, computation_timestamp, time_window):
    print(service,file=sys.stderr)
    query_ids = QUERY_CONTENT + f' AND request.operationID:{service} AND @timestamp:{time_window}'
    res = utils.es_query(query=query_ids)
    total_hits = res['hits']['total']
    print(total_hits,file=sys.stderr)
    res = utils.es_query(query=query_ids, size=total_hits)
    attempts_successes_dict = {}
    for hit in res['hits']['hits']:
        blueprint_id = utils.get_blueprint_id()
        vdc_instance_id = utils.extract_vdc_id(hit['_index'], '-')
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
                                                'response': 0,                 
                                                'success': 0,
                                                "hit-timestamp": source['@timestamp']
                                                 }

        # For each request there is a corresponding response, so the request is counted as an attempt
        # and if the response is found, then it is counted as a success. In this way a response not found
        # is automatically accounted as a fail.
        if 'request.method' in source and source['request.method'] != 'OPTIONS':
            # It is a request hit
            print('Found a request',file=sys.stderr)
            attempts_successes_dict[blueprint_id][request_id]['attempt'] += 1
        elif 'response.code' in source:
            print('Found a response',file=sys.stderr)
            # Fixing the name of the attribute: it is actually a response time
            attempts_successes_dict[blueprint_id][request_id]['response'] += 1
            if 'response.code' in source and source['response.code'] < 500:
                attempts_successes_dict[blueprint_id][request_id]['success'] += 1
            elif 'response.code' not in source:
                print('Response hit without response.code!!!',file=sys.stderr)

    availabilities = []
    # for each blueprint
    for bp_id in attempts_successes_dict.keys():
        # for each request
        for attempts_successes in attempts_successes_dict[bp_id].values():
            blueprint_id = attempts_successes['BluePrint-ID']
            operation_id = attempts_successes['Operation-ID']
            vdc_instance_id = attempts_successes['VDC-Instance-ID']
            request_id = attempts_successes['Request-ID']
            attempt = attempts_successes['attempt']
            response = attempts_successes['response']
            success = attempts_successes['success']
            timestamp = attempts_successes['hit-timestamp']
            if response > 0 and attempt > 0:
                value = 0
                if success > 0:
                    value = 1
                metric_per_hit = {"BluePrint-ID": blueprint_id,
                                  "VDC-Instance-ID": vdc_instance_id,
                                  "Operation-ID": operation_id,
                                  "Request-ID": request_id,
                                  "metric": "availability",
                                  "unit": "Boolean",
                                  "value": float(value),
                                  "hit-timestamp": timestamp,
                                  "@timestamp": computation_timestamp
                                  }
                availabilities.append(metric_per_hit)

    return availabilities


def get_availability_per_bp_and_method(computation_timestamp, time_window, method=''):
    services = utils.get_services()
    aggregate_availabilities = []

    now_ts = datetime.now(pytz.utc)
    print("Found " + str(len(services)) + " services",file=sys.stderr)
    for service in services:
        if method == '' or method == service:
            availabilities = get_service_availability_per_hit(service, computation_timestamp, time_window)
            aggregate_availabilities_per_service = {}
            infos_per_service = {}

            print("Found " + str(len(availabilities)) + " availabilites",file=sys.stderr)

            for availability in availabilities:
                #print(availability)
                bp_id = availability['BluePrint-ID']
                if bp_id not in aggregate_availabilities_per_service.keys():
                    aggregate_availabilities_per_service[bp_id] = {'attempts': 0, 'successes': 0}
                    infos_per_service[bp_id] = {'oldest_ts': now_ts, 'hits': 0}

                # Since attempt is 1 only for the request, and 0 for the response there is no risk
                # to add twice each client request (1 for request hit, and 1 for the response hit)
                aggregate_availabilities_per_service[bp_id]['attempts'] += 1
                if availability['value'] == 1:
                    aggregate_availabilities_per_service[bp_id]['successes'] += 1

                # Here take the timestamp of the hit: if ts < oldest_ts then oldest_ts = ts
                ts = utils.parse_timestamp(availability['hit-timestamp'])
                if ts < infos_per_service[bp_id]['oldest_ts']:
                    infos_per_service[bp_id]['oldest_ts'] = ts
                # Update the number of hit
                infos_per_service[bp_id]['hits'] += 1

            for bp_id in aggregate_availabilities_per_service.keys():
                # Delta is computed from now to the oldest hit found
                delta = (now_ts - infos_per_service[bp_id]['oldest_ts']).total_seconds() / 60
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


    print(aggregate_availabilities,file=sys.stderr)
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
