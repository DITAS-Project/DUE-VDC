# DUE-VDC REST API

This is the module which exposes the REST API providing the performance metrics for services and data. 

### Elastic Search source configuration
The data source is an instance of Elastic Search. The configuration information of the server running such instance
can be provided in the `conf/conf.json` file in the main root directory in the object `connections`.

### Running

To run the REST API is enough to launch the script `run_api.sh`

### REST API docs

The API structure is: <br>

{api_url}/{service}/{metrics}/{reference}/<reference_value>


- {service}: operation_id
- {metrics}: availability, throughput, response_time
- {reference}: sample, time
- <reference_value>: sample: #samples, time: minutes

### GET/POST DOC

(Here goes the documentation for the implemented GET/POST methods)

##### TODO 

(Here goes the list of GET/POST methods not yet implemented)
