### Project TAP 2022 University of Catania, Prof. Salvo Nicotra
#### Students: Privitera Salvatore, Spata Massimo

# WebMeteo
Tired of looking at web pages for the weather and hoping it matches? .. yes, me too. WebMeteo
is an application that, with the use of recent technologies, allows you to collect meteorological data
including, in particular, the weather conditions; thanks to the latter it is possible to classify appropriately
the status of a particular event and show precise data predictions!

## Features
* Collection of meteorological data with python and Selenium
* Using Fluentd for the injection of weather data
* Using Apache Kafka to stream weather events
* Elaboration of the weather conditions with Apache Spark (Data Regression and Image Classification)
* Use of Elasticsearch to store and easily retrieve the collected data
* Using Kibana to view the data recorded in Elasticsearch

## Pipeline
<p align="center">
  <img src="gitData/pipeline.png" alt="pipeline" width=800/>
</p>

## How to Run
```shell
git clone https://github.com/erotablas/WebMeteo.git
# or https://github.com/SpataMassimo/WebMeteo.git
cd WebMeteo
docker-compose up --build
```

## Links
| Container     | URL                                        | Description                                     |
| ------------- | ------------------------------------------ | ----------------------------------------------- |
| kafka UI      | http://localhost:8080                      | Open kafka UI to monitor Kafka Broker           |
| Elasticsearch | http://localhost:9200                      | Open Elasticsearch to manage indexes            |
| kibana        | http://localhost:5601                      | Open Kibana to view data and create a dashboard |

## Bibliography
[Datas Resources](http://www.meteoam.it/ta/infoStazione/LICC/catania_fontana_rossa)
[Images Resources](https://www.skylinewebcams.com/en/webcam/italia/sicilia/catania/centro-di-catania.html)

[Docker](https://www.docker.com/)
[Selenium Python](https://selenium-python.readthedocs.io/)
[Fluentd](https://www.fluentd.org/)
[Apache Kafka](https://kafka.apache.org/)
[Apache Spark](https://spark.apache.org/)
[Elasticsearch](https://www.elastic.co/elasticsearch/)
[Kibana](https://www.elastic.co/kibana/)
