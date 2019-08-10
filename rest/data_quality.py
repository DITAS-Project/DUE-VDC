import json
from flask import Blueprint, request
import rest.data_quality_metrics as dq

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
    for method in bp[BP_INTERNAL_STRUCTURE][IN_TESTING_OUTPUT_DATA]:
        if IN_TOD_ATTRIBUTES not in method.keys():
            # calcolare tutte le metriche
            dq.compute_accuracy()
            dq.compute_completeness()
            dq.compute_volume()
            dq.compute_consistency()
            dq.compute_timeliness()
            dq.compute_precision()
            pass
        else:
            #calcolare solo metriche indicate in IN_TOD_ATTRIBUTES
            for attributes in method[IN_TOD_ATTRIBUTES]:
                if attributes.lower() == 'accuracy':
                    dq.compute_accuracy()
                    pass
                elif attributes.lower() == 'completeness':
                    dq.compute_completeness()
                    pass
                elif attributes.lower() == 'volume':
                    dq.compute_volume()
                    pass
                elif attributes.lower() == 'consistency':
                    dq.compute_consistency()
                    pass
                elif attributes.lower() == 'timeliness':
                    dq.compute_timeliness()
                    pass
                elif attributes.lower() == 'precision':
                    dq.compute_precision()
                    pass

    return json.dumps({'msg': 'operation completed!'})
