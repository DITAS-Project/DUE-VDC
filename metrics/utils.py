import json
import datetime
import dateutil.parser
from elasticsearch import Elasticsearch
from flask import Response


TEMP_CONF_FILE = 'conf/conf.json'
TEMP_SERVICES_FILE = 'conf/services.json'
TEMP_INDEX = "tubvdc-*"


def format_time_window(t0, t1):
    start_time = t0.isoformat()
    end_time = t1.isoformat()
    return end_time, f'[{start_time} TO {end_time}]'


def extract_bp_id_vdc_id(es_index, separator):
    blueprint_id, vdc_instance_id = 'fakebp', es_index.split(separator)[0]
    # TODO: when data will be available on ES, uncomment the following line
    #blueprint_id, vdc_instance_id = es_index.split(separator)

    return blueprint_id, vdc_instance_id


# Compute time window of interest for the query
def get_timestamp_timewindow(minutes):
    local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    t1 = datetime.datetime.now(local_timezone)
    t0 = t1 - datetime.timedelta(minutes=minutes)
    return format_time_window(t0, t1)


def es_query(query=None, size=10, es_index=TEMP_INDEX):
    with open(TEMP_CONF_FILE) as conf_file:
        conf_data = json.load(conf_file)
    es = Elasticsearch(hosts=conf_data['connections'])

    if query is None:
        query = '*'
    print(query)
    return es.search(index=es_index, q=query, size=size)


def read_services_from_file(filepath):
    with open(filepath) as services_file:
        services = json.load(services_file)
    return services['services']


def get_services():
    return read_services_from_file(TEMP_SERVICES_FILE)


def json_response_formatter(dictionary):
    js = json.dumps(dictionary)
    return Response(js, status=200, mimetype='application/json')


def parse_timestamp(datestring):
    return dateutil.parser.parse(datestring)

