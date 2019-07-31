import json
from flask import Flask
from rest.availability import avail_page
#from rest.response_time import resp_time_page
#from rest.throughput import throughput_page

API_PREFIX = '/rest'

app = Flask(__name__)
app.debug = True

app.register_blueprint(avail_page, url_prefix=API_PREFIX + '/availability')
#app.register_blueprint(resp_time_page, url_prefix=API_PREFIX + '/response_time')
#app.register_blueprint(throughput_page, url_prefix=API_PREFIX + '/throughput')


@app.route('/')
def index():
    resp = {'msg': 'This is /'}
    return json.dumps(resp)


@app.route(API_PREFIX)
def index_msg():
    resp = {'msg': 'This is the REST API of DUE-VDC'}
    return json.dumps(resp)
