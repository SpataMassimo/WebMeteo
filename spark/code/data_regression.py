from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import PipelineModel
from elasticsearch import Elasticsearch
import os
import json
import itertools

url_prediction = "http://elastic:9200/web_data_prediction/_search?pretty"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
es = Elasticsearch("http://elastic:9200")
path = "./demo/model_data"

def load_model_data():
    if(os.path.exists(path)):
        model = PipelineModel.load(path)
        return model

def data_regression(df):
    model = load_model_data()
    data = df.withColumn("Condition", when(df.Condition == "SERENO", 0).when(df.Condition == "SERENO O NUBI NON SIGNIFICATIVE", 0) \
                   .when(df.Condition == "POCO NUVOLOSO", 1).when(df.Condition == "NUVOLOSO", 1).otherwise(2))
   
    data = data.select( 
                col("Temperature").cast("float"),
                col("Humidity").cast("float"),
                col("Wind").cast("float"),
                col("Visibility").cast("float"),
                col("Pressure").cast("float"),
                col("Condition").cast("float"))
    
    
    results = model.transform(data)
    results.show()

    for row, row2 in zip(results.collect(), df.collect()):
        #row[-1] e' il risultato dell'ultima colonna (prediction)
        dict = {"City":row2[0], "Schedule":row2[1], "Temperature":row[0], "Humidity":row[1], "Wind":row[2], "Visibility":row2[3], "Pressure":row2[4], "Prediction":row[-1]}
        val = es.index(index='web_data_prediction', id = row2[1],  document=json.dumps(dict))
        print("---------------------------------------------------------------------")
        print(val)
        print("---------------------------------------------------------------------")