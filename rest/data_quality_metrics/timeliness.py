from .data_quality_metric import DataQualityMetric

class Timeliness(DataQualityMetric):
    def __init__(self, conf_path='conf/conf.json'):
        super().__init__(conf_path)

    def compute_metric(self, body_request, blueprint):
        print('Now computing timeliness!')
        # TODO compute metrics

        bp_id = '1'
        vdc_inst = '2'
        request_id = '3'
        operation_id = '4'
        value = '5'
        name = "precision"
        unit = '7'
        hit_timestamp = '8'
        computation_timestamp = '9'
        super().write(bp_id, vdc_inst, request_id, operation_id, value, name, unit, hit_timestamp, computation_timestamp)