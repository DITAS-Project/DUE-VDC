# DUE-VDC

This is the DUE-VDC module. It is responsible for computing data metrics
both periodically and on-deman via an exposed REST API. 

### Elastic Search source configuration
The data source is an instance of Elastic Search. The configuration information of the server running such instance
can be provided in the `conf/conf.json` file in the main root directory in the object `connections`.

### Launch the REST API

To run the REST API is enough to launch the script `run_api.sh` after installing the requirements using `pip3` or to launch the docker container.

### REST API docs

The swagger documentation is at `https://{hostname}/api/doc/`

The API structure is: <br>

{api_url}/{metrics}/{service}/{reference}/<reference_value>

- {metrics}: availability, throughput, response_time
- {service}: operation_id
- {reference}: sample, time
- <reference_value>: sample: #samples, time: minutes

Quality of data API stucture: <br>

{api_url}/data_quality/

Input requested, passed via POST in a json encoded body:

- body of the request
- blueprint

Note:
for what concerns the quality of the data via REST API,
the body of the request is not proccessed by now, due to lack of examples
to test the behaviour.
The following modifications have to be done in order to complete the API:
- in rest/data_quality.py, extract from the method name from the request and assign to
"method_from_http" variable.
- implement all the methods to compute the data quality in rest/data_quality_metrics/
  The methods have to save the output to ElasticSearch by providing the following information:
	- bp_id = blueprint identifier
	- vdc_inst = instance of the VDC
	- request_id = identier of the request
	- operation_id = identifier of the operation
	- value = output to print on ElasticSearch
	- name = name of the metric
	- unit = unit of measurement of the metric
	- hit_timestamp = timestamp of the hit
	- computation_timestamp = timestamp of the computatation

In order to let the REST API use ElasticSearch, some connection information
have to be provided. This information are gathered from `conf/conf.json`.



### GET/POST DOC

(Here goes the documentation for the implemented GET/POST methods)

##### TODO 

Refer to [TODO file](https://github.com/DITAS-Project/DUE-VDC/blob/master/TODO.md)
