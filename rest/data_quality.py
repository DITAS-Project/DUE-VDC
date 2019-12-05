import json
import sys
from flask import Blueprint, request
from rest.data_quality_metrics.accuracy import Accuracy
from rest.data_quality_metrics.completeness import Completeness
from rest.data_quality_metrics.volume import Volume
from rest.data_quality_metrics.consistency import Consistency
from rest.data_quality_metrics.timeliness import Timeliness
from rest.data_quality_metrics.precision import Precision
from copy import deepcopy

BP_INTERNAL_STRUCTURE = "INTERNAL_STRUCTURE"
IN_TESTING_OUTPUT_DATA = 'Testing_Output_Data'
IN_TOD_METHOD_ID = 'method_id'
IN_TOD_ATTRIBUTES = 'attributes'

data_quality_page = Blueprint('data_quality', __name__)


@data_quality_page.route('/', methods=['POST'])
def compute_data_quality_metrics():
    # se non saranno passati come file allora bisognerà cambiare il tipo di request
    body = request.files['body']
    bp = request.files['bp']
    body = json.load(body)
    bp = json.load(bp)
    # extract method name from http body
    # non avendo idea di dove troveremo il nome del metodo al momento il sistema funziona con questo falso nome
    # TODO specificare il metodo per ottenere il nome del metodo della richiesta
    method_from_http = 'AMethod'
    print('processing method ' + method_from_http,file=sys.stderr)
    for method_id in bp[BP_INTERNAL_STRUCTURE][IN_TESTING_OUTPUT_DATA]:
        if method_id[IN_TOD_METHOD_ID] == method_from_http:
            method = deepcopy(method_id)
            break
    try:
        if IN_TOD_ATTRIBUTES not in method.keys():
            # calcolare tutte le metriche
            Accuracy().compute_metric(body, bp)
            Completeness().compute_metric(body, bp)
            Volume().compute_metric(body, bp)
            Consistency().compute_metric(body, bp)
            Timeliness().compute_metric(body, bp)
            Precision().compute_metric(body, bp)
            pass
        else:
            #calcolare solo metriche indicate in IN_TOD_ATTRIBUTES
            for attribute in method[IN_TOD_ATTRIBUTES]:
                import pdb; pdb.set_trace()
                if attribute.lower() == 'accuracy':
                    Accuracy().compute_metric(body, bp)
                elif attribute.lower() == 'completeness':
                    Completeness().compute_metric(body, bp)
                elif attribute.lower() == 'volume':
                    Volume().compute_metric(body, bp)
                elif attribute.lower() == 'consistency':
                    Consistency().compute_metric(body, bp)
                elif attribute.lower() == 'timeliness':
                    Timeliness().compute_metric(body, bp)
                elif attribute.lower() == 'precision':
                    Precision().compute_metric(body, bp)
        return json.dumps({'msg': 'operation completed!'})
    except:
        return json.dumps({'msg': 'invalid request!'})
