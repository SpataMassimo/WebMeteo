#import shutil
import os
import time
import json
import pandas as pd
from datetime import datetime
import requests
from elasticsearch import Elasticsearch
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark import SparkFiles
from pyspark.sql.functions import *
from pyspark.sql.types import *
from evaluate_image import *         # File evaluate_image.py
from alert_and_request import *      # File alert_and_request.py
from data_regression import *      # File elaborate_regression.py

os.environ['TZ'] = 'Europe/Rome'
time.tzset()

KAFKA_BOOTSTRAP_SERVERS = "10.0.100.23:9092"
DATASET_HISTORICAL_DATA_FILE = "historical.json"
DATASET_DAILY_DATA_FILE = "daily_rows.json"
DATASET_HISTORICAL_DATA_PATH = "./demo/dataset/datas/historical.json"
DATASET_DAILY_DATA_PATH = "./demo/dataset/datas/daily_rows.json"
count_alert = 0

#Create a spark session
sc = SparkContext(appName="WebMeteo")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

spark.sparkContext.addFile(DATASET_HISTORICAL_DATA_PATH)
spark.sparkContext.addFile(DATASET_DAILY_DATA_PATH)
dataset_histirical_path = SparkFiles.get(DATASET_HISTORICAL_DATA_FILE)
dataset_daily_path = SparkFiles.get(DATASET_DAILY_DATA_FILE)


#Option for the connection to the elasticsearch
url_daily="http://elastic:9200/web_data_daily/_search?pretty"
url_historical = "http://elastic:9200/web_data_historical/_search?pretty"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
es = Elasticsearch("http://elastic:9200")

#---------------------------------------------------------------------------------#
# Read Streaming data from Kafka (topic: web_data)                                #
#---------------------------------------------------------------------------------#

#Read the data from the streaming kafka and save it in a dataframe 
dt = spark \
     .readStream \
     .format("kafka") \
     .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
     .option("subscribe", "web_data").option("startingOffsets", "earliest") \
     .load()

#Schema for the dataframe 
data_schema = StructType().add("City", StringType()) \
     .add("Schedule", StringType()).add("Temperature", IntegerType()).add("Humidity", IntegerType()) \
     .add("Wind", IntegerType()).add("Visibility", IntegerType()).add("Pressure", IntegerType()) \
     .add("Condition", StringType())

#Extract the values from the dataframe in streaming  
data_received = dt.selectExpr("CAST(value AS STRING)") \
     .select(from_json(col("value"), data_schema).alias("data_received")) \
     .select("data_received.*")

#df_regression = spark.createDataFrame([], data_schema)

#---------------------------------------------------------------------------------#
# Read Streaming images from Kafka (topic: web_image)                             #
#---------------------------------------------------------------------------------#

#Read the image from the streaming kafka and save it in a dataframe 
img = spark \
     .readStream \
     .format("kafka") \
     .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
     .option("subscribe", "web_image").option("startingOffsets", "earliest") \
     .option("auto.offset.reset", "latest") \
     .load()   

#Schema for the dataframe image
image_schema = StructType().add("Image", StringType()).add("Schedule", TimestampType())

#Extract the values from the dataframe image in streaming  
image_received = img.selectExpr("CAST(value AS STRING)") \
     .select(from_json(col("value"), image_schema).alias("image_received")) \
     .select("image_received.*")



#Process the data received from the kafka
def add_row(data_row, batch_id): 
     if(data_row.count() > 0):
          print("DATA RECEIVED FROM KAFKA")
          datas = data_row.toPandas()
          print(datas)
          print("--------------------------------------------------------")
          
          #Send the data to elasticsearch in "web_data" index and save in web_data_daily.json file
          records = datas.to_dict(orient='records')
          for j in range(len(records)):
               dat = records[j]
               val = es.index(index='web_data_daily', id = dat["Schedule"],  document=json.dumps(records[j]))
               print(val)
               print("----------------------------------------------------")
               with open(DATASET_DAILY_DATA_PATH, "a+") as file_object:
                    index_diz = {"index" :{ "_id" : dat["Schedule"]}}
                    file_object.write(json.dumps(index_diz))
                    file_object.write("\n")
                    file_object.write(json.dumps(records[j]))
                    file_object.write("\n")
               file_object.close()

          #Perform Linear Regressione from the data for prediction
          data_regression(data_row)
          
          #Extract the interval Data value from dataframe for processing the query     
          day = datas.iloc[0][1]
          day = datetime.strptime(day, '%Y-%m-%d %H:%M:%S')
          today_gte = str(day.strftime('%Y-%m-%d')) + " 00:00:00"
          today_lte = str(day.strftime('%Y-%m-%d')) + " 23:59:59"

          #Query to get datas from daily relevations 
          avg_daily = """{
               "size" : 0,
               "query": {
                    "bool": {
                         "must": { "match_all": {} },
                              "filter": {
                              "range": {
                                   "Schedule": {
                                        "gte": """ + "\"" + today_gte + "\"" + """,
                                        "lte": """ + "\"" + today_lte + "\"" + """
                                   }
                              }
                         }
                    }
               },
               "aggs": {
                    "TempAvg": {
                         "avg": {
                              "field": "Temperature",
                              "format": "#0;(#0)"
                         }
                    },
                    "TempMin": {
                         "min": {
                              "field": "Temperature",
                              "format": "#0;(#0)"
                         }
                    },
                    "TempMax": {
                         "max": {
                              "field": "Temperature",
                              "format": "#0;(#0)"
                         }
                    },
                    "Humidity": {
                         "avg": {
                              "field": "Humidity",
                              "format": "#0;(#0)"
                         }
                    },
                    "Visibility": {
                         "avg": {
                              "field": "Visibility",
                              "format": "#0;(#0)"
                         }
                    },
                    "WindAvg": {
                         "avg": {
                              "field": "Wind",
                              "format": "#0;(#0)"
                         }
                    },
                    "WindMax": {
                         "max": {
                              "field": "Wind",
                              "format": "#0;(#0)"
                         }
                    },
                    "Pressure": {
                         "avg": {
                              "field": "Pressure",
                              "format": "#0;(#0)"
                         }
                    }
               } 
          }"""
     
          daily_datas = requests.post(url_daily ,data=avg_daily, headers=headers) 
          daily_json =  daily_datas.json()['aggregations']
          dict_daily = {"City": "Catania", "Day": str(day.strftime('%Y-%m-%d')), "TempAvg": daily_json["TempAvg"]["value_as_string"], "TempMin": daily_json["TempMin"]["value_as_string"], "TempMax": daily_json["TempMax"]["value_as_string"], "Humidity": daily_json["Humidity"]["value_as_string"], "Visibility":daily_json["Visibility"]["value_as_string"], "WindAvg": daily_json["WindAvg"]["value_as_string"], "WindMax": daily_json["WindMax"]["value_as_string"], "Pressure": daily_json["Pressure"]["value_as_string"]} 
          data_id = str(day.strftime('%Y-%m-%d'))
          
          #Verify if the data id is already in elasticseacrh, if exist delete it and insert new data, 
          if(es.exists(index='web_data_historical', id=data_id)):
               deleting =es.delete(index='web_data_historical', id=data_id)
               print("DELETE DATA ID: " + data_id + " FROM ELASTICSEARCH")
               print(deleting)
               print("------------------------------------------------------")
               #Modify the data in historical.json file
               elements = []
               with open(DATASET_HISTORICAL_DATA_PATH) as f:
                    for line in f:
                         elements.append(json.loads(line))
               f.close()
               for item in elements:
                    if 'Day' in item: 
                         if item['Day'] == str(day.strftime('%Y-%m-%d')):
                              item["TempAvg"] = daily_json["TempAvg"]["value_as_string"]
                              item["TempMin"] = daily_json["TempMin"]["value_as_string"]
                              item["TempMax"] = daily_json["TempMax"]["value_as_string"]
                              item["Humidity"] = daily_json["Humidity"]["value_as_string"]
                              item["Visibility"] = daily_json["Visibility"]["value_as_string"]
                              item["WindAvg"] = daily_json["WindAvg"]["value_as_string"]
                              item["WindMax"] = daily_json["WindMax"]["value_as_string"]
                              item["Pressure"] = daily_json["Pressure"]["value_as_string"]
               with open(DATASET_HISTORICAL_DATA_PATH, 'w') as f:
                    for item in elements:
                         json.dump(item, f)
                         f.write("\n")
               f.close()
               print("FILE historical.json MODIFIED")
               print("------------------------------------------------------")
          else:
               with open(DATASET_HISTORICAL_DATA_PATH, "a+") as file_object:
                    index_diz = {"index" :{ "_id" : str(day.strftime('%Y-%m-%d'))}}
                    file_object.write(json.dumps(index_diz))
                    file_object.write("\n")
                    file_object.write(json.dumps(dict_daily))
                    file_object.write("\n")
               file_object.close()
          
          indexing = es.index(index='web_data_historical', id = str(day.strftime('%Y-%m-%d')),  document=json.dumps(dict_daily))
          print(indexing)
          print("------------------------------------------------------")
     
     else:     
          print("NO DATA RECEIVED FROM KAFKA")

data_received.writeStream.trigger(processingTime='120 seconds').foreachBatch(add_row).start()




#Process the image received from the kafka
def add_image(image_data, batch_id):
     global count_alert
     if(image_data.count() > 0):
          print("IMAGE RECEIVED FROM KAFKA")
          image_data.show()

          #Convert into pandas dataframe
          pandasImage = image_data.toPandas()

          for index, row in pandasImage.iterrows():
               #Extract image string for evaluation
               image_string = str(row['Image'])
               
               #Evaluate the image
               class_prediction = evaluate_image(image_string)
               
               #Row to send to elasticsearch
               day = row['Schedule']
               dict_image = {"Schedule": day, "Evaluate": class_prediction}
               print (dict_image)
               val = es.index(index='web_image',  document=(json.dumps(dict_image, default=str)))
               print(val)
               
               #Condition alert
               count_alert = alert_condition(class_prediction, count_alert)
               #Condition reset driver
               send_restart_request(restart_condition(class_prediction), spark)
     else:
          print("NO IMAGE RECEIVED FROM KAFKA")
image_received.writeStream.foreachBatch(add_image).start().awaitTermination()