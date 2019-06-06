# DUE-VDC REST API

This is the module which exposes the REST API providing the performance metrics for services and data. 

### Elastic Search source configuration
The configuration information of the instance of Elastic Search containing the data source can be provided
in the `conf/conf.json` file in the main root directory

### API

The API structure is: <br>

{api_url}/{service}/{metrics}/{reference}/<reference_value>


- {service}: operation_id
- {metrics}: availability, throughput, response_time
- {reference}: sample, time
- <reference_value>: sample: #samples, time: minutes

### GET/POST DOC

(Here goes the documentation for the implemented GET/POST methods)
