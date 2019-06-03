import json
from elasticsearch import Elasticsearch

TEMP_SERVICES_FILE = '../conf/services.json'
TEMP_CONF_FILE = '../conf/conf.json'
TEMP_INDEX = "tubvdc-*"


def read_services_from_file(filepath):
    with open(filepath) as services_file:
        services = json.load(services_file)
    return services['services']


def get_services():
    return read_services_from_file(TEMP_SERVICES_FILE)


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


def body_formatter(operationID, value, name, unit, timestamp, delta, hits):
    body = {
        'meter': {
            'operationID': operationID,
            'value': value,
            'name': name,
            'unit': unit,
            'timestamp': timestamp,
            'delta': delta,
            'hits': hits
        }
    }
    return body
