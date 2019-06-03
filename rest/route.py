import json
from flask import Flask
from availability import avail_page

API_PREFIX = '/rest'

app = Flask(__name__)

app.register_blueprint(avail_page, url_prefix=API_PREFIX + '/availability')

@app.route(API_PREFIX)
def index_msg():
    resp = {'msg': 'This is the REST API of DUE-VDC'}
    return json.dumps(resp)