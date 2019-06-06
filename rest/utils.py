import json
import requests
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from flask import Response

TEMP_SERVICES_FILE = '../conf/services.json'
TEMP_CONF_FILE = '../conf/conf.json'
TEMP_INDEX = "tubvdc-*"


def read_services_from_file(filepath):
    with open(filepath) as services_file:
        services = json.load(services_file)
    return services['services']


def get_services():
    return read_services_from_file(TEMP_SERVICES_FILE)


# Compute time window of interest for the query
def get_timestamp_timewindow(minutes):
    t0 = datetime.now()
    t1 = t0 - timedelta(minutes=minutes)
    return format_time_window(t0, t1)


def format_time_window(t0, t1):
    start_time = t0.strftime('%Y-%m-%dT%H:%M:%S')
    end_time = t1.strftime('%Y-%m-%dT%H:%M:%S')
    return end_time, f'[{start_time} TO {end_time}]'


def es_query(query=None, size=10):
    with open(TEMP_CONF_FILE) as conf_file:
        conf_data = json.load(conf_file)
    es = Elasticsearch(hosts=conf_data['connections'])

    if query is None:
        query = '*'
    print(query)
    return es.search(index=TEMP_INDEX, q=query, size=size)


def body_formatter(meter, value, name, unit, timestamp, delta, delta_unit, hits):
    body = {
        'name': name,
        'value': value,
        'unit': unit,
        'timestamp': timestamp,
        'delta': delta,
        'delta_unit': delta_unit,
        'hits': hits
    }
    return body


def es_api_uri():
    with open(TEMP_CONF_FILE) as conf_file:
        conf_data = json.load(conf_file)
    host = conf_data['connections'][0]['host']
    port = conf_data['connections'][0]['port']
    index = conf_data['index']

    uri = 'http://'+host+':'+str(port)+'/'+index+'/_search'
    return uri

# Returns a dictionary
def es_rest(uri=es_api_uri(), body={}):
    query = json.dumps(body)
    response = requests.post(uri, json=body)
    results = json.loads(response.text)
    return results


def json_response_formatter(dictionary):
    js = json.dumps(dictionary)
    return Response(js, status=200, mimetype='application/json')
