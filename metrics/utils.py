import json
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

TEMP_CONF_FILE = '../conf/conf.json'
TEMP_INDEX = "tubvdc-*"

def format_time_window(t0, t1):
    start_time = t0.strftime('%Y-%m-%dT%H:%M:%S')
    end_time = t1.strftime('%Y-%m-%dT%H:%M:%S')
    return end_time, f'[{start_time} TO {end_time}]'


def extract_bp_id_vdc_id(es_index, separator):
    blueprint_id, vdc_instance_id = 'fakebp', es_index.split(separator)[0]
    # TODO: when data will be available on ES, uncomment the following line
    #blueprint_id, vdc_instance_id = es_index.split(separator)

    return blueprint_id, vdc_instance_id


# Compute time window of interest for the query
def get_timestamp_timewindow(minutes):
    t0 = datetime.now()
    t1 = t0 - timedelta(minutes=minutes)
    return format_time_window(t0, t1)


def es_query(query=None, size=10, es_index=TEMP_INDEX):
    with open(TEMP_CONF_FILE) as conf_file:
        conf_data = json.load(conf_file)
    es = Elasticsearch(hosts=conf_data['connections'])

    if query is None:
        query = '*'
    print(query)
    return es.search(index=es_index, q=query, size=size)
