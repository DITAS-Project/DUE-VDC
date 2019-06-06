import json
from flask import Flask
from availability import avail_page
from throughput import throughput_page

API_PREFIX = '/rest'

app = Flask(__name__)

app.register_blueprint(avail_page, url_prefix=API_PREFIX + '/availability')
app.register_blueprint(throughput_page, url_prefix=API_PREFIX + '/throughput')

@app.route(API_PREFIX)
def index_msg():
    resp = {'msg': 'This is the REST API of DUE-VDC'}
    return json.dumps(resp)