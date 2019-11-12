import json
from flask import Flask
from flask import Response
from swagger_ui import flask_api_doc
from rest.availability import avail_page
from rest.response_time import resp_time_page
from rest.throughput import throughput_page
from rest.data_quality import data_quality_page
from elasticsearch.exceptions import ConnectionError
from metrics import utils

__author__ = "Cataldo Calò, Mirco Manzoni"
__credits__ = ["Cataldo Calò", "Mirco Manzoni"]
__status__ = "Development"


#API_PREFIX = '/rest'
API_PREFIX = ''

app = Flask(__name__)
app.debug = True

# API v1
app.register_blueprint(avail_page, url_prefix=API_PREFIX + '/v1/availability')
app.register_blueprint(resp_time_page, url_prefix=API_PREFIX + '/v1/response_time')
app.register_blueprint(throughput_page, url_prefix=API_PREFIX + '/v1/throughput')
app.register_blueprint(data_quality_page, url_prefix=API_PREFIX + '/v1/data_quality')

# Future API versions go here


# Generating the docs
flask_api_doc(app, config_path='./rest/specs.yaml', url_prefix='/api/doc', title='API doc')


@app.route('/')
def index():
    resp = {'msg': 'This is the REST API of DUE-VDC'}
    return Response(json.dumps(resp), status=200, mimetype='application/json')


@app.route('/debug_es')
def ping_es():
    try:
        utils.es_query()
        output = 'ElasticSearch is online.'
    except ConnectionError:
        output = 'ElasticSearch is offline.'
    print(output)
    return Response(json.dumps(output), status=200, mimetype='application/json')
