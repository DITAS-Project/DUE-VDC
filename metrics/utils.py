import json
import datetime
import dateutil.parser
from elasticsearch import Elasticsearch
from flask import Response
import sys

TEMP_CONF_FILE = 'conf/conf.json'
CONCRETE_BLUEPRINT_PATH = 'conf/blueprint.json'

CONCRETE_ID = '_id'
CONCRETE_ABSTRACT_PROPERTIES = 'ABSTRACT_PROPERTIES'
CONCRETE_METHOD_ID = 'method_id'

CONF_CONNECTIONS = "connections"
CONF_URL = 'ElasticSearchURL'
CONF_AUTH = 'ElasticBasicAuth'
CONF_USER = 'ElasticUser'
CONF_PASSWORD = 'ElasticPassword'
CONF_QOS = 'index_qos'

def format_time_window(t0, t1):
    start_time = t0.isoformat()
    end_time = t1.isoformat()
    return end_time, f'[{start_time} TO {end_time}]'


def extract_vdc_id(es_index, separator):
    sep = es_index.split(separator)
    vdc_instance_id = sep[0] + '-' + sep[1]
    return vdc_instance_id


# Compute time window of interest for the query
def get_timestamp_timewindow(minutes):
    local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    t1 = datetime.datetime.now(local_timezone)
    t0 = t1 - datetime.timedelta(minutes=minutes)
    return format_time_window(t0, t1)


def es_query(query=None, size=10):
    with open(TEMP_CONF_FILE) as conf_file:
        conf_data = json.load(conf_file)
    es_host = []
    for host in conf_data[CONF_CONNECTIONS]:
        es_host.append(host[CONF_URL])
    if conf_data[CONF_AUTH]:
        es = Elasticsearch(hosts=es_host, http_auth=(conf_data[CONF_USER], conf_data[CONF_PASSWORD]))
    else:
        es = Elasticsearch(hosts=es_host)

    es_index = conf_data[CONF_QOS]
    sys.stderr.write("query index: " + es_index + "\n")

    if query is None:
        query = '*'
    print(query,file=sys.stderr)
    return es.search(index=es_index, q=query, size=size)


def get_services():
    with open(CONCRETE_BLUEPRINT_PATH) as bp_file:
        bp = json.load(bp_file)
    services = []
    for method in bp[CONCRETE_ABSTRACT_PROPERTIES]:
        services.append(method[CONCRETE_METHOD_ID])
    return services


def json_response_formatter(dictionary):
    js = json.dumps(dictionary)
    return Response(js, status=200, mimetype='application/json')


def parse_timestamp(datestring):
    return dateutil.parser.parse(datestring)

def get_blueprint_id():
    with open(CONCRETE_BLUEPRINT_PATH) as bp_file:
        bp = json.load(bp_file)
    return bp[CONCRETE_ID]

