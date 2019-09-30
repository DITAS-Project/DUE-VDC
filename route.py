import json
from flask import Flask
from swagger_ui import flask_api_doc
from rest.availability import avail_page
from rest.response_time import resp_time_page
from rest.throughput import throughput_page
from rest.data_quality import data_quality_page

# for Flask

__author__ = "Cataldo Calò, Mirco Manzoni"
__credits__ = ["Cataldo Calò", "Mirco Manzoni"]
__status__ = "Development"

API_PREFIX = '/rest'

app = Flask(__name__)
app.debug = True

app.register_blueprint(avail_page, url_prefix=API_PREFIX + '/availability')
app.register_blueprint(resp_time_page, url_prefix=API_PREFIX + '/response_time')
app.register_blueprint(throughput_page, url_prefix=API_PREFIX + '/throughput')
app.register_blueprint(data_quality_page, url_prefix=API_PREFIX + '/data_quality')

flask_api_doc(app, config_path='./rest/specs.yaml', url_prefix='/api/doc', title='API doc')

@app.route('/')
def index():
    resp = {'msg': 'This is /'}
    return json.dumps(resp)


@app.route(API_PREFIX)
def index_msg():
    resp = {'msg': 'This is the REST API of DUE-VDC'}
    return json.dumps(resp)
